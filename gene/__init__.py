"""The VICC library for normalizing genes."""
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)
