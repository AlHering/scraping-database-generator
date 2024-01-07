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


def update_state_dictionary(field: str, update: dict) -> None:
    """
    Function for updating a state managed dictionary.
    :param field: State field of dictionary.
    :param update: Streamlit update dictionary.
    """
    with server_state_lock[field]:
        for entry in update["added_rows"]:
            if len(entry.items()) > 1:
                server_state[field].loc[entry["_index"],
                                        ["value"]] = entry["value"]
                update["added_rows"].remove(entry)

        done = []
        for entry_key in update["edited_rows"]:
            if len(update["edited_rows"][entry_key].items()) > 1:
                entry = update["edited_rows"][entry_key]
                server_state[field].loc[entry["_index"],
                                        ["value"]] = entry["value"]
                done.append(entry_key)
        for to_remove in done:
            update["edited_rows"].pop(to_remove)
        for entry_index in update["deleted_rows"]:
            server_state[field].drop(
                server_state[field].index[entry_index], inplace=True)
        update["deleted_rows"] = []


def update_state_dictionaries() -> None:
    """
    Function for updating state dictionaries.
    """
    print_state("BEFORE")
    update_state_dictionary("headers", st.session_state["headers_update"])
    print_state("AFTER")


def update_state(update: dict) -> None:
    """
    Function for updating state.
    :param update: State update.
    """
    for key in update:
        with server_state_lock[key]:
            server_state[key] = update[key]


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
    print([i for i in server_state["headers"].iterrows()])


def send_request(method: str, url: str, headers: dict = None, parameters: dict = None, json: dict = None) -> requests.Response:
    """
    Function for sending off request.
    :param method: Method to use.
    :param url: Target URL.
    :param headers: Request headers.
    :param parameters: API parameters.
    :param json: JSON payload.
    """
    update_state({
        "method": method,
        "url": url
    })
    try:
        response = requests_utility.REQUEST_METHODS[method.upper()](
            url=url,
            params=parameters,
            headers=headers,
            json=json
        )
        update_state({"response": response.json(),
                      "response_status": response.status_code,
                      "response_status_message": "Request successful.",
                      "response_header": response.headers})
    except requests.exceptions.RequestException as ex:
        print()
        update_state({"response": {},
                      "response_status": -1,
                      "response_status_message": f"Exception '{ex}' appeared.",
                      "response_header": {}})
    st.session_state["response_status_message"] = 0


def run_page() -> None:
    """
    Function for running the main page.
    """
    st.title("API Workbench")

    column_splitter_kwargs = {"spec": [0.5, 0.5], "gap": "medium"}

    # First level

    first_left, first_right = st.columns(**column_splitter_kwargs)
    request_form = first_left.container()

    sending_line_left, sending_line_middle, sending_line_right = request_form.columns(
        [0.14, 0.76, 0.1])

    method = sending_line_left.selectbox("Method", options=["Get", "Post", "Patch", "Put", "Delete"],
                                         index=server_state.method)
    url = sending_line_middle.text_input(
        "URL", value=server_state.url)
    sending_line_right.markdown("## ")

    sending_line_right.button(
        "Send", on_click=lambda: send_request(method, url))

    first_right.subheader(
        "Response Status: " + str(server_state.response_status))
    first_right.text(
        st.session_state.get("response_status_message", 99))

    # Second level

    st.divider()
    second_left, second_right = st.columns(**column_splitter_kwargs)
    second_left.markdown("##### Request Headers: ")
    second_left.data_editor(server_state.headers.copy(),
                            key="headers_update",
                            num_rows="dynamic", use_container_width=True,
                            on_change=update_state,
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
