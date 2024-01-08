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
from typing import Any, Callable, Union, get_origin, get_args
import streamlit as st
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
                "json": None,
                "response": {},
                "response_status_message": "No request sent.",
                "response_status": -1,
                "response_headers": {}
            }

        for field in state:
            if isinstance(state[field], dict):
                st.session_state[field] = pd.DataFrame(
                    [{"key": key, "value": value}
                        for key, value in state[field].items()],
                    columns=["value"],
                    index=["key"])
            else:
                st.session_state[field] = state[field]


def update_state_dictionary(field: str, update: dict) -> None:
    """
    Function for updating a state managed dictionary.
    :param field: State field of dictionary.
    :param update: Streamlit update dictionary.
    """
    for entry in update["added_rows"]:
        if len(entry.items()) > 1:
            st.session_state[field].loc[entry["_index"],
                                        ["value"]] = entry["value"]
            update["added_rows"].remove(entry)

    done = []
    for entry_key in update["edited_rows"]:
        if len(update["edited_rows"][entry_key].items()) > 1:
            entry = update["edited_rows"][entry_key]
            st.session_state[field].loc[entry["_index"],
                                        ["value"]] = entry["value"]
            done.append(entry_key)
    for to_remove in done:
        update["edited_rows"].pop(to_remove)
    for entry_index in update["deleted_rows"]:
        st.session_state[field].drop(
            st.session_state[field].index[entry_index], inplace=True)
    update["deleted_rows"] = []


def trigger_state_dictionary_update(field: str) -> None:
    """
    Function for triggering an state dictionary update.
    :param field: State field.
    """
    print_state("BEFORE")
    update_state_dictionary(field, st.session_state[f"{field}_update"])
    print_state("AFTER")


def update_state(update: dict) -> None:
    """
    Function for updating state.
    :param update: State update.
    """
    for key in update:
        st.session_state[key] = update[key]


def print_state(header: str = "STATE") -> None:
    """
    Function for printing state.
    :param header: Header string.
    """
    header = "="*10 + header + "="*10
    print(header)
    print(dict(st.session_state))
    print("="*len(header))


def send_request() -> None:
    """
    Function for sending off request.
    """
    st.session_state["method"] = st.session_state["method_update"]
    st.session_state["url"] = st.session_state["url_update"]

    response_content = {}
    response_status = -1
    response_status_message = "An unknown error appeared"
    response_headers = {}

    response = None
    try:
        response = requests_utility.REQUEST_METHODS[st.session_state["method"]](
            url=st.session_state["url"],
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

    update_state({"response": response_content,
                  "response_status": response_status,
                  "response_status_message": response_status_message,
                  "response_headers": response_headers})

    del st.session_state.method_update
    del st.session_state.url_update
    del st.session_state.headers_update
    run_page()


def run_page() -> None:
    """
    Function for running the main page.
    """
    st.title("API Workbench")

    column_splitter_kwargs = {"spec": [0.5, 0.5], "gap": "medium"}

    # First level

    first_left, first_right = st.columns(
        **column_splitter_kwargs)
    request_form = first_left.container()

    sending_line_left, sending_line_middle, sending_line_right = request_form.columns(
        [0.14, 0.76, 0.1])

    sending_line_left.selectbox("Method",
                                key="method_update",
                                options=list(
                                    requests_utility.REQUEST_METHODS.keys()),
                                index=list(
                                    requests_utility.REQUEST_METHODS.keys()).index(st.session_state["method"]))
    sending_line_middle.text_input("URL",
                                   key="url_update",
                                   value=st.session_state["url"])
    sending_line_right.markdown("## ")

    sending_line_right.button(
        "Send", on_click=lambda: send_request())

    response_status = first_right.empty()
    response_status_message = first_right.empty()

    # Second level

    st.divider()
    second_left, second_right = st.columns(**column_splitter_kwargs)
    second_left.markdown("##### Request Headers: ")
    second_left.data_editor(st.session_state["headers"].copy(),
                            key="headers_update",
                            num_rows="dynamic", use_container_width=True,
                            on_change=lambda: trigger_state_dictionary_update(
                                "headers")
                            )

    second_right.markdown("##### Response Header: ")
    response_headers = second_right.empty()

    # Third level

    st.divider()
    third_left, third_right = st.columns(**column_splitter_kwargs)

    third_left.markdown("##### Request Parameters: ")
    third_left.divider()
    third_left.markdown("##### Request JSON Payload: ")

    third_right.markdown("##### Response Content: ")
    response = third_right.empty()

    save_cache_button = st.sidebar.button("Save state")
    if save_cache_button:
        with st.spinner("Saving State..."):
            data = dict(st.session_state)
            for key in data:
                if isinstance(data[key], pd.DataFrame):
                    data[key] = {
                        row["key"]: row["value"] for _, row in data[key].iterrows()
                    }
            json_utility.save(
                data, cfg.PATHS.FRONTEND_CACHE)

    while True:
        st.session_state["response_change"] = False
        response_status.subheader(
            f"Response Status {st.session_state['response_status']}")
        response_status_message.write(
            st.session_state["response_status_message"])
        response_headers.json(st.session_state["response_headers"])
        if isinstance(st.session_state["response"], dict):
            response.json(st.session_state["response"])
        else:
            response.write(st.session_state["response"])
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
