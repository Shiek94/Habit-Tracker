import os
import pytest
from datetime import date
from habit_repository import HabitRepository

@pytest.fixture
def repo():
    """Fixture to create a HabitRepository instance with a db connection to a test_db for testing."""
    db_path = "test.db"

    # Make sure the file is not open and delete it before the test
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pytest.skip("test.db is locked by another process")

    # Create the repo object from HabitRepository (also creates the DB)
    repo = HabitRepository(db_name=db_path)

    # return the repo object for use in tests
    yield repo

    # Final cleanup — ensure DB is closed and deleted
    repo.close()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            print("Could not delete test.db after test.")

def test_add_and_retrieve_habit(repo):
    """Test adding a habit and retrieving its attributes"""
    repo.add_habit("Read", "Read a book", "Daily")
    habits = repo.get_one_habit("Read")
    assert len(habits) == 1
    assert habits[0].name == "Read"
    assert habits[0].description == "Read a book"
    assert habits[0].periodicity.lower() == "daily"

def test_prevent_duplicate_habit(repo):
    """Test that adding a duplicate habit does not create a new entry"""
    repo.add_habit("Workout", "Exercise", "Daily")
    repo.add_habit("Workout", "Exercise", "Daily")  # Should not be added twice
    all_habits = repo.get_all_habits()
    assert len(all_habits) == 1

def test_delete_habit_and_events(repo):
    """Test deleting a habit and its associated events"""
    repo.add_habit("Meditate", "Calm mind", "Daily")
    repo.add_habit_event("Meditate")
    repo.delete_habit("Meditate")
    assert repo.get_one_habit("Meditate") == []
    assert repo.get_one_habit_events("Meditate") == []

def test_clear_database(repo):
    """Test clearing the database of all habits and events"""
    repo.add_habit("Sleep", "Track sleep", "Daily")
    repo.add_habit_event("Sleep")
    repo.clear_database()
    assert repo.get_all_habits() == []
    assert repo.get_all_habit_events() == []

def test_add_habit_event(repo):
    """Test adding a habit event and retrieving it"""
    repo.add_habit("Hydrate", "Drink water", "Daily")
    repo.add_habit_event("Hydrate")
    events = repo.get_one_habit_events("Hydrate")
    assert len(events) == 1
    assert events[0].habit_name == "Hydrate"

def test_get_last_event_date(repo):
    """Test retrieving the last event date for a habit"""
    repo.add_habit("Run", "Go jogging", "Daily")
    today = date.today()
    repo.add_habit_event("Run", today.isoformat())
    last_date = repo.get_last_event_date("Run")
    assert last_date == today