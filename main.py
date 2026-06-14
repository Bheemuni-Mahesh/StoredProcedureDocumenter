import os
import re
import time
import sqlglot
from dotenv import load_dotenv
from google import genai

# Load API key from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"


# ---------------------------
# STEP 1: CODE-WALKING OVER SQL (RAG - Retrieval)
# ---------------------------
def walk_sql_code(sql_code):
    metadata = {}

    # Use SQLGlot to parse
    try:
        parsed = sqlglot.parse(sql_code, dialect="tsql")
        metadata['sqlglot_parsed'] = True
    except Exception:
        parsed = []
        metadata['sqlglot_parsed'] = False

    # Walk 1 — Procedure Name
    name_match = re.search(
        r'CREATE\s+PROCEDURE\s+(?:\[?dbo\]?\.\s*)?(?:\[)?(\w+)(?:\])?',
        sql_code, re.IGNORECASE
    )
    metadata['procedure_name'] = name_match.group(1) if name_match else None

    # Walk 2 — Parameters (before AS keyword only)
    as_pos = re.search(r'\bAS\b', sql_code, re.IGNORECASE)
    params = []
    if as_pos:
        param_section = sql_code[:as_pos.start()]
        params = re.findall(
            r'(@\w+)\s+([\w]+(?:\s*\(\s*\d+\s*(?:,\s*\d+\s*)?\))?)',
            param_section
        )
    metadata['parameters'] = params

    # Walk 3 — Tables accessed
    tables = re.findall(
        r'(?:FROM|JOIN|INTO|UPDATE|MERGE\s+INTO)\s+\[?(\w+)\]?',
        sql_code, re.IGNORECASE
    )
    metadata['tables'] = list(set(tables))

    # Walk 4 — SQL Operations
    ops = re.findall(
        r'\b(SELECT|INSERT|UPDATE|DELETE|EXEC|EXECUTE|MERGE)\b',
        sql_code, re.IGNORECASE
    )
    metadata['operations'] = list(set([o.upper() for o in ops]))

    # Walk 5 — WHERE conditions
    conditions = re.findall(
        r'WHERE\s+(.+?)(?=\n\s*(END|ORDER|GROUP|HAVING|UNION)|$)',
        sql_code, re.IGNORECASE | re.DOTALL
    )
    metadata['conditions'] = [c[0].strip()[:150] for c in conditions]

    # Walk 6 — SELECT columns
    select_cols = re.findall(
        r'SELECT\s+(.*?)\s+FROM',
        sql_code, re.IGNORECASE | re.DOTALL
    )
    metadata['select_columns'] = [c.strip()[:200] for c in select_cols]

    # Walk 7 — Error handling
    metadata['has_error_handling'] = bool(
        re.search(r'\b(TRY|CATCH|RAISERROR|THROW)\b', sql_code, re.IGNORECASE)
    )

    # Walk 8 — Transaction
    metadata['has_transaction'] = bool(
        re.search(r'\b(BEGIN\s+TRANSACTION|COMMIT|ROLLBACK)\b', sql_code, re.IGNORECASE)
    )

    # Walk 9 — Return value
    metadata['has_return'] = bool(
        re.search(r'\bRETURN\b', sql_code, re.IGNORECASE)
    )

    # Walk 10 — Output parameters
    metadata['output_params'] = re.findall(
        r'(@\w+)\s+\w+\s+OUTPUT', sql_code, re.IGNORECASE
    )

    return metadata


# ---------------------------
# STEP 2: GENERATE DOCS WITH RETRY (RAG - Augment + Generate)
# ---------------------------
def generate_docs(sql_code, metadata):
    params_text = "\n".join([f"  - {p[0]} ({p[1]})" for p in metadata['parameters']]) \
        if metadata['parameters'] else "  - None"
    tables_text = ", ".join(metadata['tables']) if metadata['tables'] else "None"
    ops_text = ", ".join(metadata['operations']) if metadata['operations'] else "None"
    conditions_text = "\n".join([f"  - {c}" for c in metadata['conditions']]) \
        if metadata['conditions'] else "  - None"
    output_params_text = ", ".join(metadata['output_params']) if metadata['output_params'] else "None"
    select_text = "\n".join([f"  - {c}" for c in metadata['select_columns']]) \
        if metadata['select_columns'] else "  - None"

    prompt = f"""
You are a SQL documentation assistant using Code-Walking RAG over SQL.

The following metadata has been extracted by walking through the SQL code structure:

=== EXTRACTED SQL METADATA (Code-Walking RAG Context) ===
Procedure Name  : {metadata['procedure_name']}
Input Parameters:
{params_text}
Tables Accessed : {tables_text}
SQL Operations  : {ops_text}
WHERE Conditions:
{conditions_text}
SELECT Columns  :
{select_text}
Output Params   : {output_params_text}
Has Error Handling : {metadata['has_error_handling']}
Has Transaction    : {metadata['has_transaction']}
Has Return Value   : {metadata['has_return']}
=========================================================

Using this extracted context AND the raw SQL below, generate clean Markdown documentation with exactly these sections:

# Procedure: {metadata['procedure_name']}

## Purpose
## Inputs
## Outputs
## Side Effects
## Error Handling
## Sample Call

Raw SQL:
{sql_code}
"""

    # Retry logic — waits and retries if quota is hit
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"⏳ Quota limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    print("❌ Quota exhausted after all retries.")
                    print("👉 Solution: Wait until tomorrow OR use a different Google account API key.")
                    raise
            else:
                raise


# ---------------------------
# MAIN PROCESS
# ---------------------------
def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    print("=" * 55)
    print("  Stored Procedure Documenter")
    print("  Powered by Code-Walking RAG + Gemini AI")
    print("=" * 55)

    sql_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".sql")]
    print(f"\n📁 Found {len(sql_files)} SQL file(s) in /{INPUT_FOLDER}\n")

    success = 0
    failed = 0

    for i, file_name in enumerate(sql_files, 1):
        print(f"[{i}/{len(sql_files)}] ", end="")
        file_path = os.path.join(INPUT_FOLDER, file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            sql_code = file.read()

        print(f"📄 Reading file: {file_name}")

        # STEP 1: Code-Walking RAG
        print("🔍 Walking SQL code structure (RAG retrieval)...")
        metadata = walk_sql_code(sql_code)

        procedure_name = metadata['procedure_name']
        if not procedure_name:
            procedure_name = file_name.replace(".sql", "")
            metadata['procedure_name'] = procedure_name
            print(f"⚠️  Fallback name used: {procedure_name}")

        print(f"✅ Procedure found : {procedure_name}")
        print(f"📊 Tables detected : {', '.join(metadata['tables']) or 'None'}")
        print(f"⚙️  Operations      : {', '.join(metadata['operations']) or 'None'}")
        print(f"📥 Parameters      : {len(metadata['parameters'])} found")

        # STEP 2: Generate docs
        print("🤖 Generating documentation with Gemini AI...")
        try:
            
            docs = generate_docs(sql_code, metadata)
            print(f"📝 Docs length: {len(docs)} characters")
            output_file = os.path.join(OUTPUT_FOLDER, f"{procedure_name}.md")
            with open(output_file, "w", encoding="utf-8") as file:
             file.write(docs)

            print(f"💾 Created: {output_file}")
            success += 1
        except Exception as e:
            print(f"❌ Failed: {file_name} — {str(e)[:80]}")
            failed += 1

        # Wait 5 seconds between files to avoid per-minute quota
        if i < len(sql_files):
            print("⏸️  Waiting 5 seconds before next file...")
            time.sleep(5)

        print()

    print("=" * 55)
    print(f"✅ Success : {success} file(s)")
    print(f"❌ Failed  : {failed} file(s)")
    print("=" * 55)


if __name__ == "__main__":
    main()