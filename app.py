from flask import Flask, render_template_string, request
from datetime import datetime
import socket
import uuid
import os
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
# Initialize S3 client
s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))


@app.route('/')
def home():
    # Get system information
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    system_id = str(uuid.uuid4())
    private_ip = socket.gethostbyname(socket.gethostname())
    
    # HTML template with variables (same as before)
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Polypop Nigeria Limited</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            color: #4CAF50;
            margin-bottom: 20px;
        }
        p {
            color: #333;
            font-size: 18px;
        }
        .services {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 30px;
        }
        .service {
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .service h3 {
            color: #4CAF50;
        }
        footer {
            margin-top: 50px;
            font-size: 14px;
            color: #777;
        }
        .system-info {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-size: 14px;
            color: #333;
            background-color: #fff;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .nav-link {
            position: absolute;
            top: 20px;
            left: 20px;
            font-size: 16px;
            color: #4CAF50;
            text-decoration: none;
        }
        .nav-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <a href="/careers" class="nav-link">Careers</a>
    <h1>Welcome to Polypop Nigeria Limited</h1>
    <p>We specialize in providing innovative solutions to make your business thrive. Explore our services below:</p>

    <div class="services">
        <div class="service">
            <h3>Web Development</h3>
            <p>Building responsive and functional websites to meet your business needs.</p>
        </div>
        <div class="service">
            <h3>Cloud Solutions</h3>
            <p>Harnessing the power of cloud computing to drive scalability and efficiency.</p>
        </div>
        <div class="service">
            <h3>Mobile Apps</h3>
            <p>Creating user-friendly mobile apps for Android and iOS platforms.</p>
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

def upload_file_to_s3(file, acl="public-read"):
    """
    Upload a file to an S3 bucket.
    :param file: File to upload
    :param acl: ACL permissions (default is public-read)
    :return: URL of the uploaded file
    """
    try:
        # Retrieve the bucket name and region from environment variables
        bucket_name = os.getenv('S3_BUCKET_NAME')
        s3_region = os.getenv('AWS_REGION')

        if not bucket_name or not s3_region:
            raise ValueError("Bucket name or region not set in environment variables.")

        # Generate a unique filename
        filename = f"{request.form.get('name').replace(' ', '_')}_resume_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(file.filename)[1]}"

        # Upload the file to S3
        s3_client.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={"ACL": acl, "ContentType": file.content_type}
        )

        # Generate the URL to access the file
        url = f"https://{bucket_name}.s3.{s3_region}.amazonaws.com/{filename}"
        return url

    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False


@app.route('/careers', methods=['GET', 'POST'])
def careers():
    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        phone = request.form.get('phone')
        experience = request.form.get('experience')
        position = request.form.get('position')
        salary = request.form.get('salary')
        expected_salary = request.form.get('expected_salary')

        # Handle file upload to S3
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Upload to S3
                s3_url = upload_file_to_s3(file)
                if s3_url:
                    print(f"File uploaded successfully to: {s3_url}")
                else:
                    print("Failed to upload file to S3")
        
        print(f"New application received from {name} for {position} position")

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Application Submitted</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                h1 {{ color: #4CAF50; }}
                a {{ color: #4CAF50; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Application Submitted Successfully!</h1>
            <p>Thank you for your application, {name}.</p>
            <p>We have received your application for the {position} position.</p>
            <a href="/">Return to Home Page</a>
        </body>
        </html>
        '''
    
    careers_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Careers - Polypop Nigeria Limited</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
            background-color: #f8f8f8;
        }
        h1 {
            color: #4CAF50;
        }
        .upload-form {
            margin-top: 30px;
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: inline-block;
            width: 100%;
            max-width: 600px;
            text-align: left;
        }
        .form-group {
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .form-group label {
            font-size: 14px;
            font-weight: bold;
            width: 200px;
            text-align: right;
            margin-right: 20px;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            border: 1px solid #ddd;
            box-sizing: border-box;
        }
        .form-group input[type="file"] {
            border: none;
            padding: 5px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            box-sizing: border-box;
        }
        button:hover {
            background-color: #45a049;
        }
        footer {
            margin-top: 50px;
            font-size: 14px;
            color: #777;
        }
        .section-title {
            font-size: 20px;
            color: #4CAF50;
            margin-bottom: 15px;
            text-align: left;
        }
        .nav-link {
            position: absolute;
            top: 20px;
            left: 20px;
            font-size: 16px;
            color: #4CAF50;
            text-decoration: none;
        }
        .nav-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <a href="/" class="nav-link">Home</a>
    <h1>Careers at Polypop Nigeria Limited</h1>
    <p>We are always looking for talented individuals to join our team! Please fill in your details and upload your resume below:</p>

    <form method="POST" enctype="multipart/form-data" class="upload-form">
        <div class="section-title">Personal Information</div>
        <div class="form-group">
            <label for="name">Your Name:</label>
            <input type="text" name="name" id="name" required>
        </div>

        <div class="form-group">
            <label for="phone">Phone Number:</label>
            <input type="tel" name="phone" id="phone" required placeholder="Enter your phone number">
        </div>

        <div class="section-title">Professional Information</div>
        <div class="form-group">
            <label for="experience">Years of Experience:</label>
            <input type="number" name="experience" id="experience" required>
        </div>

        <div class="form-group">
            <label for="position">Position Applying For:</label>
            <input type="text" name="position" id="position" required>
        </div>

        <div class="form-group">
            <label for="salary">Current Salary:</label>
            <input type="number" name="salary" id="salary" required placeholder="Enter your current salary">
        </div>

        <div class="form-group">
            <label for="expected_salary">Expected Salary:</label>
            <input type="number" name="expected_salary" id="expected_salary" required placeholder="Enter your expected salary">
        </div>

        <div class="section-title">Upload Your Resume</div>
        <div class="form-group">
            <label for="file">Choose a file to upload:</label>
            <input type="file" name="file" id="file" required>
        </div>

        <button type="submit">Submit Application</button>
    </form>

    <footer>
        <p>From Polypop Nigeria Limited</p>
    </footer>
</body>
</html>
'''
    return render_template_string(careers_html)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)