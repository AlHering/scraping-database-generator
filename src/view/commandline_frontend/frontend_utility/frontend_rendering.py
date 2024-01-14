# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from typing import List, Optional
from rich.panel import Panel
import traceback
from rich.style import Style as RichStyle
from prompt_toolkit.styles import Style as PTStyle
from src.view.commandline_frontend.frontend_utility.frontend_commands import Command


def get_error_page(commands: List[Command]) -> dict:
    """
    Function for acquiring error page.
    :param commands: List of commands.
    :return: Error page structure.
    """
    trace = traceback.format_exc()
    if trace == "NoneType: None\n":
        content = f"[red] An error appeared."
    else:
        content = f"[red]{trace}"

    panels = [Panel(f"{content}", title="[red bold]Error",
                    border_style=RichStyle(color="red"))]
    if commands:
        panels.append(get_available_command_panel(commands))

    return {
        "pre_panels": [],
        "execute": [],
        "post_panels": panels,
        "commands": commands,
        "prompt": ""
    }


def get_available_command_panel(available_commands: List[Command] = None) -> Optional[Panel]:
    """
    Function for acquiring a panel, containing available commands.
    :param available_commands: List of available commands.
    :return: Panel, containing available commands, if there are any.
    """
    return Panel("\n".join([f"[bright_blue]{cmd.command}[cyan]: {cmd.help_text}" for cmd in available_commands]), title="[cyan bold]Commands", border_style=RichStyle(color="cyan")) if available_commands else None


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
