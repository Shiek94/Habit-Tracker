from habit_repository import HabitRepository
from rich import print
from analyzer import HabitAnalyzer
import questionary

# Initialize the HabitRepository and HabitAnalyzer Objects
repo = HabitRepository()
habit_analyzer = HabitAnalyzer(repo)

# Add some default habits for the User to interact with
# repo.add_habit("meditate", "meditate for 10 minutes", "weekly")
# repo.add_habit("cold shower", "take a cold shower for 2 minutes", "daily")
# repo.add_habit("exercise", "go to the gym for 1 hour", "daily")
# repo.add_habit("clean apartment", "clean the apartment", "weekly")
# repo.add_habit("study session", "study for 2 hours", "daily")

def cli():
    """Command Line Interface for Habit Tracker. Main menu for user interaction."""

    # Initialize the main loop control variable
    should_continue = True

    print("[bold green]Welcome to the Habit Tracker CLI![/bold green]")

    # Loop for the CLI main menu
    while should_continue:
        choice = questionary.select(
            "Main Menu: What would you like to do?",
            choices = [
                "Create new habit",
                "Delete existing habit",
                "Clear all habits and events",
                "Complete a habit task",
                "View habit details",
                "Analyze habits",
                "Exit Program",
            ]
        ).ask()

        if choice == "Create new habit":
            name = questionary.text("Enter the name of the habit:").ask()
            description = questionary.text("Enter a description for the habit:").ask()
            periodicity = questionary.select(
                "Select the periodicity of the habit:",
                choices=["Daily",
                         "Weekly",]
            ).ask()
            repo.add_habit(name, description, periodicity)

        elif choice == "Delete existing habit":
            name = questionary.text("Enter the name of the habit to delete:").ask()
            repo.delete_habit(name)

        elif choice == "Clear all habits and events":
            confirm = questionary.confirm("Are you sure you want to clear all habits and events?").ask()
            if confirm:
                repo.clear_database()

        elif choice == "Complete a habit task":
            name = questionary.text("Enter the name of the habit to complete:").ask()
            date = questionary.text("Enter the date of completion (YYYY-MM-DD): (default: current date)").ask()
            repo.add_habit_event(name, date)

        elif choice == "View habit details":
            view_menu()

        elif choice == "Analyze habits":
            analytics_menu()

        elif choice == "Exit Program":
            print("[green]Exiting the Habit Tracker CLI. Goodbye![/green]")
            should_continue = False

def view_menu():
            """Display the menu for viewing habits. Sub menu of the main menu."""
            choice = questionary.select(
                "View Menu: What would you like to do?",
                choices=["List one specific habit",
                         "List all events of a specific habit",
                         "List all habits",
                         "List all habit events",
                         "Back to main menu",
                         ]
            ).ask()

            if choice == "List one specific habit":
                name = questionary.text("Enter the name of the habit:").ask()
                repo.list_one_habit(name)

            elif choice == "List all events of a specific habit":
                name = questionary.text("Enter the name of the habit:").ask()
                repo.list_one_habit_events(name)

            elif choice == "List all habits":
                repo.list_all_habits()

            elif choice == "List all habit events":
                repo.list_all_habit_events()

            elif choice == "Back to main menu":
                return

def analytics_menu():
            """Display the menu for analyzing habits. Sub menu of the main menu."""
            choice = questionary.select(
                "Analytics Menu: What would you like to do?",
                choices=["Display completion state of a specific habit (both daily/weekly)",
                         "Display most difficult to maintain habit",
                         "Display the habit with the longest overall streak",
                         "List all overdue habits",
                         "Back to main menu",
                         ]
            ).ask()

            if choice == "Display completion state of a specific habit (both daily/weekly)":
                name = questionary.text("Enter the name of the habit:").ask()
                if repo.get_one_habit(name):
                    if repo.get_one_habit(name)[0].periodicity.lower() == "daily":
                        habit_analyzer.daily_habit_completed(name)
                    elif repo.get_one_habit(name)[0].periodicity.lower() == "weekly":
                        habit_analyzer.weekly_habit_completed(name)
                else:
                    print(f"[red]Habit '{name}' not found.[/red]")

            elif choice == "Display most difficult to maintain habit":
                habit_analyzer.biggest_struggle()

            elif choice == "Display the habit with the longest overall streak":
                habit_analyzer.longest_overall_streak()

            elif choice == "List all overdue habits":
                habit_analyzer.list_all_overdue_habits()#

            elif choice == "Back to main menu":
                return


if __name__ =="__main__":
    cli()