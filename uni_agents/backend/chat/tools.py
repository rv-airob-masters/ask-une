from typing import List, Dict
import datetime

# Fake course database for demo purposes
COURSE_CATALOG = [
    {"code": "CS320", "title": "Intro to Machine Learning", "area": "data science", "level": "undergrad", "why": "Intro to supervised learning"},
    {"code": "STAT210", "title": "Applied Statistics", "area": "data science", "level": "undergrad", "why": "Probability and stats foundations"},
    {"code": "CS250", "title": "Data Wrangling", "area": "data science", "level": "undergrad", "why": "ETL & preprocessing for ML"},
    {"code": "CS499", "title": "Data Science Capstone", "area": "data science", "level": "undergrad", "why": "Project-based course"},
    {"code": "HUM101", "title": "Creative Writing", "area": "humanities", "level": "undergrad", "why": "Writing skills and creativity"},
]

def course_lookup(topic: str = "general", level: str = "undergrad", limit: int = 4) -> Dict:
    topic = topic.lower()
    matches = [c for c in COURSE_CATALOG if topic in c["area"] and c["level"] == level]
    if not matches:
        # fallback: return top courses
        matches = COURSE_CATALOG[:limit]
    return {
        "recommendations": matches[:limit],
        "count": len(matches[:limit]),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

def academic_calendar(query: str = "") -> Dict:
    # Very simple static return for demonstration
    now = datetime.date.today()
    fall_start = datetime.date(now.year, 9, 1)
    exam_week = datetime.date(now.year, 12, 10)
    return {
        "query": query,
        "first_day_of_term": fall_start.isoformat(),
        "exam_week_start": exam_week.isoformat(),
        "notes": "Term dates are illustrative. Consult official calendar for authoritative dates."
    }
