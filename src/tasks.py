import datetime
import random
import os
from pathlib import Path

MEMBER_FILEPATH = Path("data/members/")

def add_member(member: str):
    print(member)
    with open(f"data/members/{member}.txt", 'w', newline='') as df:
        pass

def create_task():
    """Create a new task for a member with appropriate deadline based on task type."""

    for member_file in os.listdir(MEMBER_FILEPATH):
        task_deadline = None
        task = None
        task_type = random.randint(1, 2)

        if task_type == 1:
            task_deadline = datetime.date.today() + datetime.timedelta(days=7)
            task = "Roundup"
        else:
            task_deadline = datetime.date.today() + datetime.timedelta(days=14)
            task = "Blog"

        with open(MEMBER_FILEPATH / member_file, 'a') as f:
            f.write(f"Current task: {task}, due by {task_deadline}\n")


def check_due(member_name: str):
    """Check how many days remain until the member's task deadline."""
    with open(MEMBER_FILEPATH / f"{member_name}.txt", 'r') as member_file:
        last_line = member_file.readlines()[-1]
        try:
            comma_position = last_line.index(',')
            due_date_str = last_line[comma_position + 9:].strip()
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
            days_remaining = (due_date - datetime.date.today()).days
            
            return days_remaining
        except:
            return "e"


def view_task(member_name: str):
    """View the current task for a member and days remaining."""
    with open(MEMBER_FILEPATH / f"{member_name}.txt", 'r') as member_file:
        try:
            last_line = member_file.readlines()[-1]
            comma_position = last_line.index(',')
            colon_position = last_line.index(':')
            task_name = last_line[colon_position + 1:comma_position].strip()
            
            return f"{task_name} due in {check_due(member_name)} days"
        except:
            return "No tasks for now"


def submit_task(member_name: str):
    """Mark a member's task as submitted."""
    with open(MEMBER_FILEPATH / f"{member_name}.txt", 'a') as member_file:
        member_file.write('\nsubmitted')


def overdue_task(member_name: str):
    """Mark a member's task as overdue."""
    with open(MEMBER_FILEPATH / f"{member_name}.txt", 'a') as member_file:
        member_file.write('\noverdue')


def check_submit(member_name: str):
    """Check if a member has submitted their task."""
    with open(MEMBER_FILEPATH / f"{member_name}.txt", 'r') as member_file:
        file_lines = member_file.readlines()
        if file_lines[-1].strip() == 'submitted':
            return True
        else:
            return False


def check_overdue(member_name: str):
    """Check if a member has 3 overdue tasks (3 strikes)."""
    with open(MEMBER_FILEPATH / f"{member_name}.txt", 'r') as member_file:
        file_lines = member_file.readlines()
        # Check if the last 3 entries are all 'overdue'
        if (len(file_lines) >= 5 and 
            file_lines[-1].strip() == 'overdue' and 
            file_lines[-3].strip() == 'overdue' and 
            file_lines[-5].strip() == 'overdue'):
            return True
        else:
            return False