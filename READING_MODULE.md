# Reading Practice Module

The Reading Practice module is a complete adaptive learning system for IELTS/TOEFL reading comprehension.

## Features

### 1. Adaptive Difficulty
- Automatically adjusts difficulty based on user performance
- Aims for 70-80% success rate for optimal learning
- Algorithm:
  - Accuracy >= 80% → Hard level
  - Accuracy 60-80% → Medium level
  - Accuracy < 60% → Easy level

### 2. Instant Feedback
- Correct/incorrect indication with visual feedback
- Detailed explanations for each question
- Skill category tracking (inference, vocabulary, detail, main-idea)

### 3. Progress Tracking
- Total attempts counter
- Overall accuracy percentage
- Skill-by-skill breakdown
- Recommended difficulty level

### 4. Question Types
- Multiple choice (A, B, C, D)
- Various skill categories:
  - **Detail**: Finding specific information
  - **Main Idea**: Understanding overall purpose
  - **Inference**: Drawing conclusions
  - **Vocabulary**: Understanding word meanings
  - **Cause-Effect**: Understanding relationships

## Setup Instructions

### 1. Ensure Database is Running

Make sure PostgreSQL is running and the database is created:

```bash
sudo -u postgres psql -c "CREATE DATABASE web3_edu_platform;"
sudo -u postgres psql -d web3_edu_platform -f server/database/schema.sql
```

### 2. Seed Reading Data

From the server directory, run the seed script:

```bash
cd server
source venv/bin/activate
python -m database.seed_reading_data
```

This will create:
- 4 reading passages (2 easy, 1 medium, 1 hard)
- 18 comprehension questions with explanations
- Topics: Coffee History, Exercise Benefits, Wildlife Urbanization, Quantum Computing

### 3. Start the Servers

Terminal 1 (Backend):
```bash
cd server
source venv/bin/activate
python main.py
```

Terminal 2 (Frontend):
```bash
cd client
npm run dev
```

## API Endpoints

### Get Next Reading Item (Adaptive)
```
GET /api/reading/next?difficulty={easy|medium|hard}
```
If no difficulty specified, uses adaptive algorithm.

**Response:**
```json
{
  "id": 1,
  "title": "The History of Coffee",
  "passage": "...",
  "difficulty": "easy",
  "skill_tags": ["vocabulary", "main-idea"],
  "questions": [
    {
      "id": 1,
      "question": "...",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "skill_category": "detail"
    }
  ]
}
```

### Submit Answer
```
POST /api/reading/submit
```

**Request:**
```json
{
  "question_id": 1,
  "user_answer": "B",
  "time_spent_seconds": 45
}
```

**Response:**
```json
{
  "question_id": 1,
  "is_correct": true,
  "correct_answer": "B",
  "explanation": "The passage states...",
  "skill_category": "detail"
}
```

### Get User Statistics
```
GET /api/reading/stats
```

**Response:**
```json
{
  "total_attempts": 24,
  "correct_answers": 18,
  "accuracy": 75.0,
  "skill_breakdown": {
    "detail": {
      "correct": 8,
      "total": 10,
      "accuracy": 80.0
    },
    "inference": {
      "correct": 5,
      "total": 8,
      "accuracy": 62.5
    }
  },
  "recent_difficulty": "medium",
  "recommended_difficulty": "medium"
}
```

## Frontend Components

### ReadingPage
Main container component that manages:
- Loading reading items
- Question navigation
- Answer submission
- Difficulty selection

### ReadingPassage
Displays the reading passage with:
- Title
- Difficulty badge (color-coded)
- Formatted text with paragraphs

### QuestionCard
Interactive question component with:
- Question text
- Multiple choice options
- Submit button
- Instant feedback display
- Time tracking

### ReadingStats
Dashboard showing:
- Total attempts
- Overall accuracy
- Recommended difficulty level

## User Flow

1. **Load Page** → Adaptive algorithm selects appropriate difficulty
2. **Read Passage** → Split-screen view with passage on left
3. **Answer Question** → Select option and submit
4. **Receive Feedback** → Immediate correct/incorrect with explanation
5. **Next Question** → Continue through all questions in passage
6. **New Passage** → System selects next item based on performance

## Adaptive Algorithm Details

The system tracks the last 10 user attempts and calculates accuracy:

```python
# Example progression:
Initial: Medium difficulty (no history)
After 10 questions at 85% → Hard difficulty
After 10 hard questions at 55% → Medium difficulty
After 10 medium questions at 45% → Easy difficulty
```

## Database Schema

### reading_items
- id, title, passage, difficulty, skill_tags, created_at

### reading_questions
- id, reading_item_id, question, options (JSON), correct_answer, explanation, skill_category

### user_reading_attempts
- id, user_id, question_id, user_answer, is_correct, time_spent_seconds, attempted_at

## Adding More Content

To add more reading passages, you can:

1. **Manually insert into database:**
```sql
INSERT INTO reading_items (title, passage, difficulty, skill_tags)
VALUES ('Title', 'Passage text...', 'medium', ARRAY['inference', 'vocabulary']);

INSERT INTO reading_questions (reading_item_id, question, options, correct_answer, explanation, skill_category)
VALUES (1, 'Question?', '{"A": "...", "B": "...", "C": "...", "D": "..."}', 'B', 'Explanation', 'detail');
```

2. **Extend the seed script:**
Add more passages to `database/seed_reading_data.py`

3. **Create an admin interface** (future feature)

## Testing the Module

1. Register a new account
2. Navigate to Reading Practice
3. Answer questions and observe:
   - Instant feedback
   - Accuracy tracking
   - Difficulty adaptation
4. Try different difficulty levels manually using the dropdown
5. Complete multiple passages to see stats update

## Future Enhancements

- [ ] Timed reading challenges (boss mode)
- [ ] More question types (drag-and-drop, fill-in-blank)
- [ ] Reading speed tracking
- [ ] Vocabulary builder from passages
- [ ] Bookmark difficult questions
- [ ] Spaced repetition for missed questions
- [ ] Passage audio (listening practice)
- [ ] AI-generated passages using Gemini
- [ ] Collaborative reading (study groups)
