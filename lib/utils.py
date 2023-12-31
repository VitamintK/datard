import time
import datetime

## Data Collection ######################################################################

def sleep_if_not_cached(response, t):
    """If the response is a cached response from requests_cache, sleep for t seconds."""
    if not getattr(response, 'from_cache', False):
        time.sleep(t)

## Data Analysis ######################################################################

def make_trailing_average(xs: 'list[datetime.datetime]', ys, gamma_day=0.998, gamma_event=0.998):
    assert all(xs[i-1] <= xs[i] for i in range(1, len(xs)))
    avgs = []
    bounds = []
    for i in range(len(xs)):
        x = xs[i]
        y = ys[i]
        trail = y
        if i != 0:
            total_weights = 1
            for j in range(i):
                prev_x = xs[j]
                prev_y = ys[j]
                elapsed = x - prev_x
                gamma = gamma_event ** (i-j) * gamma_day ** elapsed.days
                total_weights += gamma
                trail += gamma*prev_y
            trail /= total_weights
        avgs.append(trail)
    return avgs, bounds