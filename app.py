from flask import Flask, render_template_string, request
from datetime import datetime
import socket
import uuid
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)

# S3 Configuration - Replace with your actual bucket details
S3_BUCKET = 'your-polypop-bucket-name'
S3_REGION = 'your-bucket-region'  # e.g., 'us-west-2'

# Initialize S3 client - Will use EC2 IAM role automatically
s3_client = boto3.client('s3', region_name=S3_REGION)

@app.route('/')
def home():
    # Get system information
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    system_id = str(uuid.uuid4())
    private_ip = socket.gethostbyname(socket.gethostname())
    
    # HTML template
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Polypop Nigeria Limited</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; background-color: #f0f0f0; }
        h1 { color: #4CAF50; margin-bottom: 20px; }
        p { color: #333; font-size: 18px; }
        .services { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px; }
        .service { padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }
        .service h3 { color: #4CAF50; }
        footer { margin-top: 50px; font-size: 14px; color: #777; }
        .system-info { position: fixed; bottom: 20px; right: 20px; font-size: 14px; color: #333; 
                      background-color: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }
        .nav-link { position: absolute; top: 20px; left: 20px; font-size: 16px; color: #4CAF50; text-decoration: none; }
        .nav-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <a href="/careers" class="nav-link">Careers</a>
    <h1>Welcome to Polypop Nigeria Limited</h1>
    <p>We specialize in providing innovative solutions to make your business thrive.</p>

    <div class="services">
        <div class="service">
            <h3>Web Development</h3>
            <p>Building responsive and functional websites.</p>
        </div>
        <div class="service">
            <h3>Cloud Solutions</h3>
            <p>Harnessing the power of cloud computing.</p>
        </div>
        <div class="service">
            <h3>Mobile Apps</h3>
            <p>Creating user-friendly mobile applications.</p>
        </div>
    </div>

    <footer>
        <p>From Polypop Nigeria Limited</p>
    </footer>

    <div class="system-info">
        <p><strong>Current Date:</strong> {{ current_date }}</p>
        <p><strong>System ID:</strong> {{ system_id }}</p>
        <p><strong>Private IP:</strong> {{ private_ip }}</p>
    </div>
</body>
</html>
'''
    return render_template_string(html_content, 
                               current_date=current_date,
                               system_id=system_id,
                               private_ip=private_ip)

def upload_to_s3(file, bucket_name, object_name):
    """Upload file to S3 with proper error handling and status codes"""
    try:
        s3_client.upload_fileobj(
            file,
            bucket_name,
            object_name,
            ExtraArgs={
                'ACL': 'private',
                'ContentType': file.content_type,
                'Metadata': {
                    'uploaded-by': 'polypop-careers',
                    'applicant': request.form.get('name', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            }
        )
        return True, "Upload successful", 200
    except NoCredentialsError:
        return False, "AWS credentials not available", 500
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            return False, "Access denied to S3 bucket", 403
        return False, f"AWS error: {e.response['Error']['Message']}", 500
    except Exception as e:
        return False, f"Upload error: {str(e)}", 500

@app.route('/careers', methods=['GET', 'POST'])
def careers():
    if request.method == 'POST':
        # Validate required fields
        required_fields = ['name', 'phone', 'experience', 'position', 'salary', 'expected_salary']
        missing_fields = [field for field in required_fields if field not in request.form or not request.form[field].strip()]
        
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}", 400

        # Validate file upload
        if 'file' not in request.files:
            return "No resume file uploaded", 400
            
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400

        # Process upload
        try:
            filename = f"careers/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
            success, message, status = upload_to_s3(file, S3_BUCKET, filename)
            
            if not success:
                return message, status
                
            # Success response
            response_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Application Submitted</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
        h1 {{ color: #4CAF50; }}
        .success {{ color: #4CAF50; margin: 20px 0; }}
        a {{ color: #4CAF50; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Application Submitted Successfully!</h1>
    <div class="success">{message}</div>
    <p>Thank you, {request.form['name']}!</p>
    <p>We've received your application for the {request.form['position']} position.</p>
    <a href="/">Return to Home Page</a>
</body>
</html>
'''
            return response_html, 200
            
        except Exception as e:
            return f"Error processing application: {str(e)}", 500

    # GET request - show form
    careers_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Careers - Polypop Nigeria Limited</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; background-color: #f8f8f8; }
        h1 { color: #4CAF50; }
        .upload-form { margin: 30px auto; background-color: #fff; padding: 30px; 
                      border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
                      max-width: 600px; text-align: left; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-weight: bold; margin-bottom: 5px; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background-color: #4CAF50; color: white; border: none; padding: 12px 20px; 
               border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }
        button:hover { background-color: #45a049; }
        .nav-link { position: absolute; top: 20px; left: 20px; color: #4CAF50; text-decoration: none; }
        .nav-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <a href="/" class="nav-link">← Home</a>
    <h1>Join Our Team</h1>
    <p>Complete the form below to apply:</p>

    <form method="POST" enctype="multipart/form-data" class="upload-form">
        <div class="form-group">
            <label for="name">Full Name:</label>
            <input type="text" id="name" name="name" required>
        </div>

        <div class="form-group">
            <label for="phone">Phone Number:</label>
            <input type="tel" id="phone" name="phone" required>
        </div>

        <div class="form-group">
            <label for="experience">Years of Experience:</label>
            <input type="number" id="experience" name="experience" min="0" required>
        </div>

        <div class="form-group">
            <label for="position">Desired Position:</label>
            <input type="text" id="position" name="position" required>
        </div>

        <div class="form-group">
            <label for="salary">Current Salary (NGN):</label>
            <input type="number" id="salary" name="salary" min="0" required>
        </div>

        <div class="form-group">
            <label for="expected_salary">Expected Salary (NGN):</label>
            <input type="number" id="expected_salary" name="expected_salary" min="0" required>
        </div>

        <div class="form-group">
            <label for="file">Upload Resume (PDF/DOCX):</label>
            <input type="file" id="file" name="file" accept=".pdf,.doc,.docx" required>
        </div>

        <button type="submit">Submit Application</button>
    </form>
</body>
</html>
'''
    return render_template_string(careers_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)