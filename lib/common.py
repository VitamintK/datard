from datetime import datetime, timedelta

DATA_DIR = 'data'

class EventCollection:
    @property
    def name(self) -> str:
        pass
    def fetch_and_update_raw_data(self):
        pass

class TimedEvent:
    def start_time(self) -> datetime:
        pass
    def end_time(self) -> datetime:
        pass
    def duration(self) -> timedelta:
        pass

class MonetaryEvent:
    def placement_time(self) -> datetime:
        pass
    def predicted_settle_time(self) -> datetime:
        pass
    def actual_settle_time(self) -> datetime:
        pass
    def profit(self) -> int:
        """profit in cents"""
        pass
    