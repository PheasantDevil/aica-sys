-- Row Level Security (RLS) Policies for AICA-SyS
-- This file contains all RLS policies for the database tables

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletters ENABLE ROW LEVEL SECURITY;
ALTER TABLE trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE collection_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Articles table policies
CREATE POLICY "Anyone can view published articles" ON articles
    FOR SELECT USING (status = 'published');

CREATE POLICY "Authenticated users can view their own articles" ON articles
    FOR SELECT USING (auth.uid() = author_id);

CREATE POLICY "Authors can insert their own articles" ON articles
    FOR INSERT WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Authors can update their own articles" ON articles
    FOR UPDATE USING (auth.uid() = author_id);

CREATE POLICY "Authors can delete their own articles" ON articles
    FOR DELETE USING (auth.uid() = author_id);

-- Newsletters table policies
CREATE POLICY "Anyone can view published newsletters" ON newsletters
    FOR SELECT USING (status = 'published');

CREATE POLICY "Authenticated users can view their own newsletters" ON newsletters
    FOR SELECT USING (auth.uid() = author_id);

CREATE POLICY "Authors can insert their own newsletters" ON newsletters
    FOR INSERT WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Authors can update their own newsletters" ON newsletters
    FOR UPDATE USING (auth.uid() = author_id);

CREATE POLICY "Authors can delete their own newsletters" ON newsletters
    FOR DELETE USING (auth.uid() = author_id);

-- Trends table policies
CREATE POLICY "Anyone can view published trends" ON trends
    FOR SELECT USING (status = 'published');

CREATE POLICY "Authenticated users can view their own trends" ON trends
    FOR SELECT USING (auth.uid() = author_id);

CREATE POLICY "Authors can insert their own trends" ON trends
    FOR INSERT WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Authors can update their own trends" ON trends
    FOR UPDATE USING (auth.uid() = author_id);

CREATE POLICY "Authors can delete their own trends" ON trends
    FOR DELETE USING (auth.uid() = author_id);

-- Collection Jobs table policies
CREATE POLICY "Users can view their own collection jobs" ON collection_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own collection jobs" ON collection_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own collection jobs" ON collection_jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own collection jobs" ON collection_jobs
    FOR DELETE USING (auth.uid() = user_id);

-- Analysis Results table policies
CREATE POLICY "Users can view their own analysis results" ON analysis_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own analysis results" ON analysis_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own analysis results" ON analysis_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own analysis results" ON analysis_results
    FOR DELETE USING (auth.uid() = user_id);

-- Subscriptions table policies
CREATE POLICY "Users can view their own subscriptions" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own subscriptions" ON subscriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own subscriptions" ON subscriptions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own subscriptions" ON subscriptions
    FOR DELETE USING (auth.uid() = user_id);

-- Admin policies (for superusers)
CREATE POLICY "Admins can view all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all articles" ON articles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all newsletters" ON newsletters
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all trends" ON trends
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all collection jobs" ON collection_jobs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all analysis results" ON analysis_results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can view all subscriptions" ON subscriptions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );
