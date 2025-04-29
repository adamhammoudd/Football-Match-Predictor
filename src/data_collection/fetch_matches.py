import requests
import json
import logging
from pathlib import Path

class MatchFetcher:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        self.headers = self._load_api_key()
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "processed"
        self.teams_file = Path(__file__).parent.parent.parent / "data" / "teams.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _load_api_key(self):
        """Load API key from a config file."""
        try:
            with open(Path(__file__).parent.parent.parent / "config" / "api_keys.json") as f:
                return {"X-Auth-Token": json.load(f)["FOOTBALL_DATA_API_KEY"]}
        except Exception as e:
            raise SystemExit(f"API key error: {str(e)}")

    def _resolve_team_name(self, user_input):
        """Resolve the user input to the correct team ID using teams.json."""
        try:
            with open(self.teams_file, "r") as f:
                teams = json.load(f)
            for team, details in teams.items():
                if user_input.lower() == team.lower() or user_input.lower() in [alias.lower() for alias in details["aliases"]]:
                    return details["id"]  # Return the team ID instead of the API name
            raise ValueError(f"Team '{user_input}' not found in teams.json.")
        except Exception as e:
            raise ValueError(f"Error resolving team name: {e}")

    def fetch_team_matches(self, team_name, limit=5):
        """Fetch the latest matches for a team and save as JSON."""
        try:
            team_id = self._resolve_team_name(team_name)  # Resolve to team ID
            url = f"{self.base_url}/teams/{team_id}/matches"  # Use team ID in the URL
            params = {"status": "FINISHED", "limit": limit}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            matches = response.json().get("matches", [])

            processed_matches = [
                {
                    "home_team": match["homeTeam"]["name"],
                    "away_team": match["awayTeam"]["name"],
                    "home_score": match["score"]["fullTime"]["home"],
                    "away_score": match["score"]["fullTime"]["away"],
                    "outcome": self._determine_outcome(
                        team_name,
                        match["homeTeam"]["name"],
                        match["awayTeam"]["name"],
                        match["score"]["fullTime"]
                    )
                }
                for match in matches
            ]

            self._save_data(processed_matches, team_name)
            return processed_matches

        except Exception as e:
            logging.error(f"Failed to fetch matches for {team_name}: {str(e)}")
            raise

    def _determine_outcome(self, team_name, home_team, away_team, score):
        """Determine match outcome based on scores."""
        try:
            # Resolve team_name to its canonical api_name
            with open(self.teams_file, "r") as f:
                teams = json.load(f)
            resolved_team_name = next(
                (details["api_name"] for team, details in teams.items()
                if team_name.lower() == team.lower() or team_name.lower() in [alias.lower() for alias in details["aliases"]]),
                None
            )
            if not resolved_team_name:
                logging.error(f"Team name '{team_name}' could not be resolved.")
                return "Unknown"
        except Exception as e:
            logging.error(f"Error resolving team name in _determine_outcome: {e}")
            return "Unknown"

        # Normalize team names for comparison
        resolved_team_name = resolved_team_name.strip().lower()
        home_team = home_team.strip().lower()
        away_team = away_team.strip().lower()

        # Determine outcome based on scores
        if resolved_team_name == home_team:
            if score["home"] > score["away"]:
                return "Win"
            elif score["home"] < score["away"]:
                return "Loss"
            else:
                return "Draw"
        elif resolved_team_name == away_team:
            if score["away"] > score["home"]:
                return "Win"
            elif score["away"] < score["home"]:
                return "Loss"
            else:
                return "Draw"
        return "Unknown"

    def _save_data(self, matches, team_name):
        """Save processed matches to a JSON file."""
        filename = f"{team_name.lower().replace(' ', '_')}_matches.json"
        path = self.data_dir / filename
        with open(path, "w") as f:
            json.dump(matches, f, indent=4)
        logging.info(f"Saved data to {path}")