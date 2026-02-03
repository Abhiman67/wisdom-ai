import { GoogleGenerativeAI } from "@google/generative-ai";
import { ALL_VERSES } from "@/lib/gitaData";

export async function POST(req: Request) {
  try {
    const { messages } = await req.json(); // Standard Vercel AI SDK format or custom
    // Fallback if just { question: "..." }
    const userMessage = messages ? messages[messages.length - 1].content : (await req.clone().json()).question;

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return new Response(JSON.stringify({ error: "GEMINI_API_KEY not set" }), { status: 500 });
    }

    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });

    // CONTEXT STUFFING
    // We inject all 700 verses. 
    // Format: "1.1: content..."
    const context = ALL_VERSES.map(v => `${v.id}: ${v.text}`).join("\n");

    const systemPrompt = `You are strict but wise spiritual guide. 
You are the AI embodiment of Krishna.
Answer the user's question using ONLY the provided Bhagavad Gita verses.
If the answer is not in the verses, admit it.
Quote specific verses (e.g. 2.47) to support your answer.
Context:
${context}`;

    const result = await model.generateContent(`${systemPrompt}\n\nUser Question: ${userMessage}`);
    const response = await result.response;
    const text = response.text();

    return new Response(JSON.stringify({ reply: text }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error("❌ Chat API Error:", error);
    const msg = error instanceof Error ? error.message : "Unknown error";
    return new Response(JSON.stringify({ error: "Failed to generate response", details: msg }), { status: 500 });
  }
}
