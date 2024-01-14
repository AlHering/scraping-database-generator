# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from typing import List, Optional
from rich.panel import Panel
from rich.style import Style as RichStyle
from prompt_toolkit.styles import Style as PTStyle
from src.view.commandline_frontend.frontend_utility.frontend_abstractions import Command


def get_error_page() -> dict:
    """
    Function for acquiring error page.
    :return: Error page structure.
    """
    return {
        "pre_panels": [Panel("""""", title="[red]Error", border_style=RichStyle(color="red"))],
        "execute": [],
        "post_panels": [],
        "commands": [],
        "prompt": ""
    }


def get_available_command_panel(available_commands: List[Command] = None) -> Optional[Panel]:
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
         "ctl-c to exit, ctl-d to save cache and exit",)
    ]


def get_style() -> PTStyle:
    """
    Function for getting style.
    :return: Style.
    """
    return PTStyle.from_dict({
        "bottom-toolbar": "#333333 bg:#ffcc00"
    })
