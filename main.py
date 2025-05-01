from src.data_collection.fetch_matches import MatchFetcher
from src.models.predictor import MatchPredictor
import logging

logging.basicConfig(level=logging.INFO)

class FootballAI:
    def __init__(self):
        self.fetcher = MatchFetcher()
        self.predictor = MatchPredictor()

    def predict_match(self, home_team, away_team):
        """Fetch data for both teams and predict the match outcome."""
        try:
            print(f"\nFetching data for {home_team.upper()} and {away_team.upper()}...")
            self.fetcher.fetch_team_matches(home_team)
            self.fetcher.fetch_team_matches(away_team)

            print(f"\nPredicting {home_team.upper()} vs {away_team.upper()}...")
            result = self.predictor.predict_winner(home_team, away_team)

            print("\n" + "=" * 40)
            if result['probability'] == 0.5:
                print("PREDICTION: It's a DRAW")
                print(f"\nCurrent Form:")
                print(f"- {home_team.upper()}: {result['home_team_form']}")
                print(f"- {away_team.upper()}: {result['away_team_form']}")
                print("=" * 40)
            else:
                print(f"PREDICTION: {result['winner'].upper()} is favored")
                print(f"PROBABILITY: {result['probability']:.1%}")
                print(f"\nCurrent Form:")
                print(f"- {home_team.upper()}: {result['home_team_form']}")
                print(f"- {away_team.upper()}: {result['away_team_form']}")
                print("=" * 40)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def main():
    ai = FootballAI()

    while True:
        print("\nFootball Match Predictor")
        print("1. Predict match outcome")
        print("2. Exit")

        choice = input("Select option: ").strip()

        if choice == "1":
            home = input("\nHome team: ").strip()
            away = input("Away team: ").strip()
            if home and away:
                ai.predict_match(home, away)
            else:
                print("Both team names are required")
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()