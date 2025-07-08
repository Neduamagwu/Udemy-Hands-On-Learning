from flask import Flask, render_template_string, request
from werkzeug.utils import secure_filename
from datetime import datetime
import socket
import uuid
import os

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    # Get system information
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    system_id = str(uuid.uuid4())
    private_ip = socket.gethostbyname(socket.gethostname())

    # HTML template with variables
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
    <h1>Welcome to Polypop Nigeria Limited!</h1>
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

@app.route('/careers', methods=['GET', 'POST'])
def careers():
    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        filename = None

        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Get file extension from original filename
                file_ext = os.path.splitext(file.filename)[1].lower()
                # Create filename using the entered name and original extension
                base_filename = f"{name.replace(' ', '_')}{file_ext}"
                # Secure the filename
                filename = secure_filename(base_filename)
                # Save the file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print(f"File saved as: {filename}")

        # Show confirmation page
        confirmation_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Application Submitted</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }}
        .confirmation-container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }}
        h1 {{ 
            color: #4CAF50; 
            margin-bottom: 20px;
        }}
        .file-info {{
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
            font-family: monospace;
        }}
        a {{ 
            color: #4CAF50; 
            text-decoration: none;
            margin-top: 20px;
            display: inline-block;
            padding: 10px 20px;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            transition: all 0.3s;
        }}
        a:hover {{
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="confirmation-container">
        <h1>Application Submitted Successfully!</h1>
        <p>Thank you for your application, <strong>{name}</strong>.</p>
        '''
        
        if filename:
            confirmation_html += f'''
        <p>We have received your resume:</p>
        <div class="file-info">{filename}</div>
        '''
        else:
            confirmation_html += '''
        <p>We have received your application.</p>
        '''
            
        confirmation_html += '''
        <a href="/">Return to Home Page</a>
    </div>
</body>
</html>
        '''
        return confirmation_html

    # For GET requests, show the careers page
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
            background-color: #f8f8f8;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        h1 {
            color: #4CAF50;
            margin-bottom: 20px;
        }
        .upload-form {
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 600px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: center;
        }
        .form-group label {
            font-size: 14px;
            font-weight: bold;
            display: block;
            margin-bottom: 8px;
        }
        .form-group input {
            width: 100%;
            max-width: 400px;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            border: 1px solid #ddd;
            box-sizing: border-box;
            margin: 0 auto;
        }
        .form-group input[type="file"] {
            border: none;
            padding: 5px;
            margin: 0 auto;
            display: block;
        }
        .file-info {
            font-size: 14px;
            color: #777;
            margin-top: 5px;
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
            max-width: 400px;
            box-sizing: border-box;
            margin: 0 auto;
            display: block;
        }
        button:hover {
            background-color: #45a049;
        }
        footer {
            text-align: center;
            padding: 20px;
            font-size: 14px;
            color: #777;
            width: 100%;
        }
        .requirements {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="upload-form">
            <h1>Careers at Polypop Nigeria Limited</h1>
            <p>We are always looking for talented individuals to join our team! Please fill in your details and upload your resume below:</p>

            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="name">Your Full Name:</label>
                    <input type="text" name="name" id="name" required>
                </div>

                <div class="form-group">
                    <label for="file">Upload Your Resume:</label>
                    <input type="file" name="file" id="file" required accept=".pdf,.doc,.docx">
                    <p class="file-info" id="file-info">No file chosen</p>
                    <p class="requirements">Accepted formats: PDF, DOC, DOCX</p>
                </div>

                <button type="submit">Submit Application</button>
            </form>
        </div>
    </div>

    <footer>
        <p>From Polypop Nigeria Limited</p>
    </footer>

    <script>
        const fileInput = document.getElementById('file');
        const fileInfo = document.getElementById('file-info');

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                fileInfo.textContent = `Selected file: ${fileName}`;
            } else {
                fileInfo.textContent = 'No file chosen';
            }
        });
    </script>
</body>
</html>
'''
    return render_template_string(careers_html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)