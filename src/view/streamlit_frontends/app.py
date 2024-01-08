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
from http.client import responses as status_codes
from typing import Any, Callable, Union, List, get_origin, get_args
import streamlit as st
from code_editor import code_editor
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, requests_utility
from src.utility.silver.file_system_utility import safely_create_path
import requests


###################
# State handling
###################


def load_state() -> None:
    """
    Function for loading server state.
    """
    with st.spinner("Loading State..."):
        if os.path.exists(cfg.PATHS.FRONTEND_CACHE):
            st.session_state["CACHE"] = json_utility.load(
                cfg.PATHS.FRONTEND_CACHE)
        else:
            st.session_state["CACHE"] = {
                "method": "GET",
                "url": "",
                "headers": {},
                "params": {},
                "json": {},
                "response": {},
                "response_status_message": "No request sent.",
                "response_status": -1,
                "response_headers": {}
            }


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
        "url": st.session_state["url_update"]
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


def insert_json_block(parent_widget: Any, cache_field: str) -> None:
    """
    Function for inserting an json-based code block.
    :param parent_widget: Widget to insert code block under.
    :param cache_field: Bound state cache field.
    """
    with parent_widget.empty():
        try:
            content = json.dumps(
                st.session_state["CACHE"][cache_field], indent=2)
            st.session_state["CACHE"][cache_field] = json.loads(
                code_editor("{\n\n\n\n}" if content == "{}" else content,
                            key=f"{cache_field}_update",
                            lang="json",
                            allow_reset=True,
                            options={"wrap": True},
                            buttons=get_json_editor_buttons()
                            )["text"])
        except json.JSONDecodeError:
            st.session_state["CACHE"][cache_field] = {}


###################
# Main app functionality
###################


def send_request(force: bool = False) -> None:
    """
    Function for sending off request.
    :param force: Force resending request.
    """
    if force or (st.session_state.get("url_update") and st.session_state["CACHE"]["url"] != st.session_state["url_update"]):
        update_request_state()
        response_content = {}
        response_status = -1
        response_status_message = "An unknown error appeared"
        response_headers = {}

        response = None
        try:
            with st.spinner("Fetching data ..."):
                response = requests_utility.REQUEST_METHODS[st.session_state["CACHE"]["method"]](
                    url=st.session_state["CACHE"]["url"],
                    params=st.session_state["CACHE"]["params"] if st.session_state["CACHE"].get(
                        "params") else None,
                    headers=st.session_state["CACHE"]["headers"] if st.session_state["CACHE"].get(
                        "headers") else None,
                    json=st.session_state["CACHE"]["json"] if st.session_state["CACHE"].get(
                        "json") else None
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

        update_state_cache({"response": response_content,
                            "response_status": response_status,
                            "response_status_message": response_status_message,
                            "response_headers": response_headers})

        run_page()


def run_page() -> None:
    """
    Function for running the main page.
    """
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

    sending_line_right.form_submit_button(
        "Send", on_click=lambda: send_request(True))
    request_form.divider()
    request_form.markdown("##### Request Headers: ")
    insert_json_block(request_form, "headers")
    request_form.divider()
    request_form.markdown("##### Request Parameters: ")
    insert_json_block(request_form, "params")
    request_form.divider()
    request_form.markdown(
        "##### Request JSON Payload:")
    request_form.text(
        """(Confirm with CTRL+ENTER or by pressing "save")""")
    insert_json_block(request_form, "json")
    response_status = right.empty()
    response_status_message = right.empty()
    right.divider()
    right.markdown("##### Response Header: ")
    response_headers = right.empty()
    right.markdown("##### Response Content: ")
    response = right.empty()

    save_cache_button = st.sidebar.button("Save state")
    if save_cache_button:
        with st.spinner("Saving State..."):
            json_utility.save(
                st.session_state["CACHE"], cfg.PATHS.FRONTEND_CACHE)
    state_preview = st.sidebar.empty()

    previous_header = {"placeholder": "header"}
    previous_content_length = -1
    while True:
        if previous_header != st.session_state['CACHE']["response_headers"] or previous_content_length != len(st.session_state['CACHE']["response"]):
            if st.session_state['CACHE']["response_status_message"] != "No request sent." or previous_header == {"placeholder": "header"}:
                print("New data, reloading ...")
                previous_header = st.session_state['CACHE']["response_headers"]
                previous_content_length = len(
                    st.session_state['CACHE']["response"])
                response_status.subheader(
                    f"Response Status {st.session_state['CACHE']['response_status']}")
                response_status_message.write(
                    st.session_state['CACHE']["response_status_message"])
                response_headers.json(
                    st.session_state['CACHE']["response_headers"])
                if isinstance(st.session_state['CACHE']["response"], dict):
                    response.json(st.session_state['CACHE']["response"])
                else:
                    response.write(st.session_state['CACHE']["response"])
                state_preview.json(dict(st.session_state))
        sleep(1)


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
