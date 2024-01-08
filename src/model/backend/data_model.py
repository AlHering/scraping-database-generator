# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from sqlalchemy.orm import relationship, mapped_column, declarative_base
from sqlalchemy import Engine, Column, String, JSON, ForeignKey, Integer, DateTime, func, Uuid, Text, event, Boolean
from uuid import uuid4, UUID
from typing import Any


def fix_schema(schema: str) -> str:
    """
    Function for fixing schema for populating infrastructure.
    :param schema: Schema string.
    :return: Fixed schema string.
    """
    schema = str(schema)
    if not schema.endswith("."):
        schema += "."
    return schema


def populate_data_instrastructure(engine: Engine, schema: str, model: dict) -> None:
    """
    Function for populating data infrastructure.
    :param engine: Database engine.
    :param schema: Schema for tables.
    :param model: Model dictionary for holding data classes.
    """
    schema = fix_schema(schema)
    base = declarative_base()

    class Log(base):
        """
        Log class, representing an log entry.
        """
        __tablename__ = f"{schema}log"
        __table_args__ = {
            "comment": "Log table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False,
                    comment="ID of the logging entry.")
        request = Column(JSON, nullable=False,
                         comment="Request, sent to the backend.")
        response = Column(JSON, comment="Response, given by the backend.")
        requested = Column(DateTime, server_default=func.now(),
                           comment="Timestamp of request recieval.")
        responded = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                           comment="Timestamp of reponse transmission.")

    class GenerationProfile(base):
        """
        GenerationProfile class, representing an scraping database generation profile entry.
        """
        __tablename__ = f"{schema}generation_profile"
        __table_args__ = {
            "comment": "GenerationProfile table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False,
                    comment="ID of the entry.")
        request_url = Column(String, nullable=False,
                             comment="Request URL from which profile is generated.")
        request_headers = Column(
            JSON, comment="Request headers from which profile is generated.")

        generation_profile = Column(
            JSON, comment="Generation profile.")

        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

    for dataclass in [Log, GenerationProfile]:
        model[dataclass.__tablename__.replace(schema, "")] = dataclass

    base.metadata.create_all(bind=engine)
