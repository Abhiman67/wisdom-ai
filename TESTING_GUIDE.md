# Phase 7A Testing Guide

## Quick Testing Steps

### Prerequisites
```powershell
cd C:\Users\shash\Downloads\bhagavad_gita_finetune
.venv\Scripts\python.exe -m pip install -r requirements_ui.txt
```

---

## Test 1: Simple Q&A UI (5 minutes)

### Step 1: Launch UI
```powershell
.venv\Scripts\python.exe gradio_ui.py
```

**Expected:** 
- Model loads in ~30-40 seconds
- Console shows "✓ Model loaded successfully!"
- "✓ Server starting on http://localhost:7860"
- Browser opens automatically (or open manually)

### Step 2: Test Example Questions
1. Click "Example Questions" dropdown
2. Select "What is karma yoga?"
3. Click "Ask" button
4. **Expected:** Response appears in ~2-4 seconds
5. Try 2-3 more examples

### Step 3: Test Advanced Settings
1. Open "⚙️ Advanced Settings" accordion
2. Set Temperature to 0.5
3. Set Max Response Length to 200
4. Set Repetition Penalty to 1.3
5. Ask: "What is dharma?"
6. **Expected:** Response is shorter (~200 tokens) and more focused

### Step 4: Test Streaming
1. Enable "Enable Streaming" checkbox
2. Ask: "Explain Chapter 2 Verse 47"
3. **Expected:** Words appear one-by-one (not all at once)
4. Disable streaming checkbox
5. Ask another question
6. **Expected:** Full response appears instantly

### Step 5: Test Copy Button
1. Generate any response
2. Click copy button (top-right of answer box)
3. Paste in Notepad
4. **Expected:** Response text copies correctly

**✅ If all 5 steps pass, Simple Q&A is working!**

---

## Test 2: Chat Mode (5 minutes)

### Step 1: Switch to Chat Tab
1. Click "Chat / Conversation" tab at top
2. **Expected:** Chatbot widget appears

### Step 2: Test Conversation Memory
1. Type: "What is karma yoga?"
2. Click "Send" (or press Enter)
3. **Expected:** Response appears in chat
4. Type: "How is it different from bhakti yoga?"
5. Click "Send"
6. **Expected:** Response references previous answer about karma yoga

### Step 3: Test Clear Button
1. Click "🗑️ Clear Conversation"
2. **Expected:** Chat history disappears
3. **Expected:** Status shows "Conversation cleared!"

### Step 4: Test Export (Text)
1. Have 2-3 exchanges in chat
2. Select "Text" from "Export Format" dropdown
3. Click "📥 Export"
4. **Expected:** File downloads (conversation_TIMESTAMP.txt)
5. Open file in Notepad
6. **Expected:** Shows all Q&A pairs with timestamps

### Step 5: Test Export (Markdown)
1. Select "Markdown" from dropdown
2. Click "📥 Export"
3. **Expected:** File downloads (conversation_TIMESTAMP.md)
4. Open in VS Code or browser
5. **Expected:** Formatted with headers and dividers

### Step 6: Test Export (JSON)
1. Select "JSON" from dropdown
2. Click "📥 Export"
3. **Expected:** File downloads (conversation_TIMESTAMP.json)
4. Open in VS Code
5. **Expected:** Structured JSON with "question" and "answer" fields

**✅ If all 6 steps pass, Chat Mode is working!**

---

## Test 3: Batch Processing (5 minutes)

### Step 1: Verify Test File
```powershell
type test_questions.csv
```

**Expected:** Shows 8 questions

### Step 2: Run Batch Processing
```powershell
.venv\Scripts\python.exe batch_process.py -i test_questions.csv -o test_answers.csv
```

**Expected:**
- Model loads (~30s)
- Progress bar: "Generating answers: 100%|████| 8/8"
- Summary statistics printed:
  ```
  ✓ Batch processing complete!
  📁 Output saved to: test_answers.csv
  📊 Summary Statistics:
     • Total questions: 8
     • Successful: 8
     • Failed: 0
     • Total time: 24.3s (0.4 min)
     • Average time per question: 3.04s
  ```

### Step 3: Verify Output CSV
```powershell
type test_answers.csv
```

**Expected:** CSV with columns:
- `question_id`
- `question`
- `answer`
- `inference_time_seconds`
- `answer_length_chars`
- `timestamp`

### Step 4: Open in Excel/Sheets
1. Open `test_answers.csv` in Excel or Google Sheets
2. **Expected:** 8 rows + header row
3. **Expected:** All answers are coherent and relevant

### Step 5: Test Custom Parameters
```powershell
.venv\Scripts\python.exe batch_process.py ^
  -i test_questions.csv ^
  -o test_answers_custom.csv ^
  --temperature 0.5 ^
  --max_tokens 200 ^
  --repetition_penalty 1.3
```

**Expected:** Shorter, more focused answers

**✅ If all 5 steps pass, Batch Processing is working!**

---

## Test 4: Streaming Verification (2 minutes)

### Test in Simple Q&A
1. Enable streaming checkbox
2. Ask: "Summarize the essence of the Gita in simple terms"
3. **Watch carefully:** Words should appear progressively, not all at once
4. Count seconds: Should take 5-10 seconds to complete
5. **No freezing:** UI should remain responsive

### Test in Chat Mode
1. Go to Chat tab
2. Open "⚙️ Chat Settings"
3. Enable "Enable Streaming"
4. Ask any question
5. **Expected:** Same progressive word appearance

**✅ If words appear one-by-one in both modes, streaming is working!**

---

## Full Test Checklist

Copy this to track your progress:

```
[ ] Test 1: Simple Q&A UI
    [ ] Model loads successfully
    [ ] Example questions work
    [ ] Advanced settings apply
    [ ] Streaming toggle works
    [ ] Copy button works

[ ] Test 2: Chat Mode
    [ ] Conversation memory works (follow-ups use context)
    [ ] Clear button resets chat
    [ ] Export to Text works
    [ ] Export to Markdown works
    [ ] Export to JSON works

[ ] Test 3: Batch Processing
    [ ] Processes all 8 test questions
    [ ] Creates output CSV correctly
    [ ] Summary statistics display
    [ ] Custom parameters work

[ ] Test 4: Streaming
    [ ] Streaming works in Simple Q&A
    [ ] Streaming works in Chat Mode
    [ ] No UI freezing
    [ ] Instant mode works when disabled
```

---

## If Something Fails

### Model won't load
**Symptoms:** Error on startup, "Model not loaded" message
**Solutions:**
```powershell
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Verify adapter exists
dir lora_mistral_bhagavad

# Check if 3-epoch training completed
# If not, model may be from 1-epoch training (still works but lower quality)
```

### Port already in use
**Symptoms:** "Address already in use" error
**Solution:**
```powershell
# Use different port
.venv\Scripts\python.exe gradio_ui.py --port 8080
```

### Streaming not appearing word-by-word
**Symptoms:** Full response appears instantly even with streaming enabled
**Solutions:**
- Check "Enable Streaming" checkbox is actually checked
- Try disabling browser extensions (some block streaming)
- Try different browser (Chrome/Edge/Firefox)
- If still fails, streaming functionality exists but browser may not render progressively

### Batch processing errors
**Symptoms:** "No questions found" error
**Solution:**
```powershell
# Verify CSV format
type test_questions.csv

# Should have "question" header (case-insensitive)
# If your CSV has different column name, edit the CSV or modify batch_process.py
```

### Out of memory
**Symptoms:** CUDA out of memory error
**Solutions:**
- Close other applications using GPU
- Reduce `--max_tokens` to 200
- Restart Python to clear GPU memory

---

## Performance Benchmarks

**Expected performance on RTX 4050:**

| Operation | Time | Notes |
|-----------|------|-------|
| Model loading | 30-40s | One-time on startup |
| Simple Q&A response | 2-4s | Instant mode |
| Streaming response | 5-10s | Perceived as faster |
| Chat with context | 3-5s | Slightly slower |
| Batch processing (8 questions) | 24-32s | ~3-4s per question |

**If times are significantly slower:**
- Check GPU utilization: `nvidia-smi`
- Verify 4-bit quantization is active (model loads in ~30s, not 2-3 minutes)
- Close background applications

---

## Next Steps After Testing

### If all tests pass ✅
1. Mark Test todos as complete in manage_todo_list
2. Report back: "All Phase 7A tests passed!"
3. Discuss next phase (7B: Model Optimization or evaluate 3-epoch training)

### If some tests fail ❌
1. Note which specific tests failed
2. Share error messages
3. We'll debug together

---

## Quick Commands Reference

```powershell
# Launch UI
.venv\Scripts\python.exe gradio_ui.py

# Launch with public link
.venv\Scripts\python.exe gradio_ui.py --share

# Launch without streaming default
.venv\Scripts\python.exe gradio_ui.py --no-streaming

# Batch process
.venv\Scripts\python.exe batch_process.py -i test_questions.csv -o test_answers.csv

# Check training status
# (Terminal ID: 7400b002-5bf6-4ef0-b9fd-2336a48732e4)
# Wait for "Training completed!" message
```

Happy testing! 🕉️
