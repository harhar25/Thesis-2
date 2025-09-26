import os
import pandas as pd
import numpy as np
from datetime import datetime

# Global dataset variable
current_dataset = None
CURRENT_DATASET_PATH = None

def init_dataset_path(upload_folder):
    """Initialize the dataset path"""
    global CURRENT_DATASET_PATH
    CURRENT_DATASET_PATH = os.path.join(upload_folder, "current_dataset.csv")

# Department configurations
DEPARTMENTS = {
    'BED': ['BSBA-FINANCIAL_MANAGEMENT', 'BSBA-MARKETING_MANAGEMENT'],
    'CED': ['BSIT', 'BSCS']
}

def load_current_dataset():
    """Load the current dataset into memory"""
    global current_dataset
    try:
        if os.path.exists(CURRENT_DATASET_PATH):
            current_dataset = pd.read_csv(CURRENT_DATASET_PATH)
            print(f"Current dataset loaded: {len(current_dataset)} records")
            return True
        current_dataset = None
        return False
    except Exception as e:
        print(f"Error loading current dataset: {e}")
        current_dataset = None
        return False

def analyze_dataset(df):
    """Analyze dataset and return statistics"""
    try:
        total_records = len(df)
        file_size = os.path.getsize(CURRENT_DATASET_PATH) if os.path.exists(CURRENT_DATASET_PATH) else 0
        
        # Student counts by department
        student_counts = {}
        program_counts = {}
        year_spans = {}
        
        for dept, courses in DEPARTMENTS.items():
            dept_students = 0
            dept_programs = 0
            dept_years = set()
            
            for course in courses:
                if 'Course' in df.columns:
                    course_data = df[df['Course'] == course]
                    if not course_data.empty:
                        # Count programs
                        dept_programs += 1
                        
                        # Count students
                        if 'total_enrollees' in df.columns:
                            dept_students += course_data['total_enrollees'].sum()
                        
                        # Collect unique years
                        if 'School_Year' in df.columns:
                            dept_years.update(course_data['School_Year'].unique())
            
            student_counts[dept] = int(dept_students)
            program_counts[dept] = dept_programs
            year_spans[dept] = len(dept_years)
        
        return {
            'filename': 'current_dataset.csv',
            'record_count': total_records,
            'file_size': f"{round(file_size / (1024 * 1024), 2)} MB",
            'student_counts': student_counts,
            'program_counts': program_counts,
            'year_spans': year_spans,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error analyzing dataset: {e}")
        return {
            'filename': 'current_dataset.csv',
            'record_count': len(df) if df is not None else 0,
            'file_size': "0 MB",
            'student_counts': {'BED': 0, 'CED': 0},
            'program_counts': {'BED': 0, 'CED': 0},
            'year_spans': {'BED': 0, 'CED': 0},
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def validate_dataset(df):
    """Validate uploaded dataset structure"""
    try:
        if not isinstance(df, pd.DataFrame):
            return False, "Invalid data format"
        
        # Basic required columns
        required_columns = ['School_Year', 'Semester', 'Course']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}"
        
        if len(df) == 0:
            return False, "Dataset is empty"
        
        # Check for enrollment columns
        enrollment_columns = ['1st_year_enrollees', '2nd_year_enrollees', '3rd_year_enrollees', '4th_year_enrollees', 'total_enrollees']
        missing_enrollment = [col for col in enrollment_columns if col not in df.columns]
        if missing_enrollment:
            print(f"Warning: Missing enrollment columns: {missing_enrollment}")
            # Add dummy enrollment columns if missing
            for col in missing_enrollment:
                df[col] = 0
        
        return True, "Dataset is valid"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def predict_enrollment_fallback(course, year, semester):
    """Simple prediction for future enrollment"""
    try:
        base_enrollment = 100
        
        if "BSBA" in course:
            base_enrollment = 120
        elif course in ["BSCS", "BSIT"]:
            base_enrollment = 80
        
        if semester == "1":
            base_enrollment *= 1.1
        else:
            base_enrollment *= 0.9
            
        variation = np.random.normal(0, 10)
        prediction = max(50, base_enrollment + variation)
        
        return round(prediction)
    except Exception as e:
        print(f"Prediction error: {e}")
        return 100

def get_historical_enrollment(course, year, semester):
    """Get historical enrollment data for specific course, year, and semester"""
    try:
        if current_dataset is not None:
            # Convert form semester to dataset format
            if semester == "1":
                semester_dataset = "1st"
            elif semester == "2":
                semester_dataset = "2nd"
            else:
                semester_dataset = semester
                
            record = current_dataset[
                (current_dataset['Course'] == course) &
                (current_dataset['School_Year'] == year) &
                (current_dataset['Semester'] == semester_dataset)
            ]
            
            if not record.empty:
                return {
                    'total_enrollment': int(record['total_enrollees'].iloc[0]),
                    'first_year': int(record['1st_year_enrollees'].iloc[0]),
                    'second_year': int(record['2nd_year_enrollees'].iloc[0]),
                    'third_year': int(record['3rd_year_enrollees'].iloc[0]),
                    'fourth_year': int(record['4th_year_enrollees'].iloc[0])
                }
        return None
    except Exception as e:
        print(f"Error getting historical enrollment: {e}")
        return None

def get_historical_trend(course, max_records=10):
    """Get historical trend data for charts - showing year levels over time"""
    try:
        if current_dataset is not None and 'Course' in current_dataset.columns:
            course_data = current_dataset[current_dataset['Course'] == course]
            if not course_data.empty:
                course_data = course_data.sort_values(['School_Year', 'Semester'])
                recent_data = course_data.tail(max_records)
                
                labels = []
                first_year_data = []
                second_year_data = []
                third_year_data = []
                fourth_year_data = []
                
                for _, row in recent_data.iterrows():
                    sem_display = "S1" if row['Semester'] == "1st" else "S2"
                    labels.append(f"{row['School_Year']} {sem_display}")
                    first_year_data.append(row['1st_year_enrollees'])
                    second_year_data.append(row['2nd_year_enrollees'])
                    third_year_data.append(row['3rd_year_enrollees'])
                    fourth_year_data.append(row['4th_year_enrollees'])
                
                return {
                    'labels': labels,
                    'first_year': first_year_data,
                    'second_year': second_year_data,
                    'third_year': third_year_data,
                    'fourth_year': fourth_year_data
                }
        return {
            'labels': [],
            'first_year': [],
            'second_year': [],
            'third_year': [],
            'fourth_year': []
        }
    except Exception as e:
        print(f"Error getting historical trend: {e}")
        return {
            'labels': [],
            'first_year': [],
            'second_year': [],
            'third_year': [],
            'fourth_year': []
        }