import streamlit as st  # This MUST be line 1
import pandas as pd
st.write(f"Current Streamlit Version: {st.__version__}")
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

# --- TAB 1: COMPARE (Stable Selection for 1.52.2) ---
    with tab1:
        antibiotic_list = df.columns[3:].tolist()

        selected_antibiotics = st.multiselect(
            "Select antibiotics to compare:", 
            options=antibiotic_list, 
            key="t1"
        )
        
        if selected_antibiotics:
            mask = df[selected_antibiotics].notna().any(axis=1)
            # We keep 'Information' in the dataframe but hide it
            display_cols = ["Type", "Bacteria", "Information"] + selected_antibiotics
            comparison_df = df.loc[mask, display_cols].copy()
            
            st.info("💡 **Check the box** on the left of a bacterium to see its Clinical Pearls.")

            # We use st.data_editor because it handles the selection state 
            # more reliably than st.dataframe in some environments.
            selection_table = st.data_editor(
                comparison_df.style.map(highlight_cells, subset=selected_antibiotics),
                use_container_width=True,
                hide_index=True,
                key="bacteria_selector", # This key tracks the selection
                column_config={
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Information": None # Hide info from the table view
                },
                disabled=display_cols # Prevents users from typing in the cells
            )

            # --- LOGIC TO SHOW THE INFO BOX ---
            # We look into st.session_state for the 'selection' event
            state = st.session_state.get("bacteria_selector")
            if state and "selection" in state and state["selection"]["rows"]:
                selected_index = state["selection"]["rows"][0]
                
                # Pull data from the original comparison_df using the index
                bact_name = comparison_df.iloc[selected_row_index]["Bacteria"]
                bact_info = comparison_df.iloc[selected_row_index]["Information"]
                
                # Show the pop-out box
                st.success(f"🦠 **{bact_name} Clinical Pearls:**\n\n{bact_info}")
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











