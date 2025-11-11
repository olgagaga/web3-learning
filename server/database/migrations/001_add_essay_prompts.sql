-- Migration: Add essay_prompts table and update essays table
-- Run with: psql -d web3_edu_platform -f server/database/migrations/001_add_essay_prompts.sql

-- Create essay_prompts table
CREATE TABLE IF NOT EXISTS essay_prompts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    prompt_text TEXT NOT NULL,
    essay_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    word_count_min INTEGER DEFAULT 200,
    word_count_max INTEGER DEFAULT 300,
    time_limit_minutes INTEGER DEFAULT 40,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Drop the old essays table if it exists (backup first if you have data!)
DROP TABLE IF EXISTS essays CASCADE;

-- Create new essays table with prompt_id
CREATE TABLE IF NOT EXISTS essays (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    prompt_id INTEGER REFERENCES essay_prompts(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    word_count INTEGER,

    -- AI scores
    task_response_score DECIMAL(3,1),
    coherence_cohesion_score DECIMAL(3,1),
    lexical_resource_score DECIMAL(3,1),
    grammatical_range_score DECIMAL(3,1),
    overall_score DECIMAL(3,1),

    -- AI feedback
    ai_feedback JSONB,

    -- Revision tracking
    submission_number INTEGER DEFAULT 1,
    parent_essay_id INTEGER REFERENCES essays(id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_essays_user ON essays(user_id);
CREATE INDEX IF NOT EXISTS idx_essays_prompt ON essays(prompt_id);
CREATE INDEX IF NOT EXISTS idx_essays_parent ON essays(parent_essay_id);

COMMIT;
