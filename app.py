from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from dars_scraper import parse_dars_pdf  # Assuming this parses the PDF and retrieves courses
import align  # Assuming align contains the align() function to process course data

app = Flask(__name__)

# Route for the home page to upload a PDF
@app.route('/')
def index():
    return render_template('index.html')

# Process the PDF upload and align courses
@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    # Check if the PDF is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Save the file to a temporary location
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # Parse completed courses from PDF
        completed_courses = parse_dars_pdf(file_path)
        
        # Align courses and prepare results
        alignment_results = align.align(completed_courses)
        
        # Sorting alignment_results by score (third element in each tuple)
        sorted_alignment_results = sorted(alignment_results, key=lambda x: x[2], reverse=True)  # Sorting by score, descending order
        
        # Pass the sorted alignment results to the template
        return render_template('results.html', alignment_results=sorted_alignment_results, completed_courses=completed_courses)

    return jsonify({"error": "Invalid file format"}), 400


# Helper function to check file extension
def allowed_file(filename):
    allowed_extensions = {'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


if __name__ == "__main__":
    # Create the uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Run the Flask application
    app.run(debug=True, port=8080)
