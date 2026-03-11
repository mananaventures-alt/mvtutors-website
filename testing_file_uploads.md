# Test File Upload Functionality

To test the file upload integration with your Supabase S3 buckets, follow these steps:

## 1. Update Environment Variables

Add these to your `.env` file if not already present:

```env
# Your existing Supabase configuration
SUPABASE_URL=https://jfsiusrstjoeudsvxhrt.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Email configuration
EMAIL_USER=info@mvtutors.co.za
EMAIL_PASSWORD=your_gmail_app_password_here
TO_EMAIL=info@mvtutors.co.za
CC_EMAIL=aaron@123tutors.co.za
```

## 2. Run Database Schema Updates

Execute the SQL commands in `sql_schema_tutor_applications.sql` in your Supabase SQL Editor to add the new file storage columns.

## 3. Test File Upload

1. **Start your Flask application:**
   ```bash
   python app.py
   ```

2. **Navigate to the Become a Tutor page:**
   ```
   http://localhost:8000/become-tutor
   ```

3. **Fill out the form and upload files:**
   - Profile Picture (JPG/PNG, max 5MB) → Goes to `tutor-profile-pictures` bucket
   - Matric Certificate (PDF/JPG/PNG, max 10MB) → Goes to `matric-certificates` bucket  
   - CV/Resume (PDF/DOC/DOCX, max 10MB) → Goes to `tutor-cvs` bucket
   - University Results (if applicable) → Goes to `matric-certificates` bucket

4. **Check the console output** for debug messages showing upload progress

5. **Verify in Supabase Dashboard:**
   - Go to Storage in your Supabase dashboard
   - Check each bucket for the uploaded files organized by application ID

## 4. File Organization Structure

Files will be organized as follows:

```
tutor-profile-pictures/
└── profiles/
    └── {application_id}/
        └── {uuid}.jpg

matric-certificates/
├── certificates/
│   └── {application_id}/
│       └── {uuid}.pdf
└── university-results/
    └── {application_id}/
        └── {uuid}.pdf

tutor-cvs/
└── resumes/
    └── {application_id}/
        └── {uuid}.pdf
```

## 5. Troubleshooting

If uploads fail, check:

1. **Bucket permissions** - Ensure your buckets have the correct policies
2. **File size limits** - Profile pictures: 5MB, Documents: 10MB
3. **File types** - Only allowed MIME types can be uploaded
4. **Supabase API key** - Ensure you're using the correct anon key
5. **Console logs** - Check for detailed error messages

## 6. Database Verification

After successful submission, check your `tutor_applications` table for:

- `profile_picture_url` - Public URL for profile pictures
- `profile_picture_storage_path` - Storage path for reference
- `matric_certificate_storage_path` - Private file path
- `cv_storage_path` - Private file path
- `varsity_results_storage_path` - Private file path (if uploaded)

## 7. Admin Dashboard Integration

The admin dashboard can display file information and provide download links for private files using signed URLs.

## Success Indicators

✅ Form submits successfully
✅ Files appear in correct Supabase Storage buckets
✅ Database records include file paths and URLs
✅ Profile pictures are publicly accessible
✅ Private documents are secure (no direct public access)
✅ Console shows successful upload debug messages
