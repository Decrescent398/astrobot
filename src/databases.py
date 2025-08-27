import sqlite3
from pathlib import Path

db_path = Path("data/members.db")

con = sqlite3.connect(db_path)
c = con.cursor()

c.execute('''
          
          CREATE TABLE members (
           
           uid BIGINT,
           status TINYINT,
           task_type TINYTEXT,
           task_topic TINYTEXT,
           task_status TINYINT,
           due_date DATE,
              
          )
          
          ''')

con.commit()
con.close()