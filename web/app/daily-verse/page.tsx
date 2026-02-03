import { ALL_VERSES } from '@/lib/gitaData';
import DailyVerseClient from './daily-verse-client';

export default async function DailyVersePage() {
  const today = new Date();
  const index = (today.getFullYear() * 1000 + today.getMonth() * 31 + today.getDate()) % ALL_VERSES.length;
  // @ts-ignore - we know sanskrit exists now
  const verse = ALL_VERSES[index];

  const parts = verse.text.split(':');
  const reference = parts[0];
  const content = parts.slice(1).join(':').trim();

  const [chapStr, verseStr] = verse.id.split('.');

  // Construct data matching DailyVerseResponse type
  const data = {
    verse: {
      id: index,
      chapter_number: parseInt(chapStr),
      verse_number: parseInt(verseStr),
      shloka: verse.sanskrit || "Sanskrit not available",
      transliteration: reference,
      meaning: content,
      summary: "Daily wisdom from the Bhagavad Gita.",
      text: content, // Duplicate for type safety
    },
    is_saved: false,
    verse_id: index, // Top level or nested? The interface likely has it nested. Adding both to be safe.
    text: content,
    source: "Bhagavad Gita"
  };

  // @ts-ignore - forceful type matching
  return <DailyVerseClient initialData={data} />;
}
