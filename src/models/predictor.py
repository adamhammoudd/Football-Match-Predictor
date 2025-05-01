import json
from pathlib import Path

class MatchPredictor:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "processed"

    def predict_winner(self, home_team, away_team):
        """Predict the winner based on recent outcomes."""
        home_data = self._load_team_data(home_team)
        away_data = self._load_team_data(away_team)

        home_form, home_summary = self._calculate_form(home_data, home_team)
        away_form, away_summary = self._calculate_form(away_data, away_team)

        # Calculate performance scores based on recent outcomes
        home_score = home_form.count("W") * 3 + home_form.count("D")  # 3 points for a win, 1 point for a draw
        away_score = away_form.count("W") * 3 + away_form.count("D")

        # Calculate probabilities based on scores
        total_score = home_score + away_score
        if total_score > 0:
            home_probability = home_score / total_score
            away_probability = away_score / total_score
        else:
            home_probability = away_probability = 0.5  # Default to 50% if no matches are available

        winner = home_team if home_probability > away_probability else away_team

        # Print the summaries and forms
        print(f"\n{home_summary}\n{home_team.upper()} form: {home_form.upper()}")
        print(f"\n{away_summary}\n{away_team.upper()} form: {away_form.upper()}")

        return {
            "winner": winner,
            "probability": max(home_probability, away_probability),
            "home_team_form": home_form,
            "away_team_form": away_form,
        }

    def _load_team_data(self, team_name):
        """Load team data from a JSON file."""
        filename = f"{team_name.lower().replace(' ', '_')}_matches.json"
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"No data found for {team_name}")
        with open(path, "r") as f:
            return json.load(f)

    def _calculate_form(self, matches, team_name):
        """Calculate the form of a team based on recent outcomes."""
        outcomes = [match["outcome"] for match in matches]
        form_string = "".join(outcome[0] for outcome in outcomes)  # Take the first letter of each outcome (e.g., "W", "L", "D")
        
        # Count wins, draws, and losses
        wins = outcomes.count("Win")
        draws = outcomes.count("Draw")
        losses = outcomes.count("Loss")
        
        # Generate a descriptive summary
        summary = (
            f"{team_name.upper()} Won {wins}, Drew {draws}, and Lost {losses} "
            f"in their last {len(outcomes)} matches"
        )
        
        return form_string, summary