import opendota
import typeracer
import lichess
import codeforces
from datetime import timedelta

if __name__ == '__main__':
    cf = codeforces.get_all_events()
    lc = lichess.get_all_events()
    tr = typeracer.get_all_events()
    od = opendota.get_all_events()
    for events in [cf, lc, tr, od]:
        print(len(events))
        print(sum((event.duration() for event in events), start=timedelta()))