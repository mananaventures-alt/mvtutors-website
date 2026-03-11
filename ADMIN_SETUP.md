# MV Tutors Admin Dashboard Setup Instructions

## 1. Database Setup

1. Go to your Supabase project: https://jfsiusrstjoeudsvxhrt.supabase.co
2. Navigate to the SQL Editor in your Supabase dashboard
3. Copy and paste the contents of `database_schema.sql` into the SQL Editor
4. Run the SQL commands to create all necessary tables

## 2. Environment Setup

1. Make sure you have Python 3.8+ installed
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. The `.env` file is already configured with your Supabase credentials

## 3. Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. The application will run on http://localhost:8000

## 4. Admin Access

### Admin Login URL
- **URL**: http://localhost:8000/admin
- **Email**: info@mvtutors.co.za
- **Password**: Mvtutors@123!

### Admin Dashboard Features

1. **Tutor Requests**: View all student requests for tutoring
2. **Tutor Applications**: Review and approve/reject tutor applications
3. **Approved Tutors**: Search and manage approved tutors
4. **Contact Messages**: View all contact form submissions

## 5. Database Tables Created

- `tutor_requests`: Stores student tutor requests
- `tutor_applications`: Stores tutor application forms
- `approved_tutors`: Stores approved tutors with their details
- `contact_messages`: Stores contact form submissions

## 6. Key Features

### Tutor Application Workflow
1. Applicant submits tutor application form
2. Application appears in admin dashboard as "pending"
3. Admin can approve or reject applications
4. Approved tutors are automatically added to the approved tutors list
5. Approved tutors can be searched by name, subjects, or qualifications

### Data Integration
- All form submissions (tutor requests, applications, contact messages) are automatically saved to Supabase
- Real-time data display in admin dashboard
- Status tracking for all submissions

## 7. Security Notes

- Admin authentication is session-based
- Row Level Security (RLS) is enabled on all tables
- Passwords should be changed in production
- Environment variables contain sensitive information

## 8. Next Steps for Production

1. Change default admin password
2. Set up proper file upload handling for tutor documents
3. Implement email notifications for new submissions
4. Add more detailed tutor profiles
5. Implement tutor-student matching system
6. Add export functionality for data

## 9. Troubleshooting

### If you get connection errors:
1. Check that your Supabase URL and keys are correct in `.env`
2. Ensure your Supabase project is active
3. Verify that the database tables have been created

### If forms aren't saving:
1. Check the browser console for JavaScript errors
2. Verify that all required form fields are being submitted
3. Check the Flask console for Python errors

## 10. Database Policies

The current setup allows all operations for authenticated users. In production, you may want to:
1. Create specific admin users in Supabase Auth
2. Implement more granular permissions
3. Add audit logging for admin actions

## Support

If you encounter any issues, check:
1. Flask console output for errors
2. Supabase dashboard logs
3. Browser developer tools for frontend issues
