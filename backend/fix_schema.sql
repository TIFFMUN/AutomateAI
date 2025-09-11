-- Add missing personal_goals column to user_states table
ALTER TABLE user_states ADD COLUMN IF NOT EXISTS personal_goals JSONB DEFAULT '{"goals": [{"id": 1, "name": "Training", "progress": 0, "target": 100}, {"id": 2, "name": "Onboarding", "progress": 0, "target": 100}, {"id": 3, "name": "Project Delivery", "progress": 0, "target": 100}, {"id": 4, "name": "Skill Development", "progress": 0, "target": 100}]}';

-- Verify the column was added
\d user_states;
