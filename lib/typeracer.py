import requests
import json
from datetime import datetime,timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm
import os

from common import DATA_DIR, TimedEvent

RAW_PATH = f"{DATA_DIR}/typeracer_raw.json"
TEXT_DATA_PATH = f"{DATA_DIR}/typeracer_text_data.json"

# API returns data that looks like this:
# {"wpm": 110.4, "ac": 0.98, "r": 2, "t": 1680309728.065, "sl": "L6", "tid": 3620627, "gn": 1082, "np": 2, "pts": 71.76}
# Best guesses for what these mean:
# wpm: words per minute
# ac: accuracy
# r: rank
# t: timestamp
# sl: skill level (from 1 to 6? https://teachmehelp.zendesk.com/hc/en-us/articles/14560809798423-What-do-the-Skill-Levels-and-Experience-Levels-mean- )
# tid: text id
# gn: game number
# np: number of players
# pts: points

def fetch_and_save_raw_data():
    print('fetching Typeracer data...')
    username = input('username: ')
    url = f'https://data.typeracer.com/games?playerId=tr:{username}&universe=play&startDate=1295166400&endDate=1780990695&n=10000'
    r = requests.get(url)
    j = r.json()
    print('saving')
    with open(RAW_PATH, 'w') as f:
        json.dump(j, f)

def fetch_and_update_raw_data():
    fetch_and_save_raw_data()

def load_raw_data():
    with open(RAW_PATH, 'r') as f:
        x = json.load(f)
    return x

def fetch_text(text_id):
    r = requests.get(f'https://typeracerdata.com/text?id={text_id}')
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find('p').text.strip()

def get_and_save_text_data(races):
    d = dict()
    if os.path.isfile(TEXT_DATA_PATH):
        with open(TEXT_DATA_PATH, 'r') as f:
            d = json.load(f)
    for race in tqdm(races):
        text_id = race['tid']
        if text_id in d:
            continue
        text = fetch_text(text_id)
        d[text_id] = text
    print('saving')
    with open(TEXT_DATA_PATH, 'w') as f:
        json.dump(d, f)
    return d

def load_text_data():
    with open(TEXT_DATA_PATH, 'r') as f:
        d = json.load(f)
    return d

def analyze(races):
    total_time = timedelta()
    print(f'Num games: {len(races)}')
    print(f"At a minute per race, that's {timedelta(minutes=1) * len(races)}")

class TypeRacerRace(TimedEvent):
    def __init__(self, raw_race, duration):
        self._raw = raw_race
        self._start_time = datetime.fromtimestamp(raw_race['t'])
        self._duration = duration
        self._end_time = self._start_time + self._duration
    def start_time(self) -> datetime:
        return self._start_time
    def end_time(self) -> datetime:
        return self._end_time
    def duration(self) -> timedelta:
        return self._duration
    @property
    def wpm(self) -> float:
        return self._raw['wpm']
    
def get_all_events() -> "list[TypeRacerRace]":
    races = load_raw_data()
    texts = load_text_data()
    ans = []
    for race in races:
        text = texts[str(race['tid'])]
        wpm = race['wpm']
        length = len(text)
        words = length/5
        minutes = words/wpm
        ans.append(TypeRacerRace(race, timedelta(minutes=minutes)))
    return ans

if __name__ == '__main__':
    fetch_and_save_raw_data()
    races = load_raw_data()
    get_and_save_text_data(races)
    analyze(races)