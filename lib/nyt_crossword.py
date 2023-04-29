import calendar
from datetime import date, datetime, timedelta
import os
import requests
import time
import json
from common import TimedEvent

RAW_PATH_LIST = 'data/nyt_crossword_list.json'
RAW_PATH_SOLVES = 'data/nyt_crossword_solves.json'

# First API from https://github.com/mattdodge/nyt-crossword-stats, presumably for the iOS iphone app:
# API_ROOT = 'https://nyt-games-prd.appspot.com/svc/crosswords'
# PUZZLE_INFO = API_ROOT + '/v2/puzzle/daily-{date}.json'
# SOLVE_INFO = API_ROOT + '/v2/game/{game_id}.json'
# DATE_FORMAT = '%Y-%m-%d'

# A second API for web(?) at:
# https://edge.games.nyti.nyt.net/svc/crosswords/v3/{id}/puzzles.json?publish_type=daily&sort_order=asc&sort_by=print_date&date_start=2023-04-01&date_end=2023-04-30
PUZZLE_LIST = "https://edge.games.nyti.nyt.net/svc/crosswords/v3/{user_id}/puzzles.json"
SOLVE_INFO = 'https://www.nytimes.com/svc/crosswords/v6/game/{puzzle_id}.json'

def get_and_save_puzzles_list():
    start_date = date(2014, 1, 1)
    end_date = date.today()

    results = []
    first_day = start_date
    # Iterate through each month
    while first_day <= end_date:
        # Get the year and month of the current date
        year = first_day.year
        month = first_day.month
        # Get the number of days in the current month
        num_days = calendar.monthrange(year, month)[1]   
        # Get the first and last date of the current month
        first_day = date(year, month, 1)
        last_day = date(year, month, num_days)
        # Print the first and last date of the current month
        print(f"First day of {first_day.strftime('%B %Y')}: {first_day}")
        print(f"Last day of {first_day.strftime('%B %Y')}: {last_day}")

        r = requests.get(
            PUZZLE_LIST.format(user_id=87402204),
            params={
                'publish_type': 'daily',
                'sort_order': 'asc',
                'sort_by': 'print_date',
                'date_start': first_day.strftime('%Y-%m-%d'),
                'date_end': last_day.strftime('%Y-%m-%d')
            },
            cookies={
                'NYT-S': cookie,
            },
        )
        r.raise_for_status()
        results.extend(r.json()['results'])
        time.sleep(0.2)

        r = requests.get(
            PUZZLE_LIST.format(user_id=87402204),
            params={
                'publish_type': 'mini',
                'sort_order': 'asc',
                'sort_by': 'print_date',
                'date_start': first_day.strftime('%Y-%m-%d'),
                'date_end': last_day.strftime('%Y-%m-%d')
            },
            cookies={
                'NYT-S': cookie,
            },
        )
        r.raise_for_status()
        if r.json()['results'] is not None:
            results.extend(r.json()['results'])

        # Move to the next month
        first_day = first_day + timedelta(days=32)
        time.sleep(0.75)
    # results.sort(key=lambda x: x['print_date'])
    with open(RAW_PATH_LIST, 'w') as f:
        json.dump(results, f)
    return results

def load_raw_puzzles_list():
    with open(RAW_PATH_LIST, 'r') as f:
        puzzle_list = json.load(f)
    return puzzle_list

def load_raw_puzzle_solves():
    with open(RAW_PATH_SOLVES, 'r') as f:
        puzzle_solves = json.load(f)
    return puzzle_solves

def get_puzzle_solve(puzzle_id):
    r = requests.get(
        SOLVE_INFO.format(puzzle_id=puzzle_id),
        cookies={'NYT-S': cookie}
    )
    return r.json()

def get_and_save_puzzle_solves_from_list(puzzle_list: list):
    all_puzzle_solves = dict()
    for puzzle in puzzle_list:
        if puzzle['percent_filled'] == 0:
            print('skip', puzzle['print_date'])
            continue
        puzzle_id = puzzle['puzzle_id']
        puzzle_solve = get_puzzle_solve(puzzle_id)
        all_puzzle_solves[puzzle_id] = puzzle_solve
        time.sleep(1)
        with open(RAW_PATH_SOLVES, 'w') as f:
            json.dump(all_puzzle_solves, f)
    return all_puzzle_solves



def login(username, password):
    """ Return the NYT-S cookie after logging in """
    login_resp = requests.post(
        'https://myaccount.nytimes.com/svc/ios/v2/login',
        data={
            'login': username,
            'password': password,
        },
        headers={
            'User-Agent': 'Crosswords/20191213190708 CFNetwork/1128.0.1 Darwin/19.6.0',
            'client_id': 'ios.crosswords',
        },
    )
    login_resp.raise_for_status()
    for cookie in login_resp.json()['data']['cookies']:
        if cookie['name'] == 'NYT-S':
            return cookie['cipheredValue']
    raise ValueError('NYT-S cookie not found')

class CrosswordSolve(TimedEvent):
    def __init__(self, raw_solve, raw_info):
        self._raw = raw_solve
        self._raw_info = raw_info
        self._start_time = datetime.fromtimestamp(raw_solve['firsts']['opened'])
        if 'solved' in raw_solve['firsts']:
            self._end_time = datetime.fromtimestamp(raw_solve['firsts']['solved'])
        else:
            self._end_time = None
        self._duration = timedelta(seconds=raw_solve['calcs']['secondsSpentSolving'])
        self._publish_date = datetime.strptime(raw_info['print_date'], '%Y-%m-%d').date()
        self._solved = ('solved' in raw_solve['calcs']) and raw_solve['calcs']['solved']
        self._starred = raw_info['star']=='Gold'
        assert raw_info['star'] in [None, 'Gold'], raw_info
    def start_time(self) -> datetime:
        return self._start_time
    def end_time(self) -> datetime:
        return self._end_time
    def duration(self) -> timedelta:
        return self._duration
    def is_solved(self) -> bool:
        return self._solved
    def is_starred(self) -> bool:
        return self._starred
    def counts_for_stats(self) -> bool:
        """The 'Stats' screen in web and iOS, which displays solve times by day of week"""
        return self._solved and 'revealed' not in self._raw['firsts']
    def get_publish_day_of_week(self):
        return self._publish_date.weekday()
    
def get_all_events():
    puzzle_list = load_raw_puzzles_list()
    puzzle_info_by_id = {str(puzzle['puzzle_id']): puzzle for puzzle in puzzle_list}
    puzzle_solves = load_raw_puzzle_solves()
    return [CrosswordSolve(solve, puzzle_info_by_id[puzzle_id]) for puzzle_id, solve in puzzle_solves.items()]

# def get_puzzle_stats(date, cookie):
#     puzzle_resp = requests.get(
#         PUZZLE_INFO.format(date=date),
#         cookies={
#             'NYT-S': cookie,
#         },
#     )
#     puzzle_resp.raise_for_status()
#     puzzle_date = datetime.strptime(date, DATE_FORMAT)
#     puzzle_info = puzzle_resp.json().get('results')[0]
#     solve_resp = requests.get(
#         SOLVE_INFO.format(game_id=puzzle_info['puzzle_id']),
#         cookies={
#             'NYT-S': cookie,
#         },
#     )
#     solve_resp.raise_for_status()
#     solve_info = solve_resp.json().get('results')
#     breakpoint()

    # solved = solve_info.get('solved', False)
    # checked = 'firstChecked' in solve_info
    # revealed = 'firstRevealed' in solve_info
    # solve_date = datetime.fromtimestamp(solve_info.get('firstSolved', 0))

    # A puzzle is streak eligible if they didn't cheat and they solved it
    # before midnight PST (assume 8 hour offset for now, no DST)
    # streak_eligible = solved and not checked and not revealed and (
    #     solve_date <= puzzle_date + timedelta(days=1) + timedelta(hours=8))

    # return {
    #     'elapsed_seconds': solve_info.get('timeElapsed', 0),
    #     'solved': int(solved),
    #     'checked': int(checked),
    #     'revealed': int(revealed),
    #     'streak_eligible': int(streak_eligible),
    # }


if __name__ == '__main__':
    # for example,
    # NYT_COOKIE=`cat secrets/nyt_cookie.txt` python lib/nyt_crossword.py
    # args = parser.parse_args()
    cookie = os.getenv('NYT_COOKIE')
    # print(args.username, args.password, cookie)
    # if not cookie:
    #     # sometimes this transiently fails, so try multiple times??
    #     NUM_ATTEMPTS = 3
    #     for i in range(NUM_ATTEMPTS):
    #         try:
    #             cookie = login(args.username, args.password)
    #         except requests.exceptions.HTTPError as e:
    #             if i < NUM_ATTEMPTS-1:
    #                 print(f'attempt to login failed with error {e}')
    #                 print("Trying again!")
    #                 time.sleep(1)
    #             else:
    #                 raise e
    
    get_and_save_puzzles_list()
    puzzle_list = load_raw_puzzles_list()
    get_and_save_puzzle_solves_from_list(puzzle_list)


    all_solves = get_all_events()
    times_by_weekday: "list[list[CrosswordSolve]]" = [[] for i in range(7)]
    for solve in all_solves:
        times_by_weekday[solve.get_publish_day_of_week()].append(solve)
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for weekday in range(7):
        solves = times_by_weekday[weekday]
        weekday_name = weekday_names[weekday]
        solved_solves = [solve for solve in solves if solve.counts_for_stats()]
        print(f'{weekday_name} - num started: {len(solves)}, num solved: {len(solved_solves)}, avg time: {sum((solve.duration() for solve in solved_solves), start=timedelta())/len(solved_solves)}')
    print(f'total solved: {len([solve for solve in all_solves if solve.counts_for_stats()])}')
    print(f'total solved: {len([solve for solve in all_solves if solve.is_solved()])}')
    
    # start_date = datetime.strptime(args.start_date, DATE_FORMAT)
    # end_date = datetime.strptime(args.end_date, DATE_FORMAT)
    # print("Getting stats from {} until {}".format(
    #     datetime.strftime(start_date, DATE_FORMAT),
    #     datetime.strftime(end_date, DATE_FORMAT)))
    # date = start_date
    # fields = [
    #     'date',
    #     'day',
    #     'elapsed_seconds',
    #     'solved',
    #     'checked',
    #     'revealed',
    #     'streak_eligible',
    # ]
    # with open(args.output_csv, 'w') as csvfile, \
    #         tqdm(total=(end_date-start_date).days + 1) as pbar:
    #     writer = DictWriter(csvfile, fields)
    #     writer.writeheader()
    #     count = 0
    #     while date <= end_date:
    #         date_str = datetime.strftime(date, DATE_FORMAT)
    #         try:
    #             solve = get_puzzle_stats(date_str, cookie)
    #             solve['date'] = date_str
    #             solve['day'] = datetime.strftime(date, '%a')
    #             writer.writerow(solve)
    #             count += 1
    #         except Exception as e:
    #             # Ignore missing puzzles errors in non-strict
    #             print(f'Error: {e}')
    #             if args.strict:
    #                 raise
    #         pbar.update(1)
    #         date += timedelta(days=1)
    #         time.sleep(0.8)

    # print("{} rows written to {}".format(count, args.output_csv))