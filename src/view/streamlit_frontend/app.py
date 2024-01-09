# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import copy
import json
import traceback
from time import sleep
from urllib.parse import urlparse
from http.client import responses as status_codes
from typing import Any, Callable, Union, Optional, List, get_origin, get_args
import streamlit as st
from code_editor import code_editor
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, requests_utility, time_utility
from src.utility.silver.file_system_utility import safely_create_path, get_all_files
import requests


###################
# State handling
###################


def populate_state_cache() -> None:
    """
    Function for populating state cache.
    """
    if not os.path.exists(cfg.PATHS.RESPONSE_PATH):
        os.makedirs(cfg.PATHS.RESPONSE_PATH)
    with st.spinner("Loading State..."):
        if os.path.exists(cfg.PATHS.FRONTEND_CACHE):
            st.session_state["CACHE"] = json_utility.load(
                cfg.PATHS.FRONTEND_CACHE)
        else:
            st.session_state["CACHE"] = json_utility.load(
                cfg.PATHS.FRONTEND_DEFAULT_CACHE)


def update_state_cache(update: dict) -> None:
    """
    Function for updating state cache.
    :param update: State update.
    """
    for key in update:
        st.session_state["CACHE"][key] = update[key]


def trigger_state_dictionary_update() -> None:
    """
    Function for triggering an state dictionary update.
    """
    update_state_cache({
        "method": st.session_state["method_update"],
        "url": st.session_state["url_update"] if st.session_state["url_update"] else st.session_state["url"]
    })

    for state_dict in ["headers", "params", "json"]:
        if st.session_state.get(f"{state_dict}_update") is None or not json_utility.is_json(st.session_state[f"{state_dict}_update"]["text"]):
            update_state_cache({state_dict: {}})
        else:
            update_state_cache({state_dict: json.loads(
                st.session_state[f"{state_dict}_update"]["text"])})


def update_request_state() -> None:
    """
    Function for updating request state before sending off requests.
    """
    print("="*10 + "BEFORE" + "="*10)
    print(st.session_state["CACHE"])
    trigger_state_dictionary_update()
    print("="*10 + "AFTER" + "="*10)
    print(st.session_state["CACHE"])


###################
# Helper functions
###################


def get_json_editor_buttons() -> List[dict]:
    """
    Function for acquiring json payload code editor buttons.
    :return: Buttons as list of dictionaries.
    """
    return [
        {
            "name": "save",
            "feather": "Save",
            "hasText": True,
            "alwaysOn": True,
            "commands": [
                    "save-state",
                    [
                        "response",
                        "saved"
                    ]
            ],
            "response": "saved",
            "style": {"top": "0rem", "right": "9.6rem"}
        },
        {
            "name": "copy",
            "feather": "Copy",
            "hasText": True,
            "alwaysOn": True,
            "commands": ["copyAll"],
            "style": {"top": "0rem", "right": "5rem"}
        },
        {
            "name": "clear",
            "feather": "X",
            "hasText": True,
            "alwaysOn": True,
            "commands": ["selectall", "del", ["insertstring", "{\n\n\n\n}"], "save-state",
                         ["response", "saved"]],
            "style": {"top": "0rem", "right": "0.4rem"}
        },
    ]


###################
# Main app functionality
###################


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

    while len(st.session_state["CACHE"]["responses"]) >= cfg.KEEP_RESPONSES:
        to_remove = st.session_state["CACHE"]["responses"].pop(
            list(st.session_state["CACHE"]["responses"].keys())[0])
        file_name = f"{to_remove['name']}.json"
        if os.path.exists(cfg.PATHS.RESPONSE_PATH):
            os.remove(cfg.PATHS.RESPONSE_PATH)
    data = {"response": response_content,
            "response_status": response_status,
            "response_status_message": response_status_message,
            "response_headers": response_headers}

    response_name = f"{time_utility.get_timestamp()}_STATUS{response_status}_{urlparse(url).netloc}"
    data["name"] = response_name
    json_utility.save(data, os.path.join(cfg.PATHS.RESPONSE_PATH,
                      f"{response_name}.json"))
    st.session_state["CACHE"]["responses"][response_name] = data
    st.session_state["CACHE"]["current_response"] = response_name


if __name__ == "__main__":
    st.set_page_config(
        page_title="Scraping Database Generator",
        page_icon=":books:",
        layout="wide"
    )

    if "CACHE" not in st.session_state:
        populate_state_cache()
        st.rerun()

    st.title("API Workbench")

    column_splitter_kwargs = {"spec": [0.5, 0.5], "gap": "medium"}

    left, right = st.columns(
        **column_splitter_kwargs)
    request_form = left.form("request_update")

    sending_line_left, sending_line_middle, sending_line_right = request_form.columns(
        [0.18, 0.67, 0.15])

    sending_line_left.selectbox("Method",
                                key="method_update",
                                options=list(
                                    requests_utility.REQUEST_METHODS.keys()),
                                index=list(
                                    requests_utility.REQUEST_METHODS.keys()).index(st.session_state["CACHE"]["method"]))
    sending_line_middle.text_input("URL",
                                   key="url_update",
                                   value=st.session_state.get(
                                       "url_update", ""))
    sending_line_right.markdown("## ")

    submitted = sending_line_right.form_submit_button(
        "Send")
    request_form.divider()
    request_form.markdown("##### Request Headers: ")
    request_form.text(
        """(Confirm with CTRL+ENTER or by pressing "save")""")
    with request_form.empty():
        code_editor("{\n\n\n\n}",
                    key="headers_update",
                    lang="json",
                    allow_reset=True,
                    options={"wrap": True},
                    buttons=get_json_editor_buttons()
                    )
    request_form.divider()
    request_form.markdown("##### Request Parameters: ")
    request_form.text(
        """(Confirm with CTRL+ENTER or by pressing "save")""")
    with request_form.empty():
        code_editor("{\n\n\n\n}",
                    key="params_update",
                    lang="json",
                    allow_reset=True,
                    options={"wrap": True},
                    buttons=get_json_editor_buttons()
                    )
    request_form.divider()
    request_form.markdown(
        "##### Request JSON Payload:")
    request_form.text(
        """(Confirm with CTRL+ENTER or by pressing "save")""")
    with request_form.empty():
        code_editor("{\n\n\n\n}",
                    key="json_payload_update",
                    lang="json",
                    allow_reset=True,
                    options={"wrap": True},
                    buttons=get_json_editor_buttons()
                    )

    sidebar_right, sidebar_left = st.sidebar.columns([0.5, 0.5])
    save_cache_button = sidebar_left.button("Save state")
    if save_cache_button:
        with st.spinner("Saving State..."):
            json_utility.save(
                st.session_state["CACHE"], cfg.PATHS.FRONTEND_CACHE)
    clear_cache_button = sidebar_right.button("Clear state")
    if clear_cache_button:
        with st.spinner("Clearing State..."):
            st.session_state["CACHE"] = copy.deepcopy(json_utility.load(
                cfg.PATHS.FRONTEND_DEFAULT_CACHE))
    st.sidebar.divider()

    spinner_placeholder = right.empty()
    response_status = right.empty()
    response_status_message = right.empty()
    response_status.subheader(
        f"Response Status {-1}")
    response_status_message.write(
        ["No request sent.", "Changes were made, waiting for new request..."][st.session_state.get("first_sent", 0)])
    right.divider()
    right.markdown("##### Response Header: ")
    response_headers = right.empty()
    response_headers.json({})
    right.markdown("##### Response Content: ")
    response = right.empty()
    response.json({})

    if submitted:
        st.session_state["first_sent"] = 1
        with spinner_placeholder, st.spinner("Fetching data ..."):
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
            send_request(**kwargs)
            data = st.session_state["CACHE"]["responses"][st.session_state["CACHE"]
                                                          ["current_response"]]
            response_status.subheader(
                f"Response Status {data['response_status']}")
            response_status_message.write(
                data["response_status_message"])
            response_headers.json(
                data["response_headers"])
            if isinstance(data["response"], dict):
                response.json(data["response"])
            else:
                response.write(data["response"])
