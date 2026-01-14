
import streamlit as st
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Antibiotic Comparison Tool", page_icon="💊", layout="wide")

# 2. LOAD DATA
@st.cache_data
def load_data():
    try: 
        # Using your filename 'ABO_data.xlsx'
        df = pd.read_excel("ABO_data.xlsx", index_col=None)
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

# -----------------------------------------------------------------------------
# 3. TABS AND SEARCH LOGIC
# -----------------------------------------------------------------------------

# Create the tabs
tab1, tab2 = st.tabs(["💊 Compare Antibiotics", "🦠 Search Bacteria"])

if not df.empty:
    bacteria_col = df.columns[0]
    type_col = df.columns[1]
    antibiotic_list = df.columns[2:].tolist()

    ## -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# TAB 1: COMPARISON WITH BACTERIA TOOLTIPS
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Compare Coverage")
    
    selected_antibiotics = st.multiselect(
        "Select antibiotics to see their spectrum:", 
        options=antibiotic_list,
        placeholder="Choose antibiotics...",
        key="tab1_multi"
    )
    
    if selected_antibiotics:
        # Filter logic
        mask = df[selected_antibiotics].notna().any(axis=1)
        display_cols = [type_col, bacteria_col] + selected_antibiotics
        
        # If you have a 'Notes' column in Excel, include it here
        # For now, we'll assume it's the 3rd column in your Excel (index 2)
        # display_cols.append('Clinical Notes') 
        
        comparison_df = df.loc[mask, display_cols].copy()

        # CONFIGURING THE BACTERIA COLUMN HOVER
        # We use st.column_config to add a help tooltip to the Bacteria header
        dynamic_config = {
            type_col: st.column_config.TextColumn("Type", width="small"),
            bacteria_col: st.column_config.TextColumn(
                "Bacteria Name",
                help="Hover over names to see clinical pearls." # Header tooltip
            )
        }

        # Apply the display
        st.dataframe(
            comparison_df.style.map(highlight_tab1, subset=selected_antibiotics),
            use_container_width=True,
            hide_index=True,
            column_config=dynamic_config
        )
         # ... (rest of your antibiotic coverage list logic from before)
  

# 4. SIDEBAR
with st.sidebar:
    st.write("### Legend")
    st.info("**Green (✔)**: Susceptible\n\n**Yellow (V)**: Variable \n\n**Gray**: No data/ Resistant")
