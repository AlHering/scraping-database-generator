# -*- coding: utf-8 -*-
"""
****************************************************
*                   Follower LLM                   *
*            (c) 2023 Alexander Hering             *
****************************************************
"""

import os
from datetime import datetime as dt
from src.utility.gold.text_generation.language_model_abstractions import Agent, LanguageModelInstance
from typing import List, Tuple, Any, Callable, Optional, Type


class LangchainScrapingCoder(Agent):
    """
    Class, representing Scraping Coders which utilize language models to support programming scraping infrastructure.
    """

    def __init__(self,
                 general_llm: LanguageModelInstance) -> None:
        """
        Initiation method.
        :param general_llm: LanguageModelInstance for general tasks.
        """
