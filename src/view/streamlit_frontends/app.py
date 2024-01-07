# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import copy
from time import sleep
from typing import Any
from uuid import uuid4
import streamlit as st
from src.configuration import configuration as cfg
from src.utility.bronze import streamlit_utility, json_utility
from src.utility.silver.file_system_utility import safely_create_path
import json
import requests


def run_page() -> None:
    """
    Function for running the main page.
    """
    st.title("Scraping Database Generator")
    st.header("API Workbench")


def run_app() -> None:
    """
    Main runner function.
    """
    st.set_page_config(
        page_title="Scraping Database Generator",
        page_icon=":books:"
    )
    if os.path.exists(cfg.PATHS.FRONTEND_CACHE):
        with st.spinner("Loading State..."):
            st.session_state["CACHE"] = json_utility.load(
                cfg.PATHS.FRONTEND_CACHE)
    else:
        st.session_state["CACHE"] = {
            "method": 0,
            "url": "",
            "headers": {},
            "parameters": {}
        }
    run_page()


if __name__ == "__main__":
    run_app()
