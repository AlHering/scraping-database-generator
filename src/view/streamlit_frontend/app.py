# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import copy
import json
import traceback
import requests
from urllib.parse import urlparse
from http.client import responses as status_codes
from typing import Any, Optional, List
import streamlit as st
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, requests_utility, time_utility
from src.view.streamlit_frontend.frontend_utility.state_cache_handling import populate_state_cache
from src.view.streamlit_frontend.frontend_utility.frontend_rendering import render_request_input_form, render_response_data, render_sidebar_control_header, render_sidebar_response_list


###################
# Main app functionality
###################


def prepare_request_input() -> dict:
    """
    Function for preparing request input.
    :return: Request kwargs.
    """
    kwargs = {
        "url": st.session_state["url_update"],
        "method": st.session_state["method_update"]
    }
    for field in ["headers", "params", "json_payload"]:
        try:
            kwargs[field] = json.loads(
                st.session_state[f"{field}_update"]["text"])
        except Exception:
            kwargs[field] = None
    return kwargs


def send_request(method: str, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, json_payload: Optional[dict] = None) -> None:
    """
    Function for sending off request.
    :param method: Request method.
    :param url: Target URL.
    :param headers: Request headers.
        Defaults to None.
    :param params: Request parameters.
        Defaults to None.
    :param json_payload: JSON payload.
        Defaults to None.
    """
    response_content = {}
    response_status = -1
    response_status_message = "An unknown error appeared"
    response_headers = {}

    response = None
    try:
        response = requests_utility.REQUEST_METHODS[method](
            url=url,
            params=params,
            headers=headers,
            json=json_payload
        )
        response_status = response.status_code
        response_status_message = f"Status description: {status_codes[response_status]}"
        response_headers = dict(response.headers)
    except requests.exceptions.RequestException as ex:
        response_status_message = f"Exception '{ex}' appeared.\n\nTrace:{traceback.format_exc()}"

    if response is not None:
        try:
            response_content = response.json()
        except json.decoder.JSONDecodeError:
            response_content = response.text

    handle_response_data(response_data={
        "request_method": method,
        "request_url": url,
        "request_headers": headers,
        "request_params": params,
        "request_json_payload": json_payload,
        "response": response_content,
        "response_status": response_status,
        "response_status_message": response_status_message,
        "response_headers": response_headers})


def handle_response_data(response_data: dict) -> None:
    """
    Function for handling response data after request.
    :param response_data: Gathered response data.
    """
    # Keep only the allowed number of responses
    while len(st.session_state["CACHE"]["responses"]) >= cfg.KEEP_RESPONSES:
        to_remove = st.session_state["CACHE"]["responses"].pop(
            list(st.session_state["CACHE"]["responses"].keys())[0])
        path = os.path.join(cfg.PATHS.RESPONSE_PATH,
                            f"{to_remove['name']}.json")
        if os.path.exists(path):
            os.remove(path)

    # Create individual name
    response_name = f"{time_utility.get_timestamp()}_STATUS{response_data['response_status']}_{urlparse(response_data['request_url']).netloc}"
    response_data["name"] = response_name

    # Save response to disk and cache
    json_utility.save(response_data, os.path.join(cfg.PATHS.RESPONSE_PATH,
                      f"{response_name}.json"))
    st.session_state["CACHE"]["responses"][response_name] = response_data
    st.session_state["CACHE"]["current_response"] = response_name


###################
# Entrypoint
###################


if __name__ == "__main__":
    # Basic metadata
    st.set_page_config(
        page_title="Scraping Database Generator",
        page_icon=":books:",
        layout="wide"
    )

    # Cache and config
    if "CACHE" not in st.session_state:
        populate_state_cache()
        st.rerun()
    column_splitter_kwargs = {"spec": [0.5, 0.5], "gap": "medium"}
    data = {key: val for key, val in st.session_state['CACHE'].items(
    ) if key in ["method", "url", "headers", "params", "json_payload"]}
    data.update({key: val for key, val in st.session_state.items(
    ) if key.endswith("update")})
    print(f"Running with {data}")
    # Main page
    st.title("API Workbench")
    render_sidebar_control_header()
    left, right = st.columns(
        **column_splitter_kwargs)
    submitted = render_request_input_form(left)

    data_fetching_spinner = right.empty()
    if submitted:
        st.session_state["first_sent"] = 1
        with data_fetching_spinner, st.spinner("Fetching data ..."):
            kwargs = prepare_request_input()
            send_request(**kwargs)

    render_response_data(right)
    render_sidebar_response_list()
    st.json(dict(st.session_state))
