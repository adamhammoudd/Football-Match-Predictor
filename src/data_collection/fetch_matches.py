import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
from difflib import get_close_matches
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MatchFetcher:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4/"
        self.data_dir = Path(__file__).parent / "data"