from common import MonetaryEvent
from datetime import datetime,timedelta
import csv
from typing import TypedDict
from enum import Enum

# Currently using SportsbookScout for DK and FD: https://www.sportsbookscout.com/sports-betting-guides/download-export-bet-history-draftkings-sportsbook
# TODO: some more automated solution

class Sbs_draftkings_csv_row(TypedDict):
    External_Bet_ID: str
    Bet_Date_Time: str
    Bet_Type: str
    Bet_Amount: str
    Number_of_Bets: str
    Number_of_Legs: str
    Bet_Settled: str
    Bet_Selection: str
    Market_Name: str
    Bet_American_Odds: str
    Bet_Result: str
    Payout: str
    Potential_Payout: str
    Leg_Settled: str
    Leg_Result: str
    Leg_American_Odds: str
    Bet_Settled_Date: str
    Bet_Bonus_Type: str
    Bet_Bonus_Amount: str
    Risk_Free_Bet: str
    Bet_Boosted_Odds: str
    Bet_Bonus_Max_Winning_Amount: str
    Bet_Bonus_Winning_Amount: str
    Bet_Boost_Percentage: str
    Boosted_Bet: str
    Early_Win_Settled: str
    Primary: str

class Sbs_fanduel_csv_row(TypedDict):
    External_Bet_ID: str
    Bet_Date_Time: str
    Bet_Type: str
    Bet_Amount: str
    Bet_Settled: str
    Event_Name: str
    League: str
    Bet_Selection: str
    Market_Name: str
    Leg_Handicap: str
    Teaser_Points: str
    Bet_American_Odds: str
    Bet_Decimal_Odds: str
    Leg_American_Odds: str
    Leg_Decimal_Odds: str
    Multi_Bet_American_Odds: str
    Multi_Bet_Decimal_Odds: str
    Leg_Result: str
    Bet_Result: str
    Payout: str
    Potential_Payout: str
    Leg_Bet_Type: str
    Leg_Event_Date_Time: str
    Bet_Settled_Date: str
    Same_Game_Parlay: str
    State: str
    Primary: str

class WagerOutcome(Enum):
    WIN = 1
    PUSH = 2
    LOSE = 3
    UNSETTLED = 4
    CASHED_OUT = 5

def parse_bet_result(result_string) -> WagerOutcome:
    if result_string in ['WON', 'Won']:
        return WagerOutcome.WIN
    elif result_string in ['VOID', 'Draw']:
        return WagerOutcome.PUSH
    elif result_string in ['LOST', 'Lost']:
        return WagerOutcome.LOSE
    elif result_string in ['', 'Open']:
        return WagerOutcome.UNSETTLED
    elif result_string in ['CASHED_OUT', "CashOut"]:
        return WagerOutcome.CASHED_OUT
    raise ValueError(f"Unknown result_string: {result_string}")

def parse_bet_settled(bet_settled_string) -> bool:
    if bet_settled_string in ['Settled', 'true']:
        return True
    elif bet_settled_string in ['Unsettled', 'false']:
        return False
    raise ValueError(f"Unknown bet_settled_string: {bet_settled_string}")

def parse_cents_from_string(usd_string: str) -> int:
    if usd_string == '':
        return 0
    return int(float(usd_string) * 100)

class SportsBet(MonetaryEvent):
    def placement_time(self) -> datetime:
        return None
    def predicted_settle_time(self) -> datetime:
        return None
    def actual_settle_time(self) -> datetime:
        pass
    def profit(self) -> int:
        """profit in cents"""
        return None

class FanduelSportsBet(SportsBet):
    def __init__(self, raw_wager, bet_settled: bool, placement_time, predicted_settle_time, actual_settle_time, stake_cents, outcome: WagerOutcome, actual_payout_cents):
        self._raw_wager = raw_wager
        self._bet_settled = bet_settled
        self._placement_time = placement_time
        self._predicted_settle_time = predicted_settle_time
        self._actual_settle_time = actual_settle_time
        self._stake_cents = stake_cents
        self._outcome = outcome
        self._actual_payout_cents = actual_payout_cents
    def placement_time(self):
        return self._placement_time
    def predicted_settle_time(self):
        return self._predicted_settle_time
    def actual_settle_time(self):
        return self._actual_settle_time
    def profit(self):
        """In cents"""
        if self._bet_settled == False:
            return None
        return self._actual_payout_cents - self._stake_cents

class DraftKingsSportsBet(SportsBet):
    def __init__(self, raw_wager, bet_settled: bool, placement_time, predicted_settle_time, actual_settle_time, stake_cents, outcome: WagerOutcome, actual_payout_cents):
        self._raw_wager = raw_wager
        self._bet_settled = bet_settled
        self._placement_time = placement_time
        self._predicted_settle_time = predicted_settle_time
        self._actual_settle_time = actual_settle_time
        self._stake_cents = stake_cents
        self._outcome = outcome
        self._actual_payout_cents = actual_payout_cents
    def placement_time(self):
        return self._placement_time
    def predicted_settle_time(self):
        return self._predicted_settle_time
    def actual_settle_time(self):
        return self._actual_settle_time
    def profit(self):
        """In cents"""
        if self._bet_settled == False:
            return None
        return self._actual_payout_cents - self._stake_cents

def load_raw_fanduel_from_sportsbookscout() -> "list[Sbs_fanduel_csv_row]":
    with open('data/fanduel_raw.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [field.replace(' ', '_') for field in reader.fieldnames]
        return [row for row in reader]

def load_raw_draftkings_from_sportsbookscout() -> "list[Sbs_draftkings_csv_row]":
    with open('data/draftkings_raw.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [field.replace(' ', '_') for field in reader.fieldnames]
        return [row for row in reader]

def fanduel_sportsbet_from_sbs(rw: Sbs_fanduel_csv_row) -> FanduelSportsBet:
    print(rw)
    return FanduelSportsBet(
        rw,
        bet_settled=parse_bet_settled(rw['Bet_Settled']),
        placement_time=rw['Bet_Date_Time'],
        predicted_settle_time=rw['Bet_Settled_Date'],
        actual_settle_time=rw['Bet_Settled_Date'],
        stake_cents=int(float(rw['Bet_Amount']) * 100),
        outcome=parse_bet_result(rw['Bet_Result']),
        actual_payout_cents=parse_cents_from_string(rw['Payout']),
    )

def draftkings_sportsbet_from_sbs(rw: Sbs_draftkings_csv_row) -> DraftKingsSportsBet:
    print(rw)
    return DraftKingsSportsBet(
        rw,
        bet_settled=parse_bet_settled(rw['Bet_Settled']),
        placement_time=rw['Bet_Date_Time'],
        predicted_settle_time=rw['Bet_Settled_Date'],
        actual_settle_time=rw['Bet_Settled_Date'],
        stake_cents=int(float(rw['Bet_Amount']) * 100),
        outcome=parse_bet_result(rw['Bet_Result']),
        actual_payout_cents=parse_cents_from_string(rw['Payout']),
    )

def get_all_events() -> 'tuple[list[SportsBet]]':
    fd = [fanduel_sportsbet_from_sbs(bet) for bet in load_raw_fanduel_from_sportsbookscout()]
    dk = [draftkings_sportsbet_from_sbs(bet) for bet in load_raw_draftkings_from_sportsbookscout()]
    return fd, dk

if __name__ == '__main__':
    fd, dk = get_all_events()
    for sportsbook in (fd, dk):
        profit = 0
        for event in sportsbook:
            if event.profit() is not None:
                if event._raw_wager['Primary'] == '0':
                    continue
                profit += event.profit()
        print(f'${profit / 100}')