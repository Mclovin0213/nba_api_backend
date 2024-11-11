from flask import Flask, jsonify
from flask_cors import CORS
from nba_api.live.nba.endpoints import ScoreBoard, BoxScore
from nba_api.stats.endpoints import playercareerstats
from utils import calculate_averages
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return "NBA Live Stats API"

@app.route('/live_games', methods=['GET'])
def get_live_games():
    """
    Fetches live games for today using the ScoreBoard endpoint.
    Returns a list of games with essential information only.
    """
    try:
        # Initialize the ScoreBoard for today's date
        scoreboard = ScoreBoard()
        scoreboard_data = scoreboard.get_dict()

        games = []
        if "scoreboard" in scoreboard_data and "games" in scoreboard_data["scoreboard"]:
            for game in scoreboard_data["scoreboard"]["games"]:
                game_info = {
                    'game_id': game.get('gameId', ''),
                    'game_status': game.get('gameStatusText', ''),
                    'home_team_id': game['homeTeam'].get('teamId', ''),
                    'home_score': game['homeTeam'].get('score', 0),
                    'away_team_id': game['awayTeam'].get('teamId', ''),
                    'away_score': game['awayTeam'].get('score', 0),
                    'game_time': game.get('gameTimeUTC', ''),
                }
                games.append(game_info)

        return jsonify({'live_games': games}), 200
    except Exception as e:
        return jsonify({'error': f"Failed to fetch live games: {str(e)}"}), 500

@app.route('/game/<game_id>/player_stats', methods=['GET'])
def get_player_stats(game_id):
    """
    Fetches player statistics for a specific game using the BoxScore endpoint.
    Returns detailed statistics for players in both teams.
    """
    try:
        # Initialize the BoxScore for the given game_id
        box_score = BoxScore(game_id=game_id)
        box_score_data = box_score.get_dict()

        player_stats = {}

        if "game" in box_score_data:
            game = box_score_data["game"]

            # Process Home Team Players
            home_team = game.get("homeTeam", {})
            home_team_name = home_team.get("teamName", "Home")
            home_players = []
            for player in home_team.get("players", []):
                stats = player.get("statistics", {})
                player_info = {
                    'player_id': player.get('personId', ''),
                    'name': player.get('name', ''),
                    'position': player.get('position', ''),
                    'team_tricode': player.get('teamTricode', ''),
                    'points': stats.get('points', 0),
                    'rebounds': stats.get('reboundsTotal', 0),
                    'assists': stats.get('assists', 0),
                    'steals': stats.get('steals', 0),
                    'blocks': stats.get('blocks', 0),
                    'turnovers': stats.get('turnovers', 0),
                    'minutes': stats.get('minutesCalculated', ''),
                    'field_goals_made': stats.get('fieldGoalsMade', 0),
                    'field_goals_attempted': stats.get('fieldGoalsAttempted', 0),
                    'three_pointers_made': stats.get('threePointersMade', 0),
                    'three_pointers_attempted': stats.get('threePointersAttempted', 0),
                    'free_throws_made': stats.get('freeThrowsMade', 0),
                    'free_throws_attempted': stats.get('freeThrowsAttempted', 0),
                }
                home_players.append(player_info)

            # Process Away Team Players
            away_team = game.get("awayTeam", {})
            away_team_name = away_team.get("teamName", "Away")
            away_players = []
            for player in away_team.get("players", []):
                stats = player.get("statistics", {})
                player_info = {
                    'player_id': player.get('personId', ''),
                    'name': player.get('name', ''),
                    'position': player.get('position', ''),
                    'team_tricode': player.get('teamTricode', ''),
                    'points': stats.get('points', 0),
                    'rebounds': stats.get('reboundsTotal', 0),
                    'assists': stats.get('assists', 0),
                    'steals': stats.get('steals', 0),
                    'blocks': stats.get('blocks', 0),
                    'turnovers': stats.get('turnovers', 0),
                    'minutes': stats.get('minutesCalculated', ''),
                    'field_goals_made': stats.get('fieldGoalsMade', 0),
                    'field_goals_attempted': stats.get('fieldGoalsAttempted', 0),
                    'three_pointers_made': stats.get('threePointersMade', 0),
                    'three_pointers_attempted': stats.get('threePointersAttempted', 0),
                    'free_throws_made': stats.get('freeThrowsMade', 0),
                    'free_throws_attempted': stats.get('freeThrowsAttempted', 0),
                }
                away_players.append(player_info)

            player_stats = {
                'game_id': game_id,
                'home_team': home_team_name,
                'home_players': home_players,
                'away_team': away_team_name,
                'away_players': away_players,
            }

        return jsonify({'player_stats': player_stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/player/<player_id>/season_stats_average', methods=['GET'])
def get_player_season_stats_average(player_id):
    """
    Fetches current season average statistics for a specific player using the PlayerCareerStats endpoint.
    Returns average statistics per game for the current season.
    """
    try:
        # Define the current season. NBA seasons span two calendar years.
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        if current_month >= 10:  # NBA season starts in October
            season = f"{current_year}-{str(current_year + 1)[-2:]}"
        else:
            season = f"{current_year - 1}-{str(current_year)[-2:]}"
        
        # Initialize the PlayerCareerStats for the given player_id
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_data = career_stats.get_dict()
        
        # Extract regular season stats
        regular_season_data = next((item for item in career_data['resultSets'] if item['name'] == 'SeasonTotalsRegularSeason'), None)
                
        if not regular_season_data or not regular_season_data['rowSet']:
            return jsonify({'error': 'No regular season stats found for this player.'}), 404
                
        # Find the headers and map them to the data rows
        headers = regular_season_data['headers']
        current_season_stats = next(
            (dict(zip(headers, row)) for row in regular_season_data['rowSet'] 
             if row[headers.index('SEASON_ID')] == season),
            None
        )
        
        print(current_season_stats)
        
        if not current_season_stats:
            return jsonify({'error': 'No regular season stats found for this player in the current season.'}), 404
        
        games_played = current_season_stats.get('GP', 0)
        
        # Prepare stats dictionary
        stats = {
            'player_id': current_season_stats.get('PLAYER_ID', ''),
            'season': season,
            'points': current_season_stats.get('PTS', 0),
            'rebounds': current_season_stats.get('REB', 0),
            'assists': current_season_stats.get('AST', 0),
            'steals': current_season_stats.get('STL', 0),
            'blocks': current_season_stats.get('BLK', 0),
            'turnovers': current_season_stats.get('TOV', 0),
            'minutes': current_season_stats.get('MIN', '0'),
            'field_goals_made': current_season_stats.get('FGM', 0),
            'field_goals_attempted': current_season_stats.get('FGA', 0),
            'three_pointers_made': current_season_stats.get('FG3M', 0),
            'three_pointers_attempted': current_season_stats.get('FG3A', 0),
            'free_throws_made': current_season_stats.get('FTM', 0),
            'free_throws_attempted': current_season_stats.get('FTA', 0),
        }
        
        # Calculate averages
        average_stats = calculate_averages(stats, games_played)
        
        return jsonify({'season_average_stats': average_stats}), 200
    except Exception as e:
        return jsonify({'error': f"Failed to fetch season average stats: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
