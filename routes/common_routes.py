from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from utils.data_utils import *

common_bp = Blueprint('common', __name__)

@common_bp.route("/")
def index():
    """Main page"""
    dataset_loaded = current_dataset is not None
    return render_template("frontface.html", dataset_loaded=dataset_loaded)

@common_bp.route("/check_dataset_status")
def check_dataset_status():
    """API endpoint to check dataset status"""
    dataset_loaded = current_dataset is not None
    dataset_info = None
    
    if dataset_loaded:
        dataset_info = analyze_dataset(current_dataset)
    
    return jsonify({
        'loaded': dataset_loaded,
        'dataset_info': dataset_info
    })

@common_bp.route("/upload_dataset", methods=["POST"])
def upload_dataset():
    """Handle dataset uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be a CSV'})
        
        # Read and validate the dataset
        try:
            df = pd.read_csv(file.stream)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error reading CSV: {str(e)}'})
        
        # Validate dataset structure
        is_valid, validation_message = validate_dataset(df)
        if not is_valid:
            return jsonify({'success': False, 'error': validation_message})
        
        # Save the dataset
        df.to_csv(CURRENT_DATASET_PATH, index=False)
        
        # Reload dataset
        load_current_dataset()
        
        # Analyze dataset for response
        analysis_result = analyze_dataset(df)
        analysis_result['filename'] = secure_filename(file.filename)
        
        print(f"Dataset uploaded successfully: {file.filename}")
        
        return jsonify({
            'success': True,
            'message': 'Dataset uploaded successfully',
            'dataset_info': analysis_result
        })
        
    except Exception as e:
        print(f"Error uploading dataset: {e}")
        return jsonify({'success': False, 'error': str(e)})

@common_bp.route("/select_department", methods=["POST"])
def select_department():
    """Handle department selection"""
    department = request.form.get("department")
    if department == "BED":
        return redirect(url_for("bed.bed_filter"))
    elif department == "CED":
        return redirect(url_for("ced.ced_filter"))
    else:
        flash("Invalid department selected", "error")
        return redirect(url_for("common.index"))

@common_bp.route("/predict", methods=["POST"])
def predict():
    """Handle AJAX prediction requests for future enrollment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'})
        
        course = data.get('course', '').strip()
        year = data.get('year', '').strip()
        semester = data.get('semester', '').strip()
        
        if not all([course, year, semester]):
            return jsonify({'error': 'Missing required parameters'})
        
        # Make prediction
        prediction = predict_enrollment_fallback(course, year, semester)
        
        return jsonify({
            'prediction': prediction,
            'course': course,
            'year': year,
            'semester': semester
        })
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'})