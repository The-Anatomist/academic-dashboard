import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_mock_data():
    np.random.seed(42)
    random.seed(42)

    # 1. ACADEMIC DATA
    subjects = ["Math", "Kiswahili", "English", "Physics", "Chemistry", "Biology", "Community Service Learning", "ICT"]
    exams = [
        ("Year 1 Sem 1", "Midterm", 1), ("Year 1 Sem 1", "Finals", 2),
        ("Year 1 Sem 2", "Midterm", 3), ("Year 1 Sem 2", "Finals", 4),
        ("Year 2 Sem 1", "Midterm", 5), ("Year 2 Sem 1", "Finals", 6),
        ("Year 2 Sem 2", "Midterm", 7), ("Year 2 Sem 2", "Finals", 8)
    ]

    academic_records = []
    
    # Generate somewhat realistic trajectories (some subjects strong, some weak)
    base_skills = {sub: np.random.randint(60, 85) for sub in subjects}

    for term, exam_type, order in exams:
        for sub in subjects:
            # Add some random variation to the student's base skill for this exam
            mark = base_skills[sub] + np.random.randint(-10, 12)
            # Ensure marks stay between 0 and 100
            mark = max(0, min(100, mark))
            
            academic_records.append({
                "Exam_Order": order,
                "Semester": term,
                "Exam_Type": exam_type,
                "Exam_Name": f"{term} - {exam_type}",
                "Subject": sub,
                "Mark": mark
            })

    df_academic = pd.DataFrame(academic_records)
    df_academic.to_csv("academic_data.csv", index=False)
    print("Created academic_data.csv")

    # 2. BEHAVIOR DATA
    teachers = ["Mr. Omondi", "Ms. Wanjiku", "Mrs. Mutua", "Mr. Kiprono", "Dr. Kamau"]
    categories = ["Homework", "Participation", "Tardiness", "Behavior", "Project"]
    
    behavior_records = []
    start_date = datetime(2024, 9, 1)
    
    balance = 100 # Starting points
    for _ in range(40): # 40 point events over 2 years
        days_added = np.random.randint(1, 600)
        event_date = start_date + timedelta(days=days_added)
        teacher = random.choice(teachers)
        category = random.choice(categories)
        
        # Determine if positive or negative
        if category in ["Tardiness", "Behavior"]:
            points = np.random.randint(-5, -1)
            desc = "Rule infraction or late arrival."
        elif category == "Homework":
            points = np.random.choice([-2, 2, 5])
            desc = "Homework completion/missed."
        else:
            points = np.random.randint(2, 10)
            desc = "Outstanding contribution."
            
        balance += points
        
        behavior_records.append({
            "Date": event_date.strftime("%Y-%m-%d"),
            "Teacher": teacher,
            "Category": category,
            "Points": points,
            "Description": desc,
            "Running_Balance": balance
        })

    df_behavior = pd.DataFrame(behavior_records)
    df_behavior = df_behavior.sort_values(by="Date").reset_index(drop=True)
    
    # Recalculate running balance after sorting
    df_behavior["Running_Balance"] = 100 + df_behavior["Points"].cumsum()
    
    df_behavior.to_csv("behavior_data.csv", index=False)
    print("Created behavior_data.csv")

if __name__ == "__main__":
    generate_mock_data()