import sqlite3
from pathlib import Path

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
        
        create_table()
        
        c = con.cursor()
        
        c.execute('''
                  
                  UPDATE members SET status = ?
                  WHERE uid = ?
                  
                  ''', (status, uid))