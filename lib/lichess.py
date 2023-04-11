import requests
import json
from datetime import datetime, timedelta
from common import TimedEvent

RAW_PATH = 'data/lichess_raw.json'
def get_and_save_raw_data():
    # TODO: dont download entire data each time, just new data
    username = input("username: ")
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
    # get_and_save_raw_data()
    analyze()