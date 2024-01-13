# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from typing import Optional
import requests
import traceback
from http.client import responses as status_codes
from src.utility.bronze import requests_utility


def send_request(method: str, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, json_payload: Optional[dict] = None) -> dict:
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
    :return: Response data.
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

    return {
        "request_method": method,
        "request_url": url,
        "request_headers": headers,
        "request_params": params,
        "request_json_payload": json_payload,
        "response": response_content,
        "response_status": response_status,
        "response_status_message": response_status_message,
        "response_headers": response_headers})
