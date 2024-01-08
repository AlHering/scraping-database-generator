# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import time
from threading import Thread
from src.configuration import configuration as cfg
from src.interfaces.backend_interface import run_backend
import streamlit.web.bootstrap as streamlit_bootstrap


if __name__ == "__main__":
    backend_thread = Thread(
        run_backend
    )
    frontend_thread = Thread(
        streamlit_bootstrap.run,
        args=(os.path.join(cfg.PATHS.SOURCE_PATH, "view", "streamlit_frontends", "app.py"),
              "", [], [],)
    )
    for thread in [backend_thread, frontend_thread]:
        thread.daemon = True
        thread.start()
        time.sleep(4)
