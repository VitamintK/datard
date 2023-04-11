from common import TimedEvent

import requests
import json
from datetime import datetime, timedelta

RAW_PATH = 'data/codeforces_raw.json'

def get_and_save_raw_data():
    url_base = "https://codeforces.com/api/user.rating?handle="
    username = input('username: ')
    url = url_base + username
    r = requests.get(url)
    j = r.json()
    assert j['status'] == 'OK'
    for result in j['result']:
        print(result)
        print(datetime.fromtimestamp(result['ratingUpdateTimeSeconds']))
    print(f"num of contests: {len(j['result'])}, total time spent (assuming 2 hr/contest): {len(j['result']) * 2 /24:.02} days")
    print('saving')
    with open(RAW_PATH, 'w') as f:
        json.dump(j, f)

def load_raw_data():
    with open(RAW_PATH, 'r') as f:
        d = json.load(f)
    return d

class Contest(TimedEvent):
    def __init__(self, raw_contest):
        self._raw = raw_contest
        self._end_time = datetime.fromtimestamp(raw_contest['ratingUpdateTimeSeconds'])
        # ASSUMES 2HR/CONTEST, though some are 2:15 or 2:30 or something else
        self._duration = timedelta(hours=2)
        self._start_time = self._end_time - self._duration

    def start_time(self) -> datetime:
        return self._start_time
    def end_time(self) -> datetime:
        return self._end_time
    def duration(self) -> timedelta:
        return self._duration

def get_all_events() -> "list[TimedEvent]":
    contests = load_raw_data()
    return [Contest(contest) for contest in contests['result']]

if __name__ == '__main__':
    get_and_save_raw_data()