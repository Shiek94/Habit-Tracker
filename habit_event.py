from datetime import datetime

class HabitEvent:
    """A data class to represent habit events parallel to the habit_tracker table in the db"""
    def __init__(self, completed_at: datetime, habit_name: str):
        self.completed_at = completed_at
        self.habit_name = habit_name
