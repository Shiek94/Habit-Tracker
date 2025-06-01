from datetime import date
from database import get_connection
import rich
from habit_event import HabitEvent
from habit import HabitTracker
from datetime import datetime, timedelta

def get_valid_date(event_date):
    """Validate the event date format. If the date is empty, return today's date."""
    if isinstance(event_date, date):
        return event_date
    if not event_date or not event_date.strip():
        return date.today()
    try:
        return datetime.strptime(event_date, "%Y-%m-%d").date()
    except ValueError:
        return None

class HabitRepository:
    """The most important class of this project. Repository class to manage habits and their events in the database.
    get initialized with a database connection and provides methods to add, delete, and list habits and their events."""

    def __init__(self, db_name="main.db"):
        """Initialize the repository with a database connection."""
        self.db = get_connection(db_name)

    def add_habit(self, name, description, periodicity, streak=0):
        """Add a new habit to the database."""
        cur = self.db.cursor()

        # Check if the habit already exists
        if self.get_one_habit(name):
            rich.print(f"[red]Habit '{name}' already exists. Please choose a different name.[/red]")
            return

        # If the habit name is empty, print an error message
        if name is None or name.strip() == "":
            rich.print("[red]Habit name cannot be empty. Please provide a valid name.[/red]")
            return

        # If habit does not exist, insert it into the database
        else:
            cur.execute("INSERT INTO habits (name, description, periodicity, streak) VALUES (?, ?, ?, ?)",
            (name, description, periodicity, streak))
            self.db.commit()
            rich.print(f"[green]Habit '{name}' added successfully.[/green]")

    def delete_habit(self, name):
        """Delete a habit from the database."""
        cur = self.db.cursor()

        # If the habit does not exist, print an error message
        if not self.get_one_habit(name):
            rich.print(f"[red]Habit '{name}' not found. Please select an existing habit to delete.[/red]")
            return

        # If the habit exists, delete it from the habits table
        cur.execute("DELETE FROM habits WHERE name = ?", (name,))

        # Also delete all events associated with the habit
        events = self.get_one_habit_events(name)

        if events:
            cur.execute("DELETE FROM habit_tracker WHERE habitName = ?", (name,))
            rich.print(f"[dark_orange]All events for habit '{name}' have been deleted.[/dark_orange]")
        else:
            rich.print(f"[red]No events found for habit '{name}'.[/red]")

        self.db.commit()
        rich.print(f"[dark_orange]Habit '{name}' deleted successfully.[/dark_orange]")

    def clear_database(self):
        """Clear all habits and events from the database."""
        cur = self.db.cursor()
        cur.execute("DELETE FROM habits")
        cur.execute("DELETE FROM habit_tracker")
        self.db.commit()
        rich.print("[green]All habits and events have been cleared from the database.[/green]")

    def get_one_habit(self, name):
        """Retrieve data for a specific habit."""
        cur = self.db.cursor()
        # Fetch the habit from db by name
        cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
        rows = cur.fetchall()

        # If the habit exists, return it as a HabitTracker object
        if rows:
            return [
                HabitTracker(name=row[0], description=row[1], periodicity=row[2], streak=row[3], event_count=row[4])
                for row in rows
            ]
        else:
            return []

    def list_one_habit(self, name):
        """List a specific habit in a readable format."""

        # Fetch the habit by name from the db
        habits = self.get_one_habit(name)

        # If the habit exists, print its details
        if habits:
            habit = habits[0]
            rich.print(
                f"Habit name: [bold purple]{habit.name}[/bold purple]\n"
                f" description: {habit.description}\n"
                f" periodicity: {habit.periodicity}\n"
                f" streak: {habit.streak}\n"
                f" number of events: {habit.event_count}\n\n"
            )
        # If the habit does not exist, print an error message
        else:
            rich.print(f"[red]Habit '{name}' not found. Please select an existing habit,"
                       f" or add it to your list![/red]")

    def get_all_habits(self):
        """Retrieve data for all habits."""
        cur = self.db.cursor()
        # Fetch all habits from the db
        cur.execute("SELECT * FROM habits")
        rows = cur.fetchall()

        # If habits exist, return them as a list of HabitTracker objects
        if rows:
            return [
                HabitTracker(name=row[0], description=row[1], periodicity=row[2], streak=row[3], event_count=row[4])
                for row in rows
            ]
        else:
            rich.print("[red]No habits found.[/red]")
            return []


    def list_all_habits(self):
        """List all habits in a readable format."""

        # Fetch all habits from the db
        habits = self.get_all_habits()

        # If habits exist, print their details
        if habits:
            for habit in habits:
                rich.print(
                    f"Habit name: [bold purple]{habit.name}[/bold purple]\n"
                    f" description: {habit.description}\n"
                    f" periodicity: {habit.periodicity}\n"
                    f" streak: {habit.streak}\n"
                    f" number of events: {habit.event_count}\n"
                )
        else:
            rich.print("[red]No habits found.[/red]")

    def add_habit_event(self, name, event_date = ""):
        """Add an event for a specific habit."""

        # If no event date is provided, use today's date
        if event_date == "":
            event_date = date.today()

        # If the habit does not exist, print an error message
        if not self.get_one_habit(name):
            rich.print(f"[red]Habit '{name}' not found. Please add the habit before trying to complete an event![/red]")
            return

        # If the event date is not in the correct format, print an error message
        # if get_valid_date(event_date) is None:
        #     print("Invalid format! Please use YYYY-MM-DD (e.g., 2025-06-01).")
        #     return

        # Save the habit data to a variable
        habit = self.get_one_habit(name)[0]

        # Get the last event date for the habit
        last_event_date = self.get_last_event_date(name)

        # Validate the event date
        valid_date = get_valid_date(event_date)
        if not valid_date:
            rich.print("[red]Invalid format! Please use YYYY-MM-DD (e.g., 2025-06-01).[/red]")
            return
        event_date = valid_date

        # Check if the event date is in the future
        if event_date > date.today():
            rich.print(f"[red]You cannot add an event for habit [bold purple]{name}[/bold purple]"
                       f" that's the future![/red]")
            return

        # If the habit exists, check if the user is trying to add an event too soon. Differentiate between daily
        # and weekly habits.
        if habit:
            if last_event_date:
                if habit.periodicity.lower() == "daily" and habit.event_too_soon(last_event_date, event_date):
                    rich.print(f"[red]You cannot add another event for this daily habit"
                               f" [bold purple]{name}[/bold purple] today. "
                               f"Please wait until [bold purple]tomorrow[/bold purple]"
                               f" before adding another event.[/red]")
                    return

                elif habit.periodicity.lower() == "weekly" and habit.event_too_soon(last_event_date, event_date):
                    time_until_next_event = (last_event_date + timedelta(weeks=1) - date.today()).days
                    rich.print(f"[red]You cannot add another event for habit [bold purple]{name}[/bold purple] so soon."
                               f" Please wait another [bold purple]{time_until_next_event} days[/bold purple]"
                               f" before adding another event.[/red]")
                    return

            # Check if the habit's streak should be reset based on the last event date.
            if habit.should_reset_streak(last_event_date):
                rich.print(f"[dark_orange]Streak for habit '{name}' has been reset due to inactivity.[/dark_orange]")
                habit.reset_streak()

            # If all checks pass, insert the event into the habit_tracker table and update the habit's streak and event count
            cur = self.db.cursor()

            if not event_date:
                event_date = str(date.today())

            cur.execute("INSERT INTO habit_tracker (date, habitName) VALUES (?, ?)", (event_date.isoformat(), name))
            habit.increment_streak()
            habit.increment_event()
            cur.execute("UPDATE habits SET streak = ?, event_count = ? WHERE name = ?",
                        (habit.streak, habit.event_count, name))

            self.db.commit()

            rich.print(f"[green]Event added for habit '{name}' on {event_date}.[/green]")


    def get_all_habit_events(self):
        """Retrieve all habit events."""

        # Fetch all habit events from the db
        cur = self.db.cursor()
        cur.execute("SELECT * FROM habit_tracker")
        rows = cur.fetchall()

        # If habit events exist, return them as a list of HabitEvent objects, otherwise print an error message
        if rows:
            rich.print(f"[green]Retrieved {len(rows)} habit events.[/green]")
            return [
                HabitEvent(completed_at = row[0], habit_name = row[1])
                for row in rows
            ]
        else:
            rich.print("[red]No habit events found.[/red]")
            return []


    def get_one_habit_events(self, name):
        """Retrieve all events for a specific habit."""

        # Fetch all events for a specific habit from the db
        cur = self.db.cursor()
        cur.execute("SELECT * FROM habit_tracker WHERE habitName = ?", (name,))
        rows = cur.fetchall()

        # If events exist for the habit, return them as a list of HabitEvent objects, otherwise print an error message
        if rows:
            rich.print(f"[green]Retrieved {len(rows)} events for habit '{name}'.[/green]")
            return [
                HabitEvent(completed_at = row[0], habit_name = row[1])
                for row in rows
            ]
        else:
            # rich.print(f"[red]No events found for habit '{name}'.[/red]")
            return []

    def list_one_habit_events(self, name):
        """List all events for a specific habit in a readable format."""

        # Fetch all events for the specific habit
        events = self.get_one_habit_events(name)

        # If events exist, print their details, otherwise print an error message
        if events:
            for event in events:
                rich.print(
                    f"Event date: [bold purple]{event.completed_at}[/bold purple]\n"
                    f" Habit name: {event.habit_name}\n"
                )
        else:
            rich.print(f"[red]No events found for habit '{name}'.[/red]")

    def list_all_habit_events(self):
        """List all habit events in a readable format."""

        # Fetch all habit events
        events = self.get_all_habit_events()

        # If events exist, print their details, otherwise print an error message
        if events:
            for event in events:
                rich.print(
                    f"Event date: [bold purple]{event.completed_at}[/bold purple]\n"
                    f" Habit name: {event.habit_name}\n"
                )
        else:
            rich.print("[red]No habit events found.[/red]")

    def get_last_event_date(self, name):
        """Get the date of the last event for a specific habit."""

        # Fetch the last event date for the specific habit from the db
        cur = self.db.cursor()
        cur.execute("SELECT date FROM habit_tracker WHERE habitName = ? ORDER BY date DESC LIMIT 1", (name,))
        row = cur.fetchone()

        # If an event is found, return the date as a datetime object, and strip time to return only the date
        # otherwise return None
        if row:
            return datetime.strptime(row[0], "%Y-%m-%d").date()
        else:
            return None

    def close(self):
        """Close the database connection."""
        if self.db:
            self.db.close()


