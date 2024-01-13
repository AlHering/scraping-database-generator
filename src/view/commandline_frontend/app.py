# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""

import os
import sys
import copy
import json
import traceback
from rich import print as rich_print
from rich.panel import Panel
from typing import List, Optional, Any, Callable
import requests
from src.interfaces.frontend_interface import populate_or_get_frontend_cache
from src.utility.bronze import dictionary_utility
from src.configuration import configuration as cfg
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from datetime import datetime as dt
from tqdm import tqdm


SCRIPT_FOLDER = os.path.abspath(os.path.dirname(__file__))
IMAGE_GENERATION_FOLDER = os.path.dirname(SCRIPT_FOLDER)
APP_CONFIG = {

}
CACHE = None


"""
Abstractions
"""


class Command:
    """
    Command class.
    """

    def __init__(self, command: str, function: Callable, default_kwargs: dict = None, help_text: str = None) -> None:
        """
        Initiation method.
        :param command: Command.
        :param function: Function.
        :param default_kwargs: Default keyword arguments.
            Defaults to None.
        :param help_text: Help text.
            Defaults to None.
        """
        self.command = command
        self.function = function
        self.default_kwargs = {} if default_kwargs is None else default_kwargs
        self.help_text = f"No help text available for '{command}'" if help_text is None else help_text

    def run_command(self, **kwargs: Optional[Any]) -> bool:
        """
        Method for running the command.
        :param kwargs: Additonal keyword arguments.
        :return: True if function call was successful else False.
        """
        try:
            current_kwargs = copy.deepcopy(self.default_kwargs)
            if kwargs:
                current_kwargs.update(kwargs)
            self.function(**current_kwargs)
            return True
        except Exception as ex:
            print(f"Exception {ex} appeared.\nTrace:{traceback.format_exc()}")
            return False

    def show_help_text(self) -> None:
        """
        Method for printing a help text.
        """
        print(self.help_text)


"""
Helper functions
"""


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


def run_session_loop(source: str = None) -> None:
    """
    Command line interface for Image Generation resource handling.""
    """
    allowed_sources = [source] if source else []
    session = PromptSession(
        bottom_toolbar=get_bottom_toolbar(),
        style=get_style(),
        auto_suggest=AutoSuggestFromHistory()
    )
    current_path = []
    close_session = False

    while not close_session:
        if dictionary_utility.exists(APP_CONFIG, current_path):
            current_state = dictionary_utility.extract_nested_value(
                APP_CONFIG, current_path)
        else:
            current_state = APP_CONFIG.get("error_page", {})

        for panel in current_state.get("pre_panels", []):
            rich_print(panel)
        for command in current_state.get("execute", []):
            command.run_command(**CACHE)
        for panel in current_state.get("post_panels", []):
            rich_print(panel)

        completer = WordCompleter(
            [command.command for command in current_state.get("commands", [])])
        user_input = session.prompt("> ", completer=completer).split(" ")
        # TODO: Handle input


"""
Entrypoint
"""
if __name__ == "__main__":
    CACHE = populate_or_get_frontend_cache()
    run_session_loop()
