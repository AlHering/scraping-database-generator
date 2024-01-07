# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import uvicorn
from enum import Enum
import traceback
from typing import Optional, Any
from datetime import datetime as dt
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from functools import wraps
from src.configuration import configuration as cfg
from src.control.backend_controller import BackendController, FilterMask

"""
Backend control
"""
BACKEND = FastAPI(title="Scraping Database Generator Backend", version="0.1",
                  description="Backend for serving Scraping Database Generator services.")
CONTROLLER: BackendController = BackendController()


def interface_function() -> Optional[Any]:
    """
    Validation decorator.
    :param func: Decorated function.
    :return: Error message if status is incorrect, else function return.
    """
    global CONTROLLER

    def wrapper(func: Any) -> Optional[Any]:
        """
        Function wrapper.
        :param func: Wrapped function.
        :return: Error message if status is incorrect, else function return.
        """
        @wraps(func)
        async def inner(*args: Optional[Any], **kwargs: Optional[Any]):
            """
            Inner function wrapper.
            :param args: Arguments.
            :param kwargs: Keyword arguments.
            """
            requested = dt.now()
            try:
                response = await func(*args, **kwargs)
                response["status"] = "successful"
            except Exception as ex:
                response = {
                    "status": "failed",
                    "exception": ex,
                    "trace": traceback.format_exc()
                }
            responded = dt.now()
            CONTROLLER.post_object(
                "log",
                request={
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                },
                response=response,
                requested=requested,
                responded=responded
            )
            return response
        return inner
    return wrapper


"""
Dataclasses
"""


"""
Backend endpoint enumerator
"""


class Endpoints(str, Enum):
    """
    String-based endpoint enum class.
    """
    BASE = "/api/v1"

    def __str__(self) -> str:
        """
        Getter method for a string representation.
        """
        return self.value


"""
Endpoints
"""


"""
Language model instances
"""


"""
Backend runner
"""


def run_backend(host: str = None, port: int = None, reload: bool = True) -> None:
    """
    Function for running backend server.
    :param host: Server host. Defaults to None in which case "127.0.0.1" is set.
    :param port: Server port. Defaults to None in which case either environment variable "BACKEND_PORT" is set or 7861.
    :param reload: Reload flag for server. Defaults to True.
    """
    uvicorn.run("src.interfaces.backend_interface:BACKEND",
                host="127.0.0.1" if host is None else host,
                port=int(
                    cfg.ENV.get("BACKEND_PORT", 7861) if port is None else port),
                reload=reload)


if __name__ == "__main__":
    run_backend()
