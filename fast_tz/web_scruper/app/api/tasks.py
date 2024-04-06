import datetime
import logging
import os
import time
import traceback

from celery import shared_task, states
from celery.exceptions import Ignore
from django.conf import settings

from app.api.scrupers.fb_scruper import fb_scruper
from settings.base import DEBUG_LOG_FILE_HANDLER_NAME

logger = logging.getLogger(__name__)


def get_log_dir(task):
    log_dir = settings.TASK_LOG_DIR.replace("%(task_name)", task.name)
    return log_dir


def get_log_path(task):
    log_dir = get_log_dir(task)
    os.makedirs(log_dir, exist_ok=True)
    log_path = settings.TASK_LOG_FILE_PATH.replace("%(task_name)", task.name).replace(
        "%(task_id)", task.request.id
    )
    return log_path


class TaskLogFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)

        try:
            os.utime(self.baseFilename, (time.time(), time.time()))
        except Exception:
            pass


def parse_parameters(payload):
    parameters = {}

    for arg_name, arg_value in payload.items():
        if "password" in arg_name or "refresh_token" in arg_name:
            parameters[arg_name] = "************"
        else:
            parameters[arg_name] = arg_value
    return parameters


def create_task_log_file_handler(task):
    file_handler = TaskLogFileHandler(get_log_path(task))
    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s "
        "%(name)s.%(funcName)s:%(lineno)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    file_handler.set_name(name=f'task_log_file_handler_{task.request.id}')
    return file_handler


def reset_root_logger(handlers):
    root_logger = logging.getLogger("")
    root_logger.handlers = handlers


def configure_root_logger(task):
    root_logger = logging.getLogger("")
    handlers = list(root_logger.handlers)
    for handler in handlers:
        if handler.name == DEBUG_LOG_FILE_HANDLER_NAME:
            root_logger.removeHandler(hdlr=handler)
    file_handler = create_task_log_file_handler(task=task)
    root_logger.addHandler(hdlr=file_handler)
    return root_logger, handlers


def custom_task(task_function):
    @shared_task(
        bind=True,
        name=f"{task_function.__name__}",
        time_limit=settings.CELERY_HARD_TIMEOUT,
        soft_time_limit=settings.CELERY_TIMEOUTS_BY_TASK.get(task_function.__name__, settings.CELERY_TIMEOUT),
        acks_late=True,
    )
    def wrapper(self, *args, **kwargs):
        self.backend.task_keyprefix = bytes(self.name, encoding="utf-8")
        result = {
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None,
            "log": settings.LOG_LINK.replace("%(task_name)", self.name).replace(
                "%(task_id)", self.request.id
            ),
            "data": None,
            "parameters": parse_parameters(kwargs['payload']),
            "metadata": {
                "worker_name": self.request.hostname,
            },
        }
        logger.info(f"Running '{self.name}' task with id '{self.request.id}', initial result: {result}")
        self.update_state(state=states.PENDING, meta=result)
        task_logger, previous_handlers = configure_root_logger(self)
        try:
            result_data = task_function(self, *args)
            result["data"] = result_data
            result["end_time"] = datetime.datetime.now().isoformat()
            result["return_code"] = 0
        except Exception as e:
            task_logger.error(traceback.format_exc())
            result["return_code"] = 1
            result["end_time"] = datetime.datetime.now().isoformat()
            result["error_details"] = str(e)
            result["error_type"] = str(type(e).__name__)
            self.update_state(state=states.FAILURE, meta=result)
            raise Ignore()
        finally:
            reset_root_logger(handlers=previous_handlers)
        return result

    return wrapper


class TaskFailure(Exception):
    pass

# Main tasks secution


@custom_task
def fb_scrup(self, config):
    result = fb_scruper(config)
    return result