-- Fix Tutor Applications Table - Add Missing Columns
-- Run this SQL in your Supabase SQL Editor to add missing columns

-- Add missing columns for tutoring information
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS institutions_to_tutor TEXT;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS tutoring_method VARCHAR(50);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS tutoring_experience TEXT;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS availability TEXT;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS transport BOOLEAN DEFAULT FALSE;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS preferred_locations TEXT;

-- Add missing columns for personal information
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS id_number VARCHAR(50);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS address TEXT;

-- Add missing columns for educational background
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS highest_qualification VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS institution VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS year_completed INTEGER;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS current_student BOOLEAN DEFAULT FALSE;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS current_institution VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS current_year INTEGER;

-- Add missing columns for tutoring subjects
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS subjects_to_tutor TEXT;

-- Add missing columns for file storage (if not already added)
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS profile_picture_url VARCHAR(500);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS profile_picture_filename VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS profile_picture_storage_path VARCHAR(500);

ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS matric_certificate_url VARCHAR(500);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS matric_certificate_filename VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS matric_certificate_storage_path VARCHAR(500);

ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS varsity_results_url VARCHAR(500);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS varsity_results_filename VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS varsity_results_storage_path VARCHAR(500);

ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS cv_url VARCHAR(500);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS cv_filename VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS cv_storage_path VARCHAR(500);

-- Add missing status tracking columns
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS approved_by VARCHAR(255);
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS notes TEXT;

-- Ensure status column exists with default
ALTER TABLE tutor_applications ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tutor_applications_email ON tutor_applications(email);
CREATE INDEX IF NOT EXISTS idx_tutor_applications_status ON tutor_applications(status);
CREATE INDEX IF NOT EXISTS idx_tutor_applications_created_at ON tutor_applications(created_at DESC);

-- Add updated_at trigger if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_tutor_applications_updated_at ON tutor_applications;
CREATE TRIGGER update_tutor_applications_updated_at BEFORE UPDATE
    ON tutor_applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Verify the table structure (optional - just for checking)
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'tutor_applications' 
-- ORDER BY ordinal_position;
