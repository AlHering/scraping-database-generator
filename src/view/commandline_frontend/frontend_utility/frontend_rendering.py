# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from typing import List, Optional
from rich.panel import Panel
from prompt_toolkit.styles import Style
from src.view.commandline_frontend.frontend_utility.frontend_abstractions import Command


def get_available_command_panel(available_commands: List[Command] = None) -> Optional(Panel):
    """
    Function for acquiring a panel, containing available commands.
    :param available_commands: List of available commands.
    :return: Panel, containing available commands, if there are any.
    """
    pass


def get_bottom_toolbar() -> str:
    """
    Function for getting bottom toolbar.
    :return: String for building bottom toolbar.
    """
    return [
        ("class:bottom-toolbar",
         "ctl-d or ctl-c to exit",)
    ]


def get_style() -> Style:
    """
    Function for getting style.
    :return: Style.
    """
    return Style.from_dict({
        "bottom-toolbar": "#333333 bg:#ffcc00"
    })
