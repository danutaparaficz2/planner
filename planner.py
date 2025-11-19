#!/usr/bin/env python3
"""
Simple Task Planner Application
Manages tasks with priorities, statuses, and due dates.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
import json
import os


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class Status(Enum):
    """Task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task:
    """Represents a single task in the planner"""
    
    def __init__(self, title: str, description: str = "", 
                 priority: Priority = Priority.MEDIUM,
                 due_date: Optional[str] = None):
        self.id = None  # Will be assigned when added to planner
        self.title = title
        self.description = description
        self.priority = priority
        self.status = Status.TODO
        self.due_date = due_date
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.name,
            'status': self.status.value,
            'due_date': self.due_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary"""
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            priority=Priority[data.get('priority', 'MEDIUM')],
            due_date=data.get('due_date')
        )
        task.id = data.get('id')
        task.status = Status(data.get('status', 'todo'))
        task.created_at = data.get('created_at', task.created_at)
        task.updated_at = data.get('updated_at', task.updated_at)
        return task
    
    def __str__(self) -> str:
        """String representation of task"""
        due = f" (Due: {self.due_date})" if self.due_date else ""
        return f"[{self.id}] {self.title} - {self.priority.name} - {self.status.value}{due}"


class Planner:
    """Main planner class to manage tasks"""
    
    def __init__(self, data_file: str = "planner_data.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load()
    
    def add_task(self, task: Task) -> Task:
        """Add a new task to the planner"""
        task.id = self.next_id
        self.next_id += 1
        self.tasks.append(task)
        self.save()
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def list_tasks(self, status: Optional[Status] = None, 
                   priority: Optional[Priority] = None) -> List[Task]:
        """List tasks with optional filtering"""
        filtered_tasks = self.tasks
        
        if status:
            filtered_tasks = [t for t in filtered_tasks if t.status == status]
        
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
        
        return filtered_tasks
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """Update a task's properties"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now().isoformat()
        self.save()
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self.save()
            return True
        return False
    
    def save(self):
        """Save planner data to file"""
        data = {
            'next_id': self.next_id,
            'tasks': [task.to_dict() for task in self.tasks]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load planner data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        self.next_id = data.get('next_id', 1)
                        self.tasks = [Task.from_dict(t) for t in data.get('tasks', [])]
            except (json.JSONDecodeError, ValueError):
                # If file is empty or invalid JSON, start fresh
                pass


def main():
    """Main function demonstrating planner usage"""
    planner = Planner()
    
    # Example usage
    print("Task Planner - Example Usage\n")
    
    # Add some tasks
    task1 = Task("Complete project proposal", "Write and submit the Q4 proposal", 
                 Priority.HIGH, "2025-12-01")
    planner.add_task(task1)
    
    task2 = Task("Review team code", "Review pull requests from team", 
                 Priority.MEDIUM)
    planner.add_task(task2)
    
    task3 = Task("Update documentation", "Update API documentation", 
                 Priority.LOW)
    planner.add_task(task3)
    
    # List all tasks
    print("All Tasks:")
    for task in planner.list_tasks():
        print(f"  {task}")
    
    # Update a task status
    print("\nUpdating task 1 to IN_PROGRESS...")
    planner.update_task(1, status=Status.IN_PROGRESS)
    
    # List high priority tasks
    print("\nHigh Priority Tasks:")
    for task in planner.list_tasks(priority=Priority.HIGH):
        print(f"  {task}")
    
    # Complete a task
    print("\nCompleting task 2...")
    planner.update_task(2, status=Status.COMPLETED)
    
    # List completed tasks
    print("\nCompleted Tasks:")
    for task in planner.list_tasks(status=Status.COMPLETED):
        print(f"  {task}")
    
    print(f"\nData saved to {planner.data_file}")


if __name__ == "__main__":
    main()
