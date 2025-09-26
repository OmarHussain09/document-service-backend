from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import pytz

# Define the IST timezone
ist_timezone = pytz.timezone('Asia/Kolkata')

# Get the current time in IST
# current_time_ist = datetime.now(ist_timezone)


db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(1024), nullable=False)
    ai_summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(ist_timezone))
    updated_at = db.Column(db.DateTime, default=datetime.now(ist_timezone), onupdate=datetime.now(ist_timezone))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_url": self.file_url,
            "ai_summary": self.ai_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
