"""
Tests for the scheduler module.
"""

import unittest
from datetime import date, timedelta
from scheduler import (
    Lecturer, Subject, Room, Block, TimeSlot, Scheduler, ScheduledBlock
)


class TestBlock(unittest.TestCase):
    """Test Block class."""
    
    def test_block_creation(self):
        """Test creating a block."""
        block = Block(date(2024, 9, 1), TimeSlot.MORNING)
        self.assertEqual(block.date, date(2024, 9, 1))
        self.assertEqual(block.time_slot, TimeSlot.MORNING)
    
    def test_block_equality(self):
        """Test block equality."""
        block1 = Block(date(2024, 9, 1), TimeSlot.MORNING)
        block2 = Block(date(2024, 9, 1), TimeSlot.MORNING)
        block3 = Block(date(2024, 9, 1), TimeSlot.AFTERNOON)
        
        self.assertEqual(block1, block2)
        self.assertNotEqual(block1, block3)
    
    def test_block_hashable(self):
        """Test that blocks can be used in sets."""
        block1 = Block(date(2024, 9, 1), TimeSlot.MORNING)
        block2 = Block(date(2024, 9, 1), TimeSlot.MORNING)
        block3 = Block(date(2024, 9, 1), TimeSlot.AFTERNOON)
        
        block_set = {block1, block2, block3}
        self.assertEqual(len(block_set), 2)


class TestLecturer(unittest.TestCase):
    """Test Lecturer class."""
    
    def test_lecturer_creation(self):
        """Test creating a lecturer."""
        lecturer = Lecturer(
            id=1,
            name="Dr. Smith",
            subject_id=1,
            is_high_importance=True
        )
        self.assertEqual(lecturer.id, 1)
        self.assertEqual(lecturer.name, "Dr. Smith")
        self.assertTrue(lecturer.is_high_importance)
    
    def test_lecturer_availability(self):
        """Test lecturer availability checking."""
        block1 = Block(date(2024, 9, 1), TimeSlot.MORNING)
        block2 = Block(date(2024, 9, 2), TimeSlot.MORNING)
        
        lecturer = Lecturer(
            id=1,
            name="Dr. Smith",
            subject_id=1,
            available_blocks={block1}
        )
        
        self.assertTrue(lecturer.is_available(block1))
        self.assertFalse(lecturer.is_available(block2))


class TestScheduler(unittest.TestCase):
    """Test Scheduler class."""
    
    def setUp(self):
        """Set up test data."""
        self.semester_start = date(2024, 9, 2)  # Monday
        self.semester_end = date(2024, 9, 13)    # Friday (2 weeks)
        
        # Create availability for the entire period
        self.all_blocks = set()
        current_date = self.semester_start
        while current_date <= self.semester_end:
            if current_date.weekday() < 5:  # Weekdays only
                self.all_blocks.add(Block(current_date, TimeSlot.MORNING))
                self.all_blocks.add(Block(current_date, TimeSlot.AFTERNOON))
            current_date += timedelta(days=1)
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        lecturers = [
            Lecturer(id=1, name="Dr. Smith", subject_id=1, is_high_importance=True)
        ]
        subjects = [
            Subject(id=1, name="Mathematics", required_blocks=5, lecturer_id=1)
        ]
        rooms = [Room(id=1, name="Room A")]
        
        scheduler = Scheduler(
            lecturers=lecturers,
            subjects=subjects,
            rooms=rooms,
            semester_start=self.semester_start,
            semester_end=self.semester_end,
            student_groups=2
        )
        
        self.assertEqual(len(scheduler.lecturers), 1)
        self.assertEqual(len(scheduler.subjects), 1)
        self.assertEqual(len(scheduler.rooms), 1)
        self.assertEqual(scheduler.student_groups, 2)
    
    def test_get_all_blocks(self):
        """Test generation of all semester blocks."""
        scheduler = Scheduler(
            lecturers=[],
            subjects=[],
            rooms=[],
            semester_start=self.semester_start,
            semester_end=self.semester_end
        )
        
        blocks = scheduler._get_all_blocks()
        
        # 2 weeks * 5 weekdays * 2 slots per day = 20 blocks
        self.assertEqual(len(blocks), 20)
        
        # Verify no weekend blocks
        for block in blocks:
            self.assertLess(block.date.weekday(), 5)
    
    def test_simple_scheduling(self):
        """Test simple scheduling scenario."""
        lecturer = Lecturer(
            id=1,
            name="Dr. Smith",
            subject_id=1,
            is_high_importance=True,
            available_blocks=self.all_blocks
        )
        
        subject = Subject(
            id=1,
            name="Mathematics",
            required_blocks=3,
            lecturer_id=1
        )
        
        rooms = [Room(id=1, name="Room A")]
        
        scheduler = Scheduler(
            lecturers=[lecturer],
            subjects=[subject],
            rooms=rooms,
            semester_start=self.semester_start,
            semester_end=self.semester_end,
            student_groups=2
        )
        
        scheduled = scheduler.schedule()
        
        # Should schedule 3 blocks for 2 groups = 6 total blocks
        self.assertEqual(len(scheduled), 6)
        
        # Verify all scheduled blocks are valid
        for sb in scheduled:
            self.assertEqual(sb.subject.id, 1)
            self.assertEqual(sb.lecturer.id, 1)
            self.assertIn(sb.student_group, [1, 2])
    
    def test_high_importance_priority(self):
        """Test that high importance lecturers are scheduled first."""
        # Create two lecturers with overlapping availability
        lecturer1 = Lecturer(
            id=1,
            name="Dr. Smith",
            subject_id=1,
            is_high_importance=True,
            available_blocks=self.all_blocks
        )
        
        lecturer2 = Lecturer(
            id=2,
            name="Dr. Jones",
            subject_id=2,
            is_high_importance=False,
            available_blocks=self.all_blocks
        )
        
        subject1 = Subject(id=1, name="Mathematics", required_blocks=10, lecturer_id=1)
        subject2 = Subject(id=2, name="Physics", required_blocks=10, lecturer_id=2)
        
        rooms = [Room(id=1, name="Room A")]
        
        scheduler = Scheduler(
            lecturers=[lecturer1, lecturer2],
            subjects=[subject1, subject2],
            rooms=rooms,
            semester_start=self.semester_start,
            semester_end=self.semester_end,
            student_groups=1
        )
        
        scheduled = scheduler.schedule()
        
        # High importance lecturer should get more slots
        lecturer1_blocks = [sb for sb in scheduled if sb.lecturer.id == 1]
        lecturer2_blocks = [sb for sb in scheduled if sb.lecturer.id == 2]
        
        # Lecturer 1 (high importance) should have scheduled all 10 blocks
        self.assertEqual(len(lecturer1_blocks), 10)
    
    def test_room_conflict_avoidance(self):
        """Test that room conflicts are avoided."""
        lecturer = Lecturer(
            id=1,
            name="Dr. Smith",
            subject_id=1,
            is_high_importance=True,
            available_blocks=self.all_blocks
        )
        
        subject = Subject(id=1, name="Mathematics", required_blocks=5, lecturer_id=1)
        rooms = [Room(id=1, name="Room A")]
        
        scheduler = Scheduler(
            lecturers=[lecturer],
            subjects=[subject],
            rooms=rooms,
            semester_start=self.semester_start,
            semester_end=self.semester_end,
            student_groups=3
        )
        
        scheduled = scheduler.schedule()
        
        # Check that no room has conflicts (same room, same block, same group)
        room_usage = {}
        for sb in scheduled:
            key = (sb.block, sb.room.id, sb.student_group)
            self.assertNotIn(key, room_usage, "Room conflict detected!")
            room_usage[key] = True
    
    def test_lecturer_conflict_avoidance(self):
        """Test that lecturer conflicts are avoided."""
        lecturer = Lecturer(
            id=1,
            name="Dr. Smith",
            subject_id=1,
            is_high_importance=True,
            available_blocks=self.all_blocks
        )
        
        subject = Subject(id=1, name="Mathematics", required_blocks=5, lecturer_id=1)
        rooms = [Room(id=1, name="Room A"), Room(id=2, name="Room B")]
        
        scheduler = Scheduler(
            lecturers=[lecturer],
            subjects=[subject],
            rooms=rooms,
            semester_start=self.semester_start,
            semester_end=self.semester_end,
            student_groups=3
        )
        
        scheduled = scheduler.schedule()
        
        # Check that lecturer doesn't have double bookings
        lecturer_usage = {}
        for sb in scheduled:
            key = (sb.block, sb.lecturer.id)
            self.assertNotIn(key, lecturer_usage, 
                           "Lecturer double-booked!")
            lecturer_usage[key] = True
    
    def test_schedule_summary(self):
        """Test schedule summary generation."""
        lecturer = Lecturer(
            id=1,
            name="Dr. Smith",
            subject_id=1,
            is_high_importance=True,
            available_blocks=self.all_blocks
        )
        
        subject = Subject(id=1, name="Mathematics", required_blocks=3, lecturer_id=1)
        rooms = [Room(id=1, name="Room A")]
        
        scheduler = Scheduler(
            lecturers=[lecturer],
            subjects=[subject],
            rooms=rooms,
            semester_start=self.semester_start,
            semester_end=self.semester_end,
            student_groups=2
        )
        
        scheduler.schedule()
        summary = scheduler.get_schedule_summary()
        
        self.assertEqual(summary["total_scheduled_blocks"], 6)
        self.assertEqual(summary["subjects_scheduled"], 1)
        self.assertEqual(summary["lecturers_used"], 1)
        self.assertEqual(summary["rooms_used"], 1)
        self.assertIn("Mathematics", summary["blocks_per_subject"])


if __name__ == "__main__":
    unittest.main()
