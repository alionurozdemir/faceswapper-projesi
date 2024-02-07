import logging
from logging.config import dictConfig

from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar('request_id', default='')
request_session: ContextVar[dict] = ContextVar('request_session', default={})


# import logging

class RequestIDFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True


log_config = {
    "disable_existing_loggers": False,
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s %(pathname)s %(module)s %(lineno)d -> %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S %z'
        }},
    'handlers': {'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'default',
        "stream": "ext://sys.stdout"
    }},
    "loggers": {
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
}

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    'filters': {
        'request_id_filter': {
            "()": RequestIDFilter
        }
    },
    "formatters": {
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': '[%(asctime)s] [%(request_id)s] %(levelprefix)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S %z",
            "use_colors": True
        },
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            'fmt': '[%(asctime)s] [%(request_id)s] %(levelname)s %(pathname)s %(module)s %(lineno)d -> %(message)s',
            # 'fmt': '[%(asctime)s] %(levelname)s %(pathname)s %(module)s %(lineno)d -> %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S %z',
            "use_colors": True
        },
    },
    "handlers": {
        'access': {
            'class': 'logging.StreamHandler',
            'formatter': 'access',
            'stream': 'ext://sys.stdout',
            "filters": ['request_id_filter']

        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ['request_id_filter']
        },
    },
    "loggers": {
        "log": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': 'INFO',
            'propagate': False
        },
        'uvicorn.error': {
            'level': 'INFO',
            'propagate': False
        }
    },
}

dictConfig(log_config)

logger = logging.getLogger("log")