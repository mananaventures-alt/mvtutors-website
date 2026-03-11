-- Drop the existing tutor_applications table
DROP TABLE IF EXISTS tutor_applications CASCADE;

-- Create the new tutor_applications table with all required fields
CREATE TABLE tutor_applications (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- Personal Information
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    date_of_birth DATE,
    id_number TEXT,
    address TEXT,
    
    -- Educational Background
    highest_qualification TEXT NOT NULL,
    institution TEXT NOT NULL,
    year_completed INTEGER,
    
    -- Current Studies (optional)
    current_student BOOLEAN DEFAULT FALSE,
    current_institution TEXT,
    current_year INTEGER,
    
    -- Tutoring Preferences
    institutions_to_tutor TEXT, -- comma-separated list
    subjects_to_tutor TEXT NOT NULL, -- comma-separated list
    tutoring_method TEXT, -- online, in_person, both
    tutoring_experience TEXT,
    availability TEXT,
    
    -- Transport & Location
    transport BOOLEAN DEFAULT FALSE,
    preferred_locations TEXT,
    
    -- File Storage URLs and Metadata
    profile_picture_url TEXT,
    profile_picture_filename TEXT,
    profile_picture_storage_path TEXT,
    
    matric_certificate_url TEXT,
    matric_certificate_filename TEXT,
    matric_certificate_storage_path TEXT,
    
    cv_url TEXT,
    cv_filename TEXT,
    cv_storage_path TEXT,
    
    varsity_results_url TEXT,
    varsity_results_filename TEXT,
    varsity_results_storage_path TEXT,
    
    -- Application Status and Administrative Fields
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'under_review')),
    approved_at TIMESTAMPTZ,
    approved_by TEXT,
    rejection_reason TEXT,
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_tutor_applications_email ON tutor_applications(email);
CREATE INDEX idx_tutor_applications_status ON tutor_applications(status);
CREATE INDEX idx_tutor_applications_created_at ON tutor_applications(created_at);
CREATE INDEX idx_tutor_applications_subjects ON tutor_applications USING gin(to_tsvector('english', subjects_to_tutor));

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tutor_applications_updated_at
    BEFORE UPDATE ON tutor_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE tutor_applications ENABLE ROW LEVEL SECURITY;

-- Create policy to allow anonymous users to insert applications
CREATE POLICY "Allow anonymous insert" ON tutor_applications
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Create policy to allow authenticated users to view all applications
CREATE POLICY "Allow authenticated select" ON tutor_applications
    FOR SELECT
    TO authenticated
    USING (true);

-- Create policy to allow authenticated users to update applications
CREATE POLICY "Allow authenticated update" ON tutor_applications
    FOR UPDATE
    TO authenticated
    USING (true);

-- Create policy to allow service role full access
CREATE POLICY "Allow service role all" ON tutor_applications
    FOR ALL
    TO service_role
    USING (true);

-- Grant necessary permissions
GRANT INSERT ON tutor_applications TO anon;
GRANT SELECT, UPDATE, DELETE ON tutor_applications TO authenticated;
GRANT ALL ON tutor_applications TO service_role;
GRANT USAGE, SELECT ON SEQUENCE tutor_applications_id_seq TO anon, authenticated, service_role;

-- Comment on table and important columns
COMMENT ON TABLE tutor_applications IS 'Stores tutor application submissions with file attachments';
COMMENT ON COLUMN tutor_applications.subjects_to_tutor IS 'Comma-separated list of subjects the tutor can teach';
COMMENT ON COLUMN tutor_applications.institutions_to_tutor IS 'Comma-separated list of institutions (high_school, varsity, etc.)';
COMMENT ON COLUMN tutor_applications.profile_picture_url IS 'URL to the profile picture in Supabase Storage';
COMMENT ON COLUMN tutor_applications.status IS 'Application status: pending, approved, rejected, under_review';
