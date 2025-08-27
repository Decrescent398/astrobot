import sqlite3
from pathlib import Path
from src.tasks import *

db_path = Path("data/members.db")

def create_table():
    
    with sqlite3.connect(db_path) as con:
        
        c = con.cursor()
        
        c.execute('''
                
                CREATE TABLE IF NOT EXISTS members (
                
                uid BIGINT,
                status TINYINT,
                task_type TINYTEXT,
                task_topic TEXT,
                task_status TINYINT,
                due_date DATE
                    
                )
                
                ''')
        
        con.commit()

def add_member(uid):
    
    with sqlite3.connect(db_path) as con:
        
        create_table()
        
        c = con.cursor()
        
        c.execute('''
                
                INSERT IGNORE INTO members (uid)
                VALUES (?)
                
                ''', (uid,))
        
        con.commit()
        
def update_status(uid, status):
    
    with sqlite3.connect(db_path) as con:
        
        c = con.cursor()
        
        c.execute('''
                  
                  UPDATE members SET status = ?
                  WHERE uid = ?
                  
                  ''', (status, uid))
        
        con.commit()
        
def create_task():
    
    with sqlite3.connect(db_path) as con:
        
        c = con.cursor()
        
        c.execute("SELECT uid FROM members WHERE status = 1")
        rows = c.fetchall()
        
        for (member_id,) in rows:
            
            ttd = get_task_type_and_deadline()
            
            c.execute('''
                    
                    UPDATE members
                    SET task_type = ?,
                        due_date = ?,
                        task_topic = ?
                    WHERE uid = ? AND status = 1;
                    
                    ''',(ttd[0], ttd[1], get_topic(ttd[0]), member_id))
            
        con.commit()