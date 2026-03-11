# Supabase Storage Setup Instructions

## Step 1: Create Storage Buckets in Supabase

Go to your Supabase Dashboard > Storage and create the following buckets:

### 1. Create "tutor-applications" bucket
```sql
-- Run this in Supabase SQL Editor to create the bucket programmatically
INSERT INTO storage.buckets (id, name, public)
VALUES ('tutor-applications', 'tutor-applications', false);
```

### 2. Set up Storage Policies

Run these policies in your Supabase SQL Editor:

```sql
-- Allow anyone to upload files to tutor-applications bucket
CREATE POLICY "Allow uploads to tutor-applications" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'tutor-applications');

-- Allow admin access to view files
CREATE POLICY "Allow admin access to tutor-applications" ON storage.objects
FOR ALL USING (bucket_id = 'tutor-applications' AND auth.role() = 'service_role');

-- Allow public read access if needed (optional)
-- CREATE POLICY "Allow public read access" ON storage.objects
-- FOR SELECT USING (bucket_id = 'tutor-applications');
```

## Step 2: Folder Structure

Organize files in the bucket with this structure:
```
tutor-applications/
├── profile-pictures/
│   ├── {application_id}/
│   │   └── profile.jpg
├── matric-certificates/
│   ├── {application_id}/
│   │   └── matric_cert.pdf
├── varsity-results/
│   ├── {application_id}/
│   │   └── varsity_results.pdf
├── cvs/
│   ├── {application_id}/
│   │   └── cv.pdf
└── id-copies/
    ├── {application_id}/
        └── id_copy.pdf
```

## Step 3: Python Code for File Upload

Add this to your Flask app for handling file uploads:

```python
import os
from supabase import create_client
from werkzeug.utils import secure_filename
import uuid

def upload_file_to_supabase(file, bucket_name, folder_path):
    """Upload file to Supabase Storage"""
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create full path
        full_path = f"{folder_path}/{unique_filename}"
        
        # Upload to Supabase Storage
        result = supabase.storage.from_(bucket_name).upload(
            path=full_path,
            file=file.read(),
            file_options={
                "content-type": file.content_type,
                "upsert": True
            }
        )
        
        if result.status_code == 200:
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(full_path)
            return {
                'success': True,
                'url': public_url,
                'path': full_path,
                'filename': unique_filename
            }
        else:
            return {'success': False, 'error': 'Upload failed'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Updated submit_tutor_application function with file uploads
@app.route('/submit-tutor-application', methods=['POST'])
def submit_tutor_application():
    try:
        # ... existing code for form data ...
        
        # Insert application first to get the ID
        result = supabase.table('tutor_applications').insert(data).execute()
        
        if result.data:
            application_id = result.data[0]['id']
            
            # Handle file uploads
            file_fields = {
                'profile_picture': 'profile-pictures',
                'matric_certificate': 'matric-certificates',
                'varsity_results': 'varsity-results',
                'cv': 'cvs',
                'id_copy': 'id-copies'
            }
            
            file_updates = {}
            
            for field_name, folder in file_fields.items():
                if request.files.get(field_name):
                    file = request.files[field_name]
                    if file.filename:
                        upload_result = upload_file_to_supabase(
                            file, 
                            'tutor-applications', 
                            f"{folder}/{application_id}"
                        )
                        
                        if upload_result['success']:
                            file_updates[f'{field_name}_url'] = upload_result['url']
                            file_updates[f'{field_name}_filename'] = upload_result['filename']
            
            # Update application with file URLs
            if file_updates:
                supabase.table('tutor_applications').update(file_updates).eq('id', application_id).execute()
        
        flash(f'Thank you! Your tutor application has been submitted successfully.', 'success')
        
    except Exception as e:
        flash('There was an error submitting your application. Please try again.', 'error')
        print(f"Error submitting tutor application: {e}")
    
    return redirect(url_for('become_tutor'))
```

## Step 4: Environment Variables

Add these to your .env file:

```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
```

## Step 5: Install Required Dependencies

```bash
pip install supabase python-multipart
```

## Security Considerations

1. **File Type Validation**: Always validate file types on both client and server side
2. **File Size Limits**: Set appropriate file size limits (5MB for images, 10MB for documents)
3. **Virus Scanning**: Consider adding virus scanning for uploaded files
4. **Access Control**: Use proper RLS policies to control who can access files
5. **File Naming**: Use UUIDs to prevent filename conflicts and improve security

## Alternative: Direct Upload from Frontend

For better performance, you can also implement direct uploads from the frontend:

```javascript
// Frontend direct upload to Supabase Storage
const uploadFile = async (file, bucket, path) => {
    const { data, error } = await supabase.storage
        .from(bucket)
        .upload(path, file, {
            cacheControl: '3600',
            upsert: false
        });
    
    if (error) {
        console.error('Upload error:', error);
        return null;
    }
    
    return data;
};
```
