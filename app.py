import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import io

# --- 🔐 Access Control ---
st.sidebar.title("🔐 Restricted Access")
password = st.sidebar.text_input("Enter access key", type="password")

if not password.endswith("@icici"):
    st.error("❌ Unauthorized. Access key must be your organisation e mail id")
    st.stop()
else:
    st.success("✅ Access granted!")

# --- Header Section ---
header_col1, header_col2 = st.columns([0.1, 0.9])
with header_col1:
    st.image("bank.png", width=80)
with header_col2:
    st.markdown("""
        <div style='padding-left: 15px;'>
            <h1 style='margin-bottom:0; color: #003366;'>ICICI Bank Ltd - Education Loan</h1>
            <h3 style='margin-top:5px; color: #444;'>🎓 Institute Category Search</h3>
        </div>
    """, unsafe_allow_html=True)

# --- Load Excel File ---
@st.cache_data
def load_data():
    return pd.read_excel("consolidated_institute list.xlsx")

df = load_data()

# --- Input & Output Setup ---
input_cols = ["Institute name", "City"]
last_col_name = df.columns[-1]

output_col_map = {
    "🏷️ Unique Code": "Unique Code",
    "🌍 State / Country": "State / Country",
    "📚 Course / Stream": "Course / Stream",
    "🏢 Category": "Category",
    "💰 Repayment": last_col_name
}
output_cols_ui = list(output_col_map.keys())
actual_output_cols = [output_col_map[c] for c in output_cols_ui if output_col_map[c] in df.columns]

# --- Instructions ---
st.header("🔍 How To Search")
st.markdown("""
#### 📝 Steps:
1. Start typing the **Institute Name** or **City**.
2. Select from the dropdown suggestions.
3. View results or export them.
""")

# --- Search Inputs ---
user_selections = {}
cols = st.columns(2)
for i, col in enumerate(input_cols):
    col_values = df[col].dropna().astype(str).unique()
    typed = cols[i].text_input(f"Type {col}:", key=f"{col}_input")

    suggestion = None
    if typed:
        matches = process.extract(typed, col_values, scorer=fuzz.WRatio, limit=10)
        filtered_matches = [m for m, score, _ in matches if score > 60]
        if filtered_matches:
            suggestion = cols[i].selectbox(f"Suggestions for {col}:", filtered_matches, key=f"{col}_suggest")
        else:
            cols[i].info(f"No close matches found for '{typed}', using raw input.")
            suggestion = typed

    user_selections[col] = suggestion if suggestion else None

# --- Filter Logic ---
filtered = df.copy()
for col, val in user_selections.items():
    if val:
        best_match = process.extractOne(val, df[col].dropna().astype(str), scorer=fuzz.WRatio)
        if best_match and best_match[1] > 60:
            filtered = filtered[filtered[col].astype(str) == best_match[0]]
        else:
            filtered = filtered.iloc[0:0]

# --- Display Results ---
st.divider()
st.header("📊 Matching Results")

if not filtered.empty and any(user_selections.values()):
    st.success(f"✅ Found {filtered.shape[0]} matching record(s).")

    # Add S.No column
    if "S.No" not in filtered.columns:
        filtered.insert(0, "S.No", range(1, len(filtered) + 1))

    if filtered.shape[0] == 1:
        st.subheader("🏫 Institute Details")

        row = filtered.iloc[0]

        # Styling for HTML table
        st.markdown("""
        <style>
            .styled-table {
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 16px;
                width: 100%;
                background-color: #fdfdfd;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .styled-table td, .styled-table th {
                padding: 12px 15px;
                border: 1px solid #ddd;
            }
            .styled-table th {
                background-color: #f4f4f4;
                text-align: left;
                font-weight: bold;
                width: 30%;
                color: #333;
            }
            .styled-table td {
                color: #222;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <table class='styled-table'>
            <tr><th>🏷️ Unique Code</th><td>{row['Unique Code']}</td></tr>
            <tr><th>🌍 State / Country</th><td>{row['State / Country']}</td></tr>
            <tr><th>📚 Course / Stream</th><td>{row['Course / Stream'].replace('\\n', '<br>')}</td></tr>
            <tr><th>🏢 Category</th><td>{row['Category']}</td></tr>
            <tr><th>💰 Partial Simple Interest Repayment</th><td>{row[last_col_name]}</td></tr>
        </table>
        """, unsafe_allow_html=True)

    else:
        styled_table = filtered[["S.No"] + actual_output_cols].style.set_table_styles([
            {'selector': 'thead', 'props': [('background-color', '#003366'), ('color', 'white'), ('font-weight', 'bold')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]},
            {'selector': 'tbody tr:hover', 'props': [('background-color', '#e6f7ff')]},
        ]).set_properties(**{
            'text-align': 'left',
            'border': '1px solid #ccc',
            'padding': '8px',
        })
        st.write(styled_table.to_html(escape=False), unsafe_allow_html=True)

elif any(user_selections.values()):
    st.warning("⚠️ No matching records found.")
else:
    st.info("ℹ️ Enter at least one field above to begin your search.")

# --- Footer ---
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 15px;
    bottom: 10px;
    font-size: 13px;
    color: #888;
}
</style>

<div class="footer">
    Developed by Prasoon Mathur 🧑‍💻<br>
    Last updated: March 31, 2025
</div>
""", unsafe_allow_html=True)
