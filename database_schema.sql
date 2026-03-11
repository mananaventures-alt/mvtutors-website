-- MV Tutors Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Create tutor_requests table
CREATE TABLE IF NOT EXISTS tutor_requests (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    contact_number VARCHAR(20),
    tutoring_service VARCHAR(50),
    group_size INTEGER,
    institution VARCHAR(50),
    grade_year VARCHAR(50),
    tutoring_type VARCHAR(50),
    subjects TEXT,
    reason TEXT,
    start_date DATE,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending'
);

-- Create tutor_applications table
CREATE TABLE IF NOT EXISTS tutor_applications (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    id_number VARCHAR(20),
    address TEXT,
    highest_qualification VARCHAR(255),
    institution VARCHAR(255),
    year_completed INTEGER,
    current_student BOOLEAN DEFAULT FALSE,
    current_institution VARCHAR(255),
    current_year INTEGER,
    subjects_to_tutor TEXT,
    tutoring_experience TEXT,
    availability TEXT,
    transport BOOLEAN DEFAULT FALSE,
    preferred_locations TEXT,
    matric_certificate_filename VARCHAR(255),
    varsity_results_filename VARCHAR(255),
    cv_filename VARCHAR(255),
    id_copy_filename VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by VARCHAR(255)
);

-- Create approved_tutors table (for tutors that have been approved)
CREATE TABLE IF NOT EXISTS approved_tutors (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES tutor_applications(id),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    subjects TEXT,
    qualifications VARCHAR(255),
    experience_level VARCHAR(50),
    hourly_rate DECIMAL(10,2),
    availability TEXT,
    location_preference TEXT,
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_sessions INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create contact_messages table
CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    subject VARCHAR(255),
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'unread'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tutor_requests_status ON tutor_requests(status);
CREATE INDEX IF NOT EXISTS idx_tutor_requests_created_at ON tutor_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_tutor_applications_status ON tutor_applications(status);
CREATE INDEX IF NOT EXISTS idx_tutor_applications_created_at ON tutor_applications(created_at);
CREATE INDEX IF NOT EXISTS idx_approved_tutors_active ON approved_tutors(active);
CREATE INDEX IF NOT EXISTS idx_contact_messages_status ON contact_messages(status);

-- Enable Row Level Security (RLS)
ALTER TABLE tutor_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE approved_tutors ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;

-- Create policies for admin access (you'll need to create admin users separately)
-- For now, we'll allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users" ON tutor_requests
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON tutor_applications
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON approved_tutors
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON contact_messages
    FOR ALL USING (auth.role() = 'authenticated');

-- Insert sample admin user (you should change this password!)
-- Note: You'll need to create this user through Supabase Auth UI or API
-- This is just for reference
-- INSERT INTO auth.users (email, encrypted_password, email_confirmed_at, created_at, updated_at)
-- VALUES ('info@mvtutors.co.za', crypt('Mvtutors@123!', gen_salt('bf')), NOW(), NOW(), NOW());
