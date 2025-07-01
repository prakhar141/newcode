import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

# --- Setup Page ---
st.set_page_config(page_title="Institute Finder", layout="wide")

# --- Header ---
st.title("🏫 Institute Live Search")
st.subheader("Find institutes with smart autofill, fuzzy search, and repayment info")

# --- Load Excel ---
@st.cache_data
def load_data():
    return pd.read_excel("consolidated_institute list.xlsx")

df = load_data()

# --- Input & Output Columns ---
input_cols = ["Unique Code", "Institute name", "City"]
last_col_name = df.columns[-1]  # Get Repayment dynamically

output_col_map = {
    "State / Country": "State / Country",
    "Course / Stream": "Course / Stream",
    "Category": "Category",
    "Repayment": last_col_name
}
output_cols_ui = list(output_col_map.keys())
actual_output_cols = [output_col_map[c] for c in output_cols_ui if output_col_map[c] in df.columns]

# --- Live Suggestion Inputs ---
st.header("🔍 Search Criteria")
user_selections = {}
cols = st.columns(3)

for i, col in enumerate(input_cols):
    col_values = df[col].dropna().astype(str).unique()
    typed = cols[i].text_input(f"Type {col}:", key=f"{col}_input")

    suggestion = None
    if typed:
        matches = process.extract(typed, col_values, scorer=fuzz.WRatio, limit=10)
        filtered_matches = [m for m, score, _ in matches if score > 60]
        if filtered_matches:
            suggestion = cols[i].selectbox(
                f"Suggestions for {col}:", 
                filtered_matches, 
                format_func=lambda x: x, 
                key=f"{col}_suggest"
            )
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
    st.dataframe(filtered[actual_output_cols], use_container_width=True)

elif any(user_selections.values()):
    st.warning("⚠️ No matching records found.")
else:
    st.info("Enter at least one field above to begin your search.")
