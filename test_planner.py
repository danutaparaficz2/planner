#!/usr/bin/env python3
"""
Unit tests for the Task Planner
"""

import unittest
import os
import tempfile
from planner import Planner, Task, Priority, Status


class TestTask(unittest.TestCase):
    """Tests for Task class"""
    
    def test_task_creation(self):
        """Test creating a task"""
        task = Task("Test task", "Test description", Priority.HIGH, "2025-12-01")
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.description, "Test description")
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertEqual(task.status, Status.TODO)
        self.assertEqual(task.due_date, "2025-12-01")
    
    def test_task_to_dict(self):
        """Test converting task to dictionary"""
        task = Task("Test task", "Test description", Priority.HIGH)
        task.id = 1
        data = task.to_dict()
        
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], "Test task")
        self.assertEqual(data['priority'], "HIGH")
        self.assertEqual(data['status'], "todo")
    
    def test_task_from_dict(self):
        """Test creating task from dictionary"""
        data = {
            'id': 1,
            'title': "Test task",
            'description': "Test description",
            'priority': "HIGH",
            'status': "todo",
            'due_date': "2025-12-01"
        }
        task = Task.from_dict(data)
        
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertEqual(task.status, Status.TODO)


class TestPlanner(unittest.TestCase):
    """Tests for Planner class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.planner = Planner(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_task(self):
        """Test adding a task"""
        task = Task("Test task", "Description", Priority.HIGH)
        added_task = self.planner.add_task(task)
        
        self.assertIsNotNone(added_task.id)
        self.assertEqual(len(self.planner.tasks), 1)
        self.assertEqual(self.planner.tasks[0].title, "Test task")
    
    def test_get_task(self):
        """Test getting a task by ID"""
        task = Task("Test task")
        self.planner.add_task(task)
        
        retrieved_task = self.planner.get_task(1)
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.title, "Test task")
        
        # Test non-existent task
        self.assertIsNone(self.planner.get_task(999))
    
    def test_list_tasks(self):
        """Test listing tasks"""
        task1 = Task("Task 1", priority=Priority.HIGH)
        task2 = Task("Task 2", priority=Priority.LOW)
        
        self.planner.add_task(task1)
        self.planner.add_task(task2)
        
        all_tasks = self.planner.list_tasks()
        self.assertEqual(len(all_tasks), 2)
        
        # Test filtering by priority
        high_priority = self.planner.list_tasks(priority=Priority.HIGH)
        self.assertEqual(len(high_priority), 1)
        self.assertEqual(high_priority[0].title, "Task 1")
    
    def test_list_tasks_by_status(self):
        """Test filtering tasks by status"""
        task1 = Task("Task 1")
        task2 = Task("Task 2")
        
        self.planner.add_task(task1)
        self.planner.add_task(task2)
        self.planner.update_task(2, status=Status.COMPLETED)
        
        todo_tasks = self.planner.list_tasks(status=Status.TODO)
        self.assertEqual(len(todo_tasks), 1)
        
        completed_tasks = self.planner.list_tasks(status=Status.COMPLETED)
        self.assertEqual(len(completed_tasks), 1)
    
    def test_update_task(self):
        """Test updating a task"""
        task = Task("Original title")
        self.planner.add_task(task)
        
        updated_task = self.planner.update_task(1, title="New title", status=Status.IN_PROGRESS)
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task.title, "New title")
        self.assertEqual(updated_task.status, Status.IN_PROGRESS)
        
        # Test updating non-existent task
        self.assertIsNone(self.planner.update_task(999, title="Test"))
    
    def test_delete_task(self):
        """Test deleting a task"""
        task = Task("Test task")
        self.planner.add_task(task)
        self.assertEqual(len(self.planner.tasks), 1)
        
        result = self.planner.delete_task(1)
        self.assertTrue(result)
        self.assertEqual(len(self.planner.tasks), 0)
        
        # Test deleting non-existent task
        result = self.planner.delete_task(999)
        self.assertFalse(result)
    
    def test_persistence(self):
        """Test saving and loading tasks"""
        task = Task("Persistent task", "Description", Priority.HIGH, "2025-12-01")
        self.planner.add_task(task)
        
        # Create a new planner instance with the same data file
        new_planner = Planner(self.temp_file.name)
        
        self.assertEqual(len(new_planner.tasks), 1)
        loaded_task = new_planner.tasks[0]
        self.assertEqual(loaded_task.title, "Persistent task")
        self.assertEqual(loaded_task.priority, Priority.HIGH)
        self.assertEqual(loaded_task.due_date, "2025-12-01")


class TestPriority(unittest.TestCase):
    """Tests for Priority enum"""
    
    def test_priority_levels(self):
        """Test priority levels"""
        self.assertEqual(Priority.LOW.value, 1)
        self.assertEqual(Priority.MEDIUM.value, 2)
        self.assertEqual(Priority.HIGH.value, 3)
        self.assertEqual(Priority.URGENT.value, 4)


class TestStatus(unittest.TestCase):
    """Tests for Status enum"""
    
    def test_status_values(self):
        """Test status values"""
        self.assertEqual(Status.TODO.value, "todo")
        self.assertEqual(Status.IN_PROGRESS.value, "in_progress")
        self.assertEqual(Status.COMPLETED.value, "completed")
        self.assertEqual(Status.CANCELLED.value, "cancelled")


if __name__ == "__main__":
    unittest.main()
