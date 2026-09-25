# STUDY AGENT SPEC (Phased)

> How to use: Change the "CURRENT PHASE" line below, then give this whole file to your AI. The AI must build ONLY the current phase and keep earlier phases working.

**CURRENT PHASE: 1**

---

## 1. Project Overview

- **Project name:** Study Agent
- **One-line description:** A terminal AI agent that talks with students, summarizes their notes (PDF), and creates quizzes to help them learn.
- **Who it is for:** Students who want to revise faster.
- **Build plan:** Features are added one phase at a time. Each phase must work fully before the next begins and next phase will only begin when i approve the work and give prompt to start the 2nd phase.

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Chat: the agent talks with the student | To build |
| 2 | Summarize a PDF of notes | Not started |
| 3 | Create and run quizzes from the notes | Not started |
| 4+ | Future features (see Section 8) | Ideas only |

## 2. Environment

- **Where it runs:** GitHub Codespaces (terminal only)
- **Language:** Python
- **Libraries:** `openrouter` (Phase 1 onward), `pypdf` (Phase 2 onward)
- **API key:** Read from the api.gitignore `OPEN-ROUTER-API`. Never write the key inside the code.
- **Model:** MiMo-V2.6-Flash Free

## 3. Design Rule for Growth

> This keeps the project easy to extend in later phases.

- The main file is a loop that talks to the AI model.
- Every new feature (reading a PDF, making a quiz, and so on) is written as a **separate function**, so it can be added without rewriting the rest.
- Features the model can use are registered as **tools**. Adding a feature later means adding one function and one tool description.

---

## PHASE 1: Chat agent

- **Goal:** The student types a message, the agent replies, and the conversation continues until the student quits.
- **Input:** Text typed in the terminal.
- **Output:** The agent's reply printed in the terminal.

**How it works:**
1. Print a short welcome message.
2. Ask the student for input.
3. If the student types `quit`, say goodbye and stop.
4. Otherwise send the message to the AI model, along with the earlier conversation so it remembers context.
5. Print the reply and repeat from step 2.

**The agent's personality (system instruction):** A friendly, clear study helper. Explains things simply, keeps answers short, and asks if the student wants more detail.

**Done when:**
- [ ] Runs with `python study_agent.py` without errors
- [ ] Agent remembers what was said earlier in the same session
- [ ] Typing `quit` ends the program cleanly
- [ ] Missing API key gives a clear message, then stops

---

## PHASE 2: Summarize PDF Notes

- **Goal:** The student gives a PDF file name, and the agent summarizes it.
- **Input:** A PDF file name (the file is in the same folder), for example: "Summarize notes.pdf".
- **Output:** A short summary in simple bullet points, printed in the terminal.
- **New tool:** `read_pdf`. Takes a file name and returns all the text from every page.

**How it works:**
1. The student asks for a summary in the chat.
2. The model asks to use `read_pdf` on the file.
3. The program reads the PDF and sends the text back to the model.
4. The model writes the summary and the program prints it.
5. Chat continues normally afterwards, so the student can ask follow-up questions about the notes.

**Errors:**
- File not found: tell the student, and let them try again.
- PDF has no text (scanned pages): tell the student no text was found.

**Done when:**
- [ ] Phase 1 still works
- [ ] A typed PDF is summarized correctly
- [ ] Follow-up questions about the notes work
- [ ] Both error cases are handled

---

## PHASE 3: Quizzes

- **Goal:** The agent creates a quiz from the student's notes and runs it in the terminal.
- **Input:** Student says something like "Quiz me on notes.pdf" (optional: number of questions, default 5).
- **Output:** One multiple-choice question at a time (options A to D), feedback after each answer, and a final score.
- **New tool:** Reuses `read_pdf`. Add one more tool if needed to keep track of the score.

**How it works:**
1. The agent reads the notes (using `read_pdf`).
2. It creates the questions from the notes only (not from outside knowledge).
3. It asks one question at a time and waits for the student's answer.
4. It says right or wrong, with a one-line explanation.
5. At the end it shows the score (for example, 4 out of 5) and offers to quiz again or revise weak topics.

**Rules:**
- Questions must come from the notes only.
- Exactly one correct answer per question.
- Student can type `stop` to leave the quiz early.

**Done when:**
- [ ] Phases 1 and 2 still work
- [ ] Quiz has the requested number of questions
- [ ] Each answer gets feedback
- [ ] Final score is shown
- [ ] `stop` exits the quiz without crashing

---

## 8. Future Ideas (DO NOT BUILD YET)

> Move an idea into a numbered phase above when you are ready.

- Flashcards from the notes
- Save summaries and quiz scores to a file
- Study plan based on exam date
- Explain a difficult topic in simpler words
- Support more file types (Word, text)
- Track weak topics across sessions

---

## 9. Coding Rules for the AI

- Keep the code **simple and beginner-friendly**.
- Use only basic constructs: `while`, `break`, `if`, `for`, functions, and variables.
- Avoid list comprehensions, `join`, lambdas, and classes (unless the API absolutely requires a list or dictionary).
- Add a short plain-English comment above each major step.
- Use clear variable names (`filename`, not `f`).
- Keep everything in as few files as possible: `study_agent.py` to start.

## 10. Instructions to the AI

- Build **only the current phase**. Do not add anything from later phases or from Section 8.
- Do not break features from earlier phases.
- Give the **complete, working code** for each file, ready to copy and run.
- Keep explanations **brief**. No long tutorials.
- List the exact terminal commands to install and run.
- If anything is unclear or missing, ask me **before** writing code.