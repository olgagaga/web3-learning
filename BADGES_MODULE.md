# Badges Module Implementation

Complete implementation of the badges system with automatic awarding, progress tracking, and beautiful UI.

## Overview

The badges module automatically tracks user achievements across reading, writing, and quest activities, awarding badges when criteria are met. Badges are displayed in a beautiful showcase with locked/unlocked states.

## Backend Components

### 1. Badge Service (`server/app/services/badge_service.py`)

Core service handling all badge logic:

#### Key Methods:
- **`check_and_award_badges(db, user_id)`**: Automatically checks all badge criteria and awards eligible badges
- **`award_badge(db, user_id, badge_id, transaction_hash=None)`**: Awards a specific badge
- **`_meets_badge_criteria(db, user_id, badge)`**: Checks if user meets all badge requirements
- **`get_badge_progress(db, user_id, badge_id)`**: Returns progress toward specific badge
- **`get_user_badge_showcase(db, user_id)`**: Returns organized badge collection by category

#### Badge Criteria Supported:
- **Reading Accuracy**: Percentage of correct answers with minimum items completed
- **Writing Average Score**: Average essay score with minimum essay count
- **Minimum Score**: Any single essay achieving target score
- **Quests Completed**: Total quests completed
- **Weekly Quests**: Weekly quest completions
- **Boss Challenges**: Boss challenge completions (reading/writing)

### 2. Integration Points

**Reading Service** (`server/app/services/reading_service.py:131`):
```python
# Check and award badges after each reading answer
newly_earned_badges = BadgeService.check_and_award_badges(db, user_id)
return is_correct, question, newly_earned_badges
```

**Writing Service** (`server/app/services/writing_service.py:90`):
```python
# Check and award badges after essay submission
newly_earned_badges = BadgeService.check_and_award_badges(db, user_id)
return essay, newly_earned_badges
```

### 3. API Endpoints

All badge endpoints are in `server/app/api/routes/quests.py`:

- **`GET /api/quests/badges`**: Get user's earned badges
- **`GET /api/quests/badges/all`**: Get all available badges
- **`GET /api/quests/badges/showcase`**: Get organized badge showcase
- **`GET /api/quests/badges/{badge_id}/progress`**: Get progress toward specific badge

## Frontend Components

### 1. Badge Notification (`client/src/components/badges/BadgeNotification.jsx`)

Animated celebration modal that appears when badges are earned:

**Features:**
- 🎉 Celebration header with animation
- 🏆 Large badge icon with gradient background
- ✨ Bounce-in and scale animations
- 📜 Badge name, description, and type
- ➡️ Supports multiple badges (Next button)
- ❌ User-dismissible

**Usage:**
```jsx
<BadgeNotification
  badges={newlyEarnedBadges}
  onClose={() => setNewBadges([])}
/>
```

### 2. Badges Page (`client/src/pages/BadgesPage.jsx`)

Complete badge showcase page:

**Sections:**
1. **Stats Overview**: Total, Mastery, Achievement, Special badge counts
2. **Earned Badges**: Organized by category with full details
3. **Available Badges**: Locked badges showing what's possible to earn
4. **Empty State**: Call-to-action to view quests

**Features:**
- 🔒 Locked badge display (blurred with lock icon)
- 🎨 Gradient backgrounds based on badge type
- 📊 Statistics cards
- 🔄 Loading and error states

### 3. Badge Card (`client/src/components/quests/BadgeCard.jsx`)

Individual badge display component:

**Features:**
- Gradient icon background (type-based colors)
- Badge name and level
- Description
- Earned date
- Web3 verification indicator

### 4. API Service (`client/src/services/questsAPI.js`)

Badge-related API methods:
```javascript
questsAPI.getBadges()           // Get user's earned badges
questsAPI.getAllBadges()        // Get all available badges
questsAPI.getBadgeShowcase()    // Get organized showcase
questsAPI.getBadgeProgress(id)  // Get progress toward badge
```

## Database Models

### Badge Model (`app/models/quest.py`)
```python
class Badge(Base):
    id: Primary Key
    name: Badge name
    description: Badge description
    badge_type: "mastery" | "achievement" | "special"
    skill_level: "L1" | "L2" | "L3"
    icon_url: Icon file path
    criteria: JSON with requirements

    # Web3 fields (for future blockchain integration)
    blockchain_address: Contract address
    token_id: NFT token ID
    metadata_uri: IPFS metadata URI
```

### UserBadge Model
```python
class UserBadge(Base):
    id: Primary Key
    user_id: Foreign Key to users
    badge_id: Foreign Key to badges
    transaction_hash: Blockchain transaction hash
    minted_at: Timestamp when earned
```

## Badge Types & Examples

### Mastery Badges (🎓)
Reward long-term skill development:
- **Reading Mastery L1**: 70% accuracy + 50 items completed
- **Writing Mastery L1**: 6.5 average score + 10 essays

### Achievement Badges (🏆)
Reward specific accomplishments:
- **Beginner Badge**: Complete first quest
- **Excellence Badge**: Score 7.0+ on any essay
- **Weekly Champion**: Complete weekly quest

### Special Badges (⭐)
Reward exceptional achievements:
- **Reading Boss Conqueror**: Complete reading boss challenge
- **Writing Boss Conqueror**: Complete writing boss challenge

## How Badge Awarding Works

### Automatic Flow:

1. **User Activity**
   - User answers reading question OR submits essay

2. **Service Processing**
   - Activity is saved to database
   - User stats are updated
   - Quest progress is updated

3. **Badge Check** (Automatic)
   - `BadgeService.check_and_award_badges()` is called
   - All badge criteria are evaluated
   - Eligible badges are awarded

4. **Response**
   - API returns newly earned badges in response
   - Frontend can display BadgeNotification

5. **Display**
   - Badges appear in user's collection
   - Badge count is incremented
   - Badges visible in showcase page

### Example Response:
```json
{
  "question_id": 123,
  "is_correct": true,
  "correct_answer": "B",
  "explanation": "...",
  "newly_earned_badges": [
    {
      "id": 2,
      "name": "Reading Mastery L1",
      "description": "Mastered basic reading comprehension",
      "badge_type": "mastery",
      "icon_url": "/badges/reading-l1.png"
    }
  ]
}
```

## Badge Criteria Examples

### Reading Accuracy Badge
```json
{
  "reading_accuracy": 70,
  "items_completed": 50
}
```
User must achieve 70% accuracy AND complete at least 50 reading items.

### Writing Excellence Badge
```json
{
  "min_score": 7.0
}
```
User must achieve a score of 7.0 or higher on any single essay.

### Quest Achievement Badge
```json
{
  "quests_completed": 1
}
```
User must complete at least 1 quest.

### Boss Challenge Badge
```json
{
  "boss_reading": 1
}
```
User must complete at least 1 reading boss challenge.

## Testing the Module

### 1. Seed Badge Data
```bash
cd server
source venv/bin/activate
python -m database.seed_quest_data
```

### 2. Test Badge Awarding
1. Complete 5 reading items correctly → Should earn "First Steps" quest progress
2. Submit an essay → Should earn "First Steps" quest progress
3. Complete the quest → May earn "Beginner Badge"
4. Continue practicing → Progress toward mastery badges

### 3. View Badges
- Navigate to `/badges` page
- See earned badges organized by category
- See locked badges showing what's available

## Web3 Integration (Future)

The badge system is prepared for Web3 integration:

### Fields Available:
- `blockchain_address`: Smart contract address
- `token_id`: NFT token ID
- `metadata_uri`: IPFS metadata URI
- `transaction_hash`: Minting transaction hash

### Future Features:
- Mint badges as soulbound NFTs on Polygon
- Store metadata on IPFS
- Shareable public badge page with blockchain verification
- Custodial wallet integration (Web3Auth/Privy)

## API Reference

### Get User's Earned Badges
```
GET /api/quests/badges
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "badge_id": 2,
    "badge": { ... },
    "transaction_hash": null,
    "minted_at": "2025-11-10T12:00:00Z"
  }
]
```

### Get All Available Badges
```
GET /api/quests/badges/all
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "name": "Beginner Badge",
    "description": "...",
    "badge_type": "achievement",
    "criteria": { ... }
  }
]
```

### Get Badge Showcase
```
GET /api/quests/badges/showcase
Authorization: Bearer {token}

Response:
{
  "total_badges": 3,
  "mastery_badges": 1,
  "achievement_badges": 2,
  "special_badges": 0,
  "badges_by_category": {
    "mastery": [...],
    "achievement": [...],
    "special": [...]
  }
}
```

### Get Badge Progress
```
GET /api/quests/badges/{badge_id}/progress
Authorization: Bearer {token}

Response:
{
  "badge_id": 2,
  "earned": false,
  "progress": 65,
  "criteria_progress": {
    "reading_accuracy": {
      "current": 68.5,
      "required": 70,
      "items_completed": 45,
      "items_required": 50
    }
  }
}
```

## Summary

✅ **Complete badge system** with automatic awarding
✅ **7 pre-seeded badges** across 3 categories
✅ **Automatic integration** with reading and writing modules
✅ **Beautiful UI** with animations and locked states
✅ **Progress tracking** for each badge
✅ **Web3-ready** for future blockchain integration
✅ **Comprehensive API** for all badge operations

The badges module successfully gamifies the learning experience and provides tangible rewards for user achievements!
