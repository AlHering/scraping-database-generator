# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from rich import print as rich_print
from src.interfaces.frontend_interface import populate_or_get_frontend_cache, save_frontend_cache
from src.view.commandline_frontend.frontend_utility.frontend_commands import Command
from src.view.commandline_frontend.frontend_utility import frontend_rendering
from src.utility.bronze import dictionary_utility
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent


BINDINGS = KeyBindings()
APP_CONFIG = {
    "main_page": {
        "pre_panels": [],
        "execute": [],
        "post_panels": [],
        "commands": [],
        "prompt": ""
    },
    "error_page": frontend_rendering.get_error_page([])
}
CACHE = None
CLOSE_SESSION = None


@BINDINGS.add("c-c")
@BINDINGS.add("c-d")
def exit_app(event: KeyPressEvent) -> None:
    """
    Function for exiting app.
    :param event: Event that resulted in entering the function.
    """
    global CLOSE_SESSION, CACHE

    CLOSE_SESSION = True
    if event.key_sequence[0].key.value == "c-d":
        rich_print("[green bold]Saving cache...")
        save_frontend_cache(CACHE, ignore=["current_path"])
    rich_print("[bold]Bye [white]...")
    event.app.exit()


def run_session_loop(source: str = None) -> None:
    """
    Command line interface for Image Generation resource handling.""
    """

    global CLOSE_SESSION, CACHE, BINDINGS
    allowed_sources = [source] if source else []
    CACHE = populate_or_get_frontend_cache()

    session = PromptSession(
        bottom_toolbar=frontend_rendering.get_bottom_toolbar(),
        style=frontend_rendering.get_style(),
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=BINDINGS
    )
    CACHE["current_path"] = ["error_page"]
    CLOSE_SESSION = False

    while not CLOSE_SESSION:
        if dictionary_utility.exists(APP_CONFIG, CACHE["current_path"]):
            current_state = dictionary_utility.extract_nested_value(
                APP_CONFIG, CACHE["current_path"])
        else:
            current_state = APP_CONFIG.get("error_page", {})

        try:
            for panel in current_state.get("pre_panels", []):
                rich_print(panel)
            for command in current_state.get("execute", []):
                command.run_command(cache=CACHE)
            for panel in current_state.get("post_panels", []):
                rich_print(panel)
            commands = current_state.get("commands", [])
            command_panel = frontend_rendering.get_available_command_panel()
            if command_panel is not None:
                rich_print(command_panel)

            completer = WordCompleter(
                [command.command for command in commands])

            user_input = session.prompt(
                f"{current_state.get('prompt', '')}> ", completer=completer)
            if user_input is not None:
                user_input = user_input.split(" ")
            # TODO: Handle inpu
        except Exception:
            current_path = ["error_page"]


"""
Entrypoint
"""
if __name__ == "__main__":
    run_session_loop()
