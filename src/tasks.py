import os, random, datetime
from pathlib import Path

TOPIC_FILEPATH = Path("data/topics/")
MEMBER_FILEPATH = Path("data/members/")

def get_task_type_and_deadline():
    """Create a new task for a member with appropriate deadline based on task type."""

    task_deadline = None
    task = None
    task_type = random.randint(1, 2)

    if task_type == 1:
        
        task_deadline = datetime.date.today() + datetime.timedelta(days=14)
        task = "Roundup"
        
    else:
        
        task_deadline = datetime.date.today() + datetime.timedelta(days=14)
        task = "Blog"
 
    return (task, task_deadline)

def get_topic(task_name):
    
    if task_name.startswith('R'):
        
        f = open(TOPIC_FILEPATH / "roundup-topics.txt", 'r')
        f.seek(0)
            
        lines = [line for line in f.readlines() if line != '\n']
        topic_index = random.randint(0, len(lines) - 1)
        topic = lines[topic_index]
        lines.pop(topic_index)
        
        f.close()
        
        with open(TOPIC_FILEPATH / "roundup-topics.txt", 'w') as f:
            for line in lines:
                f.write(line)
        
        return topic
        
    else:
        
        f = open(TOPIC_FILEPATH / "blog-topics.txt", 'r')
        f.seek(0)
            
        lines = [line for line in f.readlines() if line != '\n']
        topic_index = random.randint(0, len(lines) - 1)
        topic = lines[topic_index]
        lines.pop(topic_index)
        
        f.close()
        
        with open(TOPIC_FILEPATH / "blog-topics.txt", 'w') as f:
            for line in lines:
                f.write(line)
        
        return topic
    
def add_topics(ttype, task):
    
    if ttype == 'r':
        
        f = open(TOPIC_FILEPATH / "roundup-topics.txt", 'a')
        f.write(task+'\n')
        f.close()
        
    elif ttype == 'b':
        
        f = open(TOPIC_FILEPATH / "blog-topics.txt", 'a')
        f.write(task+'\n')
        f.close()