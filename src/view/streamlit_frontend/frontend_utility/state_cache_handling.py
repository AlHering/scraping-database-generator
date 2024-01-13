# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import streamlit as st
from typing import List, Any
from src.interfaces.frontend_interface import populate_or_get_frontend_cache, delete_response_file, load_response_file


def populate_state_cache() -> None:
    """
    Function for populating state cache.
    """
    with st.spinner("Loading State..."):
        st.session_state["CACHE"] = populate_or_get_frontend_cache()


def update_state_cache(update: dict) -> None:
    """
    Function for updating state cache.
    :param update: State update.
    """
    for key in update:
        st.session_state["CACHE"][key] = update[key]


def remove_state_cache_element(field_path: List[Any]) -> None:
    """
    Function for removing a target element from cache.
    :param field_path: Field path for traversing cache to target element.
    """
    target = field_path[-1]
    field_path.remove(target)
    data = st.session_state["CACHE"]
    for key in field_path:
        data = data[key]
    data.pop(target)


def delete_response(response_name: str) -> None:
    """
    Function for deleting a response.
    :param response_name: Target response name.
    """
    if response_name == st.session_state["CACHE"]["current_response"]:
        update_state_cache({
            "current_response": "default"
        })
    remove_state_cache_element(["responses", response_name])
    delete_response_file(response_name)


def reload_request(response_name: str) -> None:
    """
    Function for deleting a response.
    :param response_name: Target response name.
    """
    data = load_response_file(response_name)

    update_state_cache({
        "current_response": response_name,
        "headers": data["request_headers"],
        "params": data["request_params"],
        "json_payload": data["request_json_payload"]
    })
    for field in ["method_update", "url_update"]:
        request_field = "request_" + "_".join(field.split("_")[:-1])
        st.session_state[field] = data[request_field]
    for field in ["headers_update", "params_update", "json_payload_update"]:
        st.session_state.pop(field)
