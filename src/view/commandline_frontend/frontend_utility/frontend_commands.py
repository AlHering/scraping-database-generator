# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from typing import Optional, Any, Callable, Dict
import copy
import traceback
from src.interfaces.frontend_interface import populate_or_get_frontend_cache
from src.view.commandline_frontend.frontend_utility.coloring import RichColors


class Command(object):
    """
    Command class.
    """

    def __init__(self, command: str, function: Callable, kwargs_description: Dict[str, str], default_kwargs: dict = None, help_text: str = None) -> None:
        """
        Initiation method.
        :param command: Command.
        :param function: Function.
        :param kwargs_description: Keyword argument descriptions.
        :param default_kwargs: Default keyword arguments.
            Defaults to None.
        :param help_text: Help text.
            Defaults to None.
        """
        self.command = command
        self.function = function
        self.kwargs_description = kwargs_description
        self.default_kwargs = {} if default_kwargs is None else default_kwargs
        self.help_text = f"[{RichColors.commands}]No help text available for '[{RichColors.command}]{command}[{RichColors.commands}]'" if help_text is None else help_text
        for keyword in kwargs_description:
            self.helptext = f"\n\t[{RichColors.command}]{keyword}{RichColors.commands}: {kwargs_description[keyword]}"

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


def reset_and_return(**kwargs: Optional[Any]) -> None:
    """
    Function for resetting and return.
    :param kwargs: Additonal keyword arguments.
    """
    kwargs["cache"] = populate_or_get_frontend_cache(force_default=True)
    kwargs["cache"]["current_path"] = ["main_page"]


RESET_CACHE_AND_RETURN_TO_MAIN = Command(
    command="reset-and-return",
    function=lambda **kwargs: reset_and_return(kwargs),
    help_text="Reset the cache and return to the main page."
)
