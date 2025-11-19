"""
Scheduler for distributing subjects across a semester based on lecturer availability.

This module implements a scheduling system that:
- Manages up to 5 student groups, 20 lecturers, 15 subjects, and 10 rooms
- Prioritizes 5 high-importance lecturers
- Uses availability calendars to distribute subjects
- Assigns half-day blocks (morning/afternoon) for each subject
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Optional, Tuple
from datetime import date, timedelta


class TimeSlot(Enum):
    """Represents a half-day time slot."""
    MORNING = "morning"
    AFTERNOON = "afternoon"


@dataclass
class Block:
    """Represents a half-day teaching block."""
    date: date
    time_slot: TimeSlot
    
    def __hash__(self):
        return hash((self.date, self.time_slot))
    
    def __eq__(self, other):
        if not isinstance(other, Block):
            return False
        return self.date == other.date and self.time_slot == other.time_slot


@dataclass
class Lecturer:
    """Represents a lecturer with their teaching subject and availability."""
    id: int
    name: str
    subject_id: int
    is_high_importance: bool = False
    available_blocks: Set[Block] = field(default_factory=set)
    
    def is_available(self, block: Block) -> bool:
        """Check if lecturer is available for a specific block."""
        return block in self.available_blocks


@dataclass
class Subject:
    """Represents a subject with required teaching blocks."""
    id: int
    name: str
    required_blocks: int
    lecturer_id: int


@dataclass
class Room:
    """Represents a theory room available for scheduling."""
    id: int
    name: str


@dataclass
class ScheduledBlock:
    """Represents a scheduled teaching block."""
    subject: Subject
    lecturer: Lecturer
    room: Room
    block: Block
    student_group: int


class Scheduler:
    """
    Scheduler for distributing subjects across a semester.
    
    Prioritizes high-importance lecturers and uses availability calendars
    to schedule all required blocks for each subject.
    """
    
    def __init__(
        self,
        lecturers: List[Lecturer],
        subjects: List[Subject],
        rooms: List[Room],
        semester_start: date,
        semester_end: date,
        student_groups: int = 5
    ):
        """
        Initialize the scheduler.
        
        Args:
            lecturers: List of lecturers (max 20)
            subjects: List of subjects (max 15)
            rooms: List of rooms (max 10)
            semester_start: Start date of the semester
            semester_end: End date of the semester
            student_groups: Number of student groups (max 5)
        """
        self.lecturers = {lecturer.id: lecturer for lecturer in lecturers}
        self.subjects = {subject.id: subject for subject in subjects}
        self.rooms = rooms
        self.semester_start = semester_start
        self.semester_end = semester_end
        self.student_groups = min(student_groups, 5)
        
        # Track scheduled blocks to avoid conflicts
        self.scheduled_blocks: List[ScheduledBlock] = []
        self.room_occupancy: Dict[Tuple[Block, int], Set[int]] = {}  # (block, room_id) -> set of group_ids
        self.lecturer_schedule: Dict[Tuple[Block, int], bool] = {}  # (block, lecturer_id) -> is_busy
        
    def _get_all_blocks(self) -> List[Block]:
        """Generate all possible blocks in the semester."""
        blocks = []
        current_date = self.semester_start
        
        while current_date <= self.semester_end:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                blocks.append(Block(current_date, TimeSlot.MORNING))
                blocks.append(Block(current_date, TimeSlot.AFTERNOON))
            current_date += timedelta(days=1)
        
        return blocks
    
    def _is_room_available(self, room: Room, block: Block, group: int) -> bool:
        """Check if a room is available for a specific block and group."""
        key = (block, room.id)
        if key not in self.room_occupancy:
            return True
        return group not in self.room_occupancy[key]
    
    def _is_lecturer_available(self, lecturer: Lecturer, block: Block) -> bool:
        """Check if a lecturer is available and not already scheduled."""
        if not lecturer.is_available(block):
            return False
        
        key = (block, lecturer.id)
        return not self.lecturer_schedule.get(key, False)
    
    def _reserve_slot(self, lecturer: Lecturer, room: Room, block: Block, group: int):
        """Reserve a time slot for a lecturer, room, and group."""
        room_key = (block, room.id)
        if room_key not in self.room_occupancy:
            self.room_occupancy[room_key] = set()
        self.room_occupancy[room_key].add(group)
        
        lecturer_key = (block, lecturer.id)
        self.lecturer_schedule[lecturer_key] = True
    
    def schedule(self) -> List[ScheduledBlock]:
        """
        Create a schedule for all subjects prioritizing high-importance lecturers.
        
        Returns:
            List of scheduled blocks
        """
        # Get high-importance lecturers and their subjects
        high_importance_lecturers = [
            lecturer for lecturer in self.lecturers.values()
            if lecturer.is_high_importance
        ]
        
        # Sort by high importance first
        sorted_lecturers = sorted(
            self.lecturers.values(),
            key=lambda l: (not l.is_high_importance, l.id)
        )
        
        # Get all possible blocks
        all_blocks = self._get_all_blocks()
        
        # Schedule each lecturer's subject
        for lecturer in sorted_lecturers:
            subject = self.subjects.get(lecturer.subject_id)
            if not subject:
                continue
            
            # Schedule blocks for each student group
            for group in range(1, self.student_groups + 1):
                blocks_scheduled = 0
                
                # Try to schedule all required blocks for this subject
                for block in all_blocks:
                    if blocks_scheduled >= subject.required_blocks:
                        break
                    
                    # Check if lecturer is available
                    if not self._is_lecturer_available(lecturer, block):
                        continue
                    
                    # Find an available room
                    room_found = None
                    for room in self.rooms:
                        if self._is_room_available(room, block, group):
                            room_found = room
                            break
                    
                    if room_found:
                        # Schedule the block
                        scheduled_block = ScheduledBlock(
                            subject=subject,
                            lecturer=lecturer,
                            room=room_found,
                            block=block,
                            student_group=group
                        )
                        
                        self.scheduled_blocks.append(scheduled_block)
                        self._reserve_slot(lecturer, room_found, block, group)
                        blocks_scheduled += 1
        
        return self.scheduled_blocks
    
    def get_schedule_summary(self) -> Dict[str, any]:
        """
        Get a summary of the generated schedule.
        
        Returns:
            Dictionary with schedule statistics
        """
        total_blocks = len(self.scheduled_blocks)
        subjects_scheduled = len(set(sb.subject.id for sb in self.scheduled_blocks))
        lecturers_used = len(set(sb.lecturer.id for sb in self.scheduled_blocks))
        rooms_used = len(set(sb.room.id for sb in self.scheduled_blocks))
        
        # Count blocks per subject
        blocks_per_subject = {}
        for sb in self.scheduled_blocks:
            key = sb.subject.name
            blocks_per_subject[key] = blocks_per_subject.get(key, 0) + 1
        
        return {
            "total_scheduled_blocks": total_blocks,
            "subjects_scheduled": subjects_scheduled,
            "lecturers_used": lecturers_used,
            "rooms_used": rooms_used,
            "blocks_per_subject": blocks_per_subject
        }
    
    def print_schedule(self):
        """Print the schedule in a readable format."""
        if not self.scheduled_blocks:
            print("No blocks scheduled yet. Run schedule() first.")
            return
        
        # Sort by date and time
        sorted_schedule = sorted(
            self.scheduled_blocks,
            key=lambda sb: (sb.block.date, sb.block.time_slot.value, sb.student_group)
        )
        
        print("\n" + "="*80)
        print("SCHEDULE SUMMARY")
        print("="*80)
        
        summary = self.get_schedule_summary()
        print(f"\nTotal Scheduled Blocks: {summary['total_scheduled_blocks']}")
        print(f"Subjects Scheduled: {summary['subjects_scheduled']}")
        print(f"Lecturers Used: {summary['lecturers_used']}")
        print(f"Rooms Used: {summary['rooms_used']}")
        
        print("\n" + "="*80)
        print("DETAILED SCHEDULE")
        print("="*80)
        
        current_date = None
        for sb in sorted_schedule:
            if current_date != sb.block.date:
                current_date = sb.block.date
                print(f"\n{current_date.strftime('%Y-%m-%d (%A)')}")
                print("-" * 80)
            
            importance = " [HIGH IMPORTANCE]" if sb.lecturer.is_high_importance else ""
            print(f"  {sb.block.time_slot.value.upper():10} | "
                  f"Group {sb.student_group} | "
                  f"{sb.subject.name:20} | "
                  f"{sb.lecturer.name:20}{importance} | "
                  f"Room {sb.room.name}")
