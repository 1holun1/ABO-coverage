import streamlit as st  # This MUST be line 1
import pandas as pd

# -----------------------------------------------------------------------------
# 1. LOAD DATA (Positions: 0=Bacteria, 1=Type, 2=Info, 3+=Antibiotics)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    file_name = "ABO_data.xlsx"
    try: 
        df = pd.read_excel(file_name, index_col=None, engine='openpyxl')
        # Standardize the first 3 columns regardless of Excel headers
        df.columns.values[0] = "Bacteria"
        df.columns.values[1] = "Type"
        df.columns.values[2] = "Information"
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

# -----------------------------------------------------------------------------
# 2. GLOBAL STYLING FUNCTION
# -----------------------------------------------------------------------------
def highlight_cells(val):
    v_str = str(val).strip().lower()
    if pd.isna(val) or v_str == "" or v_str == 'none':
        return 'background-color: #f0f2f6; color: #999999' # Gray
    if v_str == 'v':
        return 'background-color: #ffeeba; color: black'   # Yellow
    return 'background-color: #d4edda; color: black'       # Green

# -----------------------------------------------------------------------------
# 3. UI TABS
# -----------------------------------------------------------------------------
st.title("💊 Antibiotic Coverage Comparison")

tab1, tab2 = st.tabs(["💊 Compare Antibiotics", "🦠 Search Bacteria"])

if not df.empty:
    # Antibiotics start from the 4th column in your new Excel layout
    antibiotic_list = df.columns[3:].tolist()

    # --- TAB 1: COMPARE ---
    with tab1:
        selected_antibiotics = st.multiselect(
            "Select antibiotics to compare:", options=antibiotic_list, key="t1"
        )
        
        if selected_antibiotics:
            mask = df[selected_antibiotics].notna().any(axis=1)
            
            # Show ONLY Type and Bacteria on the left. Hide "Information" here.
            display_cols = ["Type", "Bacteria"] + selected_antibiotics
            comparison_df = df.loc[mask, display_cols].copy()
            
            st.dataframe(
                comparison_df.style.map(highlight_cells, subset=selected_antibiotics),
                use_container_width=True,
                hide_index=True,
                column_config={"Type": st.column_config.TextColumn("Type", width="small")}
            )
        else:
            for _ in range(10): st.write("")

    # --- TAB 2: SEARCH BACTERIA ---
    with tab2:
        selected_organism = st.selectbox(
            "Search for a bacterium:", options=df["Bacteria"].unique(), index=None, key="t2"
        )
        
        if selected_organism:
            row = df[df["Bacteria"] == selected_organism].iloc[0]
            
            # This is your "Hover Info" replacement! 
            # It shows your clinical notes in a nice blue box.
            st.info(f"**Clinical Info for {selected_organism}:**\n\n{row['Information']}")
            
            # List antibiotics that have data for this organism
            coverage = row[antibiotic_list].dropna()
            coverage = coverage[coverage.astype(str).str.lower() != 'none']
            
            if not coverage.empty:
                res_df = pd.DataFrame({"Antibiotic": coverage.index, "Effectiveness": coverage.values})
                st.dataframe(
                    res_df.style.map(highlight_cells, subset=['Effectiveness']),
                    use_container_width=True,
                    hide_index=True
                )
