import opendota
import typeracer
import lichess
import codeforces
import nyt_crossword
from datetime import timedelta
from matplotlib import pyplot as plt

if __name__ == '__main__':
    cf = codeforces.get_all_events()
    lc = lichess.get_all_events()
    tr = typeracer.get_all_events()
    od = opendota.get_all_events()
    nyt = nyt_crossword.get_all_events()
    for title, events in zip('Codeforces Lichess Typeracer Dota NYT-Crossword'.split(), [cf, lc, tr, od, nyt]):
        print(title)
        print(len(events))
        print(sum((event.duration() for event in events), start=timedelta()))
        time_per_year = []
        years = list(range(2009,2023+1))
        for year in years:
            all_events = [event for event in events if event.start_time().year==year]
            time_per_year.append(sum((event.duration() for event in all_events), start=timedelta()).total_seconds()/3600)
        print(len([event for event in events if event.start_time().year not in years]))
        plt.plot(years, time_per_year, label=title, marker='o')
        print(f'{title} {time_per_year}')
    plt.ylabel('Hours')
    plt.xlabel('Year')
    plt.xticks(years, rotation=300)
    plt.legend()
    plt.show()