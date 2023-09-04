from datetime import datetime, timedelta
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
    