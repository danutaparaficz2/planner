"""
Example usage of the scheduler.

This script demonstrates how to:
1. Create lecturers with availability calendars
2. Define subjects with required blocks
3. Set up rooms
4. Run the scheduler
5. View the results
"""

from datetime import date, timedelta
from scheduler import Lecturer, Subject, Room, Block, TimeSlot, Scheduler


def create_availability_calendar(start_date: date, end_date: date, 
                                 unavailable_dates: list = None) -> set:
    """
    Create an availability calendar for a lecturer.
    
    Args:
        start_date: Start of the semester
        end_date: End of the semester
        unavailable_dates: List of dates when lecturer is unavailable
    
    Returns:
        Set of available blocks
    """
    if unavailable_dates is None:
        unavailable_dates = []
    
    available_blocks = set()
    current_date = start_date
    
    while current_date <= end_date:
        # Skip weekends and unavailable dates
        if current_date.weekday() < 5 and current_date not in unavailable_dates:
            available_blocks.add(Block(current_date, TimeSlot.MORNING))
            available_blocks.add(Block(current_date, TimeSlot.AFTERNOON))
        
        current_date += timedelta(days=1)
    
    return available_blocks


def main():
    """Run example scheduler."""
    # Define semester dates
    semester_start = date(2024, 9, 1)  # September 1, 2024
    semester_end = date(2024, 12, 20)  # December 20, 2024
    
    print("="*80)
    print("SCHEDULER EXAMPLE - Setting up data")
    print("="*80)
    
    # Create 5 high-importance lecturers with availability calendars
    high_importance_lecturers = []
    
    # Lecturer 1: Mathematics - available most days
    lecturer1 = Lecturer(
        id=1,
        name="Dr. Smith",
        subject_id=1,
        is_high_importance=True,
        available_blocks=create_availability_calendar(
            semester_start, semester_end,
            unavailable_dates=[date(2024, 10, 15), date(2024, 11, 20)]
        )
    )
    high_importance_lecturers.append(lecturer1)
    
    # Lecturer 2: Physics - unavailable on Mondays
    unavailable_mondays = []
    current = semester_start
    while current <= semester_end:
        if current.weekday() == 0:  # Monday
            unavailable_mondays.append(current)
        current += timedelta(days=1)
    
    lecturer2 = Lecturer(
        id=2,
        name="Prof. Johnson",
        subject_id=2,
        is_high_importance=True,
        available_blocks=create_availability_calendar(
            semester_start, semester_end,
            unavailable_dates=unavailable_mondays
        )
    )
    high_importance_lecturers.append(lecturer2)
    
    # Lecturer 3: Computer Science - available all semester
    lecturer3 = Lecturer(
        id=3,
        name="Dr. Williams",
        subject_id=3,
        is_high_importance=True,
        available_blocks=create_availability_calendar(
            semester_start, semester_end
        )
    )
    high_importance_lecturers.append(lecturer3)
    
    # Lecturer 4: Chemistry - unavailable first two weeks
    unavailable_first_weeks = []
    current = semester_start
    while current < semester_start + timedelta(days=14):
        unavailable_first_weeks.append(current)
        current += timedelta(days=1)
    
    lecturer4 = Lecturer(
        id=4,
        name="Dr. Brown",
        subject_id=4,
        is_high_importance=True,
        available_blocks=create_availability_calendar(
            semester_start, semester_end,
            unavailable_dates=unavailable_first_weeks
        )
    )
    high_importance_lecturers.append(lecturer4)
    
    # Lecturer 5: Biology - unavailable on Fridays
    unavailable_fridays = []
    current = semester_start
    while current <= semester_end:
        if current.weekday() == 4:  # Friday
            unavailable_fridays.append(current)
        current += timedelta(days=1)
    
    lecturer5 = Lecturer(
        id=5,
        name="Prof. Davis",
        subject_id=5,
        is_high_importance=True,
        available_blocks=create_availability_calendar(
            semester_start, semester_end,
            unavailable_dates=unavailable_fridays
        )
    )
    high_importance_lecturers.append(lecturer5)
    
    # Create additional regular lecturers (not high importance)
    regular_lecturers = []
    for i in range(6, 11):  # 5 more lecturers (total 10)
        lecturer = Lecturer(
            id=i,
            name=f"Lecturer {i}",
            subject_id=i,
            is_high_importance=False,
            available_blocks=create_availability_calendar(
                semester_start, semester_end
            )
        )
        regular_lecturers.append(lecturer)
    
    all_lecturers = high_importance_lecturers + regular_lecturers
    
    # Create subjects
    subjects = [
        Subject(id=1, name="Mathematics", required_blocks=10, lecturer_id=1),
        Subject(id=2, name="Physics", required_blocks=12, lecturer_id=2),
        Subject(id=3, name="Computer Science", required_blocks=15, lecturer_id=3),
        Subject(id=4, name="Chemistry", required_blocks=8, lecturer_id=4),
        Subject(id=5, name="Biology", required_blocks=10, lecturer_id=5),
        Subject(id=6, name="History", required_blocks=6, lecturer_id=6),
        Subject(id=7, name="Literature", required_blocks=8, lecturer_id=7),
        Subject(id=8, name="Economics", required_blocks=7, lecturer_id=8),
        Subject(id=9, name="Geography", required_blocks=5, lecturer_id=9),
        Subject(id=10, name="Art", required_blocks=6, lecturer_id=10),
    ]
    
    # Create rooms
    rooms = [
        Room(id=1, name="Room A1"),
        Room(id=2, name="Room A2"),
        Room(id=3, name="Room B1"),
        Room(id=4, name="Room B2"),
        Room(id=5, name="Room C1"),
        Room(id=6, name="Room C2"),
        Room(id=7, name="Room D1"),
        Room(id=8, name="Room D2"),
        Room(id=9, name="Lab 1"),
        Room(id=10, name="Lab 2"),
    ]
    
    print(f"\nCreated {len(all_lecturers)} lecturers ({len(high_importance_lecturers)} high importance)")
    print(f"Created {len(subjects)} subjects")
    print(f"Created {len(rooms)} rooms")
    print(f"Semester: {semester_start} to {semester_end}")
    
    # Create scheduler
    print("\n" + "="*80)
    print("RUNNING SCHEDULER")
    print("="*80)
    
    scheduler = Scheduler(
        lecturers=all_lecturers,
        subjects=subjects,
        rooms=rooms,
        semester_start=semester_start,
        semester_end=semester_end,
        student_groups=5
    )
    
    # Run scheduling
    scheduled_blocks = scheduler.schedule()
    
    print(f"\nSuccessfully scheduled {len(scheduled_blocks)} blocks")
    
    # Print the schedule
    scheduler.print_schedule()
    
    # Print high-importance lecturer summary
    print("\n" + "="*80)
    print("HIGH-IMPORTANCE LECTURER SUMMARY")
    print("="*80)
    
    for lecturer in high_importance_lecturers:
        lecturer_blocks = [sb for sb in scheduled_blocks if sb.lecturer.id == lecturer.id]
        subject = next((s for s in subjects if s.id == lecturer.subject_id), None)
        
        if subject:
            total_required = subject.required_blocks * 5  # 5 student groups
            print(f"\n{lecturer.name} ({subject.name}):")
            print(f"  Required blocks: {total_required}")
            print(f"  Scheduled blocks: {len(lecturer_blocks)}")
            print(f"  Coverage: {len(lecturer_blocks)/total_required*100:.1f}%")


if __name__ == "__main__":
    main()
