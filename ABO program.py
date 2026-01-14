import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. LOAD DATA & SET UP HEADERS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    file_name = "ABO_data.xlsx"
    try: 
        df = pd.read_excel(file_name, index_col=None, engine='openpyxl')
        # Standardize headers regardless of Excel spelling
        df.columns.values[0] = "Bacteria"
        df.columns.values[1] = "Type"
        df.columns.values[2] = "Information" 
        return df
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        return pd.DataFrame()

df = load_data()

# -----------------------------------------------------------------------------
# 2. GLOBAL STYLING FUNCTION
# -----------------------------------------------------------------------------
def highlight_coverage(val):
    v_str = str(val).strip().lower()
    if pd.isna(val) or v_str == "" or v_str == 'none':
        return 'background-color: #f0f2f6; color: #999999' # Gray
    if v_str == 'v':
        return 'background-color: #ffeeba; color: black'   # Yellow
    return 'background-color: #d4edda; color: black'       # Green

# -----------------------------------------------------------------------------
# 3. UI AND TABS
# -----------------------------------------------------------------------------
st.title("💊 Antibiotic Coverage Comparison")

tab1, tab2 = st.tabs(["💊 Compare Antibiotics", "🦠 Search Bacteria"])

if not df.empty:
    bacteria_col = "Bacteria"
    type_col = "Type"
    info_col = "Information"
    antibiotic_list = df.columns[3:].tolist() # Antibiotics start from 4th column

    # --- TAB 1: COMPARE ANTIBIOTICS ---
    with tab1:
        selected_antibiotics = st.multiselect(
            "Select antibiotics to compare:", options=antibiotic_list, key="t1"
        )
        
        if selected_antibiotics:
            st.divider()
            mask = df[selected_antibiotics].notna().any(axis=1)
            
            # Show Type and Bacteria first, then selected antibiotics
            display_cols = [type_col, bacteria_col] + selected_antibiotics
            comparison_df = df.loc[mask, display_cols].copy()
            
            # Apply styling ONLY to antibiotic columns (subset)
            st.dataframe(
                comparison_df.style.map(highlight_coverage, subset=selected_antibiotics),
                use_container_width=True,
                hide_index=True,
                column_config={
                    type_col: st.column_config.TextColumn("Type", width="small"),
                    bacteria_col: st.column_config.TextColumn("Bacteria", help="Check Tab 2 for detailed clinical info!")
                }
            )
        else:
            for _ in range(15): st.write("") # Buffer to force dropdown DOWN

    # --- TAB 2: BACTERIA SEARCH & INFO ---
    with tab2:
        selected_organism = st.selectbox(
            "Search for a bacterium to see coverage:", 
            options=df[bacteria_col].unique(), 
            index=None, 
            key="t2"
        )

        if selected_organism:
            row = df[df[bacteria_col] == selected_organism].iloc[0]
            
            # THE INFO BOX: Pulls directly from your 'Information' column in Excel
            st.info(f"**Clinical Pearls for {selected_organism}:** \n{row[info_col]}")
            
            # Display Coverage list
            coverage = row[antibiotic_list].dropna()
            coverage = coverage[coverage.astype(str).str.lower() != 'none']
            
            if not coverage.empty:
                res_df = pd.DataFrame({"Antibiotic": coverage.index, "Effectiveness": coverage.values})
                st.dataframe(
                    res_df.style.map(highlight_coverage, subset=['Effectiveness']),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            for _ in range(15): st.write("")
