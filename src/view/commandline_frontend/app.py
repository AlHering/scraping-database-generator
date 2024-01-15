# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from typing import List
import traceback
from rich import print as rich_print
from src.interfaces.frontend_interface import populate_or_get_frontend_cache, save_frontend_cache
from src.view.commandline_frontend.frontend_utility.frontend_commands import Command, IGNORED_CACHE_FIELDS, RESET_CACHE_AND_RETURN_TO_MAIN
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
    "error_page": frontend_rendering.get_error_page([RESET_CACHE_AND_RETURN_TO_MAIN])
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
        save_frontend_cache(CACHE, ignore=IGNORED_CACHE_FIELDS)
    rich_print("[bold]\nBye [white]...")
    event.app.exit()


def setup_session() -> PromptSession:
    """
    Function for setting up prompt session.
    :return: Prompt session.
    """
    global CLOSE_SESSION, CACHE, BINDINGS

    CACHE = populate_or_get_frontend_cache()
    CACHE["last_path"] = None
    CACHE["current_path"] = ["error_page"]
    CLOSE_SESSION = False
    return PromptSession(
        bottom_toolbar=frontend_rendering.get_bottom_toolbar(),
        style=frontend_rendering.get_style(),
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=BINDINGS
    )


def get_current_state() -> dict:
    """
    Function for getting current state config.
    :return: Current state config.
    """
    global CACHE, APP_CONFIG

    CACHE["last_path"] = CACHE["current_path"]
    if dictionary_utility.exists(APP_CONFIG, CACHE["current_path"]):
        if len(CACHE["current_path"]) == 0:
            CACHE["current_path"] = ["main_page"]
        current_state = dictionary_utility.extract_nested_value(
            APP_CONFIG, CACHE["current_path"])
    else:
        current_state = APP_CONFIG.get("error_page", {})
    return current_state


def handle_step(current_state: dict) -> List[Command]:
    """
    Function for handling a loop step.
    :param current_state: Current state config.
    :return: List of active commands.
    """
    global CACHE

    for panel in current_state.get("pre_panels", []):
        rich_print(panel)
    for command in current_state.get("execute", []):
        command.run_command(cache=CACHE)
    for panel in current_state.get("post_panels", []):
        rich_print(panel)
    commands = current_state.get("commands", [])
    command_panel = frontend_rendering.get_available_command_panel(
        commands)

    if command_panel is not None:
        rich_print(command_panel)
    return commands


def get_completer(commands: List[Command]) -> WordCompleter:
    """
    Function for getting completer based on commands.
    :param commands: Active commands.
    :return: Completer.
    """
    completion = []
    for command in commands:
        completion.append(command.command)
        completion.extend(
            [f"--{argument}" for argument in list(command.argument_descriptions)])
    return WordCompleter(completion)


def handle_user_input(session: PromptSession, commands: List[Command], prompt: str = None) -> None:
    """
    Function to handle user input.
    :param session: Prompt session.
    :param commands: List of active commands.
    :param prompt: A specific prompt for prompting for user input.
        Defaults to None.
    """
    global CACHE

    user_input = session.prompt(
        f"{'' if prompt is None else prompt}> ", completer=get_completer(commands=commands))
    if user_input is not None:
        user_input = user_input.split(" --")
        cmd = user_input[0]
        cmd_obj = [
            cmd_obj for cmd_obj in commands if cmd_obj.command == cmd][0]
        cmd_kwargs = {"cache": CACHE}
        for index, argument in enumerate(user_input[1:]):
            if "=" in argument:
                keyword, value = argument.split("=")
                cmd_kwargs[keyword] = True if value.lower(
                ) == "true" else False if value.lower() == "false" else value
            else:
                cmd_kwargs[list(cmd_obj.argument_descriptions.keys())[index]
                           ] = True
        cmd_obj.run_command(**cmd_kwargs)


def run_session_loop() -> None:
    """
    Command line interface for Image Generation resource handling.
    """
    global CLOSE_SESSION, CACHE

    session = setup_session()
    while not CLOSE_SESSION:
        current_state = get_current_state()
        try:
            commands = handle_step(current_state=current_state)
            handle_user_input(session=session,
                              commands=commands,
                              prompt=current_state.get("prompt"))
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
            CACHE["current_path"] = ["error_page"]


"""
Entrypoint
"""
if __name__ == "__main__":
    run_session_loop()
