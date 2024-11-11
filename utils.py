

def calculate_averages(stats, games_played):
    """
    Calculate average statistics per game.
    """
    if games_played == 0:
        return {key: 0 for key in stats.keys() if key not in ['player_id', 'player_name', 'season']}
    
    averages = {}
    for key, value in stats.items():
        if key in ['player_id', 'player_name', 'season']:
            averages[key] = value
        else:
            try:
                averages[key] = round(value / games_played, 2)
            except:
                averages[key] = 0
    return averages
