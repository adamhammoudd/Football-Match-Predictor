import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
import joblib
import logging

logging.basicConfig(level=logging.INFO)

class MatchPredictor:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.model_path = self.data_dir / "model" / "predictor.pkl"
        self.model = self._load_model() or RandomForestClassifier(n_estimators=100, random_state=42)
        self.features = ['home_form', 'away_form', 'goals_diff']
        self.target = 'outcome'

    def _load_model(self):
        """Load trained model if exists"""
        try:
            self.model_path.parent.mkdir(exist_ok=True)
            return joblib.load(self.model_path)
        except Exception:
            return None

    def predict_winner(self, home_team, away_team):
        """Predict match winner with automatic data handling"""
        try:
            # Ensure we have data for both teams
            home_data = self._ensure_team_data(home_team)
            away_data = self._ensure_team_data(away_team)
            
            # Prepare features
            features = {
                'home_form': self._calculate_form(home_data),
                'away_form': self._calculate_form(away_data),
                'goals_diff': self._calculate_goals_diff(home_data, away_data)
            }
            
            # Train model if needed
            if not self._load_model():
                self._train_model(home_data, away_data)
            
            # Make prediction
            return self._make_prediction(features, home_team, away_team)
            
        except Exception as e:
            logging.error(f"Prediction failed: {str(e)}")
            raise ValueError(f"Couldn't predict match: {str(e)}")

    def _ensure_team_data(self, team_name):
        """Ensure team data exists or fetch it"""
        try:
            return self._load_team_data(team_name)
        except FileNotFoundError:
            from src.data_collection.fetch_matches import MatchFetcher
            logging.info(f"Fetching data for {team_name}...")
            return MatchFetcher().fetch_team_matches(team_name)

    def _load_team_data(self, team_name):
        """Load team data with validation"""
        filename = f"{team_name.lower().replace(' ', '_')}_matches.csv"
        path = self.data_dir / "processed" / filename
        
        if not path.exists():
            raise FileNotFoundError(f"No data file for {team_name}")
            
        df = pd.read_csv(path)
        
        # Validate required columns
        required_cols = ['home_team', 'away_team', 'home_score', 'away_score', 'outcome']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Invalid data format for {team_name}")
            
        return df

    def _calculate_form(self, team_data):
        """Calculate team form (win percentage)"""
        last_5 = team_data.tail(5)
        if len(last_5) < 3:
            return 0.5  # Neutral form if insufficient data
            
        wins = (last_5['outcome'] == 'Win').sum()
        draws = (last_5['outcome'] == 'Draw').sum()
        return (wins + 0.5 * draws) / len(last_5)

    def _calculate_goals_diff(self, home_data, away_data):
        """Calculate goal difference metric"""
        home_goals = home_data['home_score'].mean() if 'home_score' in home_data else 1.0
        away_conceded = away_data['away_score'].mean() if 'away_score' in away_data else 1.0
        return home_goals - away_conceded

    def _train_model(self, home_data, away_data):
        """Train and save the prediction model"""
        train_data = self._prepare_training_data(home_data, away_data)
        self.model.fit(train_data[self.features], train_data[self.target])
        joblib.dump(self.model, self.model_path)
        logging.info("Trained and saved new model")

    def _prepare_training_data(self, home_data, away_data):
        """Prepare combined training data"""
        combined = pd.concat([home_data, away_data])
        
        # Calculate features
        combined['home_form'] = combined.groupby('home_team')['outcome'].transform(
            lambda x: x.rolling(5, min_periods=3).apply(
                lambda y: (y == 'Win').mean()
            )
        )
        combined['away_form'] = combined.groupby('away_team')['outcome'].transform(
            lambda x: x.rolling(5, min_periods=3).apply(
                lambda y: (y == 'Win').mean()
            )
        )
        combined['goals_diff'] = combined['home_score'] - combined['away_score']
        
        # Encode target
        combined['outcome'] = combined['outcome'].map({'Win': 1, 'Draw': 0.5, 'Loss': 0})
        
        return combined.dropna(subset=self.features + [self.target])

    def _make_prediction(self, features, home_team, away_team):
        """Make final prediction"""
        proba = self.model.predict_proba(pd.DataFrame([features]))[0]
        winner = home_team if proba[1] > 0.5 else away_team
        confidence = max(proba)
        
        return {
            'winner': winner,
            'probability': float(confidence),
            'home_team_form': f"{features['home_form']:.0%}",
            'away_team_form': f"{features['away_form']:.0%}"
        }