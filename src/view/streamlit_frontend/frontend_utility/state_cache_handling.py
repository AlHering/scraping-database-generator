# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import json
import streamlit as st
from typing import List, Any
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility


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
    path = os.path.join(cfg.PATHS.RESPONSE_PATH, f"{response_name}.json")
    if os.path.exists(path):
        os.remove(path)


def reload_request(response_name: str) -> None:
    """
    Function for deleting a response.
    :param response_name: Target response name.
    """
    data = json_utility.load(os.path.join(
        cfg.PATHS.RESPONSE_PATH, f"{response_name}.json"))

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
