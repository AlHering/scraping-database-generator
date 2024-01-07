# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import copy
from typing import Any, Callable
import streamlit as st
import pandas as pd
from streamlit_server_state import server_state, server_state_lock, force_rerun_bound_sessions
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, requests_utility
from src.utility.silver.file_system_utility import safely_create_path
import requests


def load_state() -> None:
    """
    Function for loading server state.
    """
    with st.spinner("Loading State..."):
        if os.path.exists(cfg.PATHS.FRONTEND_CACHE):
            state = json_utility.load(
                cfg.PATHS.FRONTEND_CACHE)
        else:
            state = {
                "method": 0,
                "url": "",
                "headers": {},
                "parameters": {},
                "json": None,
                "response": {},
                "response_status_message": "No request sent.",
                "response_status": -1,
                "response_header": {}
            }

        for field in state:
            with server_state_lock[field]:
                if isinstance(state[field], dict):
                    state[field] = pd.DataFrame(
                        [{"key": key, "value": value}
                            for key, value in state[field].items()],
                        columns=["value"],
                        index=["key"])
                setattr(server_state, field, state[field])


def update_state() -> None:
    """
    Function for updating state.
    """
    print_state("BEFORE")
    # Headers
    print_state("AFTER")


def print_state(header: str = "STATE") -> None:
    """
    Function for printing state.
    :param header: Header string.
    """
    header = "="*10 + header + "="*10
    print(header)
    print(dict(server_state))
    print(dict(st.session_state))
    print("="*len(header))


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
    st.title("API Workbench")

    column_splitter_kwargs = {"spec": [0.5, 0.5], "gap": "medium"}

    # First level

    first_left, first_right = st.columns(**column_splitter_kwargs)
    request_form = first_left.form("Request", clear_on_submit=True)

    sending_line_left, sending_line_middle, sending_line_right = request_form.columns(
        [0.14, 0.76, 0.1])

    method = sending_line_left.selectbox("Method", options=["Get", "Post", "Patch", "Put", "Delete"],
                                         index=server_state.method)
    url = sending_line_middle.text_input(
        "URL", value=server_state.url)
    sending_line_right.markdown("## ")
    if sending_line_right.form_submit_button("Send"):
        response = send_request(
            method=method, url=url, )
        server_state.response = response.json()
        server_state.response_status = response.status_code
        server_state.response_header = response.headers

    first_right.subheader(
        "Response Status: " + str(server_state.response_status))
    first_right.text(
        server_state.response_status_message)

    # Second level

    st.divider()
    second_left, second_right = st.columns(**column_splitter_kwargs)
    second_left.markdown("##### Request Headers: ")
    second_left.data_editor(server_state.headers,
                            key="headers_update",
                            num_rows="dynamic", use_container_width=True,
                            on_change=print_state,
                            )

    second_right.markdown("##### Response Header: ")
    second_right.json(server_state.response_header)

    # Third level

    st.divider()
    third_left, third_right = st.columns(**column_splitter_kwargs)

    third_left.markdown("##### Request Parameters: ")
    third_left.divider()
    third_left.markdown("##### Request JSON Payload: ")

    third_right.markdown("##### Response Content: ")
    third_right.json(server_state.response)

    save_cache_button = st.sidebar.button("Save state")
    if save_cache_button:
        with st.spinner("Saving State..."):
            data = dict(server_state.cache)
            for key in data:
                if isinstance(data[key], pd.DataFrame):
                    data[key] = {
                        row["key"]: row["value"] for _, row in data[key].iterrows()
                    }
            json_utility.save(
                server_state.cache, cfg.PATHS.FRONTEND_CACHE)
    st.sidebar.json(dict(server_state))


def run_app() -> None:
    """
    Main runner function.
    """
    st.set_page_config(
        page_title="Scraping Database Generator",
        page_icon=":books:",
        layout="wide"
    )
    load_state()
    run_page()


if __name__ == "__main__":
    run_app()
