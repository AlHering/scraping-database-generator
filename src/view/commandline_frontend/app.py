# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from rich import print as rich_print
from src.interfaces.frontend_interface import populate_or_get_frontend_cache
from src.view.commandline_frontend.frontend_utility.frontend_abstractions import Command
from src.view.commandline_frontend.frontend_utility import frontend_rendering
from src.utility.bronze import dictionary_utility
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter


APP_CONFIG = {
    "main_page": {
        "pre_panels": [],
        "execute": [],
        "post_panels": [],
        "commands": [],
        "prompt": ""
    },
    "error_page": {
        "pre_panels": [],
        "execute": [],
        "post_panels": [],
        "commands": [],
        "prompt": ""
    }
}
CACHE = None


def run_session_loop(source: str = None) -> None:
    """
    Command line interface for Image Generation resource handling.""
    """
    allowed_sources = [source] if source else []
    session = PromptSession(
        bottom_toolbar=frontend_rendering.get_bottom_toolbar(),
        style=frontend_rendering.get_style(),
        auto_suggest=AutoSuggestFromHistory()
    )
    current_path = ["main_page"]
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
        commands = current_state.get("commands", [])
        command_panel = frontend_rendering.get_available_command_panel()
        if command_panel is not None:
            rich_print(command_panel)

        completer = WordCompleter([command.command for command in commands])
        user_input = session.prompt(
            f"{current_state.get('prompt', '')}> ", completer=completer).split(" ")
        # TODO: Handle input


"""
Entrypoint
"""
if __name__ == "__main__":
    CACHE = populate_or_get_frontend_cache()
    run_session_loop()
