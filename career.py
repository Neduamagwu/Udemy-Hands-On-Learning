from flask import Blueprint, render_template, request
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from datetime import datetime

# Initialize the s3 client
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION')  # Optional, depending on your region
)

# S3 bucket name
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

careers_blueprint = Blueprint('careers', __name__)

@careers_blueprint.route('', methods=['GET', 'POST'])
def careers():
    if request.method == 'POST':
        # Get the user inputs from the form
        user_name = request.form.get('name')
        user_experience = request.form.get('experience')
        user_position = request.form.get('position')
        user_ctc = request.form.get('ctc')
        user_phone_number = request.form.get('phone')
        user_expected_ctc = request.form.get('expected_ctc')

        # Handle file upload
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']

        if file.filename == '':
            return "No selected file", 400

        # Extract file extension and create the file name
        file_extension = os.path.splitext(file.filename)[1]  # Get the file extension
        file_name = f"{user_name}{file_extension}"  # Combine user name with the file extension

        # Get the current date in ddmmyyyy format
        current_date = datetime.now().strftime('%d%m%Y')

        # Create the S3 folder path based on the current date
        s3_folder = f"{current_date}/{file_name}"

        try:
            # Debugging - Check if we are hitting this point
            print(f"Attempting to upload file to: {s3_folder} in bucket: {S3_BUCKET_NAME}")
            
            # Upload file to S3 within the folder structure
            s3_client.upload_fileobj(file, S3_BUCKET_NAME, s3_folder)
            
            # Debugging - Check if the upload succeeded
            print(f"File uploaded successfully: {s3_folder}")

            # Return success message
            return f"File '{file_name}' uploaded successfully to S3 folder '{current_date}'"

        except NoCredentialsError:
            print("Error: Credentials not available")
            return "Credentials not available", 400
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"An error occurred: {str(e)}", 500
        
        # Render the careers page template
        return render_template('careers.html')