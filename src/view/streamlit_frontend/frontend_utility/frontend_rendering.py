# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import copy
from typing import Any, List
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from code_editor import code_editor
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, requests_utility
from src.view.streamlit_frontend.frontend_utility.state_cache_handling import update_state_cache, delete_response, reload_request


###################
# Helper functions
###################


def convert_response_name_to_label(response_name: str) -> str:
    """
    Function for converting response name to a label text.
    :param response_name: Response name.
    :return: Label text.
    """
    time_text, rest_text = response_name.split("_STATUS")
    time_text = time_text.replace("_", " ").replace(
        "-(", " (").replace("-", ":")
    status_text, *url_text = rest_text.split("_")
    url_text = "_".join(url_text)
    if status_text == "200":
        mail = ":mailbox_with_mail:"
    elif status_text == "-1":
        mail = ":mailbox_with_no_mail:"
    else:
        mail = ":mailbox_closed:"
    return f"{time_text}\n\nStatus: {status_text}  ... {mail} \n\n {url_text if url_text else '<unkown>'}"


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
# Rendering functions
###################


def render_sidebar_control_header() -> None:
    """
    Function for rendering the sidebar control header.
    """
    sidebar_left, sidebar_right = st.sidebar.columns([0.5, 0.5])
    if sidebar_right.button(":floppy_disk: Save state"):
        with st.spinner("Saving State..."):
            json_utility.save(
                st.session_state["CACHE"], cfg.PATHS.FRONTEND_CACHE)
    if sidebar_left.button(":cd: Clear state"):
        with st.spinner("Clearing State..."):
            st.session_state["CACHE"] = copy.deepcopy(json_utility.load(
                cfg.PATHS.FRONTEND_DEFAULT_CACHE))
    if st.sidebar.button(":wastebasket: Delete all responses"):
        with st.spinner("Deleting responses..."):
            for response_name in list(st.session_state["CACHE"]["responses"].keys()):
                if response_name != "default":
                    delete_response(response_name)
        st.rerun()
    st.sidebar.divider()


def render_sidebar_response_list() -> None:
    """
    Function for rendering the sidebar response list.
    """
    for response_name in st.session_state["CACHE"]["responses"]:
        if response_name != "default":
            left, right = st.sidebar.columns([0.8, 0.2])
            left.button(f"{convert_response_name_to_label(response_name)}",
                        on_click=update_state_cache,
                        args=({"current_response": response_name}, ),
                        use_container_width=True)
            right.button(":incoming_envelope:",
                         key=f"reload_{response_name}",
                         on_click=reload_request,
                         args=(response_name, ),
                         use_container_width=True)
            right.button(":wastebasket:",
                         key=f"delete_{response_name}",
                         on_click=delete_response,
                         args=(response_name, ),
                         use_container_width=True)


def render_request_input_form(parent_widget: Any) -> Any:
    """
    Function for rendering request input form.
    :param parent_widget: Parent widget.
    :return: Submit button widget.
    """
    request_form = parent_widget.form("request_update")

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
    return submitted


def render_response_data(parent_widget: Any) -> None:
    """
    Function for rendering response data.
    :param parent_widget: Parent widget.
    """
    data_rendering_spinner = parent_widget.empty()
    response_status = parent_widget.empty()
    response_status_message = parent_widget.empty()
    parent_widget.divider()
    parent_widget.markdown("##### Response Header: ")
    response_headers = parent_widget.empty()
    parent_widget.markdown("##### Response Content: ")
    response = parent_widget.empty()

    # TODO: Check rendering spinner -> seems to have no effect
    with data_rendering_spinner, st.spinner("Rendering data ..."):
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
