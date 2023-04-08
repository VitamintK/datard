import requests
import json
import datetime

def get_and_save_raw_data():
    url_base = "https://codeforces.com/api/user.rating?handle="
    username = input('username: ')
    url = url_base + username
    r = requests.get(url)
    j = r.json()
    assert j['status'] == 'OK'
    for result in j['result']:
        print(result)
        print(datetime.datetime.fromtimestamp(result['ratingUpdateTimeSeconds']))
    print(f"num of contests: {len(j['result'])}, total time spent (assuming 2 hr/contest): {len(j['result']) * 2 /24:.02} days")
    print('saving')
    with open('data/codeforces_raw.json', 'w') as f:
        json.dump(j, f)