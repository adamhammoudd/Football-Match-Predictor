# Football Match Predictor

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Steps](#steps)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
   - [Data Flow](#data-flow)
   - [Prediction Algorithm](#prediction-algorithm)
- [File Structure](#file-structure)
- [API Requirements](#api-requirements)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

## Overview
This is a Python-based football match prediction system that analyzes recent team performance to predict match outcomes. The system fetches historical match data from the Football-Data.org API, processes this information, and provides predictions based on team form.

## Features
- Fetches recent match data for any team in the database
- Calculates team form based on last 5 matches
- Provides prediction with confidence percentage
- Displays recent form for both teams
- Supports over 200 teams across major European leagues
- Simple command-line interface
- Data persistence (saves fetched matches locally)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Football-Data.org API key (free tier available)

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/football-match-predictor.git
    cd football-match-predictor
    ```
2. Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
1. Get your API key from Football-Data.org.
2. Create a `config/api_keys.json` file with the following content:
    ```json
    {
       "FOOTBALL_DATA_API_KEY": "your_api_key_here"
    }
    ```
3. The program comes with a pre-populated `data/teams.json` containing team IDs and aliases. You can modify this file to add more teams if needed.

## Usage
Run the program:
```bash
python src/main.py
```
Follow the on-screen prompts:
1. Select option "1" to predict a match.
2. Enter the home team name (can use official name or any alias).
3. Enter the away team name.
4. View the prediction results.

Example session:
```
Football Match Predictor
1. Predict match outcome
2. Exit

Select option: 1
Home team: man city
Away team: liverpool

Fetching data for man city and liverpool...

Predicting man city vs liverpool...

Manchester City FC won 3, drew 1, and lost 1 in their last 5 matches
man city form: WWDLW
Liverpool FC won 4, drew 0, and lost 1 in their last 5 matches
liverpool form: WWWLW

========================================
PREDICTION: LIVERPOOL FC is favored
Confidence: 66.7%

Current Form:
- man city: WWDLW
- liverpool: WWWLW
========================================
```

## How It Works

### Data Flow
1. **Data Collection (`fetch_matches.py`)**:
    - Resolves team names to API IDs.
    - Fetches last 5 finished matches from Football-Data.org.
    - Processes and saves match data locally.
2. **Prediction Engine (`predictor.py`)**:
    - Loads saved match data.
    - Calculates team form (win/draw/loss sequence).
    - Computes performance scores.
    - Generates prediction probabilities.
3. **Main Application (`main.py`)**:
    - Provides user interface.
    - Coordinates data fetching and prediction.
    - Displays results.

### Prediction Algorithm
The system uses a simple form-based algorithm:
- Win = 3 points
- Draw = 1 point
- Loss = 0 points
- Probability is calculated based on the ratio of these points.
- Recent form (last 5 matches) is displayed as a string (e.g., "WWDLW").

## File Structure
```
football-match-predictor/
├── config/
│   └── api_keys.json          # API key configuration
├── data/
│   ├── processed/             # Saved match data
│   └── teams.json             # Team database
├── src/
│   ├── data_collection/
│   │   └── fetch_matches.py   # Data fetching module
│   ├── models/
│   │   └── predictor.py       # Prediction engine
│   └── main.py                # Main application
├── .gitignore
└── README.md
```

## API Requirements
This program uses the Football-Data.org API:
- Free tier allows 10 requests per minute.
- Requires registration to get an API key.
- Rate limiting is handled by the API provider.

## Limitations
- Only considers last 5 matches by default.
- Doesn't account for injuries/suspensions.
- No head-to-head history analysis.
- Basic probability calculation.
- Dependent on API availability.

## Future Improvements
- Add machine learning model for predictions.
- Incorporate more statistics (goals scored/conceded).
- Add head-to-head historical data.
- Implement GUI/web interface.
- Add league table position consideration.
- Include player statistics.

## Contributing
Contributions are welcome! Please open an issue or pull request for any:
- Bug fixes
- New features
- Documentation improvements
- Performance optimizations

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```