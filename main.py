from src.data_collection.fetch_matches import MatchFetcher
from src.models.predictor import MatchPredictor
import logging

logging.basicConfig(level=logging.INFO)

class FootballAI:
    def __init__(self):
        self.fetcher = MatchFetcher()
        self.predictor = MatchPredictor()

    def update_all_data(self):
        """Update data for all teams"""
        print("\nUpdating data for all teams:")
        for team_name in self.fetcher.team_ids.keys():
            try:
                self.fetcher.fetch_team_matches(team_name)
                print(f"✓ {team_name}")
            except Exception as e:
                print(f"✗ {team_name}: {str(e)}")

    def update_team_data(self, team_name):
        """Update data for specific team"""
        try:
            print(f"\nUpdating data for {team_name}...")
            self.fetcher.fetch_team_matches(team_name)
            print("✓ Success")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")

    def predict_match(self, home_team, away_team):
        """Predict match outcome with full error handling"""
        try:
            print(f"\nPredicting {home_team} vs {away_team}...")
            result = self.predictor.predict_winner(home_team, away_team)
            
            print("\n" + "="*40)
            print(f"PREDICTION: {result['winner'].upper()} is favored")
            print(f"Confidence: {result['probability']:.1%}")
            print(f"\nCurrent Form:")
            print(f"- {home_team}: {result['home_team_form']}")
            print(f"- {away_team}: {result['away_team_form']}")
            print("="*40)
            
            return result
            
        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            print("Possible fixes:")
            print("- Check team name spelling")
            print("- Verify team exists in teams.json")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")

def main():
    ai = FootballAI()
    
    while True:
        print("\nFootball Match Predictor")
        print("1. Predict match outcome")
        print("2. Check available teams")
        print("3. Exit")
        
        choice = input("Select option: ").strip()
        
        if choice == "1":
            home = input("Home team: ").strip()
            away = input("Away team: ").strip()
            if home and away:
                ai.predict_match(home, away)
            else:
                print("Both team names are required")
                
        elif choice == "2":
            print("\nAvailable Teams:")
            for team in ai.fetcher.team_ids.keys():
                print(f"- {team}")
                
        elif choice == "3":
            print("Goodbye!")
            break
            
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()