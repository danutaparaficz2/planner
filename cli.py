#!/usr/bin/env python3
"""
Command-line interface for the Task Planner
"""

import argparse
import sys
from planner import Planner, Task, Priority, Status


def cmd_add(args, planner):
    """Add a new task"""
    priority = Priority[args.priority.upper()] if args.priority else Priority.MEDIUM
    task = Task(args.title, args.description or "", priority, args.due_date)
    planner.add_task(task)
    print(f"Task added: {task}")


def cmd_list(args, planner):
    """List tasks"""
    status = Status(args.status) if args.status else None
    priority = Priority[args.priority.upper()] if args.priority else None
    
    tasks = planner.list_tasks(status=status, priority=priority)
    
    if not tasks:
        print("No tasks found.")
        return
    
    print(f"Found {len(tasks)} task(s):")
    for task in tasks:
        print(f"  {task}")


def cmd_update(args, planner):
    """Update a task"""
    task = planner.get_task(args.id)
    if not task:
        print(f"Task {args.id} not found.")
        return
    
    kwargs = {}
    if args.title:
        kwargs['title'] = args.title
    if args.description:
        kwargs['description'] = args.description
    if args.priority:
        kwargs['priority'] = Priority[args.priority.upper()]
    if args.status:
        kwargs['status'] = Status(args.status)
    if args.due_date:
        kwargs['due_date'] = args.due_date
    
    if not kwargs:
        print("No updates specified.")
        return
    
    planner.update_task(args.id, **kwargs)
    print(f"Task updated: {task}")


def cmd_delete(args, planner):
    """Delete a task"""
    if planner.delete_task(args.id):
        print(f"Task {args.id} deleted.")
    else:
        print(f"Task {args.id} not found.")


def cmd_show(args, planner):
    """Show task details"""
    task = planner.get_task(args.id)
    if not task:
        print(f"Task {args.id} not found.")
        return
    
    print(f"Task ID: {task.id}")
    print(f"Title: {task.title}")
    print(f"Description: {task.description}")
    print(f"Priority: {task.priority.name}")
    print(f"Status: {task.status.value}")
    print(f"Due Date: {task.due_date or 'Not set'}")
    print(f"Created: {task.created_at}")
    print(f"Updated: {task.updated_at}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Task Planner CLI")
    parser.add_argument('--data-file', default='planner_data.json',
                       help='Path to data file (default: planner_data.json)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('-d', '--description', help='Task description')
    add_parser.add_argument('-p', '--priority', 
                           choices=['low', 'medium', 'high', 'urgent'],
                           help='Task priority')
    add_parser.add_argument('--due-date', help='Due date (YYYY-MM-DD)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-s', '--status', 
                            choices=['todo', 'in_progress', 'completed', 'cancelled'],
                            help='Filter by status')
    list_parser.add_argument('-p', '--priority',
                            choices=['low', 'medium', 'high', 'urgent'],
                            help='Filter by priority')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('-t', '--title', help='New title')
    update_parser.add_argument('-d', '--description', help='New description')
    update_parser.add_argument('-p', '--priority',
                              choices=['low', 'medium', 'high', 'urgent'],
                              help='New priority')
    update_parser.add_argument('-s', '--status',
                              choices=['todo', 'in_progress', 'completed', 'cancelled'],
                              help='New status')
    update_parser.add_argument('--due-date', help='New due date (YYYY-MM-DD)')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show task details')
    show_parser.add_argument('id', type=int, help='Task ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    planner = Planner(args.data_file)
    
    commands = {
        'add': cmd_add,
        'list': cmd_list,
        'update': cmd_update,
        'delete': cmd_delete,
        'show': cmd_show
    }
    
    commands[args.command](args, planner)


if __name__ == "__main__":
    main()
