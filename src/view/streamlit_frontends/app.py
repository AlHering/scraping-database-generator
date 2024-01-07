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
from src.utility.bronze import streamlit_utility, json_utility, requests_utility
from src.utility.silver.file_system_utility import safely_create_path
import requests


def send_request(method: str, url: str, headers: dict = None, parameters: dict = None, json: dict = None) -> requests.Response:
    """
    Function for sending off request.
    :param method: Method to use.
    :param url: Target URL.
    :param headers: Request headers.
    :param parameters: API parameters.
    :param json: JSON payload.
    """
    return requests_utility.REQUEST_METHODS[method.upper()](
        url=url,
        params=parameters,
        headers=headers,
        json=json
    )


def run_page() -> None:
    """
    Function for running the main page.
    """
    st.title("Scraping Database Generator")
    st.header("API Workbench")

    left, right = st.columns(2)

    method = left.selectbox(
        "Request method", options=["Get", "Post", "Patch", "Put", "Delete"],
        index=st.session_state["CACHE"]["method"])
    url = left.text_input("URL", value=st.session_state["CACHE"]["url"])
    if left.button("Send"):
        response = send_request(
            method=method, url=url, )
        st.session_state["CACHE"]["response"] = response.json()
        st.session_state["CACHE"]["response_status"] = response.status_code
        st.session_state["CACHE"]["response_header"] = response.headers

    left.divider()
    right.text("Headers: ")
    st.session_state["CACHE"]["headers"] = None
    left.divider()
    right.text("Parameters: ")
    st.session_state["CACHE"]["parameters"] = None
    left.divider()
    right.text("JSON Payload: ")
    st.session_state["CACHE"]["json"] = None

    right.text("Status: " + str(st.session_state["CACHE"]["response_status"]))
    right.divider()
    right.text("Header: ")
    right.json(st.session_state["CACHE"]["response_header"])
    right.divider()
    right.text("Response Content: ")
    right.json(st.session_state["CACHE"]["response"])

    save_cache_button = st.sidebar.button("Save state")
    if save_cache_button:
        with st.spinner("Saving State..."):
            json_utility.save(
                st.session_state["CACHE"], cfg.PATHS.FRONTEND_CACHE)


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
            "parameters": {},
            "json": None,
            "response": {},
            "response_status": -1,
            "response_header": {}
        }
    run_page()


if __name__ == "__main__":
    run_app()
