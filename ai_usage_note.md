# AI Usage Note
## Project: Stored Procedure Documenter | Team 19
## Submitted to Infinite Computer Solutions

---

## 1. What AI Helped With

**Project Planning:** AI helped design the overall project structure, suggested the folder layout (input/, output/, tests/), and recommended using SQLGlot for SQL parsing combined with Code-Walking RAG technique.

**Core Code Development:** AI helped write the `walk_sql_code()` function that extracts 10 metadata points from SQL code including procedure name, parameters, tables, operations, conditions, error handling, transactions, return values, output parameters, and SELECT columns.

**Streamlit Web UI:** AI helped build the complete web interface including file uploader, sidebar API key input, progress bar, output display, download buttons per procedure, and dark themed styling.

**Prompt Engineering:** AI helped design the RAG-augmented prompt that sends structured metadata to Gemini instead of raw SQL — resulting in more accurate and detailed documentation output.

**Debugging:** AI helped fix the `CREATE.md` bug caused by incorrect regex matching on `[dbo].[ProcedureName]` format. Also helped resolve model not found errors and quota exhaustion issues by suggesting `gemini-2.0-flash-lite` as the working model.

**Security:** AI suggested using `python-dotenv` to hide the Gemini API key in a `.env` file instead of hardcoding it in source files — preventing accidental exposure on GitHub.

**Reliability:** AI suggested adding a 5 second delay between API calls and auto-retry logic to handle per-minute quota limits gracefully instead of crashing.

---

## 2. What AI Got Wrong

**SQLGlot Full Parsing:** AI suggested using SQLGlot's AST to fully parse T-SQL stored procedures. In practice, SQLGlot treats T-SQL procedures as `Command` nodes and falls back to basic parsing. We combined SQLGlot with regex-based code walking to properly extract all metadata.

**Wrong Model Names:** AI suggested `gemini-1.5-flash` and `gemini-1.5-flash-8b` as alternatives when quota was exhausted. Both returned 404 NOT_FOUND errors. The correct working model was `gemini-2.0-flash-lite`.

**RAG Misconception:** AI initially described RAG as requiring a vector database and embeddings. For our use case (Code-Walking RAG over SQL), no vector database is needed. RAG in our project means retrieving structured SQL metadata using SQLGlot and augmenting the Gemini prompt with that context.

**Streamlit API Key:** AI suggested reading API key from sidebar input in app.py but the correct approach was reading directly from `.env` file using `os.getenv()` to match how `main.py` handles it.

---

## 3. Best Prompts Used

**Main RAG-Augmented Prompt (used in main.py and app.py):**
```
You are a SQL documentation assistant using Code-Walking RAG over SQL.
Extracted metadata: procedure name, parameters, tables, operations,
conditions, error handling, transactions, return values.
Generate documentation: Purpose, Inputs, Outputs, Side Effects,
Error Handling, Sample Call.
```
This worked best because it provides rich structured context to Gemini before asking it to generate documentation — resulting in accurate and consistent output every time.

---

## 4. Tools Used

| Tool | Purpose |
|---|---|
| Google Gemini AI (gemini-2.0-flash-lite) | Documentation generation |
| SQLGlot | SQL parsing and AST analysis |
| Streamlit | Web UI development |
| ChatGPT | Initial project planning and structure |
| Claude AI | Debugging, code improvement, documentation |
| python-dotenv | Secure API key management |

---

## 5. Key Learning

AI tools significantly accelerated development but required constant verification. Every AI suggestion was tested before use. The most important lesson was that understanding your own code is critical — especially when explaining it in the demo video. AI is a tool to assist development, not replace understanding.

---

*Team 19 | Stored Procedure Documenter | Infinite Computer Solutions*
