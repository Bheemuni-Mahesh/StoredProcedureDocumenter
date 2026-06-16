import os
import re
import time
import streamlit as st
import sqlglot
from google import genai
from dotenv import load_dotenv

# Load API key
load_dotenv()

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="SQL Procedure Documenter",
    page_icon="🗄️",
    layout="wide"
)

# ---------------------------
# STYLING
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0f1117;
}
[data-testid="stSidebar"] {
    background-color: #161b27;
}
.main-header {
    background: linear-gradient(90deg, #1a2540 0%, #0f1a35 100%);
    border: 1px solid #2a3a5c;
    border-radius: 10px;
    padding: 20px 28px;
    margin-bottom: 24px;
}
.main-title {
    font-size: 26px;
    font-weight: 700;
    color: #e2e8f0;
}
.main-sub {
    font-size: 13px;
    color: #64748b;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.markdown("""
<div class="main-header">
    <div class="main-title">🗄️ SQL Procedure Documenter</div>
    <div class="main-sub">
        Powered by Code-Walking RAG + Google Gemini AI | Team 19
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        placeholder="Paste your Gemini API key"
    )
    st.markdown("---")
    st.markdown("### 📖 How It Works")
    st.markdown("""
1. Upload `.sql` files
2. Click **Generate Docs**
3. AI walks SQL code (RAG)
4. Gemini generates docs
5. Download `.md` files
""")
    st.markdown("---")
    st.markdown("### 🛠️ Tech Stack")
    st.markdown("`Python` · `SQLGlot` · `Gemini AI` · `Streamlit`")

# ---------------------------
# CODE WALKING RAG
# ---------------------------
def walk_sql_code(sql_code):
    metadata = {}
    try:
        sqlglot.parse(sql_code, dialect="tsql")
        metadata['sqlglot_parsed'] = True
    except Exception:
        metadata['sqlglot_parsed'] = False

    name_match = re.search(
        r'CREATE\s+PROCEDURE\s+(?:\[?dbo\]?\.\s*)?(?:\[)?(\w+)(?:\])?',
        sql_code, re.IGNORECASE
    )
    metadata['procedure_name'] = name_match.group(1) if name_match else None

    as_pos = re.search(r'\bAS\b', sql_code, re.IGNORECASE)
    params = []
    if as_pos:
        param_section = sql_code[:as_pos.start()]
        params = re.findall(
            r'(@\w+)\s+([\w]+(?:\s*\(\s*\d+\s*(?:,\s*\d+\s*)?\))?)',
            param_section
        )
    metadata['parameters'] = params

    tables = re.findall(
        r'(?:FROM|JOIN|INTO|UPDATE|MERGE\s+INTO)\s+\[?(\w+)\]?',
        sql_code, re.IGNORECASE
    )
    metadata['tables'] = list(set(tables))

    ops = re.findall(
        r'\b(SELECT|INSERT|UPDATE|DELETE|EXEC|EXECUTE|MERGE)\b',
        sql_code, re.IGNORECASE
    )
    metadata['operations'] = list(set([o.upper() for o in ops]))

    conditions = re.findall(
        r'WHERE\s+(.+?)(?=\n\s*(END|ORDER|GROUP|HAVING|UNION)|$)',
        sql_code, re.IGNORECASE | re.DOTALL
    )
    metadata['conditions'] = [c[0].strip()[:150] for c in conditions]

    select_cols = re.findall(
        r'SELECT\s+(.*?)\s+FROM',
        sql_code, re.IGNORECASE | re.DOTALL
    )
    metadata['select_columns'] = [c.strip()[:200] for c in select_cols]

    metadata['has_error_handling'] = bool(
        re.search(r'\b(TRY|CATCH|RAISERROR|THROW)\b', sql_code, re.IGNORECASE)
    )
    metadata['has_transaction'] = bool(
        re.search(r'\b(BEGIN\s+TRANSACTION|COMMIT|ROLLBACK)\b', sql_code, re.IGNORECASE)
    )
    metadata['has_return'] = bool(
        re.search(r'\bRETURN\b', sql_code, re.IGNORECASE)
    )
    metadata['output_params'] = re.findall(
        r'(@\w+)\s+\w+\s+OUTPUT', sql_code, re.IGNORECASE
    )

    return metadata

# ---------------------------
# GENERATE DOCS
# ---------------------------
def generate_docs(sql_code, metadata, client):
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

Using this extracted context AND the raw SQL below, generate clean Markdown documentation:

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ---------------------------
# MAIN UI
# ---------------------------
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📂 Upload SQL Files")
    uploaded_files = st.file_uploader(
        "Drop .sql files here",
        type=["sql"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        for f in uploaded_files:
            st.markdown(f"📄 `{f.name}`")

        st.markdown("")
        run = st.button("⚡ Generate Documentation", type="primary", use_container_width=True)
    else:
        st.info("Upload one or more `.sql` files to get started.")
        run = False

with col2:
    st.markdown("### 📄 Generated Documentation")
    if not uploaded_files:
        st.markdown("""
<div style="color:#4a6080;font-size:13px;border:1px dashed #1e2d45;
border-radius:8px;padding:20px;text-align:center;">
Documentation will appear here after processing.
</div>
""", unsafe_allow_html=True)

# ---------------------------
# PROCESSING
# ---------------------------
if run and uploaded_files:
    if not api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar!")
        st.stop()


    try:
      client = genai.Client(api_key=api_key)
    except Exception as e:
      st.error(f"Failed to connect to Gemini: {e}")
      st.stop()

    st.markdown("---")
    st.markdown("### 🔄 Processing Files...")

    results = []
    progress = st.progress(0, text="Starting...")

    for i, uploaded_file in enumerate(uploaded_files):
        sql_code = uploaded_file.read().decode("utf-8")
        fname = uploaded_file.name

        progress.progress(i / len(uploaded_files), text=f"Walking SQL: {fname}...")

        metadata = walk_sql_code(sql_code)
        procedure_name = metadata['procedure_name']
        if not procedure_name:
            procedure_name = fname.replace(".sql", "")
            metadata['procedure_name'] = procedure_name

        progress.progress((i + 0.5) / len(uploaded_files), text=f"Generating docs: {procedure_name}...")

        try:
            docs = generate_docs(sql_code, metadata, client)
            results.append({
                "file": fname,
                "procedure": procedure_name,
                "docs": docs,
                "error": None
            })
        except Exception as e:
            results.append({
                "file": fname,
                "procedure": procedure_name,
                "docs": None,
                "error": str(e)
            })

        if i < len(uploaded_files) - 1:
            time.sleep(5)

    progress.progress(1.0, text="✅ Done!")

    # Show results
    success = sum(1 for r in results if not r["error"])
    st.markdown(f"**{success}/{len(results)} files processed successfully**")

    for r in results:
        if r["error"]:
            st.error(f"❌ {r['file']} — {r['error'][:100]}")
        else:
            st.success(f"✅ {r['procedure']}.md generated")
            with st.expander(f"📄 View: {r['procedure']}.md", expanded=(len(results) == 1)):
                st.markdown(r["docs"])
            st.download_button(
                label=f"⬇️ Download {r['procedure']}.md",
                data=r["docs"],
                file_name=f"{r['procedure']}.md",
                mime="text/markdown",
                key=f"dl_{r['procedure']}"
            )
        st.markdown("")
