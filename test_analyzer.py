import os
import pytest
from datetime import date, timedelta
from habit_repository import HabitRepository
from analyzer import HabitAnalyzer

@pytest.fixture
def analyzer_fixture():
    """Fixture to create HabitRepository and HabitAnalyzer instances with a db connection to a test_db for testing."""
    db_path = "test.db"

    # Make sure the file is not open and delete it before the test
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pytest.skip("test.db is locked by another process")

    # Create the repo and analyzer object from HabitRepository and HabitAnalyzer (also creates the DB)
    repo = HabitRepository(db_name=db_path)
    analyzer = HabitAnalyzer(repo)

    # return the analyzer object for use in tests
    yield analyzer

    # Final cleanup — ensure DB is closed and deleted
    analyzer.close()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            print("Could not delete test.db after test.")

def test_longest_overall_streak(analyzer_fixture):
    """Test the longest overall streak calculation."""
    repo = analyzer_fixture.repo
    repo.add_habit("A", "Test A", "Daily", streak=3)
    repo.add_habit("B", "Test B", "Daily", streak=5)
    result = analyzer_fixture.longest_overall_streak()
    assert "B" in result
    assert "5" in result

def test_daily_habit_completed(analyzer_fixture):
    """Test if a daily habit is marked as completed."""
    repo = analyzer_fixture.repo
    repo.add_habit("DailyTest", "Test", "Daily")
    repo.add_habit_event("DailyTest", date.today().isoformat())
    assert analyzer_fixture.daily_habit_completed("DailyTest") is True

def test_daily_habit_not_completed(analyzer_fixture):
    """Test if a daily habit is not marked as completed."""
    repo = analyzer_fixture.repo
    repo.add_habit("NoEventDaily", "Test", "Daily")
    assert analyzer_fixture.daily_habit_completed("NoEventDaily") is False

def test_weekly_habit_completed(analyzer_fixture):
    """Test if a weekly habit is marked as completed."""
    repo = analyzer_fixture.repo
    repo.add_habit("WeeklyOK", "Test", "Weekly")
    recent = (date.today() - timedelta(days=3)).isoformat()
    repo.add_habit_event("WeeklyOK", recent)
    assert analyzer_fixture.weekly_habit_completed("WeeklyOK") is True

def test_weekly_habit_overdue(analyzer_fixture):
    """Test if a weekly habit is overdue."""
    repo = analyzer_fixture.repo
    repo.add_habit("WeeklyLate", "Test", "Weekly")
    late = (date.today() - timedelta(days=8)).isoformat()
    repo.add_habit_event("WeeklyLate", late)
    assert analyzer_fixture.weekly_habit_completed("WeeklyLate") is False

def test_biggest_struggle(analyzer_fixture):
    """Test the biggest struggle calculation."""
    repo = analyzer_fixture.repo
    repo.add_habit("Perfect", "No struggle", "Daily", streak=5)
    repo.add_habit("Tough", "Breaks often", "Daily", streak=1)
    for _ in range(5):
        repo.add_habit_event("Tough")
    repo.add_habit_event("Perfect")
    analyzer_fixture.biggest_struggle()  # Just ensure it runs

def test_list_all_overdue_habits(analyzer_fixture):
    """Test listing all overdue habits."""
    repo = analyzer_fixture.repo
    repo.add_habit("LateDaily", "Missed it", "Daily")
    repo.add_habit_event("LateDaily", (date.today() - timedelta(days=2)).isoformat())
    analyzer_fixture.list_all_overdue_habits()  # Just ensure it runs