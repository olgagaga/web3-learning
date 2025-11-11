# Writing Coach Module

The Writing Coach module provides AI-powered essay feedback using Gemini AI with IELTS/TOEFL rubric-based scoring.

## Features

### 1. Essay Prompts
- 8 pre-loaded prompts across difficulty levels
- Multiple essay types: Opinion, Discussion, Advantages/Disadvantages, Problem/Solution
- Word count guidelines (200-350 words)
- Time limits (40 minutes)

### 2. AI-Powered Scoring
- **Task Response (0-9)**: How well the essay addresses the prompt
- **Coherence and Cohesion (0-9)**: Organization and logical flow
- **Lexical Resource (0-9)**: Vocabulary range and accuracy
- **Grammatical Range (0-9)**: Grammar variety and correctness
- **Overall Score**: Average of all criteria

### 3. Detailed Feedback
- **Strengths**: What you did well
- **Weaknesses**: Areas needing improvement
- **Criterion-specific feedback**: Detailed analysis for each rubric
- **Actionable suggestions**: Specific improvements to make
- **Revised outline**: Suggested structure for improvement

### 4. Revision System
- One-click revision button
- Pre-filled with previous content
- Track revision numbers
- Compare scores across submissions
- Show improvement over time

## Setup Instructions

### 1. Database Setup

Ensure the database tables are created (already in schema.sql):
- `essay_prompts` - Essay prompts
- `essays` - User submissions with scores

### 2. Seed Essay Prompts

From the server directory:

```bash
cd server
source venv/bin/activate
python -m database.seed_writing_data
```

This creates 8 essay prompts:
- **Easy**: 2 prompts (Learning English, Exercise Benefits)
- **Medium**: 3 prompts (Technology in Education, Working from Home, Environment)
- **Hard**: 3 prompts (Social Media, AI in Workplace, Globalization)

### 3. Configure Gemini API (Optional)

Add your Gemini API key to `server/.env`:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

**Without Gemini API**: The system uses mock feedback for development. Scores are based on word count and length, with generic feedback.

**With Gemini API**: Get detailed, personalized AI feedback tailored to your specific essay.

### 4. Start Servers

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

### Get Essay Prompts
```
GET /api/writing/prompts?difficulty={easy|medium|hard}
```

### Get Specific Prompt
```
GET /api/writing/prompts/{prompt_id}
```

### Submit Essay
```
POST /api/writing/submit
```

**Request:**
```json
{
  "prompt_id": 1,
  "content": "Essay text here...",
  "parent_essay_id": null  // For revisions, ID of original essay
}
```

**Response:**
```json
{
  "id": 1,
  "prompt_id": 1,
  "prompt_title": "Technology and Education",
  "content": "...",
  "word_count": 267,
  "scores": {
    "task_response_score": 7.0,
    "coherence_cohesion_score": 6.5,
    "lexical_resource_score": 6.0,
    "grammatical_range_score": 6.5,
    "overall_score": 6.5
  },
  "feedback": {
    "strengths": ["Clear thesis", "Good examples", ...],
    "weaknesses": ["Limited vocabulary", ...],
    "task_response": "Detailed feedback...",
    "coherence_cohesion": "...",
    "lexical_resource": "...",
    "grammatical_range": "...",
    "suggestions": ["Add counterarguments", ...],
    "revised_outline": "Suggested structure..."
  },
  "submission_number": 1,
  "parent_essay_id": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get User Essays
```
GET /api/writing/essays?limit=10
```

### Get Specific Essay
```
GET /api/writing/essays/{essay_id}
```

### Get Essay Revisions
```
GET /api/writing/essays/{essay_id}/revisions
```

### Get Writing Statistics
```
GET /api/writing/stats
```

**Response:**
```json
{
  "total_essays": 12,
  "average_score": 6.8,
  "best_score": 7.5,
  "total_revisions": 4,
  "average_word_count": 267,
  "score_trends": [
    {
      "date": "2024-01-15T10:30:00Z",
      "overall_score": 6.5,
      "submission_number": 1
    }
  ],
  "skill_averages": {
    "task_response": 6.7,
    "coherence_cohesion": 6.8,
    "lexical_resource": 6.5,
    "grammatical_range": 6.9
  }
}
```

## Frontend Components

### WritingPage
Main container with three views:
1. **Prompts View**: Browse and select essay prompts
2. **Editor View**: Write essays with word counter
3. **Feedback View**: View scores and AI feedback

### EssayPromptCard
- Displays prompt title, excerpt, and metadata
- Color-coded difficulty badges
- Clickable to start writing

### EssayEditor
- Large textarea for essay composition
- Real-time word counter with min/max indicators
- Validates word count before submission
- Pre-fills content for revisions

### EssayFeedback
- Overall score with color coding (red <5.5, yellow 5.5-7, green 7+)
- Individual criterion scores (4 rubric areas)
- Strengths (green card)
- Weaknesses (yellow card)
- Detailed feedback per criterion
- Suggestions (blue card)
- Revised outline (purple card)
- Revision CTA button

## User Flow

1. **Browse Prompts** → View available essay prompts by difficulty
2. **Select Prompt** → Click a prompt card to start writing
3. **Write Essay** → Compose 200-300 word essay in editor
4. **Submit** → Get instant AI feedback (5-10 seconds)
5. **Review Feedback** → See scores and detailed suggestions
6. **Revise** → Click "Revise Essay" to improve
7. **Resubmit** → Submit revision and see score improvement

## Scoring Algorithm

### Without Gemini API (Mock Mode)
- Base score: 6.5
- Length bonus: +0.5 if 200-300 words
- Simple, consistent feedback for testing

### With Gemini API
Gemini analyzes:
- How well the essay addresses the prompt
- Logical organization and transitions
- Vocabulary variety and accuracy
- Grammar complexity and correctness
- Provides specific, actionable feedback
- Tailored suggestions for improvement

## Revision Tracking

Each revision:
- Links to parent essay (`parent_essay_id`)
- Increments `submission_number`
- Tracks improvement over time
- Allows comparison between versions

Example progression:
- Essay 1 (Initial): Score 6.0
- Essay 2 (Revision 1): Score 6.8 (improved!)
- Essay 3 (Revision 2): Score 7.2 (keep improving!)

## Database Schema

### essay_prompts
- id, title, prompt_text, essay_type, difficulty
- word_count_min, word_count_max, time_limit_minutes

### essays
- id, user_id, prompt_id, content, word_count
- task_response_score, coherence_cohesion_score, lexical_resource_score, grammatical_range_score, overall_score
- ai_feedback (JSON), submission_number, parent_essay_id
- created_at

## Adding More Prompts

### Method 1: Database Insert
```sql
INSERT INTO essay_prompts (title, prompt_text, essay_type, difficulty, word_count_min, word_count_max)
VALUES (
  'Your Title',
  'Your prompt text...',
  'opinion',
  'medium',
  200,
  300
);
```

### Method 2: Extend Seed Script
Edit `server/database/seed_writing_data.py` and add more `EssayPrompt` objects.

## Gemini API Integration

### Getting an API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `server/.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ```

### API Usage

The `GeminiService` class:
- Sends essay + prompt to Gemini
- Requests structured JSON response
- Parses scores and feedback
- Falls back to mock data on error

### Prompt Engineering

The scoring prompt includes:
- Clear rubric definitions
- Structured JSON format requirement
- Instructions for constructive feedback
- Examples of good feedback

## Testing the Module

1. **Register/Login** to the platform
2. **Navigate** to Writing Coach
3. **Select** an easy prompt to start
4. **Write** a 200-word essay
5. **Submit** and observe feedback (5-10 sec wait)
6. **Review** scores and suggestions
7. **Revise** the essay with improvements
8. **Compare** original vs revised scores

## Future Enhancements

- [ ] Timer during writing (40-minute countdown)
- [ ] Auto-save drafts
- [ ] Essay templates and examples
- [ ] Peer review system
- [ ] Writing analytics dashboard
- [ ] Grammar checker integration
- [ ] Plagiarism detection
- [ ] Export essays as PDF
- [ ] Writing streaks and goals
- [ ] Vocabulary builder from essays
- [ ] Compare with other users' essays (anonymized)
- [ ] Video lessons on essay structure
- [ ] Writing challenges and competitions

## Troubleshooting

### Mock Feedback Instead of Gemini
- Check `GEMINI_API_KEY` is set in `.env`
- Verify API key is valid
- Check console logs for errors

### Slow Feedback
- Gemini API can take 5-10 seconds
- Consider adding loading animation
- Check internet connection

### Database Errors
- Ensure tables are created (`schema.sql`)
- Run seed script for prompts
- Check database connection in `.env`

## Best Practices for Users

1. **Read prompt carefully** before writing
2. **Plan structure** (intro, body, conclusion)
3. **Use specific examples** from knowledge/experience
4. **Vary sentence structure** for better scores
5. **Revise based on feedback** - scores improve!
6. **Track progress** over multiple essays
7. **Practice regularly** for best results

## Scoring Interpretation

- **9.0**: Expert user - exceptional control
- **8.0-8.5**: Very good user - fully operational
- **7.0-7.5**: Good user - operational with occasional issues
- **6.0-6.5**: Competent user - adequate for most purposes
- **5.0-5.5**: Modest user - partial command
- **Below 5.0**: Needs significant improvement

The system aims to help users progress from 5-6 range to 7-8 range through targeted feedback and revision.
