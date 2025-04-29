import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
from difflib import get_close_matches
import logging

logging.basicConfig(level=logging.INFO)

class MatchFetcher:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.headers = self._load_api_key()
        self.team_ids = self._load_team_ids()
        self._setup_dirs()

    def _setup_dirs(self):
        """Create required directories"""
        (self.data_dir / "processed").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "raw").mkdir(parents=True, exist_ok=True)

    def _load_api_key(self):
        """Load API key from config"""
        try:
            with open(self.config_dir / "api_keys.json") as f:
                return {"X-Auth-Token": json.load(f)["FOOTBALL_DATA_API_KEY"]}
        except Exception as e:
            raise SystemExit(f"API key error: {str(e)}")

    def _load_team_ids(self):
        """Load team IDs with API name normalization and aliases"""
        teams_file = self.data_dir / "teams.json"
        try:
            with open(teams_file) as f:
                teams_data = json.load(f)
            
            # Create a comprehensive mapping dictionary
            team_mapping = {}
            
            for team_key, team_info in teams_data.items():
                # Add main name mapping
                team_mapping[team_key.lower()] = {
                    'api_name': team_info['api_name'],
                    'id': team_info['id']
                }
                
                # Add all aliases as alternative keys
                for alias in team_info.get('aliases', []):
                    team_mapping[alias.lower()] = {
                        'api_name': team_info['api_name'],
                        'id': team_info['id']
                    }
            
            return team_mapping
            
        except Exception as e:
            raise SystemExit(f"Error loading team IDs: {str(e)}")

    def _make_api_request(self, url, params=None):
        """Make API request with error handling"""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            raise

    def fetch_team_matches(self, team_name, limit=5):
        """Fetch matches for a team with proper name handling"""
        try:
            # Normalize input name
            team_name = team_name.lower().strip()
            
            # Find best match in our team IDs
            if team_name not in self.team_ids:
                matches = get_close_matches(team_name, self.team_ids.keys(), n=1, cutoff=0.6)
                if not matches:
                    available = "\n- ".join(self.team_ids.keys())
                    raise ValueError(f"Team not found. Available:\n- {available}")
                team_name = matches[0]
            
            team_info = self.team_ids[team_name]
            team_id = team_info['id']
            api_name = team_info['api_name']
            
            # Fetch data
            url = f"{self.base_url}/teams/{team_id}/matches"
            params = {"status": "FINISHED", "limit": limit}
            data = self._make_api_request(url, params)
            
            # Process and save
            processed = self._process_matches(data.get("matches", []), api_name)
            self._save_data(processed, team_name)
            
            return processed
            
        except Exception as e:
            logging.error(f"Failed to fetch matches: {str(e)}")
            raise

    def _process_matches(self, matches, api_team_name):
        """Process raw matches into structured data"""
        processed = []
        for match in matches:
            try:
                processed.append({
                    "date": datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                    "competition": match["competition"]["name"],
                    "home_team": match["homeTeam"]["name"],
                    "away_team": match["awayTeam"]["name"],
                    "home_score": int(match["score"]["fullTime"]["home"]),
                    "away_score": int(match["score"]["fullTime"]["away"]),
                    "outcome": self._determine_outcome(
                        api_team_name,
                        match["homeTeam"]["name"],
                        match["awayTeam"]["name"],
                        match["score"]["fullTime"]
                    )
                })
            except Exception as e:
                logging.warning(f"Skipping match due to error: {str(e)}")
                continue
                
        return pd.DataFrame(processed)

    def _determine_outcome(self, team_name, home_team, away_team, score):
        """Determine match outcome from team's perspective"""
        if team_name.lower() == home_team.lower():
            if score["home"] > score["away"]: return "Win"
            if score["home"] < score["away"]: return "Loss"
            return "Draw"
        elif team_name.lower() == away_team.lower():
            if score["away"] > score["home"]: return "Win"
            if score["away"] < score["home"]: return "Loss"
            return "Draw"
        return "Unknown"

    def _save_data(self, df, team_name):
        """Save processed data to CSV"""
        filename = f"{team_name.lower().replace(' ', '_')}_matches.csv"
        path = self.data_dir / "processed" / filename
        df.to_csv(path, index=False)
        logging.info(f"Saved data to {path}")