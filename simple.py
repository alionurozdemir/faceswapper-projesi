import gradio as gr
from PIL import Image
import sys
import tempfile
from facefusion import core

def run_cli(cli_args):
  old_argv = sys.argv
  try:
    sys.argv = ['run.py', *cli_args]
    core.cli()
  finally:
    sys.argv = old_argv

def swap_faces(source_image_path, target_image_path, enhance_face=True, enhance_frame=True):
  provider = 'cpu'

  target_ext = target_image_path.split('.')[-1]
  output_image_file = tempfile.NamedTemporaryFile(suffix=f'.{target_ext}')
  output_image_path = output_image_file.name

  print(source_image_path)
  print(target_image_path)
  print(output_image_path)

  cli_args = [
    '--headless',
    '-s', source_image_path,
    '-t', target_image_path,
    '-o', output_image_path,
    '--output-image-quality', '80',
    '--execution-providers', provider,
    # '--face-detector-model', 'yunet',
    '--face-analyser-order', 'large-small',
  ]

  cli_args += [ '--frame-processors', 'face_swapper' ]
    
  if enhance_face:
    cli_args += [
      'face_enhancer',
    ]

  if enhance_frame:
    cli_args += [
      'frame_enhancer',
    ]

  from facefusion.processors.frame.core import clear_frame_processors_modules
  clear_frame_processors_modules()

  run_cli(cli_args)

  return Image.open(output_image_path)

demo = gr.Interface(
  fn=swap_faces,
  inputs=[
      gr.Image(type="filepath"),
      gr.Image(type="filepath"),
      gr.Checkbox(label="Enhance Face", value=True),
      gr.Checkbox(label="Enhance Frame", value=True),
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

if __name__ == "__main__":
    demo.launch()