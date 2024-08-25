import click
import bs4
import requests

from pathlib import Path
from flask import current_app

from memorybox.config import Config, MemoriesSourceType
from memorybox import db

def _fetch_memories_from_local_directory():
    local_directory_path = Config().memories_local_path
    current_app.logger.info(f"Looking for packages in {local_directory_path}")
    db.get_db()
    for zip_file in Path(local_directory_path).rglob('*.zip'):
        current_app.logger.info(f"Found zip file : {zip_file}")
    for tar_file in Path(local_directory_path).rglob('*.tar'):
        current_app.logger.info(f"Found tar file : {tar_file}")

def _fetch_memories_from_remote_repository():
    current_app.logger.info("Fetching packages from remote repository.")

def fetch_memories():
    """Fetch new memories (pictures) from packages."""
    if Config().memories_source_type == MemoriesSourceType.LOCAL:
        _fetch_memories_from_local_directory()
    elif Config().memories_source_type == MemoriesSourceType.REPOSITORY:
        _fetch_memories_from_remote_repository()
    else:
        current_app.logger.info(Config().memories_source_type)
        pass # TODO : throw error
