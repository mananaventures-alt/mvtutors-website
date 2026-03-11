-- Updated Tutor Applications Table Schema for Supabase with S3 Storage Integration
-- Run this SQL in your Supabase SQL Editor

-- First, check if table exists and add new columns if needed
-- For existing tables, use ALTER TABLE to add new columns

-- Add new columns for file storage (if table already exists)
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

-- If creating a new table from scratch, use this instead:
/*
CREATE TABLE IF NOT EXISTS tutor_applications (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Personal Information
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    date_of_birth DATE,
    id_number VARCHAR(50),
    address TEXT,
    
    -- Educational Background
    highest_qualification VARCHAR(255),
    institution VARCHAR(255),
    year_completed INTEGER,
    current_student BOOLEAN DEFAULT FALSE,
    current_institution VARCHAR(255),
    current_year INTEGER,
    
    -- Tutoring Information
    institutions_to_tutor TEXT, -- "high_school, varsity"
    subjects_to_tutor TEXT NOT NULL, -- "mathematics, physics, chemistry"
    tutoring_method VARCHAR(50), -- "online", "in_person", "both"
    tutoring_experience TEXT,
    availability TEXT,
    transport BOOLEAN DEFAULT FALSE,
    preferred_locations TEXT,
    
    -- File Storage References (Supabase S3 Storage)
    profile_picture_url VARCHAR(500),
    profile_picture_filename VARCHAR(255),
    profile_picture_storage_path VARCHAR(500),
    
    matric_certificate_url VARCHAR(500),
    matric_certificate_filename VARCHAR(255),
    matric_certificate_storage_path VARCHAR(500),
    
    varsity_results_url VARCHAR(500),
    varsity_results_filename VARCHAR(255),
    varsity_results_storage_path VARCHAR(500),
    
    cv_url VARCHAR(500),
    cv_filename VARCHAR(255),
    cv_storage_path VARCHAR(500),
    
    -- Application Status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    approved_at TIMESTAMPTZ,
    approved_by VARCHAR(255),
    rejection_reason TEXT,
    notes TEXT
);
*/

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

-- Helper function to get signed URL for private files
CREATE OR REPLACE FUNCTION get_signed_url(bucket_name TEXT, file_path TEXT, expires_in INTEGER DEFAULT 3600)
RETURNS TEXT
LANGUAGE SQL
AS $$
    SELECT 
        CASE 
            WHEN bucket_name = 'tutor-profile-pictures' THEN 
                -- Public bucket - return public URL
                'https://jfsiusrstjoeudsvxhrt.supabase.co/storage/v1/object/public/' || bucket_name || '/' || file_path
            ELSE 
                -- Private bucket - would need signed URL (implement as needed)
                'https://jfsiusrstjoeudsvxhrt.supabase.co/storage/v1/object/sign/' || bucket_name || '/' || file_path
        END;
$$;
