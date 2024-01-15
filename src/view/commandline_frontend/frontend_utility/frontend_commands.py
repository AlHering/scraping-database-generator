# -*- coding: utf-8 -*-
"""
****************************************************
*           Scraping Database Generator            *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
import os
from typing import Optional, Any, Callable, Dict
import copy
import traceback
from src.interfaces.frontend_interface import populate_or_get_frontend_cache, save_frontend_cache
from src.view.commandline_frontend.frontend_utility.coloring import RichColors


IGNORED_CACHE_FIELDS = ["current_path", "last_path"]


class Command(object):
    """
    Command class.
    """

    def __init__(self, command: str, function: Callable, argument_descriptions: Dict[str, str], default_kwargs: dict = None, help_text: str = None) -> None:
        """
        Initiation method.
        :param command: Command.
        :param function: Function.
        :param argument_descriptions: Keyword argument descriptions.
        :param default_kwargs: Default keyword arguments.
            Defaults to None.
        :param help_text: Help text.
            Defaults to None.
        """
        self.command = command
        self.function = function
        self.argument_descriptions = argument_descriptions
        self.default_kwargs = {} if default_kwargs is None else default_kwargs
        self.help_text = f"[{RichColors.commands}]No help text available for '[{RichColors.command}]{command}[{RichColors.commands}]'" if help_text is None else help_text
        for keyword in argument_descriptions:
            self.help_text += f"\n    [{RichColors.command}]--{keyword}[{RichColors.commands}]: {argument_descriptions[keyword]}"

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
    if kwargs.get("dumpCache", False):
        dump_path = kwargs.get("dumpPath", False)
        if dump_path:
            dump_folder = os.path.dirname(dump_path)
            if os.path.exists(dump_folder):
                save_frontend_cache(
                    kwargs["cache"], ignore=IGNORED_CACHE_FIELDS, output_path=dump_path)
            else:
                raise OSError(f"Could not find '{dump_folder}'")
        else:
            
    kwargs["cache"] = populate_or_get_frontend_cache(force_default=True)
    kwargs["cache"]["current_path"] = ["main_page"]


RESET_CACHE_AND_RETURN_TO_MAIN = Command(
    command="reset-and-return",
    function=lambda **kwargs: reset_and_return(kwargs),
    argument_descriptions={
        "dumpCache": "(optional flag) Dump cache before returning.",
        "dumpPath": "(optional argument) Path for dumping cache."
    },
    help_text="Reset the cache and return to the main page."
)
