# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any
import streamlit as st
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, requests_utility
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

    column_splitter_args = tuple([0.5, 0.5], gap="medium")
    first_left, first_right = st.columns(*column_splitter_args)
    request_form = first_left.form("Request", clear_on_submit=True)

    sending_line_left, sending_line_middle, sending_line_right = request_form.columns(
        [0.14, 0.76, 0.1])

    method = sending_line_left.selectbox("Method", options=["Get", "Post", "Patch", "Put", "Delete"],
                                         index=st.session_state["CACHE"]["method"])
    url = sending_line_middle.text_input(
        "URL", value=st.session_state["CACHE"]["url"])
    sending_line_right.markdown("## ")
    if sending_line_right.form_submit_button("Send"):
        response = send_request(
            method=method, url=url, )
        st.session_state["CACHE"]["response"] = response.json()
        st.session_state["CACHE"]["response_status"] = response.status_code
        st.session_state["CACHE"]["response_header"] = response.headers

    first_right.subheader(
        "Status: " + str(st.session_state["CACHE"]["response_status"]))

    st.divider()
    second_left, second_right = st.columns(*column_splitter_args)
    second_left.text("Headers: ")

    second_right.text("Header: ")
    second_right.json(st.session_state["CACHE"]["response_header"])
    st.session_state["CACHE"]["headers"] = None

    st.divider()
    third_left, third_right = st.columns(*column_splitter_args)

    third_left.text("Parameters: ")
    st.session_state["CACHE"]["parameters"] = None
    third_left.divider()
    third_left.text("JSON Payload: ")
    st.session_state["CACHE"]["json"] = None

    third_right.text("Response Content: ")
    third_right.json(st.session_state["CACHE"]["response"])

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
        page_icon=":books:",
        layout="wide"
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
