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
    field_path = field_path.remove(target)
    data = st.session_state["CACHE"]
    for key in field_path:
        data = data[key]
    data.pop(target)


def delete_response(response_name: str) -> None:
    """
    Function for deleting a response.
    :param response_name: Target response name.
    """
    remove_state_cache_element(["responses", response_name])
    path = os.path.join(cfg.PATHS.RESPONSE_PATH, f"{response_name}.json")
    if os.path.exists(path):
        os.remove(path)


def reload_request(response_name: str) -> None:
    """
    Function for deleting a response.
    :param response_name: Target response name.
    """
    pass


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
