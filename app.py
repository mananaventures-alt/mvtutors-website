import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
from werkzeug.utils import secure_filename
import uuid
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Create a service role client for file uploads (bypasses RLS)
if supabase_service_key:
    supabase_admin: Client = create_client(supabase_url, supabase_service_key)
else:
    supabase_admin = supabase  # Fallback to regular client

# Admin credentials
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'info@mvtutors.co.za')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Mvtutors@123!')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER', 'info@mvtutors.co.za')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'info@mvtutors.co.za')
TO_EMAIL = os.getenv('TO_EMAIL', 'info@mvtutors.co.za')
CC_EMAIL = os.getenv('CC_EMAIL', 'aaron@123tutors.co.za')

def send_email(subject, body, to_email, cc_email=None):
    """Send email notification"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        if cc_email:
            msg['Cc'] = cc_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'html'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable security
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Send email
        recipients = [to_email]
        if cc_email:
            recipients.append(cc_email)
        
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, recipients, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def upload_file_to_supabase_storage(file, bucket_name, folder_path, application_id):
    """Upload file to Supabase Storage"""
    try:
        if not file or not file.filename:
            return {'success': False, 'error': 'No file provided'}
        
        # Generate unique filename with original extension
        file_extension = os.path.splitext(secure_filename(file.filename))[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create full path: folder/application_id/filename
        full_path = f"{folder_path}/{application_id}/{unique_filename}"
        
        # Read file content
        file.seek(0)  # Reset file pointer
        file_content = file.read()
        
        # Determine content type based on file extension if not provided
        content_type = file.content_type
        if not content_type or content_type == 'application/octet-stream' or not isinstance(content_type, str):
            # Fallback content types based on file extension
            if file_extension.lower() in ['.jpg', '.jpeg']:
                content_type = 'image/jpeg'
            elif file_extension.lower() == '.png':
                content_type = 'image/png'
            elif file_extension.lower() == '.gif':
                content_type = 'image/gif'
            elif file_extension.lower() == '.pdf':
                content_type = 'application/pdf'
            elif file_extension.lower() in ['.doc', '.docx']:
                content_type = 'application/msword'
            else:
                content_type = 'application/octet-stream'
        
        print(f"DEBUG: Uploading file - Path: {full_path}, Content-Type: {content_type}, Size: {len(file_content)} bytes")
        
        # First, try to delete existing file if it exists (to handle overwrites)
        try:
            existing_files = supabase_admin.storage.from_(bucket_name).list(f"{folder_path}/{application_id}")
            print(f"DEBUG: Existing files check result: {existing_files}")
        except Exception as e:
            print(f"DEBUG: Could not check existing files (folder might not exist): {e}")
        
        # Upload to Supabase Storage using service role client (bypasses RLS)
        result = supabase_admin.storage.from_(bucket_name).upload(
            path=full_path,
            file=file_content,
            file_options={
                "content-type": content_type,
                "cache-control": "3600"
            }
        )
        
        print(f"DEBUG: Upload result type: {type(result)}, Result: {result}")
        
        # Check if upload was successful
        # Supabase storage upload returns different response formats
        if result and (not hasattr(result, 'error') or result.error is None):
            # Get public URL for public buckets, signed URL for private buckets
            if bucket_name == 'tutor-profile-pictures':
                public_url = supabase_admin.storage.from_(bucket_name).get_public_url(full_path)
            else:
                # For private buckets, store the path and generate signed URLs when needed
                public_url = full_path
            
            return {
                'success': True,
                'url': public_url,
                'path': full_path,
                'filename': unique_filename,
                'original_filename': file.filename
            }
        else:
            error_msg = result.error if hasattr(result, 'error') and result.error else 'Upload failed'
            print(f"Upload failed with error: {error_msg}")
            return {'success': False, 'error': str(error_msg)}
            
    except Exception as e:
        print(f"Error uploading file to Supabase Storage: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def hash_password(password):
    """Simple password hashing function"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_admin_auth():
    """Check if user is authenticated as admin"""
    return session.get('admin_authenticated', False)

# Jinja2 filter for datetime formatting (simplified without dateutil)
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    """Format a datetime string from Supabase"""
    if not value:
        return 'N/A'
    try:
        # If it's already a datetime object
        if isinstance(value, datetime):
            return value.strftime(format)
        # If it's a string, try to parse it
        elif isinstance(value, str):
            # Handle ISO format datetime strings from Supabase
            if 'T' in value:
                # Remove timezone info if present and parse
                dt_str = value.split('+')[0].split('Z')[0]
                dt = datetime.fromisoformat(dt_str)
                return dt.strftime(format)
            else:
                return value  # Return as is if not ISO format
        else:
            return 'N/A'
    except (ValueError, TypeError):
        return str(value)  # Return the original value if parsing fails

@app.template_filter('dateformat')
def dateformat(value):
    """Format a date string from Supabase"""
    return datetimeformat(value, '%Y-%m-%d')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('index.html', section='how-it-works')

@app.route('/pricing')
def pricing():
    return render_template('index.html', section='pricing')

@app.route('/about')
def about():
    return render_template('index.html', section='about')

@app.route('/book-call')
def book_call():
    return render_template('index.html', section='book-call')

@app.route('/request-tutor')
def request_tutor():
    # Simply render the form - no database operations needed
    return render_template('request_tutor.html')

@app.route('/submit-tutor-request', methods=['POST'])
def submit_tutor_request():
    try:
        # Handle subjects including "other" option
        subjects_list = request.form.getlist('subjects')
        other_subjects = request.form.get('other_subjects', '').strip()
        
        # If "other" is selected and other_subjects field has content, add it to the subjects
        if 'other' in subjects_list and other_subjects:
            subjects_list = [s for s in subjects_list if s != 'other']  # Remove 'other' from list
            subjects_list.append(f"Other: {other_subjects}")
        elif 'other' in subjects_list:
            subjects_list = [s for s in subjects_list if s != 'other']  # Remove 'other' if no text provided
        
        # Get form data
        data = {
            'full_name': request.form.get('full_name'),
            'contact_number': request.form.get('contact_number'),
            'email': request.form.get('email'),
            'tutoring_service': request.form.get('tutoring_service'),
            'group_size': request.form.get('group_size') if request.form.get('tutoring_service') == 'group' else None,
            'institution': request.form.get('institution'),
            'grade_year': request.form.get('grade_year'),
            'tutoring_type': request.form.get('tutoring_type'),
            'subjects': ', '.join(subjects_list),
            'reason': request.form.get('reason'),
            'start_date': request.form.get('start_date') or None,
            'comments': request.form.get('comments'),
            'status': 'new_request'  # Set default status
        }
        
        print(f"DEBUG: Attempting to insert data: {data}")
        
        # Only POST to Supabase - no reading/fetching data
        result = supabase.table('tutor_requests').insert(data).execute()
        
        print(f"DEBUG: Insert result: {result}")
        
        # Send email notification
        if result.data:
            email_subject = "New Tutor Request"
            email_body = f"""
            <html>
            <body>
                <h2>New Tutor Request Received</h2>
                
                <h3>Student Information:</h3>
                <p><strong>Full Name:</strong> {data['full_name']}</p>
                <p><strong>Email:</strong> {data['email']}</p>
                <p><strong>Contact Number:</strong> {data['contact_number']}</p>
                
                <h3>Request Details:</h3>
                <p><strong>Tutoring Service:</strong> {data['tutoring_service'].replace('_', ' ').title() if data['tutoring_service'] else 'N/A'}</p>
                {f"<p><strong>Group Size:</strong> {data['group_size']} students</p>" if data['group_size'] else ""}
                <p><strong>Institution:</strong> {data['institution'].replace('_', ' ').title() if data['institution'] else 'N/A'}</p>
                <p><strong>Grade/Year:</strong> {data['grade_year'].replace('_', ' ').title() if data['grade_year'] else 'N/A'}</p>
                <p><strong>Tutoring Type:</strong> {data['tutoring_type'].title() if data['tutoring_type'] else 'N/A'}</p>
                <p><strong>Subjects:</strong> {data['subjects']}</p>
                <p><strong>Reason for Tutoring:</strong> {data['reason'] if data['reason'] else 'N/A'}</p>
                <p><strong>Preferred Start Date:</strong> {data['start_date'] if data['start_date'] else 'N/A'}</p>
                <p><strong>Additional Comments:</strong> {data['comments'] if data['comments'] else 'N/A'}</p>
                
                <h3>Administrative Details:</h3>
                <p><strong>Request ID:</strong> {result.data[0]['id'] if result.data else 'N/A'}</p>
                <p><strong>Status:</strong> New Request</p>
                <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <p style="margin-top: 20px;">
                    <a href="https://mvtutors.co.za/admin/dashboard" style="background-color: #3B82F6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        View in Admin Dashboard
                    </a>
                </p>
            </body>
            </html>
            """
            
            # Send email notification
            send_email(email_subject, email_body, TO_EMAIL, CC_EMAIL)
        
        flash('Your tutor request has been submitted successfully!', 'success')
    except Exception as e:
        # Enhanced error handling for RLS issues
        error_msg = str(e)
        print(f"Error submitting tutor request: {e}")
        print(f"Error type: {type(e)}")
        
        if '42501' in error_msg or 'row-level security' in error_msg.lower():
            flash('Database security configuration needs to be updated. Please contact the administrator.', 'error')
            print("RLS POLICY ERROR: Need to disable RLS or create proper policies in Supabase")
        else:
            flash('There was an error submitting your request. Please try again.', 'error')
    
    return redirect(url_for('request_tutor'))

@app.route('/contact')
def contact():
    # Simply render the contact form - no database operations needed
    return render_template('contact.html')

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    try:
        # Get form data
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message'),
            'status': 'unread'
        }
        
        print(f"DEBUG: Attempting to insert contact message: {data}")
        
        # Insert to Supabase
        result = supabase.table('contact_messages').insert(data).execute()
        
        print(f"DEBUG: Contact insert result: {result}")
        
        # Send email notification if insert was successful
        if result.data:
            email_subject = "New Contact Message Received"
            email_body = f"""
            <html>
            <body>
                <h2>New Contact Message</h2>
                
                <h3>Contact Information:</h3>
                <p><strong>Name:</strong> {data['name']}</p>
                <p><strong>Email:</strong> {data['email']}</p>
                <p><strong>Phone:</strong> {data['phone'] if data['phone'] else 'Not provided'}</p>
                
                <h3>Message Details:</h3>
                <p><strong>Subject:</strong> {data['subject'] if data['subject'] else 'No subject'}</p>
                <p><strong>Message:</strong></p>
                <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #3B82F6; margin: 10px 0;">
                    {data['message'].replace('\n', '<br>') if data['message'] else 'No message'}
                </div>
                
                <h3>Administrative Details:</h3>
                <p><strong>Message ID:</strong> {result.data[0]['id'] if result.data else 'N/A'}</p>
                <p><strong>Status:</strong> Unread</p>
                <p><strong>Received:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <p style="margin-top: 20px;">
                    <a href="https://mvtutors.co.za/admin/dashboard" style="background-color: #3B82F6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        View in Admin Dashboard
                    </a>
                </p>
            </body>
            </html>
            """
            
            # Send email notification
            send_email(email_subject, email_body, TO_EMAIL, CC_EMAIL)
        
        contact_method = request.form.get('contact_method', 'email')
        flash(f'Thank you {data["name"]}! Your message has been sent successfully. We will get back to you via {contact_method} within 24 hours.', 'success')
    except Exception as e:
        flash('There was an error sending your message. Please try again.', 'error')
        print(f"Error submitting contact message: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('contact'))

@app.route('/become-tutor')
def become_tutor():
    # Simply render the application form - no database operations needed
    return render_template('become_tutor.html')

@app.route('/submit-tutor-application', methods=['POST'])
def submit_tutor_application():
    try:
        # Handle subjects including "other" option
        subjects_list = request.form.getlist('subjects_to_tutor')
        other_subjects = request.form.get('specific_subjects', '').strip()
        
        # If "other" is selected and specific_subjects field has content, add it to the subjects
        if 'other' in subjects_list and other_subjects:
            subjects_list = [s for s in subjects_list if s != 'other']  # Remove 'other' from list
            subjects_list.append(f"Other: {other_subjects}")
        elif 'other' in subjects_list:
            subjects_list = [s for s in subjects_list if s != 'other']  # Remove 'other' if no text provided
        
        # Get form data
        data = {
            'full_name': f"{request.form.get('name')} {request.form.get('surname')}",
            'email': request.form.get('email'),
            'phone': request.form.get('contact_number'),
            'date_of_birth': request.form.get('date_of_birth') or None,
            'id_number': request.form.get('id_number'),
            'address': request.form.get('address'),
            'highest_qualification': request.form.get('highest_qualification'),
            'institution': request.form.get('institution'),
            'year_completed': int(request.form.get('year_completed')) if request.form.get('year_completed') else None,
            'current_student': request.form.get('current_student') == 'yes',
            'current_institution': request.form.get('current_institution'),
            'current_year': int(request.form.get('current_year')) if request.form.get('current_year') else None,
            'institutions_to_tutor': ', '.join(request.form.getlist('institutions_to_tutor')),
            'subjects_to_tutor': ', '.join(subjects_list),
            'tutoring_method': request.form.get('tutoring_method'),
            'tutoring_experience': request.form.get('experience'),
            'availability': request.form.get('availability'),
            'transport': request.form.get('transport') == 'yes',
            'preferred_locations': request.form.get('preferred_locations'),
            'status': 'pending'
        }
        
        print(f"DEBUG: Attempting to insert tutor application data: {data}")
        
        # Insert application first to get the ID
        result = supabase.table('tutor_applications').insert(data).execute()
        
        print(f"DEBUG: Insert result: {result}")
        
        if result.data:
            application_id = result.data[0]['id']
            print(f"DEBUG: Application created with ID: {application_id}")
            
            # Send email notification for new tutor application
            email_subject = "New Tutor Application Received"
            email_body = f"""
            <html>
            <body>
                <h2>New Tutor Application Submitted</h2>
                
                <h3>Personal Information:</h3>
                <p><strong>Full Name:</strong> {data['full_name']}</p>
                <p><strong>Email:</strong> {data['email']}</p>
                <p><strong>Phone:</strong> {data['phone']}</p>
                <p><strong>Date of Birth:</strong> {data['date_of_birth'] if data['date_of_birth'] else 'Not provided'}</p>
                <p><strong>ID Number:</strong> {data['id_number'] if data['id_number'] else 'Not provided'}</p>
                <p><strong>Address:</strong> {data['address'] if data['address'] else 'Not provided'}</p>
                
                <h3>Educational Background:</h3>
                <p><strong>Highest Qualification:</strong> {data['highest_qualification'].replace('_', ' ').title() if data['highest_qualification'] else 'N/A'}</p>
                <p><strong>Institution:</strong> {data['institution']}</p>
                <p><strong>Year Completed:</strong> {data['year_completed'] if data['year_completed'] else 'N/A'}</p>
                <p><strong>Currently a Student:</strong> {'Yes' if data['current_student'] else 'No'}</p>
                {f"<p><strong>Current Institution:</strong> {data['current_institution']}</p>" if data['current_institution'] else ""}
                {f"<p><strong>Current Year:</strong> {data['current_year']}</p>" if data['current_year'] else ""}
                
                <h3>Tutoring Information:</h3>
                <p><strong>Institutions to Tutor:</strong> {data['institutions_to_tutor'].replace('_', ' ').title() if data['institutions_to_tutor'] else 'N/A'}</p>
                <p><strong>Subjects to Tutor:</strong> {data['subjects_to_tutor']}</p>
                <p><strong>Tutoring Method:</strong> {data['tutoring_method'].replace('_', ' ').title() if data['tutoring_method'] else 'N/A'}</p>
                <p><strong>Experience:</strong> {data['tutoring_experience'] if data['tutoring_experience'] else 'N/A'}</p>
                <p><strong>Availability:</strong> {data['availability'] if data['availability'] else 'N/A'}</p>
                <p><strong>Has Transport:</strong> {'Yes' if data['transport'] else 'No'}</p>
                <p><strong>Preferred Locations:</strong> {data['preferred_locations'] if data['preferred_locations'] else 'N/A'}</p>
                
                <h3>Administrative Details:</h3>
                <p><strong>Application ID:</strong> {application_id}</p>
                <p><strong>Status:</strong> Pending Review</p>
                <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <p style="margin-top: 20px;">
                    <a href="https://mvtutors.co.za/admin/dashboard" style="background-color: #3B82F6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        View Application in Admin Dashboard
                    </a>
                </p>
                
                <p style="margin-top: 10px; color: #666; font-size: 12px;">
                    Files uploaded will be available for review in the admin dashboard.
                </p>
            </body>
            </html>
            """
            
            # Send email notification
            send_email(email_subject, email_body, TO_EMAIL, CC_EMAIL)
            
            # File upload configuration
            file_mappings = {
                'profile_picture': {
                    'bucket': 'tutor-profile-pictures',
                    'folder': 'profiles'
                },
                'matric_certificate': {
                    'bucket': 'matric-certificates',
                    'folder': 'certificates'
                },
                'cv': {
                    'bucket': 'tutor-cvs',
                    'folder': 'resumes'
                },
                'varsity_results': {
                    'bucket': 'university-results',
                    'folder': 'university-results'
                }
            }
            
            file_updates = {}
            upload_errors = []
            
            # Process each file upload
            for field_name, config in file_mappings.items():
                if request.files.get(field_name):
                    file = request.files[field_name]
                    if file.filename:
                        print(f"DEBUG: Uploading {field_name}: {file.filename}")
                        
                        upload_result = upload_file_to_supabase_storage(
                            file=file,
                            bucket_name=config['bucket'],
                            folder_path=config['folder'],
                            application_id=application_id
                        )
                        
                        if upload_result['success']:
                            file_updates[f'{field_name}_url'] = upload_result['url']
                            file_updates[f'{field_name}_filename'] = upload_result['original_filename']
                            file_updates[f'{field_name}_storage_path'] = upload_result['path']
                            print(f"DEBUG: Successfully uploaded {field_name}")
                        else:
                            upload_errors.append(f"Failed to upload {field_name}: {upload_result['error']}")
                            print(f"ERROR: Failed to upload {field_name}: {upload_result['error']}")
            
            # Update application with file information
            if file_updates:
                print(f"DEBUG: Updating application with file data: {file_updates}")
                update_result = supabase.table('tutor_applications').update(file_updates).eq('id', application_id).execute()
                print(f"DEBUG: Update result: {update_result}")
            
            # Show success message even if some file uploads failed
            if upload_errors:
                flash(f'Your tutor application has been submitted successfully! However, some files failed to upload: {"; ".join(upload_errors)}', 'warning')
            else:
                flash(f'Thank you {data["full_name"]}! Your tutor application has been submitted successfully. We will review your application and get back to you within 3-5 business days.', 'success')
        else:
            flash('There was an error submitting your application. Please try again.', 'error')
            
    except Exception as e:
        flash('There was an error submitting your application. Please try again.', 'error')
        print(f"Error submitting tutor application: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('become_tutor'))

# Admin routes
@app.route('/admin')
def admin_login():
    if check_admin_auth():
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin', methods=['POST'])
def admin_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Check if fields are empty
    if not email or not password:
        return render_template('admin_login.html', error='Please enter both email and password')
    
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session['admin_authenticated'] = True
        flash('Login successful!', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('admin_login.html', error='Invalid email or password. Please try again.')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    try:
        # Fetch data from Supabase
        tutor_requests = supabase.table('tutor_requests').select('*').order('created_at', desc=True).execute()
        # Get tutor applications excluding approved ones (only pending and rejected)
        tutor_applications = supabase.table('tutor_applications').select('*').neq('status', 'approved').order('created_at', desc=True).execute()
        # Get approved tutors from tutor_applications table where status is 'approved'
        approved_tutors = supabase.table('tutor_applications').select('*').eq('status', 'approved').order('approved_at', desc=True).execute()
        contact_messages = supabase.table('contact_messages').select('*').order('created_at', desc=True).execute()
        
        return render_template('admin_dashboard.html',
                             tutor_requests=tutor_requests.data,
                             tutor_applications=tutor_applications.data,
                             approved_tutors=approved_tutors.data,
                             contact_messages=contact_messages.data)
    except Exception as e:
        flash('Error loading dashboard data', 'error')
        print(f"Error: {e}")
        return render_template('admin_dashboard.html',
                             tutor_requests=[],
                             tutor_applications=[],
                             approved_tutors=[],
                             contact_messages=[])

@app.route('/admin/approve-tutor/<int:application_id>', methods=['POST'])
def approve_tutor(application_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    try:
        # Update application status to approved
        supabase.table('tutor_applications').update({
            'status': 'approved',
            'approved_at': datetime.now().isoformat(),
            'approved_by': 'admin'
        }).eq('id', application_id).execute()
        
        flash('Tutor approved successfully!', 'success')
        
    except Exception as e:
        flash('Error approving tutor', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject-tutor/<int:application_id>', methods=['POST'])
def reject_tutor(application_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    try:
        # Update application status
        supabase.table('tutor_applications').update({
            'status': 'rejected'
        }).eq('id', application_id).execute()
        
        flash('Tutor application rejected', 'info')
    except Exception as e:
        flash('Error rejecting application', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-tutor/<int:application_id>', methods=['POST'])
def delete_tutor(application_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    try:
        # Get application data first to clean up files
        application = supabase.table('tutor_applications').select('*').eq('id', application_id).single().execute()
        app_data = application.data
        
        if app_data:
            # Clean up files from storage
            file_paths = [
                (app_data.get('profile_picture_storage_path'), 'tutor-profile-pictures'),
                (app_data.get('matric_certificate_storage_path'), 'matric-certificates'),
                (app_data.get('cv_storage_path'), 'tutor-cvs'),
                (app_data.get('varsity_results_storage_path'), 'university-results')
            ]
            
            for file_path, bucket in file_paths:
                if file_path:
                    try:
                        supabase_admin.storage.from_(bucket).remove([file_path])
                        print(f"Deleted file: {file_path} from bucket: {bucket}")
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
            
            # Delete the application record
            supabase.table('tutor_applications').delete().eq('id', application_id).execute()
            flash('Tutor application deleted successfully', 'success')
        else:
            flash('Application not found', 'error')
    except Exception as e:
        flash('Error deleting application', 'error')
        print(f"Error deleting application: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    try:
        # Delete the tutor request record
        result = supabase.table('tutor_requests').delete().eq('id', request_id).execute()
        
        if result.data:
            flash('Tutor request deleted successfully', 'success')
        else:
            flash('Request not found', 'error')
    except Exception as e:
        flash('Error deleting request', 'error')
        print(f"Error deleting request: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update-request-status', methods=['POST'])
def update_request_status():
    if not check_admin_auth():
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        new_status = data.get('status')
        
        if not request_id or not new_status:
            return {'success': False, 'error': 'Missing request_id or status'}, 400
        
        # Valid status options
        valid_statuses = ['new_request', 'contacted', 'invoice_sent', 'tutor_assigned', 'not_interested', 'spam']
        if new_status not in valid_statuses:
            return {'success': False, 'error': 'Invalid status'}, 400
        
        # Update status in Supabase
        result = supabase.table('tutor_requests').update({
            'status': new_status
        }).eq('id', request_id).execute()
        
        if result.data:
            return {'success': True, 'message': 'Status updated successfully'}
        else:
            return {'success': False, 'error': 'Failed to update status'}, 500
            
    except Exception as e:
        print(f"Error updating request status: {e}")
        return {'success': False, 'error': str(e)}, 500

@app.route('/admin/update-message-status', methods=['POST'])
def update_message_status():
    if not check_admin_auth():
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        new_status = data.get('status')
        
        if not message_id or not new_status:
            return {'success': False, 'error': 'Missing message_id or status'}, 400
        
        # Valid status options for contact messages
        valid_statuses = ['unread', 'read', 'replied', 'resolved']
        if new_status not in valid_statuses:
            return {'success': False, 'error': 'Invalid status'}, 400
        
        # Update status in Supabase
        result = supabase.table('contact_messages').update({
            'status': new_status
        }).eq('id', message_id).execute()
        
        if result.data:
            return {'success': True, 'message': 'Message status updated successfully'}
        else:
            return {'success': False, 'error': 'Failed to update status'}, 500
            
    except Exception as e:
        print(f"Error updating message status: {e}")
        return {'success': False, 'error': str(e)}, 500

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/view-file/<int:application_id>/<file_type>')
def view_file(application_id, file_type):
    """Generate signed URL for viewing files"""
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    try:
        # Get application data
        application = supabase.table('tutor_applications').select('*').eq('id', application_id).single().execute()
        app_data = application.data
        
        if not app_data:
            return "Application not found", 404
        
        # File type mapping
        file_mappings = {
            'profile_picture': {
                'url_field': 'profile_picture_url',
                'bucket': 'tutor-profile-pictures'
            },
            'matric_certificate': {
                'url_field': 'matric_certificate_url', 
                'bucket': 'matric-certificates'
            },
            'cv': {
                'url_field': 'cv_url',
                'bucket': 'tutor-cvs'
            },
            'varsity_results': {
                'url_field': 'varsity_results_url',
                'bucket': 'university-results'
            }
        }
        
        if file_type not in file_mappings:
            return "Invalid file type", 400
        
        file_config = file_mappings[file_type]
        file_url = app_data.get(file_config['url_field'])
        
        if not file_url:
            return "File not found", 404
        
        # For profile pictures (public bucket), redirect to public URL
        if file_type == 'profile_picture':
            return redirect(file_url)
        else:
            # For private buckets, generate signed URL
            try:
                signed_url = supabase_admin.storage.from_(file_config['bucket']).create_signed_url(file_url, 3600)  # 1 hour expiry
                return redirect(signed_url['signedURL'])
            except Exception as e:
                print(f"Error generating signed URL: {e}")
                return "Error accessing file", 500
    
    except Exception as e:
        print(f"Error viewing file: {e}")
        return "Error accessing file", 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
