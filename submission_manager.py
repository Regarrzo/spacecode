from dataclasses import dataclass
import datetime
import sqlite3

@dataclass
class Submission:
    user_id: int
    name: str
    date: datetime.date
    match_outcomes: list
    elo: float

class SubmissionManager:
    def __init__(self, db_path: str, submissions_path: str):
        self.db_path = db_path
        self.submissions_path = submissions_path
        self.conn = sqlite3.connect(db_path)
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, exc_type, exc, tb):
        # commit on success, rollback on exception, then close
        try:
            if self.conn:
                if exc_type:
                    self.conn.rollback()
                else:
                    self.conn.commit()
        finally:
            self.close()