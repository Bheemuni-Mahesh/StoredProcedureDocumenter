# Stored Procedure Documenter
### AI-Powered SQL Documentation Generator
**Team 19 | Submitted to Infinite Computer Solutions**

---

## 👥 Team Members

| Name | Roll Number |
|---|---|
| Bheemuni Mahesh | 23U41A0508 |
| Murapaka Venkata Daya | 24U45A0233 |
| Nammi Lokesh | 24U45A0421 |
| Donkada Yamini | 23U41A4218 |

---

## 📌 Problem Statement

Stored procedures are widely used in database applications to implement business logic. However, they are rarely documented, making it difficult for new developers to understand, maintain, and reuse them. Important knowledge about procedure functionality often exists only with experienced developers, creating a "tribal knowledge" problem.

---

## 🎯 Objective

To develop an AI-powered agent that automatically scans SQL stored procedure files, parses them using SQLGlot, and generates clean, structured Markdown documentation using Google Gemini AI — accessible via both a Web UI and CLI.

---

## ✨ Features

- Web UI built with Streamlit for easy file upload and documentation display
- Command line interface (CLI) for batch processing
- Automatically walks a folder of `.sql` files
- Parses SQL code using **SQLGlot** (Code-Walking RAG)
- Extracts procedure name, parameters, tables, operations, conditions, and error handling
- Sends structured metadata to **Google Gemini AI**
- Generates one clean `.md` documentation file per procedure
- Covers: Purpose, Inputs, Outputs, Side Effects, Error Handling, Sample Call
- Download button for each generated `.md` file
- Auto-retry logic if API quota is temporarily hit
- 5 second delay between files to avoid per-minute quota limits
- API key secured using `.env` file and `python-dotenv`

---

## 🧠 AI Capability Demonstrated

**Code-Walking RAG over SQL**

Instead of sending raw SQL directly to the AI, the system first walks through the SQL code structure using SQLGlot and regex to extract structured metadata (parameters, tables, operations, conditions). This retrieved context is then used to augment the Gemini AI prompt — resulting in more accurate and detailed documentation.

```
SQL File
   ↓
SQLGlot + Regex walks the code (Retrieval)
   ↓
Extracted metadata added to prompt (Augmentation)
   ↓
Gemini AI generates documentation (Generation)
   ↓
Saved as .md file / Displayed in Web UI
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web UI for file upload and documentation display |
| SQLGlot | SQL parsing and AST analysis |
| Regex (re) | Metadata extraction from SQL code |
| Google Gemini AI (gemini-2.0-flash-lite) | Markdown documentation generation |
| python-dotenv | Secure API key management |
| Markdown | Output documentation format |
| pytest | Testing |
| Git | Version control |

---

## 📁 Project Structure

```
StoredProcedureDocumenter/
├── app.py                    ← Streamlit web application
├── main.py                   ← CLI application
├── requirements.txt
├── README.md
├── prompts.md
├── ai_usage_note.md
├── .gitignore
├── input/
│   ├── employee.sql
│   ├── payroll.sql
│   ├── GetAllDepartments.sql
│   ├── InsertNewEmployee.sql
│   └── UpdateEmployeeDetails.sql
├── output/
│   ├── GetEmployee.md
│   ├── GetSalary.md
│   ├── GetAllDepartments.md
│   ├── InsertNewEmployee.md
│   └── UpdateEmployeeDetails.md
└── tests/
    └── test_basic.py
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/StoredProcedureDocumenter.git
cd StoredProcedureDocumenter
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a Free Gemini API Key
- Go to [aistudio.google.com](https://aistudio.google.com)
- Click **"Get API Key"**
- Click **"Create API Key"**
- Copy the key

### 4. Create `.env` File
Create a file called `.env` in the project root:
```
GEMINI_API_KEY=your_actual_gemini_key_here
```

---

## ▶️ How to Run

### Option A — Web App (Recommended)
```bash
python -m streamlit run app.py
```
Then open **http://localhost:8501** in your browser.

1. Paste your Gemini API key in the sidebar
2. Upload one or more `.sql` files
3. Click **"Generate Documentation"**
4. View and download the generated `.md` files

### Option B — Command Line
```bash
python main.py
```
Place `.sql` files in `/input` folder. Generated `.md` files appear in `/output` folder.

---

## 📥 Sample Input

**File:** `input/employee.sql`
```sql
CREATE PROCEDURE GetEmployee
    @EmployeeId INT
AS
BEGIN
    SELECT
        EmployeeId,
        FirstName,
        LastName,
        Email,
        DepartmentId,
        DateOfJoining,
        Salary
    FROM Employees
    WHERE EmployeeId = @EmployeeId
END
```

---

## 📤 Sample Output

**File:** `output/GetEmployee.md`
```markdown
# Procedure: GetEmployee

## Purpose
Retrieves complete details of a specific employee from
the Employees table based on their unique EmployeeId.

## Inputs
| Parameter | Data Type | Description |
|---|---|---|
| @EmployeeId | INT | Unique identifier of the employee |

## Outputs
Returns a single row with all employee details.

## Side Effects
None — this is a read-only SELECT procedure.

## Error Handling
None implemented.

## Sample Call
EXEC GetEmployee @EmployeeId = 101
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/
```

Expected output:
```
2 passed
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────┐
│           app.py (Streamlit Web UI)         │
│    OR     main.py (CLI)                     │
│                                             │
│  1. Accept .sql files (upload or folder)    │
│  2. walk_sql_code() — Code-Walking RAG      │
│     ├── SQLGlot parses SQL into AST         │
│     ├── Extract procedure name              │
│     ├── Extract parameters                  │
│     ├── Extract tables, operations          │
│     └── Extract conditions, error handling  │
│  3. generate_docs() — Augmented Generation  │
│     ├── Build rich structured prompt        │
│     ├── Send to Gemini AI                   │
│     └── Receive Markdown documentation      │
│  4. Display in UI / Save to /output folder  │
└─────────────────────────────────────────────┘
```

---

## ⚠️ Assumptions and Limitations

- Input files must be `.sql` format
- Designed for T-SQL (Microsoft SQL Server) stored procedures
- Requires a valid Google Gemini API key (free tier available)
- Free tier has a daily request limit — process files in one run
- SQLGlot partially parses T-SQL and falls back to command mode for complex procedures
- API key must be stored in `.env` file — never hardcode in source code

---

## 🎥 Demo Video

[Click here to watch the demo video](#)

> https://drive.google.com/file/d/1MdaQRFNHVW901Cxhipkc5D1h28aiXirk/view?usp=drivesdk

---

## 📦 Requirements

```
google-genai
sqlglot
pytest
python-dotenv
streamlit
```

Install with:
```bash
pip install -r requirements.txt
```

---

*Team 19 | Stored Procedure Documenter | Infinite Computer Solutions*
