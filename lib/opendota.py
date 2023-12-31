import requests
import json
from datetime import datetime, timedelta

from common import DATA_DIR, TimedEvent

RAW_PATH = f"{DATA_DIR}/opendota_raw.json"

def fetch_and_save_raw_data():
    print('fetching Dota data from Opendota...')
    user_id = input('id: ')
    url = f'https://api.opendota.com/api/players/{user_id}/matches'
    r = requests.get(url)
    j = r.json()
    print('saving')
    with open(RAW_PATH, 'w') as f:
        json.dump(j, f)

def fetch_and_update_raw_data():
    games = load_raw_data()
    fetch_and_save_raw_data()
    new_games = load_raw_data()
    new_games_by_match_id = {game['match_id']: game for game in new_games}
    for game in games:
        assert game['match_id'] in new_games_by_match_id, game['match_id']
        assert game == new_games_by_match_id[game['match_id']], (game, new_games_by_match_id[game['match_id']])

def load_raw_data():
    with open(RAW_PATH, 'r') as f:
        games = json.load(f)
    return games

def analyze():
    with open(RAW_PATH, 'r') as f:
        games = json.load(f)
    total_time = timedelta()
    for game in games:
        # print(result)
        # print(datetime.datetime.fromtimestamp(result['ratingUpdateTimeSeconds']))
        elapsed = timedelta(seconds=game['duration'])
        total_time += elapsed
    # this doesn't exactly match dotabuff's count. It's missing about 7%.
    # It's about the same as Dotabuff's "significant" count. (which excludes holiday and fun modes)
    print(f'Num games: {len(games)}, Total time: {total_time}')

class OpenDotaGame(TimedEvent):
    def __init__(self, raw_game):
        self._raw = raw_game
        self._start_time = datetime.fromtimestamp(raw_game['start_time'])
        self._duration = timedelta(seconds=raw_game['duration'])
        self._end_time = self._start_time + self._duration
    def start_time(self) -> datetime:
        return self._start_time
    def end_time(self) -> datetime:
        return self._end_time
    def duration(self) -> timedelta:
        return self._duration
    
def get_all_events():
    games = load_raw_data()
    return [OpenDotaGame(game) for game in games]

if __name__ == '__main__':
    fetch_and_save_raw_data()
    analyze()