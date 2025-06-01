from datetime import date, datetime, timedelta

class HabitTracker:
    """Class to track habits with periodicity, streaks, and event counts. A data class with local logic representing
    habits in the habit_tracker table in the db."""

    def __init__(self, name: str, description: str, periodicity: str = "daily", streak: int = 0, event_count: int = 0):
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.streak = streak
        self.event_count = event_count

    def increment_streak(self):
        """Increment the streak count for the habit."""
        self.streak += 1

    def increment_event(self):
        """Increment the event count for the habit."""
        self.event_count += 1

    def reset_streak(self):
        """Reset the streak count for the habit."""
        self.streak = 0

    def should_reset_streak(self, last_event_date: date):
        """Check if the streak should be reset based on periodicity and last event date.
           Returns True if the streak should be reset, False otherwise.
        """
        today = datetime.now().date()

        # Check if there is an event date to compare against
        if last_event_date:
            if self.periodicity.lower() == "daily":
                return (today - last_event_date) > timedelta(days=1)
            elif self.periodicity.lower() == "weekly":
                return (today - last_event_date) > timedelta(weeks=1)
        return False

    def event_too_soon(self, last_event_date, event_date: date):
        """Check if the user is trying to add another habit event too soon."""

        # Calculate the difference in days between the last event date and the new event date
        delta = (event_date - last_event_date).days

        if self.periodicity.lower() == "daily":
            return delta < 1
        elif self.periodicity.lower() == "weekly":
            return delta < 7
        return False
