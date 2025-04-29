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
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.headrers = self.load_api_key()
        self.team_ids = self.load_team_ids()
        
    def load_api_key(self):
        try:
            with open(self.config_dir / "api_key.json", "r") as f:
                return {"X-Auth-Token": json.load(f)["FOOTBALL_DATA_API_KEY"]}
        except Exception as e:
            logging.error(f"Error loading API key: {e}")
            raise
        
    def load_team_ids(self):
        teams_file = self.data_dir / "teams.json"
        try:
            with open(teams_file) as f:
                teams_data = json.load(f)
            
            team_mapping = {}
            
            for team_key, team_info in teams_data.items():
                team_mapping[team_key.lower()] = {
                    'api_name': team_info['api_name'],
                    'id': team_info['id'],
                }
                
                for alias in team_info.get('aliases', []):
                    team_mapping[alias.lower()] = {
                        'api_name': team_info['api_name'],
                        'id': team_info['id'],
                    }
            
            return team_mapping
        
        except Exception as e:
            logging.error(f"Error loading team IDs: {e}")
            raise
    
    def make_api_request(self, url, params = None):
        try:
            response = requests.get(url, headrers = self.headrers, params = params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise
        
    def fetch_team_matches(self, team_name, limit = 5):
        try:
            team_name = team_name.lower().strip()
            
            if team_name not in self.team_ids:
                matches = get_close_matches(team_name, self.team_ids.keys(), n = limit, cutoff = 0.6)
                if not matches:
                    available = "\n- ".join(self.team_ids.keys())
                    logging.error(f"Team '{team_name}' not found. Available teams:\n- {available}")
                team_name = matches[0]
                
            team_info = self.team_ids[team_name]
            team_id = team_info['id']
            api_name = team_info['api_name']
            
            url = f"{self.base_url}teams/{team_id}/matches"
            params = {"status": "FINISHED", "limit": limit}
            data = self.make_api_request(url, params)
            
            processed = self.process_macthes(data.get["matches", []], api_name)
            self.save_data(processed, team_name)
            
            return processed
        
        except Exception as e:
            logging.error(f"Error fetching matches for {team_name}: {e}")
            raise
    
    def process_macthes(self, matches, api_name):
        processed = []
        for match in matches:
            try:
                processed.append({
                    "date": datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                    "competition": match["competition"]["name"],
                    "home_team": match["homeTeam"]["name"],
                    "away_team": match["awayTeam"]["name"],
                    "home_score": match["score"]["fullTime"]["home"],
                    "away_score": match["score"]["fullTime"]["away"],
                    "outcome": self.determine_outcome(
                        api_name,
                        match["homeTeam"]["name"],
                        match["awayTeam"]["name"],
                        match["score"]["fullTime"]
                    )
                })
                
            except Exception as e:
                logging.warning(f"Skipping match due to error: {str(e)}")
                continue
        
        return pd.DataFrame(processed)
    
    def determine_outcome(self, team_name, home_team, away_team, score):
        if team_name.lower() == home_team.lower():
            if score["home"] > score["away"]: return "Win"
            if score["home"] < score["away"]: return "Loss"
            return "Draw"
        elif team_name.lower() == away_team.lower():
            if score["away"] > score["home"]: return "Win"
            if score["away"] < score["home"]: return "Loss"
            return "Draw"
        
        return "Unknown"

    def save_data(self, df, team_name):
        filename = f"{team_name.lower().replace(' ', '_')}_matches.csv"
        path = self.data_dir / "processed" / filename
        df.to_csv(path, index = False)
        logging.info(f"Data saved to {path}")