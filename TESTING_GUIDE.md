# Testing Guide

This doc is the quickest way to sanity-check the app after changes.

## What to test

- the Gradio UI
- the FastAPI backend
- the batch question runner
- streaming behavior
- basic saved-verse and profile flows

## 1) Gradio UI

Start the app:

```powershell
.\.venv\Scripts\python.exe gradio_ui.py
```

Then check:

- the page opens
- example questions work
- responses look coherent
- streaming can be turned on and off
- the copy button works

## 2) Chat flow

In the chat UI, try:

- asking a first question
- asking a follow-up question that depends on the first answer
- clearing the conversation
- starting a fresh thread

What you want to see:

- the assistant keeps enough context for follow-ups
- the conversation resets cleanly

## 3) Batch processing

Run a small batch:

```powershell
.\.venv\Scripts\python.exe batch_process.py -i test_questions.csv -o test_answers.csv
```

Check that:

- the output file is created
- each row has an answer
- timing information is written

## 4) Evaluation

Run the validation pass:

```powershell
.\.venv\Scripts\python.exe evaluate_model.py
```

For a faster sample:

```powershell
.\.venv\Scripts\python.exe evaluate_model.py --limit 10
```

What to look for:

- the outputs stay on topic
- the answers are verse-grounded
- the model is not repeating itself too much

## 5) Backend health

Start FastAPI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Then check:

```text
http://localhost:8000/health
```

## Quick checklist

- [ ] Gradio opens
- [ ] Example prompts work
- [ ] Streaming works
- [ ] Follow-up chat works
- [ ] Batch CSV export works
- [ ] Evaluation runs
- [ ] API health endpoint responds

## If something feels off

- if the model is slow, check GPU availability
- if the app errors on startup, confirm the LoRA adapter exists
- if streaming looks instant instead of progressive, try another browser
- if batch processing fails, make sure the CSV has a `question` column
