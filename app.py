# app.py
# Main Streamlit application — Chat to SQL Query Interface

import streamlit as st
import pandas as pd
import os

from sample_data import create_sample_database, get_schema_description
from database import execute_query, get_all_tables, get_table_preview, is_safe_query
from nl_to_sql import convert_nl_to_sql

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat to SQL",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
    }
    .sql-box {
        background-color: #1e1e2e;
        color: #cdd6f4;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        border-left: 4px solid #89b4fa;
    }
    .mode-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .mode-rule   { background: #d4edda; color: #155724; }
    .mode-openai { background: #d1ecf1; color: #0c5460; }
    .stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INITIALIZE DATABASE
# ─────────────────────────────────────────────────────────────
DB_PATH = "company.db"

@st.cache_resource
def init_db():
    create_sample_database(DB_PATH)
    return get_schema_description()

SCHEMA = init_db()

# ─────────────────────────────────────────────────────────────
# SESSION STATE — chat history
# ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []  # list of {question, sql, df, error, mode}

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    openai_key = st.text_input(
        "OpenAI API Key (optional)",
        type="password",
        placeholder="sk-...",
        help="Add your key to handle complex queries not covered by built-in rules."
    )

    st.divider()
    st.header("📋 Database Schema")

    tables = get_all_tables(DB_PATH)
    for table in tables:
        with st.expander(f"📊 {table}"):
            df_prev, _ = get_table_preview(table, DB_PATH, limit=3)
            if df_prev is not None:
                st.dataframe(df_prev, use_container_width=True)

    st.divider()
    st.header("💡 Example Questions")
    examples = [
        "How many employees are there?",
        "What is the average salary?",
        "Show top 5 earners",
        "List employees in Engineering",
        "Average salary by department",
        "Show sales by region",
        "Female employees",
        "Employees with salary above 80000",
        "Show all departments",
        "Who made the highest sale?",
    ]
    for ex in examples:
        if st.button(f"▶ {ex}", key=f"ex_{ex}", use_container_width=True):
            st.session_state["prefill"] = ex

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ─────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🗄️ Chat to SQL</p>', unsafe_allow_html=True)
st.caption("Ask questions in plain English — get SQL queries and results instantly.")

tab1, tab2, tab3 = st.tabs(["💬 Chat", "✏️ Manual SQL Editor", "📖 Schema Reference"])

# ─────────────────────────────────────────────────────────────
# TAB 1: CHAT
# ─────────────────────────────────────────────────────────────
with tab1:

    # Input box
    prefill = st.session_state.pop("prefill", "")
    question = st.text_input(
        "Ask a question about the data:",
        value=prefill,
        placeholder="e.g. Show me employees with salary above 70000",
        key="question_input"
    )

    col1, col2 = st.columns([1, 6])
    with col1:
        ask_btn = st.button("🔍 Ask", type="primary", use_container_width=True)

    if ask_btn and question.strip():
        with st.spinner("Generating SQL and fetching results..."):
            # Convert NL → SQL
            sql, explanation, mode = convert_nl_to_sql(
                question,
                SCHEMA,
                openai_key if openai_key else None
            )

            if not sql:
                st.session_state.history.append({
                    "question": question,
                    "sql": None,
                    "df": None,
                    "error": explanation,
                    "mode": mode
                })
            else:
                # Safety check
                if not is_safe_query(sql):
                    st.session_state.history.append({
                        "question": question,
                        "sql": sql,
                        "df": None,
                        "error": "⚠️ Unsafe query blocked (only SELECT is allowed).",
                        "mode": mode
                    })
                else:
                    df, err = execute_query(sql, DB_PATH)
                    st.session_state.history.append({
                        "question": question,
                        "sql": sql,
                        "df": df,
                        "error": err,
                        "mode": mode
                    })
        st.rerun()

    # ── Display chat history ──
    if not st.session_state.history:
        st.info("👋 Ask a question above to get started! Try clicking an example from the sidebar.")
    else:
        # Newest first
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.container():
                st.markdown(f"**🙋 You:** {entry['question']}")

                # Mode badge
                if entry["mode"] == "Rule-Based":
                    st.markdown('<span class="mode-badge mode-rule">⚡ Rule-Based</span>', unsafe_allow_html=True)
                elif "OpenAI" in entry["mode"]:
                    st.markdown('<span class="mode-badge mode-openai">🤖 OpenAI GPT</span>', unsafe_allow_html=True)

                if entry["sql"]:
                    st.markdown("**Generated SQL:**")
                    st.markdown(f'<div class="sql-box">{entry["sql"]}</div>', unsafe_allow_html=True)

                if entry["error"]:
                    st.error(entry["error"])
                elif entry["df"] is not None:
                    df = entry["df"]
                    if df.empty:
                        st.warning("Query ran successfully but returned no rows.")
                    else:
                        st.success(f"✅ {len(df)} row(s) returned")
                        st.dataframe(df, use_container_width=True)

                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "⬇️ Download CSV",
                            data=csv,
                            file_name=f"result_{i}.csv",
                            mime="text/csv",
                            key=f"dl_{i}"
                        )

            st.divider()

# ─────────────────────────────────────────────────────────────
# TAB 2: MANUAL SQL EDITOR
# ─────────────────────────────────────────────────────────────
with tab2:
    st.subheader("✏️ Write & Run SQL Directly")
    manual_sql = st.text_area(
        "SQL Query:",
        height=150,
        placeholder="SELECT * FROM employees WHERE salary > 70000;",
        value="SELECT e.name, d.dept_name, e.salary, e.city\nFROM employees e\nJOIN departments d ON e.dept_id = d.dept_id\nORDER BY e.salary DESC\nLIMIT 10;"
    )

    if st.button("▶️ Run Query", type="primary"):
        if manual_sql.strip():
            if not is_safe_query(manual_sql):
                st.error("⚠️ Only SELECT queries are allowed.")
            else:
                df, err = execute_query(manual_sql, DB_PATH)
                if err:
                    st.error(err)
                elif df is not None:
                    if df.empty:
                        st.warning("Query returned no rows.")
                    else:
                        st.success(f"✅ {len(df)} row(s) returned")
                        st.dataframe(df, use_container_width=True)
                        csv = df.to_csv(index=False)
                        st.download_button("⬇️ Download CSV", csv, "result.csv", "text/csv")

# ─────────────────────────────────────────────────────────────
# TAB 3: SCHEMA REFERENCE
# ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📖 Full Database Schema")
    st.code(SCHEMA, language="sql")

    st.subheader("📊 Table Previews")
    for table in tables:
        st.markdown(f"**{table}**")
        df_full, _ = execute_query(f"SELECT * FROM {table};", DB_PATH)
        if df_full is not None:
            st.dataframe(df_full, use_container_width=True)
        st.divider()