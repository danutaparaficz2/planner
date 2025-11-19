# Task Planner

A simple, lightweight task planning application written in Python. Manage your tasks with priorities, statuses, and due dates.

## Features

- **Task Management**: Create, read, update, and delete tasks
- **Priority Levels**: Low, Medium, High, and Urgent priorities
- **Status Tracking**: Track tasks through TODO, In Progress, Completed, and Cancelled states
- **Due Dates**: Set optional due dates for tasks
- **Persistent Storage**: Tasks are saved to a JSON file
- **CLI Interface**: Easy-to-use command-line interface
- **Filtering**: List tasks by status or priority

## Installation

No external dependencies required. Just Python 3.6+.

```bash
git clone https://github.com/danutaparaficz2/planner.git
cd planner
```

## Usage

### Programmatic Usage

```python
from planner import Planner, Task, Priority, Status

# Create a planner instance
planner = Planner()

# Add a task
task = Task("Complete project", "Finish the documentation", Priority.HIGH, "2025-12-01")
planner.add_task(task)

# List all tasks
for task in planner.list_tasks():
    print(task)

# Update a task
planner.update_task(1, status=Status.COMPLETED)

# Delete a task
planner.delete_task(1)
```

### Command-Line Interface

```bash
# Add a task
python cli.py add "Complete project proposal" -d "Write Q4 proposal" -p high --due-date 2025-12-01

# List all tasks
python cli.py list

# List tasks by status
python cli.py list -s todo

# List tasks by priority
python cli.py list -p high

# Show task details
python cli.py show 1

# Update a task
python cli.py update 1 -s in_progress

# Delete a task
python cli.py delete 1
```

## Examples

Run the example:

```bash
python planner.py
```

This will demonstrate creating tasks, updating statuses, and filtering tasks.

## Data Storage

Tasks are stored in `planner_data.json` by default. You can specify a different file:

```python
planner = Planner("my_tasks.json")
```

Or via CLI:

```bash
python cli.py --data-file my_tasks.json list
```

## Task Structure

Each task has the following properties:

- **ID**: Unique identifier (auto-generated)
- **Title**: Task name
- **Description**: Detailed description (optional)
- **Priority**: LOW, MEDIUM, HIGH, or URGENT
- **Status**: TODO, IN_PROGRESS, COMPLETED, or CANCELLED
- **Due Date**: Optional due date (YYYY-MM-DD format)
- **Created At**: Timestamp when task was created
- **Updated At**: Timestamp of last update

## License

MIT License