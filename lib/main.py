import codeforces
import lichess
import nyt_crossword
import opendota
import sportsbooks
import typeracer
from datetime import timedelta
from matplotlib import pyplot as plt
from utils import make_trailing_average

all_statistics = [
    # codeforces,
    # lichess,
    # typeracer,
    # nyt_crossword,
    # opendota,
    # sportsbooks
]

if __name__ == '__main__':
    for statistic in all_statistics:
        statistic.fetch_and_update_raw_data()
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
    plt.title("Time spent by Kevin on various activities")
    plt.xticks(years, rotation=300)
    plt.legend()
    plt.show()

    # sports betting:
    fd, dk = sportsbooks.get_all_events()
    all_sportbets = fd+dk
    all_sportbets.sort(key=lambda x: x.start_time())
    cum_profits_x, cum_profits_y = sportsbooks.get_cumulative_profits(all_sportbets, x_point='settle_time')
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.5, zorder=-1)
    plt.scatter([bet.actual_settle_time() for bet in all_sportbets], [bet.profit_usd() for bet in all_sportbets], alpha=0.4, s=12, zorder=2)
    plt.plot(cum_profits_x, [cum_profit/100 for cum_profit in cum_profits_y], label='Cumulative profit', color='grey', linewidth=1, zorder=0)
    plt.ylabel('Profit (USD)')
    plt.xlabel('Date Settled')
    plt.xticks(rotation='vertical')
    plt.legend()
    plt.title("Sports betting profits")
    plt.show()

    # typeracer:
    tr.sort(key=lambda x: x.start_time())
    xs, ys = [t.start_time() for t in tr], [t.wpm for t in tr]
    avgs, _ = make_trailing_average(xs, ys, gamma_day=0.998, gamma_event=0.99)
    plt.plot(xs, avgs, label='Trailing average', color='grey', linewidth=1, zorder=5)
    plt.scatter(xs, ys, alpha=0.4, s=12, zorder=4)
    plt.ylim(70, plt.ylim()[1])
    plt.title("Typeracer WPM")
    plt.legend()
    plt.grid()
    plt.show()
