import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
# from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Supabase configuration (commented out)
# supabase_url = os.getenv('SUPABASE_URL')
# supabase_key = os.getenv('SUPABASE_ANON_KEY')
# supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
# supabase = create_client(supabase_url, supabase_key)
# supabase_admin = create_client(supabase_url, supabase_service_key) if supabase_service_key else supabase

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
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        if cc_email:
            msg['Cc'] = cc_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        recipients = [to_email]
        if cc_email:
            recipients.append(cc_email)

        server.sendmail(FROM_EMAIL, recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# upload_file_to_supabase_storage commented out (Supabase not in use)
# def upload_file_to_supabase_storage(file, bucket_name, folder_path, application_id): ...

def hash_password(password):
    """Simple password hashing function"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_admin_auth():
    """Check if user is authenticated as admin"""
    return session.get('admin_authenticated', False)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if not value:
        return 'N/A'
    try:
        if isinstance(value, datetime):
            return value.strftime(format)
        elif isinstance(value, str):
            if 'T' in value:
                dt_str = value.split('+')[0].split('Z')[0]
                dt = datetime.fromisoformat(dt_str)
                return dt.strftime(format)
            else:
                return value
        else:
            return 'N/A'
    except (ValueError, TypeError):
        return str(value)

@app.template_filter('dateformat')
def dateformat(value):
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
        subjects_list = request.form.getlist('subjects')
        other_subjects = request.form.get('other_subjects', '').strip()

        if 'other' in subjects_list and other_subjects:
            subjects_list = [s for s in subjects_list if s != 'other']
            subjects_list.append(f"Other: {other_subjects}")
        elif 'other' in subjects_list:
            subjects_list = [s for s in subjects_list if s != 'other']

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
        }

        # Send email notification directly (no database)
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

            <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        send_email(email_subject, email_body, TO_EMAIL, CC_EMAIL)

        flash('Your tutor request has been submitted successfully!', 'success')
    except Exception as e:
        flash('There was an error submitting your request. Please try again.', 'error')

    return redirect(url_for('request_tutor'))

@app.route('/contact')
def contact():
    # Simply render the contact form - no database operations needed
    return render_template('contact.html')

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    try:
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message'),
        }

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
                {data['message'].replace(chr(10), '<br>') if data['message'] else 'No message'}
            </div>

            <p><strong>Received:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        send_email(email_subject, email_body, TO_EMAIL, CC_EMAIL)

        contact_method = request.form.get('contact_method', 'email')
        flash(f'Thank you {data["name"]}! Your message has been sent successfully. We will get back to you via {contact_method} within 24 hours.', 'success')
    except Exception as e:
        flash('There was an error sending your message. Please try again.', 'error')

    return redirect(url_for('contact'))

@app.route('/become-tutor')
def become_tutor():
    # Simply render the application form - no database operations needed
    return render_template('become_tutor.html')

@app.route('/submit-tutor-application', methods=['POST'])
def submit_tutor_application():
    try:
        subjects_list = request.form.getlist('subjects_to_tutor')
        other_subjects = request.form.get('specific_subjects', '').strip()

        if 'other' in subjects_list and other_subjects:
            subjects_list = [s for s in subjects_list if s != 'other']
            subjects_list.append(f"Other: {other_subjects}")
        elif 'other' in subjects_list:
            subjects_list = [s for s in subjects_list if s != 'other']

        data = {
            'full_name': f"{request.form.get('name')} {request.form.get('surname')}",
            'email': request.form.get('email'),
            'phone': request.form.get('contact_number'),
            'date_of_birth': request.form.get('date_of_birth') or None,
            'id_number': request.form.get('id_number'),
            'address': request.form.get('address'),
            'highest_qualification': request.form.get('highest_qualification'),
            'institution': request.form.get('institution'),
            'year_completed': request.form.get('year_completed'),
            'current_student': request.form.get('current_student') == 'yes',
            'current_institution': request.form.get('current_institution'),
            'current_year': request.form.get('current_year'),
            'institutions_to_tutor': ', '.join(request.form.getlist('institutions_to_tutor')),
            'subjects_to_tutor': ', '.join(subjects_list),
            'tutoring_method': request.form.get('tutoring_method'),
            'tutoring_experience': request.form.get('experience'),
            'availability': request.form.get('availability'),
            'transport': request.form.get('transport') == 'yes',
            'preferred_locations': request.form.get('preferred_locations'),
        }

        # Send email notification directly (no database)
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

            <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        send_email(email_subject, email_body, TO_EMAIL, CC_EMAIL)

        flash(f'Thank you {data["full_name"]}! Your tutor application has been submitted successfully. We will review your application and get back to you within 3-5 business days.', 'success')
    except Exception as e:
        flash('There was an error submitting your application. Please try again.', 'error')

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

    # Supabase disabled - returning empty data
    return render_template('admin_dashboard.html',
                         tutor_requests=[],
                         tutor_applications=[],
                         approved_tutors=[],
                         contact_messages=[])

@app.route('/admin/approve-tutor/<int:application_id>', methods=['POST'])
def approve_tutor(application_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    # Supabase disabled
    flash('Supabase is currently disabled.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject-tutor/<int:application_id>', methods=['POST'])
def reject_tutor(application_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    # Supabase disabled
    flash('Supabase is currently disabled.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-tutor/<int:application_id>', methods=['POST'])
def delete_tutor(application_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    # Supabase disabled
    flash('Supabase is currently disabled.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    # Supabase disabled
    flash('Supabase is currently disabled.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update-request-status', methods=['POST'])
def update_request_status():
    if not check_admin_auth():
        return {'success': False, 'error': 'Unauthorized'}, 401
    # Supabase disabled
    return {'success': False, 'error': 'Supabase is currently disabled.'}, 503

@app.route('/admin/update-message-status', methods=['POST'])
def update_message_status():
    if not check_admin_auth():
        return {'success': False, 'error': 'Unauthorized'}, 401
    # Supabase disabled
    return {'success': False, 'error': 'Supabase is currently disabled.'}, 503

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/view-file/<int:application_id>/<file_type>')
def view_file(application_id, file_type):
    """File viewing disabled - Supabase not in use"""
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    return "File storage is currently disabled.", 503

if __name__ == '__main__':
    app.run(debug=True, port=8000)
