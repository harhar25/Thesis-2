from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from utils.data_utils import *

ced_bp = Blueprint('ced', __name__)

@ced_bp.route("/ced_filter")
def ced_filter():
    """CED filter page"""
    return render_template("CEDfilter.html")

@ced_bp.route("/predict-enrollment", methods=["POST"])
def predict_enrollment():
    """Prediction endpoint for CED page"""
    try:
        data = request.get_json()
        course = data.get('course', '').strip()
        year = data.get('year', '').strip()
        semester = data.get('semester', '').strip()
        
        if not all([course, year, semester]):
            return jsonify({'error': 'Missing required parameters'})
        
        prediction = predict_enrollment_fallback(course, year, semester)
        
        return jsonify({
            'prediction': prediction,
            'course': course,
            'year': year,
            'semester': semester
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@ced_bp.route("/forecast", methods=["POST"])
def forecast():
    """Handle CED historical data visualization"""
    return process_forecast_request()

@ced_bp.route("/forecast_history", methods=['POST'])
def forecast_history():
    """Alias for forecast endpoint for CED page"""
    return process_forecast_request()

def process_forecast_request():
    """Common forecast processing for CED department"""
    if current_dataset is None:
        flash("Please upload a dataset to view historical data", "error")
        return redirect(url_for("ced.ced_filter"))
    
    course = request.form.get("course", "").strip()
    year = request.form.get("year", "").strip()
    semester = request.form.get("semester", "").strip()

    if not course or not year or not semester:
        flash("Please complete all required fields", "error")
        return redirect(url_for("ced.ced_filter"))

    semester_text = "1st" if semester == "1" else "2nd"
    
    historical_enrollment = get_historical_enrollment(course, year, semester)
    
    if historical_enrollment is None:
        flash(f"No historical data found for {course} in {year} ({semester_text} Semester)", "error")
        return redirect(url_for("ced.ced_filter"))
    
    historical_trend = get_historical_trend(course)
    
    return render_template(
        "CED_result.html",
        course=course,
        year=year,
        semester=semester_text,
        total_enrollment=historical_enrollment['total_enrollment'],
        year_levels={
            'first_year': historical_enrollment['first_year'],
            'second_year': historical_enrollment['second_year'],
            'third_year': historical_enrollment['third_year'],
            'fourth_year': historical_enrollment['fourth_year']
        },
        historical_trend=historical_trend,
        dataset_info=analyze_dataset(current_dataset) if current_dataset is not None else None
    )