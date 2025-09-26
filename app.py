from flask import Flask
from routes.common_routes import common_bp
from routes.bed_routes import bed_bp
from routes.ced_routes import ced_bp
from utils.data_utils import init_dataset_path, load_current_dataset
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MODEL_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize dataset path
init_dataset_path(app.config['UPLOAD_FOLDER'])

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

# Register blueprints
app.register_blueprint(common_bp)
app.register_blueprint(bed_bp, url_prefix='/bed')
app.register_blueprint(ced_bp, url_prefix='/ced')

# Initialize the application
load_current_dataset()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)