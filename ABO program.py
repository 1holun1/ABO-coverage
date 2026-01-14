import streamlit as st
import pandas as pd

# 1. LOAD DATA
@st.cache_data
def load_data():
    file_name = "ABO_data.xlsx"
    try: 
        # Make sure your Excel has 'Bacteria' in A1 and 'Type' in B1
        df = pd.read_excel(file_name, index_col=None, engine='openpyxl')
        df.columns.values[0] = "Bacteria"
        df.columns.values[1] = "Type"
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

# 2. STYLING FUNCTIONS (Move these here so both tabs can see them!)
def highlight_cells(val):
    v_str = str(val).strip().lower()
    if pd.isna(val) or v_str == "" or v_str == 'none':
        return 'background-color: #f0f2f6; color: #999999' # Gray
    if v_str == 'v':
        return 'background-color: #ffeeba; color: black'   # Yellow
    return 'background-color: #d4edda; color: black'       # Green

# 3. THE UI AND TABS
st.title("💊 Antibiotic Coverage Comparison")

tab1, tab2 = st.tabs(["💊 Compare Antibiotics", "🦠 Search Bacteria"])

if not df.empty:
    bacteria_col = "Bacteria"
    type_col = "Type"
    antibiotic_list = df.columns[2:].tolist()

    # --- TAB 1: COMPARE ---
    with tab1:
        selected_antibiotics = st.multiselect(
            "Select antibiotics:", options=antibiotic_list, key="t1"
        )
        if selected_antibiotics:
            mask = df[selected_antibiotics].notna().any(axis=1)
            display_cols = [type_col, bacteria_col] + selected_antibiotics
            comparison_df = df.loc[mask, display_cols].copy()
            
            # Apply styling using the function defined above
            st.dataframe(
                comparison_df.style.map(highlight_cells, subset=selected_antibiotics),
                use_container_width=True,
                hide_index=True,
                column_config={type_col: st.column_config.TextColumn("Type", width="small")}
            )
        else:
            for _ in range(10): st.write("")

    # --- TAB 2: BACTERIA LOOKUP ---
    with tab2:
        selected_organism = st.selectbox(
            "Search for a bacterium:", options=df[bacteria_col].unique(), index=None, key="t2"
        )
        if selected_organism:
            row = df[df[bacteria_col] == selected_organism].iloc[0]
            
            # HOVER/INFO BOX (The solution for your bacteria info request)
            st.info(f"**Clinical Info for {selected_organism}:** This is where you can add your descriptions.")
            
            # Filter for active coverage
            coverage = row[antibiotic_list].dropna()
            coverage = coverage[coverage.astype(str).str.lower() != 'none']
            
            if not coverage.empty:
                res_df = pd.DataFrame({"Antibiotic": coverage.index, "Effectiveness": coverage.values})
                st.dataframe(
                    res_df.style.map(highlight_cells, subset=['Effectiveness']),
                    use_container_width=True,
                    hide_index=True
                )
