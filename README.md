# Planner - Academic Scheduler

A scheduling system that distributes subjects across a semester based on lecturer availability.

## Features

- Manages up to 5 student groups, 20 lecturers, 15 subjects, and 10 rooms
- Prioritizes high-importance lecturers (up to 5)
- Uses availability calendars to schedule subjects
- Distributes subjects across half-day blocks (morning/afternoon)
- Automatically assigns available rooms
- Avoids scheduling conflicts (lecturer double-booking, room conflicts)

## Requirements

- Python 3.7 or higher
- No external dependencies required

## Usage

### Basic Example

```python
from datetime import date, timedelta
from scheduler import Lecturer, Subject, Room, Block, TimeSlot, Scheduler

# Define semester dates
semester_start = date(2024, 9, 1)
semester_end = date(2024, 12, 20)

# Create a lecturer with availability
lecturer = Lecturer(
    id=1,
    name="Dr. Smith",
    subject_id=1,
    is_high_importance=True,
    available_blocks={
        Block(date(2024, 9, 2), TimeSlot.MORNING),
        Block(date(2024, 9, 2), TimeSlot.AFTERNOON),
        # ... more blocks
    }
)

# Create a subject
subject = Subject(
    id=1,
    name="Mathematics",
    required_blocks=10,
    lecturer_id=1
)

# Create rooms
rooms = [Room(id=1, name="Room A1")]

# Create and run scheduler
scheduler = Scheduler(
    lecturers=[lecturer],
    subjects=[subject],
    rooms=rooms,
    semester_start=semester_start,
    semester_end=semester_end,
    student_groups=5
)

# Generate schedule
scheduled_blocks = scheduler.schedule()

# Print the schedule
scheduler.print_schedule()
```

### Running the Example

A complete example is provided in `example_usage.py`:

```bash
python example_usage.py
```

This demonstrates:
- Creating 5 high-importance lecturers with different availability patterns
- Creating 10 subjects with varying block requirements
- Setting up 10 rooms
- Running the scheduler
- Viewing the generated schedule

## Running Tests

Run the test suite to verify the scheduler works correctly:

```bash
python -m unittest test_scheduler.py -v
```

## Core Components

### Data Models

- **Block**: Represents a half-day time slot (morning or afternoon on a specific date)
- **Lecturer**: A lecturer with availability calendar and assigned subject
- **Subject**: A subject requiring a certain number of teaching blocks
- **Room**: A theory room available for scheduling
- **ScheduledBlock**: A scheduled teaching session linking subject, lecturer, room, block, and student group

### Scheduler

The `Scheduler` class:
1. Takes lecturers, subjects, rooms, and semester dates as input
2. Prioritizes high-importance lecturers (scheduled first)
3. For each subject, schedules all required blocks across available time slots
4. Assigns rooms avoiding conflicts
5. Ensures lecturers aren't double-booked
6. Generates schedules for all student groups

### Availability Calendars

Lecturers have availability calendars (sets of `Block` objects) indicating when they can teach. The scheduler only assigns blocks when:
- The lecturer is available (block is in their availability calendar)
- The lecturer isn't already scheduled for that block
- A room is available for that block and student group

## Scheduling Algorithm

1. Sort lecturers by priority (high-importance first)
2. For each lecturer:
   - Get their subject
   - For each student group:
     - Schedule required number of blocks
     - Check lecturer availability
     - Find available room
     - Reserve the slot

This ensures high-importance lecturers get their preferred time slots first.

## Output

The scheduler provides:
- **Detailed schedule**: Day-by-day listing of all scheduled blocks
- **Summary statistics**: Total blocks, subjects covered, resources used
- **Coverage metrics**: How many blocks were scheduled vs. required

## Constraints

- Maximum 5 student groups
- Maximum 20 lecturers
- Maximum 15 subjects
- Maximum 10 rooms
- Maximum 50 blocks per subject
- Each lecturer teaches only one subject
- All rooms have sufficient capacity
- Scheduling only on weekdays (no weekends)

## Example Output

```
================================================================================
SCHEDULE SUMMARY
================================================================================

Total Scheduled Blocks: 435
Subjects Scheduled: 10
Lecturers Used: 10
Rooms Used: 9

================================================================================
HIGH-IMPORTANCE LECTURER SUMMARY
================================================================================

Dr. Smith (Mathematics):
  Required blocks: 50
  Scheduled blocks: 50
  Coverage: 100.0%

Prof. Johnson (Physics):
  Required blocks: 60
  Scheduled blocks: 60
  Coverage: 100.0%
```

## License

MIT License