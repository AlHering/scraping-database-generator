# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from src.configuration import configuration as cfg
import streamlit.web.bootstrap as streamlit_bootstrap


if __name__ == "__main__":
    streamlit_bootstrap.run(os.path.join(cfg.PATHS.SOURCE_PATH, "view", "streamlit_frontends", "app.py"),
                            "", [], [],)
