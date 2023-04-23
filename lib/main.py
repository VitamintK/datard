import opendota
import typeracer
import lichess
import codeforces
import nyt_crossword
from datetime import timedelta

if __name__ == '__main__':
    cf = codeforces.get_all_events()
    lc = lichess.get_all_events()
    tr = typeracer.get_all_events()
    od = opendota.get_all_events()
    nyt = nyt_crossword.get_all_events()
    for title, events in zip('cf lc tr od nyt'.split(), [cf, lc, tr, od, nyt]):
        print(title)
        print(len(events))
        print(sum((event.duration() for event in events), start=timedelta()))