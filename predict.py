# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md
import shutil
import gradio as gr

# from cog import BasePredictor, Input, Path

import insightface
import onnxruntime
from insightface.app import FaceAnalysis
import cv2
import gfpgan
import tempfile
import time
import uuid
from typing import Any, Union
from loggers import logger, request_id as _request_id
import ssl
from datetime import datetime
import traceback
import torch
import os
import requests
import subprocess
import sys
from PIL import Image
import numpy as np

ssl._create_default_https_context = ssl._create_unverified_context

if sys.platform == 'darwin':
    cache_file_dir = '/tmp/file'
else:
    cache_file_dir = '/src/file'
os.makedirs(cache_file_dir, exist_ok=True)


def img_url_to_local_path(img_url, file_path=None):
    filename = img_url.split('/')[-1]
    max_count = 3
    count = 0
    if file_path is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
        temp_file_name = temp_file.name
    else:
        temp_file_name = file_path
    while True:
        count += 1
        try:
            res = requests.get(img_url, timeout=60)
            res.raise_for_status()
            with open(temp_file_name, "wb") as f:
                f.write(res.content)
            return temp_file_name
        except Exception as e:
            logger.error(e)
        if count >= max_count:
            msg = f'request {max_count} time url: {img_url} failed, please check'
            logger.error(msg)
            raise Exception(msg)


def delete_files_day_ago(cache_days=10):
    command = f"find {cache_file_dir} -type f -ctime +{cache_days} -exec rm {{}} \;"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    logger.info(result.stdout)


def image_format_by_path(image_path):
    image = Image.open(image_path)
    image_format = image.format
    if not image_format:
        image_format = 'jpg'
    elif image_format == "JPEG":
        image_format = 'jpg'
    else:
        image_format = image_format.lower()
    return image_format


def local_file_for_url(url, cache_days=10):
    filename = url.split('/')[-1]
    _, ext = filename.split('.')
    file_path = f'{cache_file_dir}/{filename}'
    if not os.path.exists(file_path):
        img_url_to_local_path(url, file_path)
        logger.info(f'download file to {file_path}')
        delete_files_day_ago(cache_days)
    else:
        logger.info(f'cache file {file_path}')
    return file_path


class Predictor:
    def __init__(self):
        self.det_thresh = 0.1

    def setup(self):
        self.face_swapper = insightface.model_zoo.get_model('cache/inswapper_128.onnx', providers=onnxruntime.get_available_providers())
        self.face_enhancer = gfpgan.GFPGANer(model_path='cache/GFPGANv1.4.pth', upscale=1)
        self.face_analyser = FaceAnalysis(name='buffalo_l')

    def get_face(self, img_data, image_type='target'):
        try:
            logger.info(self.det_thresh)
            self.face_analyser.prepare(ctx_id=0, det_thresh=0.5)
            if image_type == 'source':
                self.face_analyser.prepare(ctx_id=0, det_thresh=self.det_thresh)
            analysed = self.face_analyser.get(img_data)
            logger.info(f'face num: {len(analysed)}')
            if len(analysed) == 0:
                msg = 'no face'
                logger.error(msg)
                raise Exception(msg)
            largest = max(analysed, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
            return largest
        except Exception as e:
            logger.error(str(e))
            raise Exception(str(e))

    def enhance_face(self, target_face, target_frame, weight=0.5):
        start_x, start_y, end_x, end_y = map(int, target_face['bbox'])
        padding_x = int((end_x - start_x) * 0.5)
        padding_y = int((end_y - start_y) * 0.5)
        start_x = max(0, start_x - padding_x)
        start_y = max(0, start_y - padding_y)
        end_x = max(0, end_x + padding_x)
        end_y = max(0, end_y + padding_y)
        temp_face = target_frame[start_y:end_y, start_x:end_x]
        if temp_face.size:
            _, _, temp_face = self.face_enhancer.enhance(
                temp_face,
                paste_back=True,
                weight=weight
            )
            target_frame[start_y:end_y, start_x:end_x] = temp_face
        return target_frame

    def predict(
            self,
            source_image_path,
            target_image_path,
            enhance_face,
            # request_id: str = Input(description="request_id", default=""),
            # det_thresh: float = Input(description="det_thresh default 0.1", default=0.1),
            # local_target: Path = Input(description="local target image", default=None),
            # local_source: Path = Input(description="local source image", default=None),
            # cache_days: int = Input(description="cache days default 10", default=10),
            # weight: float = Input(description="weight default 0.5", default=0.5)

    ) -> Any:
        """Run a single prediction on the model"""
        request_id = None
        det_thresh = 0.1
        cache_days = 10
        weight = 0.5

        device = 'cuda' if torch.cuda.is_available() else 'mps'
        logger.info(f'device: {device}, det_thresh:{det_thresh}')

        try:
            self.det_thresh = det_thresh
            start_time = time.time()
            if not request_id:
                request_id = str(uuid.uuid4())
            _request_id.set(request_id)
            frame = cv2.imread(str(target_image_path))
            source_frame = cv2.imread(str(source_image_path))
            source_face = self.get_face(source_frame, image_type='source')
            target_face = self.get_face(frame)
            try:
                logger.info(f'{frame.shape}, {target_face.shape}, {source_face.shape}')
            except Exception as e:
                logger.error(f"printing shapes failed,  error:{str(e)}")
                raise Exception(str(e))
            ext = image_format_by_path(target_image_path)
            size = os.path.getsize(target_image_path)
            logger.info(f'origin {size/1024}k')
            result = self.face_swapper.get(frame, target_face, source_face, paste_back=True)
            if enhance_face:
                result = self.enhance_face(target_face, result, weight)
            # _, _, result = self.face_enhancer.enhance(
            #     result,
            #     paste_back=True
            # )
            out_path = f"{tempfile.mkdtemp()}/{uuid.uuid4()}.{ext}"
            cv2.imwrite(str(out_path), result)
            return Image.open(out_path) 

            size = os.path.getsize(out_path)
            logger.info(f'result {size / 1024}k')
            cost_time = time.time() - start_time
            logger.info(f'total time: {cost_time * 1000} ms')
            data = {'code': 200, 'msg': 'succeed', 'image': out_path, 'status': 'succeed'}
            return data
        except Exception as e:
            logger.error(traceback.format_exc())
            data = {'code': 500, 'msg': str(e), 'image': '', 'status': 'failed'}
            logger.error(f"{str(e)}")
            return data

def swap_faces(source_image_path, target_image_path, enhance_face):
    predictor = Predictor()
    predictor.setup()
    return predictor.predict(
        source_image_path,
        target_image_path,
        enhance_face
    )

if __name__ == "__main__":
    demo = gr.Interface(
      fn=swap_faces,
      inputs=[
          gr.Image(type="filepath"),
          gr.Image(type="filepath"),
          gr.Checkbox(label="Enhance Face", value=True),
        #   gr.Checkbox(label="Enhance Frame", value=True),
      ],
      outputs=[
          gr.Image(
            type="pil",
            show_download_button=True,
          )
      ],
      title="Swap Faces",
      allow_flagging="never"
    )
    demo.launch()