-- Wisdom AI Database Schema for Supabase
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard)

-- ============================================
-- PROFILES TABLE (extends Supabase auth.users)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  name TEXT,
  email TEXT,
  avatar_url TEXT,
  streak INTEGER DEFAULT 0,
  last_mood TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, name, email)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'name', NEW.email),
    NEW.email
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- SAVED VERSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.saved_verses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  verse_text TEXT NOT NULL,
  verse_source TEXT NOT NULL,
  reflection TEXT,
  saved_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.saved_verses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own saved verses" ON public.saved_verses
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can save verses" ON public.saved_verses
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own saved verses" ON public.saved_verses
  FOR DELETE USING (auth.uid() = user_id);

CREATE INDEX idx_saved_verses_user ON public.saved_verses(user_id);

-- ============================================
-- COLLECTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.collections (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  is_public BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own collections" ON public.collections
  FOR SELECT USING (auth.uid() = user_id OR is_public = TRUE);

CREATE POLICY "Users can create collections" ON public.collections
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own collections" ON public.collections
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own collections" ON public.collections
  FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- COLLECTION VERSES (junction table)
-- ============================================
CREATE TABLE IF NOT EXISTS public.collection_verses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  collection_id UUID REFERENCES public.collections(id) ON DELETE CASCADE NOT NULL,
  verse_text TEXT NOT NULL,
  verse_source TEXT NOT NULL,
  added_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.collection_verses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view collection verses" ON public.collection_verses
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.collections 
      WHERE id = collection_id AND (user_id = auth.uid() OR is_public = TRUE)
    )
  );

CREATE POLICY "Users can add to own collections" ON public.collection_verses
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.collections 
      WHERE id = collection_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete from own collections" ON public.collection_verses
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.collections 
      WHERE id = collection_id AND user_id = auth.uid()
    )
  );

-- ============================================
-- CHAT HISTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.chat_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  mood TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat history" ON public.chat_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert chat messages" ON public.chat_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE INDEX idx_chat_history_user ON public.chat_history(user_id, created_at DESC);

-- ============================================
-- MOOD HISTORY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.mood_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  mood TEXT NOT NULL,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.mood_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own mood history" ON public.mood_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert mood entries" ON public.mood_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE INDEX idx_mood_history_user ON public.mood_history(user_id, recorded_at DESC);

-- ============================================
-- READING PLANS TABLE (admin-managed)
-- ============================================
CREATE TABLE IF NOT EXISTS public.reading_plans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  duration_days INTEGER NOT NULL,
  verses JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.reading_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view reading plans" ON public.reading_plans
  FOR SELECT TO authenticated USING (TRUE);

-- ============================================
-- USER READING PLANS (enrollment)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_reading_plans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  plan_id UUID REFERENCES public.reading_plans(id) ON DELETE CASCADE NOT NULL,
  current_day INTEGER DEFAULT 1,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  UNIQUE(user_id, plan_id)
);

ALTER TABLE public.user_reading_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own enrollments" ON public.user_reading_plans
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can enroll in plans" ON public.user_reading_plans
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own progress" ON public.user_reading_plans
  FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- Insert sample reading plans
-- ============================================
INSERT INTO public.reading_plans (title, description, duration_days, verses) VALUES
(
  '7 Days of Peace',
  'A week-long journey through verses about finding inner peace and tranquility.',
  7,
  '[
    {"day": 1, "text": "Be still, and know that I am God.", "source": "Psalms 46:10"},
    {"day": 2, "text": "Peace I leave with you; my peace I give you.", "source": "John 14:27"},
    {"day": 3, "text": "You will keep in perfect peace those whose minds are steadfast.", "source": "Isaiah 26:3"},
    {"day": 4, "text": "The mind is restless and difficult to restrain, but it is subdued by practice.", "source": "Bhagavad Gita 6:35"},
    {"day": 5, "text": "Verily, in the remembrance of Allah do hearts find rest.", "source": "Quran 13:28"},
    {"day": 6, "text": "Let not your heart be troubled, neither let it be afraid.", "source": "John 14:27"},
    {"day": 7, "text": "When meditation is mastered, the mind is unwavering like the flame of a candle in a windless place.", "source": "Bhagavad Gita 6:19"}
  ]'
),
(
  '14 Days of Wisdom',
  'Two weeks exploring wisdom teachings from sacred texts around the world.',
  14,
  '[
    {"day": 1, "text": "The fear of the Lord is the beginning of wisdom.", "source": "Proverbs 9:10"},
    {"day": 2, "text": "Wisdom is better than rubies; and all the things that may be desired are not to be compared to it.", "source": "Proverbs 8:11"},
    {"day": 3, "text": "One who has control over the mind is tranquil in heat and cold, pleasure and pain.", "source": "Bhagavad Gita 6:7"},
    {"day": 4, "text": "And whoever is granted wisdom is indeed granted abundant good.", "source": "Quran 2:269"},
    {"day": 5, "text": "For wisdom is a defence, and money is a defence: but the excellency of knowledge is, that wisdom giveth life.", "source": "Ecclesiastes 7:12"},
    {"day": 6, "text": "The wise see knowledge and action as one.", "source": "Bhagavad Gita 5:4"},
    {"day": 7, "text": "My Lord, increase me in knowledge.", "source": "Quran 20:114"},
    {"day": 8, "text": "Get wisdom, get understanding: forget it not.", "source": "Proverbs 4:5"},
    {"day": 9, "text": "Those who have wisdom know themselves.", "source": "Bhagavad Gita 4:38"},
    {"day": 10, "text": "Indeed, the patient will be given their reward without account.", "source": "Quran 39:10"},
    {"day": 11, "text": "A wise man will hear, and will increase learning.", "source": "Proverbs 1:5"},
    {"day": 12, "text": "The senses are higher than the body, the mind higher than the senses.", "source": "Bhagavad Gita 3:42"},
    {"day": 13, "text": "So remember Me; I will remember you.", "source": "Quran 2:152"},
    {"day": 14, "text": "Happy is the man that findeth wisdom, and the man that getteth understanding.", "source": "Proverbs 3:13"}
  ]'
),
(
  '21 Days of Gratitude',
  'Three weeks cultivating a grateful heart through divine teachings.',
  21,
  '[
    {"day": 1, "text": "Give thanks to the Lord, for he is good.", "source": "Psalms 107:1"},
    {"day": 2, "text": "If you are grateful, I will surely increase you.", "source": "Quran 14:7"},
    {"day": 3, "text": "Content with whatever comes unsought.", "source": "Bhagavad Gita 3:22"},
    {"day": 4, "text": "In every thing give thanks.", "source": "1 Thessalonians 5:18"},
    {"day": 5, "text": "And be grateful to Me and do not deny Me.", "source": "Quran 2:152"},
    {"day": 6, "text": "A man is made by his belief. As he believes, so he is.", "source": "Bhagavad Gita 17:3"},
    {"day": 7, "text": "O give thanks unto the Lord; for he is good.", "source": "1 Chronicles 16:34"},
    {"day": 8, "text": "Which of the favors of your Lord would you deny?", "source": "Quran 55:13"},
    {"day": 9, "text": "Those who are always satisfied and self-controlled.", "source": "Bhagavad Gita 12:14"},
    {"day": 10, "text": "Enter into his gates with thanksgiving.", "source": "Psalms 100:4"},
    {"day": 11, "text": "And He gave you from all you asked of Him.", "source": "Quran 14:34"},
    {"day": 12, "text": "Whatever happened, happened for the good.", "source": "Bhagavad Gita 2:48"},
    {"day": 13, "text": "Giving thanks always for all things.", "source": "Ephesians 5:20"},
    {"day": 14, "text": "Allah is full of bounty to mankind.", "source": "Quran 2:243"},
    {"day": 15, "text": "They who know the Self as enjoyer of happiness become content.", "source": "Bhagavad Gita 5:29"},
    {"day": 16, "text": "It is a good thing to give thanks unto the Lord.", "source": "Psalms 92:1"},
    {"day": 17, "text": "Show gratitude to Allah.", "source": "Quran 31:12"},
    {"day": 18, "text": "One who is satisfied with whatever comes gains tranquility.", "source": "Bhagavad Gita 4:22"},
    {"day": 19, "text": "Thanks be unto God for his unspeakable gift.", "source": "2 Corinthians 9:15"},
    {"day": 20, "text": "He rewards the grateful.", "source": "Quran 3:145"},
    {"day": 21, "text": "When you are grateful, you find peace in any circumstance.", "source": "Bhagavad Gita 2:55"}
  ]'
);

-- Done! Your database is ready.
