from datetime import timedelta, date
import rich

class HabitAnalyzer:
    """Class to analyze habits and provide insights based on their periodicity, streaks, and events."""

    # pass in HabitRepository instance so we can access its methods and the db connection
    def __init__(self, repo):
        self.repo = repo

    def longest_overall_streak(self):
        """Calculate the longest overall streak for all habits."""

        # Get all habits from the db
        habits = self.repo.get_all_habits()
        top_habit = None

        # If no habits are found, return "No habits found."
        if not habits:
            return "No habits found."

        # Find the habit with the longest streak and save it in top_habit
        longest_streak = 0
        for habit in habits:
            if habit.streak > longest_streak:
                longest_streak = habit.streak
                top_habit = habit

        # Intercept the possibility that no habit has a streak
        if top_habit is None:
            return "No habits with a streak were found."

        # If the top_habit is a daily habit, print the longest streak in days
        if top_habit.periodicity.lower() == "daily":
            rich.print(f"The longest overall streak is [bold purple]{longest_streak} days[/bold purple] for daily the"
                       f" habit [bold purple]{top_habit.name}[/bold purple].")
            return (f"The longest overall streak is [bold purple]{longest_streak} days[/bold purple] for the daily"
                    f" habit [bold purple]{top_habit.name}[/bold purple].")

        # If the top_habit is a weekly habit, print the longest streak in weeks
        elif top_habit.periodicity.lower() == "weekly":
            rich.print(f"The longest overall streak is [bold purple]{longest_streak} week/s[/bold purple] for the weekly"
                       f" habit [bold purple]{top_habit.name}[/bold purple].")
            return (f"The longest overall streak is [bold purple]{longest_streak} week/s[/bold purple] for the weekly"
                    f" habit [bold purple]{top_habit.name}[/bold purple].")
        return None

    def daily_habit_completed(self, habit_name: str):
        """Check if a daily habit was completed today."""

        # Get today's date and the last event date for the habit
        today = date.today()
        last_event_date = self.repo.get_last_event_date(habit_name)

        # If today's date is the same as the last event date, the habit has been completed today
        if today == last_event_date:
                rich.print(f"[green]Daily habit [bold purple]{habit_name}[/bold purple] has already been completed"
                           f" today![/green]")
                return True

        # If today's date is not the same as the last event date, habit has not been completed today
        rich.print(f"[red]Daily habit [bold purple]{habit_name}[/bold purple] still to be completed today![/red]")
        return False

    def weekly_habit_completed(self, habit_name: str):
        """Check if a weekly habit was completed this week."""

        # Get today's date and the last event date for the habit
        today: date = date.today()
        last_event_date: date = self.repo.get_last_event_date(habit_name)

        # If a last event date exists, calculate next_due_date and next_due_in_days
        if last_event_date:
            next_due_date = last_event_date + timedelta(weeks=1)
            next_due_in_days = (next_due_date - today).days

            delta = (today - last_event_date).days

            # If the last event date is within the current week, it has been completed this week
            if delta < 7:
                rich.print(f"[green]Weekly habit [bold purple]{habit_name}[/bold purple] was completed on the"
                           f" [bold purple]{last_event_date}[/bold purple] of this week! Next completion due in"
                           f" [bold purple]{next_due_in_days} days[/bold purple] on the"
                           f" [bold purple]{next_due_date}[/bold purple]![/green]")
                return True

            # If the last event date is exactly 7 days ago, it is due today
            elif delta == 7:
                rich.print(f"[red]Weekly habit [bold purple]{habit_name}[/bold purple] was not completed this week"
                           f" and is due today![/red]")
                return False

        # If there is no last even date, or it is more than 7 days ago, the habit is considered overdue
        rich.print(f"[red]Weekly habit [bold purple]{habit_name}[/bold purple] was not completed this week and is"
                   f" due today![/red]")
        return False

    def list_all_overdue_habits(self):
        """List all habits that are overdue today"""

        # Get today's date and initialize an empty list for overdue habits
        today = date.today()
        overdue_habits = []

        # Iterate through all habits and check their last event date
        for habit in self.repo.get_all_habits():
            last_event_date = self.repo.get_last_event_date(habit.name)

            # If a last event date exists, check if the habit is overdue based on its periodicity
            if last_event_date:
                if habit.periodicity.lower() == "daily":
                    if (today - last_event_date).days >= 1:
                        overdue_habits.append(habit)
                elif habit.periodicity.lower() == "weekly":
                    if (today - last_event_date).days >= 7:
                        overdue_habits.append(habit)

            # If there is no last event date, the habit is considered overdue
            elif not self.repo.get_one_habit_events(habit.name):
                overdue_habits.append(habit)

        # Incase no overdue habits are found, print No overdue habits found and return
        if not overdue_habits:
            rich.print("[green]No overdue habits found![/green]")
            return

        # Print the overdue habits with their last completed date, differentiate between if there ever was an event or not
        rich.print("[dark_orange]Overdue habits:[/dark_orange]")
        for habit in overdue_habits:
            if self.repo.get_last_event_date(habit.name):
                rich.print(f"[bold purple]{habit.name}[/bold purple] - Last completed on:[bold purple] {self.repo.get_last_event_date(habit.name)}[/bold purple]")
            else:
                rich.print(f"[bold purple]{habit.name}[/bold purple] - Last completed on:[bold purple] Never[/bold purple]")

    def biggest_struggle(self):
        """Identify the habit the user struggles with the most, based on streak stability."""

        # Get all habits from the db
        habits = self.repo.get_all_habits()

        # If no habits are found, print a message and return
        if not habits:
            rich.print("[red]No habits found to analyze.[/red]")
            return

        # Initialize variables to track the habit with the highest struggle score
        struggle_habit = None
        highest_score = -1

        # No data to analyze
        for habit in habits:
            if habit.event_count == 0:
                continue

            # No struggle if streak equals event count
            if habit.event_count == habit.streak:
                continue

            # Calculate the struggle score as a relation between event count and streak
            score = (habit.event_count - habit.streak) / habit.event_count

            if score > highest_score:
                highest_score = score
                struggle_habit = habit

        # if a struggling habit was found, print its details
        if struggle_habit:
            rich.print(
                f"[dark_orange]Your biggest struggle is the habit [bold purple]{struggle_habit.name}[/bold purple], "
                f"with a struggle score of [bold purple]{highest_score:.2f}[/bold purple]. "
                f"This is your most difficult to maintain habit currently."
                f"\n The struggle score lives between '0' and '1', scores closer to '1' indicate a bigger struggle, "
                f"scores closer to '0' indicate a smaller struggle :) [/dark_orange]"
            )
        # If no struggling habits were found, print You're doing great! No struggling habits found
        else:
            rich.print("[green]You're doing great! No struggling habits found.[/green]")

    def close(self):
        """Close the repository’s database connection if it exists."""
        if self.repo and hasattr(self.repo, "db") and self.repo.db:
            self.repo.db.close()
            self.repo.db = None

