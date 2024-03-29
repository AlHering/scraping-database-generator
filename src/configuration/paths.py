# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os

"""
Base 
"""
PACKAGE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(
    os.path.dirname(__file__))))
SOURCE_PATH = os.path.join(PACKAGE_PATH, "src")
DOCS_PATH = os.path.join(PACKAGE_PATH, "docs")
SUBMODULE_PATH = os.path.join(SOURCE_PATH, "submodules")
DATA_PATH = os.path.join(PACKAGE_PATH, "data")
TEST_PATH = os.path.join(DATA_PATH, "testing")
PLUGIN_PATH = os.path.join(SOURCE_PATH, "plugins")
DUMP_PATH = os.path.join(DATA_PATH, "processes", "dumps")


"""
Machine Learning Models
"""
TEXTGENERATION_MODEL_PATH = os.path.join(
    PACKAGE_PATH, "machine_learning_models", "MODELS")
TEXTGENERATION_LORA_PATH = os.path.join(
    PACKAGE_PATH, "machine_learning_models", "LORAS")
EMBEDDING_MODEL_PATH = os.path.join(
    PACKAGE_PATH, "machine_learning_models", "EMBEDDING_MODELS")

"""
Backends
"""
BACKEND_PATH = os.path.join(DATA_PATH, "backend")


"""
Frontends
"""
FRONTEND_PATH = os.path.join(DATA_PATH, "frontend")
FRONTEND_DEFAULT_CACHE = os.path.join(FRONTEND_PATH, "default_cache.json")
FRONTEND_CACHE = os.path.join(FRONTEND_PATH, "cache.json")
RESPONSE_PATH = os.path.join(FRONTEND_PATH, "responses")
