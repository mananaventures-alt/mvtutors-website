-- Update approved_tutors table to include all tutor application fields
-- This script adds new columns to match the tutor_applications table structure

-- Add personal information fields
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS id_number TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS address TEXT;

-- Add educational background fields
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS highest_qualification TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS institution TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS year_completed INTEGER;

-- Add current studies fields
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS current_student BOOLEAN DEFAULT FALSE;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS current_institution TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS current_year INTEGER;

-- Add tutoring preference fields
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS institutions_to_tutor TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS tutoring_method TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS tutoring_experience TEXT;

-- Add transport and location fields
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS transport BOOLEAN DEFAULT FALSE;
-- Note: location_preference already exists, keeping it for compatibility

-- Add file storage fields
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS profile_picture_url TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS profile_picture_filename TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS profile_picture_storage_path TEXT;

ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS matric_certificate_url TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS matric_certificate_filename TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS matric_certificate_storage_path TEXT;

ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS cv_url TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS cv_filename TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS cv_storage_path TEXT;

ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS varsity_results_url TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS varsity_results_filename TEXT;
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS varsity_results_storage_path TEXT;

-- Add administrative fields
ALTER TABLE approved_tutors ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_approved_tutors_email ON approved_tutors(email);
CREATE INDEX IF NOT EXISTS idx_approved_tutors_active ON approved_tutors(active);
CREATE INDEX IF NOT EXISTS idx_approved_tutors_approved_at ON approved_tutors(approved_at);
CREATE INDEX IF NOT EXISTS idx_approved_tutors_subjects ON approved_tutors USING gin(to_tsvector('english', subjects));

-- Update existing records to have approved_at if not set
UPDATE approved_tutors 
SET approved_at = created_at 
WHERE approved_at IS NULL;

-- Add comments for documentation
COMMENT ON TABLE approved_tutors IS 'Stores approved tutor information with complete application data';
COMMENT ON COLUMN approved_tutors.subjects IS 'Comma-separated list of subjects the tutor can teach';
COMMENT ON COLUMN approved_tutors.institutions_to_tutor IS 'Comma-separated list of institutions (high_school, varsity, etc.)';
COMMENT ON COLUMN approved_tutors.profile_picture_url IS 'URL to the profile picture in Supabase Storage';
COMMENT ON COLUMN approved_tutors.approved_at IS 'Timestamp when the tutor was approved';
