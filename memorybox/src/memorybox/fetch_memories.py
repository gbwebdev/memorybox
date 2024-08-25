import click
import bs4
import requests
from pathlib import Path
import shutil

from flask import current_app

from PIL import Image

from memorybox.config import Config, MemoriesSourceType
from memorybox.model.memory import Memory
from memorybox.db import db


def _fetch_memories_from_local_directory():
    local_directory_path = Config().memories_local_path
    current_app.logger.info(f"Looking for packages in {local_directory_path}")
    for jpeg_file in Path(local_directory_path).rglob('*.[jJ][pP]*[gG]'):
        filename = Path(jpeg_file).name
        current_app.logger.info(f"Found JPEG file : {filename}")
        res = Memory.query.filter_by(filename=filename).first()
        if not res :
            current_app.logger.info(f"File not found in database : {filename}")
            new_path = Path(current_app.config['memories_path']).joinpath(filename)
            shutil.move(jpeg_file, new_path)

            thumbnail_path = Path(current_app.config['thumbnails_path']).joinpath(filename)
            image = Image.open(new_path)
            #Define the thumbnail size as a tuple (width, height)

            base_width = 1280
            wpercent = (base_width / float(image.size[0]))
            hsize = int((float(image.size[1]) * float(wpercent)))
            image = image.resize((base_width, hsize), Image.BOX)
            image.save(thumbnail_path)
            


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
