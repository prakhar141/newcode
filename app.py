import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
from st_aggrid import AgGrid, GridOptionsBuilder
import io

# --- Header Section ---
header_col1, header_col2 = st.columns([0.1, 0.9])
with header_col1:
    st.image("bank.png", width=80)
with header_col2:
    st.markdown("""
        <div style='padding-left: 15px;'>
            <h1 style='margin-bottom:0;'>ICICI Bank Ltd - Education Loan</h1>
            <h3 style='margin-top:5px;'>🎓 Institute Category Search</h3>
        </div>
    """, unsafe_allow_html=True)

# --- Load Excel File ---
@st.cache_data
def load_data():
    return pd.read_excel("consolidated_institute list.xlsx")

df = load_data()

# --- Input & Output Setup ---
input_cols = ["Institute name", "City"]
last_col_name = df.columns[-1]  # Usually "Repayment"

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

    if filtered.shape[0] == 1:
        st.subheader("🏷️ Institute Summary")

        row = filtered.iloc[0]

        fields = {
            "Unique Code": row["Unique Code"],
            "State / Country": row["State / Country"],
            "Course / Stream": row["Course / Stream"],
            "Category": row["Category"],
            "Partial Simple Interest Repayment": row[last_col_name]
        }

        for label, value in fields.items():
            st.markdown(f"""
            <div style='padding: 10px; border-bottom: 1px solid #ddd;'>
                <strong style='display: inline-block; width: 250px;'>{label}</strong>
                <span>{value}</span>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Multiple results? Show in table/grid format
        st.dataframe(filtered[actual_output_cols], use_container_width=True)


    # --- Export Button ---
    to_download = filtered[["S.No"] + actual_output_cols]
    buffer = io.BytesIO()
    to_download.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Download Excel",
        data=buffer.getvalue(),
        file_name="matching_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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
