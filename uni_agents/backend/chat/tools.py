from typing import List, Dict
import datetime

# Fake course database for demo purposes
COURSE_CATALOG = [
    # Data Science Courses
    {"code": "CS320", "title": "Intro to Machine Learning", "area": "data science", "level": "undergrad", "why": "Intro to supervised learning"},
    {"code": "STAT210", "title": "Applied Statistics", "area": "data science", "level": "undergrad", "why": "Probability and stats foundations"},
    {"code": "CS250", "title": "Data Wrangling", "area": "data science", "level": "undergrad", "why": "ETL & preprocessing for ML"},
    {"code": "CS499", "title": "Data Science Capstone", "area": "data science", "level": "undergrad", "why": "Project-based course"},
    
    # Computer Science Courses
    {"code": "CS101", "title": "Introduction to Programming", "area": "computer science", "level": "undergrad", "why": "Programming fundamentals"},
    {"code": "CS201", "title": "Data Structures", "area": "computer science", "level": "undergrad", "why": "Core CS concepts"},
    {"code": "CS301", "title": "Algorithms", "area": "computer science", "level": "undergrad", "why": "Algorithm design and analysis"},
    {"code": "CS401", "title": "Software Engineering", "area": "computer science", "level": "undergrad", "why": "Large-scale software development"},
    
    # Other Courses
    {"code": "HUM101", "title": "Creative Writing", "area": "humanities", "level": "undergrad", "why": "Writing skills and creativity"},
    {"code": "MATH201", "title": "Calculus II", "area": "mathematics", "level": "undergrad", "why": "Advanced calculus concepts"},
    {"code": "PHYS101", "title": "General Physics", "area": "physics", "level": "undergrad", "why": "Physics fundamentals"},
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

# Course schedule data with start dates, exam dates, and class times
COURSE_SCHEDULES = {
    # Data Science Courses
    "CS320": {
        "start_date": "2024-09-03",
        "end_date": "2024-12-15", 
        "midterm_exam": "2024-10-15",
        "final_exam": "2024-12-12",
        "class_times": "MWF 10:00-11:00 AM",
        "location": "Science Building 201"
    },
    "STAT210": {
        "start_date": "2024-09-03",
        "end_date": "2024-12-15",
        "midterm_exam": "2024-10-18",
        "final_exam": "2024-12-14",
        "class_times": "TTh 2:00-3:30 PM",
        "location": "Math Building 105"
    },
    "CS250": {
        "start_date": "2024-09-05",
        "end_date": "2024-12-17",
        "midterm_exam": "2024-10-20",
        "final_exam": "2024-12-16",
        "class_times": "MW 1:00-2:30 PM",
        "location": "Computer Lab 301"
    },
    "CS499": {
        "start_date": "2024-09-03",
        "end_date": "2024-12-15",
        "midterm_presentation": "2024-11-01",
        "final_presentation": "2024-12-10",
        "class_times": "F 3:00-5:00 PM",
        "location": "Conference Room A"
    },
    
    # Computer Science Courses
    "CS101": {
        "start_date": "2024-09-03",
        "end_date": "2024-12-15",
        "midterm_exam": "2024-10-12",
        "final_exam": "2024-12-11",
        "class_times": "MWF 9:00-10:00 AM",
        "location": "Computer Lab 101"
    },
    "CS201": {
        "start_date": "2024-09-03",
        "end_date": "2024-12-15",
        "midterm_exam": "2024-10-17",
        "final_exam": "2024-12-13",
        "class_times": "TTh 11:00-12:30 PM",
        "location": "Computer Lab 201"
    },

}

def academic_calendar(query: str = "") -> Dict:
    """
    Enhanced academic calendar with course-specific schedules and exam dates.
    Supports queries for specific courses, general semester dates, or exam schedules.
    """
    query_lower = query.lower()
    now = datetime.date.today()
    current_year = now.year
    
    # General semester dates
    semester_info = {
        "fall_semester_start": f"{current_year}-09-03",
        "fall_semester_end": f"{current_year}-12-15",
        "spring_semester_start": f"{current_year + 1}-01-15",
        "spring_semester_end": f"{current_year + 1}-05-10",
        "final_exams_week": f"{current_year}-12-10 to {current_year}-12-16",
        "midterm_exams_week": f"{current_year}-10-15 to {current_year}-10-22",
        "registration_deadline": f"{current_year}-08-25",
        "add_drop_deadline": f"{current_year}-09-15"
    }
    
    # Check if query is asking about a specific course
    course_code = None
    for code in COURSE_SCHEDULES.keys():
        if code.lower() in query_lower:
            course_code = code
            break
    
    if course_code and course_code in COURSE_SCHEDULES:
        # Return specific course schedule
        course_schedule = COURSE_SCHEDULES[course_code]
        course_info = next((c for c in COURSE_CATALOG if c["code"] == course_code), None)
        
        return {
            "query": query,
            "course_code": course_code,
            "course_title": course_info["title"] if course_info else "Unknown Course",
            "schedule": course_schedule,
            "semester_dates": semester_info,
            "notes": f"Schedule for {course_code}. All dates are subject to change."
        }
    
    # Check for specific query types
    if any(word in query_lower for word in ['exam', 'final', 'midterm']):
        # Return exam-focused information
        exam_schedule = {}
        for code, schedule in COURSE_SCHEDULES.items():
            exam_info = {}
            if 'midterm_exam' in schedule:
                exam_info['midterm'] = schedule['midterm_exam']
            if 'final_exam' in schedule:
                exam_info['final'] = schedule['final_exam']
            if 'midterm_presentation' in schedule:
                exam_info['midterm_presentation'] = schedule['midterm_presentation']
            if 'final_presentation' in schedule:
                exam_info['final_presentation'] = schedule['final_presentation']
            
            if exam_info:
                exam_schedule[code] = exam_info
        
        return {
            "query": query,
            "exam_schedules": exam_schedule,
            "general_exam_periods": {
                "midterm_week": semester_info["midterm_exams_week"],
                "final_week": semester_info["final_exams_week"]
            },
            "notes": "Exam dates for all courses. Check with instructors for room assignments."
        }
    
    elif any(word in query_lower for word in ['start', 'begin', 'class']):
        # Return course start dates
        start_dates = {code: schedule["start_date"] for code, schedule in COURSE_SCHEDULES.items()}
        
        return {
            "query": query,
            "course_start_dates": start_dates,
            "semester_start": semester_info["fall_semester_start"],
            "notes": "Course start dates may vary. Most courses begin with the semester."
        }
    
    else:
        # Return general semester information
        return {
            "query": query,
            "semester_dates": semester_info,
            "total_courses_available": len(COURSE_CATALOG),
            "notes": "General academic calendar. Use specific course codes for detailed schedules."
        }