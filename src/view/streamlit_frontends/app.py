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
from typing import Any, Callable, Union, List, get_origin, get_args
import streamlit as st
from code_editor import code_editor
import pandas as pd
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, requests_utility
from src.utility.silver.file_system_utility import safely_create_path
import requests


CUSTOM_SESSION_FIELDS = {
    "method": str,
    "url": str,
    "headers": pd.DataFrame,
    "parameters": pd.DataFrame,
    "json": dict,
    "response": Union[str, dict],
    "response_status_message": str,
    "response_status": int,
    "response_headers": dict
}


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
                "method": "GET",
                "url": "",
                "headers": {},
                "parameters": {},
                "json": {},
                "response": {},
                "response_status_message": "No request sent.",
                "response_status": -1,
                "response_headers": {}
            }

        st.session_state["CACHE"] = {}

        for field in CUSTOM_SESSION_FIELDS:
            if CUSTOM_SESSION_FIELDS[field] is pd.DataFrame:
                st.session_state["CACHE"][field] = key_value_dataframe_from_dict(
                    state[field])
            else:
                st.session_state["CACHE"][field] = state[field]


def update_state_dictionary(field: str, update: dict) -> None:
    """
    Function for updating a state managed dictionary.
    :param field: State field of dictionary.
    :param update: Streamlit update dictionary.
    """
    for entry in update["added_rows"]:
        if len(entry.items()) > 1:
            st.session_state["CACHE"][field].loc[entry["_index"],
                                                 ["value"]] = entry["value"]
            update["added_rows"].remove(entry)

    done = []
    for entry_key in update["edited_rows"]:
        if len(update["edited_rows"][entry_key].items()) > 1:
            entry = update["edited_rows"][entry_key]
            st.session_state["CACHE"][field].loc[entry["_index"],
                                                 ["value"]] = entry["value"]
            done.append(entry_key)
    for to_remove in done:
        update["edited_rows"].pop(to_remove)
    for entry_index in update["deleted_rows"]:
        st.session_state["CACHE"][field].drop(
            st.session_state["CACHE"][field].index[entry_index], inplace=True)
    update["deleted_rows"] = []


def trigger_state_dictionary_update(field: str) -> None:
    """
    Function for triggering an state dictionary update.
    :param field: State field.
    """
    for state_dicts in ["headers", "parameters"]:
        update_state_dictionary(
            state_dicts, st.session_state[f"{state_dicts}_update"])


def update_state_cache(update: dict) -> None:
    """
    Function for updating state cache.
    :param update: State update.
    """
    for key in update:
        st.session_state["CACHE"][key] = update[key]


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
            "commands": ["selectall", "del", ["insertstring", "{\n\n\n\n}"]],
            "style": {"top": "0rem", "right": "0.4rem"}
        },
    ]


def key_value_dataframe_to_dict(dataframe: pd.DataFrame) -> dict:
    """
    Helper function for translating key-value DataFrames to dict.
    :param dataframe: DataFrame.
    :return: Dictionary with DataFrame content.
    """
    return {row["key"]: row["value"] for _, row in dataframe.iterrows()}


def key_value_dataframe_from_dict(data: dict) -> pd.DataFrame:
    """
    Helper function for translating dictionaries to key-value DataFrames.
    :param data: Dictionary.
    :return: Key-value DataFrame.
    """
    return pd.DataFrame([{"key": key, "value": value} for key, value in data.items()], columns=["value"], index=["key"])


def send_request(force: bool = False) -> None:
    """
    Function for sending off request.
    :param force: Force resending request.
    """
    if force or (st.session_state.get("url_update") and st.session_state["CACHE"]["url"] != st.session_state["url_update"]):

        response_content = {}
        response_status = -1
        response_status_message = "An unknown error appeared"
        response_headers = {}

        response = None
        try:
            response = requests_utility.REQUEST_METHODS[st.session_state["CACHE"]["method"]](
                url=st.session_state["CACHE"]["url"],
                params=None,
                headers=None,
                json=None
            )
            response_status = response.status_code
            response_status_message = "Response successfully fetched"
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

        del st.session_state.url_update
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
    request_form.data_editor(st.session_state["CACHE"]["headers"].copy(),
                             key="headers_update",
                             num_rows="dynamic", use_container_width=True)
    request_form.divider()
    request_form.markdown("##### Request Parameters: ")
    request_form.data_editor(st.session_state["CACHE"]["parameters"].copy(),
                             key="parameters_update",
                             num_rows="dynamic", use_container_width=True)
    request_form.divider()
    request_form.markdown(
        "##### Request JSON Payload:")
    request_form.text(
        """(Confirm with CTRL+ENTER or by pressing "save")""")
    with request_form.empty():
        try:
            content = json.dumps(st.session_state["CACHE"]["json"], indent=2)
            st.session_state["CACHE"]["json"] = json.loads(
                code_editor("{\n\n\n\n}" if content == "{}" else content,
                            key="json_update",
                            lang="json",
                            allow_reset=True,
                            options={"wrap": True},
                            buttons=get_json_editor_buttons()
                            )["text"])
        except json.JSONDecodeError:
            st.session_state["CACHE"]["json"] = {}
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
            data = st.session_state["CACHE"]
            for field in CUSTOM_SESSION_FIELDS:
                if CUSTOM_SESSION_FIELDS[field] is pd.DataFrame:
                    data[field] = key_value_dataframe_to_dict(data[field])
            json_utility.save(
                data, cfg.PATHS.FRONTEND_CACHE)
    state_preview = st.sidebar.empty()

    while True:
        response_status.subheader(
            f"Response Status {st.session_state['CACHE']['response_status']}")
        response_status_message.write(
            st.session_state['CACHE']["response_status_message"])
        response_headers.json(st.session_state['CACHE']["response_headers"])
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
