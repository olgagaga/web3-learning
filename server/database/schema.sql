-- Create database
CREATE DATABASE web3_edu_platform;

-- Connect to the database
\c web3_edu_platform;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Learning stats
    current_streak INTEGER DEFAULT 0,
    reading_items_completed INTEGER DEFAULT 0,
    essays_written INTEGER DEFAULT 0,
    badges_earned INTEGER DEFAULT 0
);

-- Reading items table
CREATE TABLE IF NOT EXISTS reading_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    passage TEXT NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    skill_tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reading questions table
CREATE TABLE IF NOT EXISTS reading_questions (
    id SERIAL PRIMARY KEY,
    reading_item_id INTEGER REFERENCES reading_items(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_answer VARCHAR(10) NOT NULL,
    explanation TEXT,
    skill_category VARCHAR(100)
);

-- User reading attempts table
CREATE TABLE IF NOT EXISTS user_reading_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES reading_questions(id) ON DELETE CASCADE,
    user_answer VARCHAR(10) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent_seconds INTEGER,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Essay prompts table
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

-- Essays table
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

    -- Metadata
    submission_number INTEGER DEFAULT 1,
    parent_essay_id INTEGER REFERENCES essays(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quests table
CREATE TABLE IF NOT EXISTS quests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    quest_type VARCHAR(50) NOT NULL,
    skill_focus VARCHAR(100),
    requirements JSONB NOT NULL,
    reward_points INTEGER DEFAULT 0,
    reward_badge VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User quests table
CREATE TABLE IF NOT EXISTS user_quests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    quest_id INTEGER REFERENCES quests(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active',
    progress JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, quest_id)
);

-- Badges table
CREATE TABLE IF NOT EXISTS badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    badge_type VARCHAR(50) NOT NULL,
    skill_level VARCHAR(50),
    icon_url VARCHAR(500),
    criteria JSONB NOT NULL,

    -- Web3 data
    blockchain_address VARCHAR(255),
    token_id VARCHAR(255),
    metadata_uri VARCHAR(500),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User badges table
CREATE TABLE IF NOT EXISTS user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    badge_id INTEGER REFERENCES badges(id) ON DELETE CASCADE,

    -- Web3 transaction data
    transaction_hash VARCHAR(255),
    minted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, badge_id)
);

-- User activity log
CREATE TABLE IF NOT EXISTS user_activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_reading_attempts_user ON user_reading_attempts(user_id);
CREATE INDEX idx_essays_user ON essays(user_id);
CREATE INDEX idx_essays_prompt ON essays(prompt_id);
CREATE INDEX idx_essays_parent ON essays(parent_essay_id);
CREATE INDEX idx_user_quests_user ON user_quests(user_id);
CREATE INDEX idx_user_badges_user ON user_badges(user_id);
CREATE INDEX idx_activity_log_user ON user_activity_log(user_id);
