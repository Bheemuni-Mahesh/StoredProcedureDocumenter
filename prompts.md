# Prompts Used During Development
## Project: Stored Procedure Documenter
## Team 19 | Submitted to Infinite Computer Solutions

---

## Prompt 1 — Main RAG-Augmented Documentation Prompt
**Used in:** `main.py` → `generate_docs()` function
**Sent to:** Google Gemini AI

```
You are a SQL documentation assistant using Code-Walking RAG over SQL.

The following metadata has been extracted by walking through the SQL code structure:

=== EXTRACTED SQL METADATA (Code-Walking RAG Context) ===
Procedure Name  : {procedure_name}
Input Parameters:
{parameters}
Tables Accessed : {tables}
SQL Operations  : {operations}
WHERE Conditions:
{conditions}
SELECT Columns  :
{select_columns}
Output Params   : {output_params}
Has Error Handling : {has_error_handling}
Has Transaction    : {has_transaction}
Has Return Value   : {has_return}
=========================================================

Using this extracted context AND the raw SQL below, generate clean 
Markdown documentation with exactly these sections:

# Procedure: {procedure_name}

## Purpose
## Inputs
## Outputs
## Side Effects
## Error Handling
## Sample Call
```

**Why this prompt works well:**
- Provides structured context extracted by the code walker (RAG Retrieval)
- Tells Gemini exactly what sections to generate
- Combines both extracted metadata and raw SQL for maximum accuracy
- Results in consistent and structured Markdown output every time

---

## Prompt 2 — Initial Simple Prompt (used during early development)
**Used in:** Early version of `main.py`
**Sent to:** Google Gemini AI

```
You are a SQL documentation assistant.
Analyze the following SQL stored procedure.
Generate a clean Markdown document with:
1. Purpose
2. Inputs
3. Outputs
4. Side Effects
5. Sample Call

SQL:
{sql_code}
```

**Why we moved away from this:**
- Sends raw SQL only — no structured context
- Gemini has to figure out everything itself
- Less accurate and less structured output
- Does not demonstrate Code-Walking RAG capability

---

## Prompt 3 — Project Planning Prompt
**Used with:** ChatGPT
**Purpose:** Initial project structure and planning

```
Help me build a Python CLI tool that:
1. Reads .sql files from an input folder
2. Parses stored procedure names using regex
3. Sends the SQL code to Google Gemini AI
4. Gets back Markdown documentation
5. Saves each documentation as a .md file in output folder

Give me the project structure and main.py code.
```

**What AI helped with:**
- Suggested the folder structure (input/, output/, tests/)
- Gave initial main.py code structure
- Suggested using os.listdir() to walk the folder

---

## Prompt 4 — SQLGlot Integration Prompt
**Used with:** ChatGPT / Claude AI
**Purpose:** Adding Code-Walking RAG with SQLGlot

```
I want to upgrade my SQL documenter to use 
Code-Walking RAG over SQL. 

Instead of sending raw SQL to Gemini, I want to:
1. Use SQLGlot to parse the SQL into structured parts
2. Extract: procedure name, parameters, tables, 
   operations, conditions, error handling
3. Send this structured metadata to Gemini as context
4. Generate better documentation

Help me write the walk_sql_code() function.
```

**What AI helped with:**
- Explained how SQLGlot parses T-SQL
- Helped write the walk_sql_code() function
- Suggested extracting 10 different metadata points

---

## Prompt 5 — Regex Debugging Prompt
**Used with:** Claude AI
**Purpose:** Fixing the CREATE.md bug

```
My Python regex for extracting stored procedure names 
is not working correctly.

For this SQL:
CREATE PROCEDURE [dbo].[GetEmployee]

My regex picks up CREATE as the name instead of 
GetEmployee and creates a file called CREATE.md.

Current regex:
re.search(r'CREATE\s+PROCEDURE\s+(\w+)', sql_code)

How do I fix it to handle [dbo].[ProcedureName] format?
```

**What AI helped with:**
- Identified the issue with `(\w+)` not handling brackets
- Provided the fixed regex pattern:
  `r'CREATE\s+PROCEDURE\s+(?:\[?dbo\]?\.\s*)?(?:\[)?(\w+)(?:\])?'`

---

## Prompt 6 — API Key Security Prompt
**Used with:** Claude AI
**Purpose:** Hiding API key before GitHub push

```
I have my Gemini API key hardcoded in main.py.
I want to push to GitHub but don't want to expose 
the key publicly.

How do I use python-dotenv to hide the API key 
in a .env file and read it in main.py?
```

**What AI helped with:**
- Suggested using python-dotenv library
- Explained how to create .env file
- Explained how to add .env to .gitignore

---

## Prompt 7 — Test Case Prompt
**Used with:** ChatGPT
**Purpose:** Writing pytest test case

```
Write a simple pytest happy-path test for my 
Stored Procedure Documenter project.

The test should verify that:
1. A .sql file containing CREATE PROCEDURE 
   can be read successfully
2. The procedure name can be extracted correctly

Keep it simple - just one happy path test.
```

**What AI helped with:**
- Wrote the basic test_basic.py structure
- Suggested testing the regex extraction function

---

*This file documents all key prompts used during development of the Stored Procedure Documenter project by Team 19.*