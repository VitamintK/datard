import requests
import json
from datetime import datetime, timedelta
from common import TimedEvent, DATA_DIR

RAW_PATH = f'{DATA_DIR}/lichess_raw.json'
def fetch_and_save_raw_data():
    print('fetching all Lichess data...')
    # TODO: dont download entire data each time, just new data
    username = input("Lichess username: ")
    # url = f'https://lichess.org/api/user/{username}/activity'
    nb = 10000000
    # for now, don't get moves or PGN
    url = f'https://lichess.org/api/games/user/{username}?max={nb}&moves=no&pgnInJson=false'
    r = requests.get(url, headers={'Accept': 'application/x-ndjson'})
    games = []
    for l in r.iter_lines():
        obj = json.loads(l)
        games.append(obj)
    print(games)
    with open(RAW_PATH, 'w') as f:
        json.dump(games, f)

def fetch_and_update_raw_data():
    print('fetching new Lichess data...')
    with open(RAW_PATH, 'r') as f:
        games = json.load(f)
    game_ids = {game['id'] for game in games}

    username = input("Lichess username: ")
    # url = f'https://lichess.org/api/user/{username}/activity'
    nb = 10000000
    # for now, don't get moves or PGN
    url = f'https://lichess.org/api/games/user/{username}?max={nb}&moves=no&pgnInJson=false'
    r = requests.get(url, headers={'Accept': 'application/x-ndjson'})
    for l in r.iter_lines():
        obj = json.loads(l)
        game_id = obj['id']
        if game_id in game_ids:
            # TODO: uh, wait... the request already requested everything, so this does not save any time (the bottleneck is the server request)
            #       instead, look for a parameter to only get games that take place after that time.
            print(f'Game {game_id} already saved. Breaking.')
            break
        games.append(obj)
        game_ids.add(game_id)
    
    with open(RAW_PATH, 'w') as f:
        json.dump(games, f)

def load_raw_data():
    with open(RAW_PATH, 'r') as f:
        games = json.load(f)
    return games

def analyze():
    with open(RAW_PATH, 'r') as f:
        games = json.load(f)
    all_time = timedelta()
    speeds = set()
    for game in games:
        speeds.add(game['speed'])
        if game['speed'] in ['correspondence']:
            continue
        start = datetime.fromtimestamp(game['createdAt']/1000)
        end = datetime.fromtimestamp(game['lastMoveAt']/1000)
        # print(end-start, game['status'])
        elapsed = end-start
        all_time += elapsed
    print(speeds)
    print(f'Total games played: {len(games)}')
    print(f'Total time spent: {all_time} (This is different than lichess calculation on profile page for some reason)')

class LichessGame(TimedEvent):
    def __init__(self, raw_game):
        self._raw = raw_game
        self._start_time = datetime.fromtimestamp(raw_game['createdAt']/1000)
        self._end_time = datetime.fromtimestamp(raw_game['lastMoveAt']/1000)
        if raw_game['speed'] == 'correspondence':
            self._duration = timedelta()
        else:
            self._duration = self._end_time - self._start_time
    def start_time(self) -> datetime:
        return self._start_time
    def end_time(self) -> datetime:
        return self._end_time
    def duration(self) -> timedelta:
        return self._duration

def get_all_events():
    games = load_raw_data()
    return [LichessGame(game) for game in games]    

if __name__ == '__main__':
    # fetch_and_save_raw_data()
    analyze()