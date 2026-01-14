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

# --- POPUP DIALOG FUNCTION ---
@st.dialog("Bacterium Information")
def show_bacteria_details(name, classifications, details):
    st.markdown(f"### {name}")
    st.markdown(f"**Classification:** {classifications}")
    st.divider()
    st.write(details if pd.notna(details) else "No additional details available for this organism.")
    if st.button("Close"):
        st.rerun()

# -----------------------------------------------------------------------------
# 3. TABS AND SEARCH LOGIC
# -----------------------------------------------------------------------------

if not df.empty:
    # Initialize Session State for the popup "event"
    if 'popup_data' not in st.session_state:
        st.session_state.popup_data = None

    bacteria_col = df.columns[0]   # Col 1: Name
    type_col = df.columns[1]       # Col 2: Type
    details_col = df.columns[2]    # Col 3: Details
    antibiotic_list = df.columns[3:].tolist() # Col 4 onwards: Antibiotics

    tab1, tab2 = st.tabs(["💊 Compare Antibiotics", "🦠 Search Bacteria"])

    # --- TAB 1: COMPARE ANTIBIOTICS ---
    with tab1:
        st.subheader("Compare Coverage")
        st.info("💡 **Tip:** Click a row in the table to see bacterium details.")
        
        selected_antibiotics = st.multiselect(
            "Select antibiotics to see their spectrum:", 
            options=antibiotic_list,
            placeholder="Choose antibiotics...",
            key="tab1_multi"
        )
        
        if selected_antibiotics:
            mask = df[selected_antibiotics].notna().any(axis=1)
            display_cols = [bacteria_col, type_col, details_col] + selected_antibiotics
            comparison_df = df.loc[mask, display_cols].copy()
            
            # Styling Logic
            def highlight_tab1(val):
                v_str = str(val).strip().lower()
                if pd.isna(val) or v_str == "" or v_str == 'none':
                    return 'background-color: #f0f2f6; color: #999999'
                if v_str == 'v':
                    return 'background-color: #ffeeba; color: black'
                return 'background-color: #d4edda; color: black'

            # Display Dataframe
            event = st.dataframe(
                comparison_df.style.map(highlight_tab1, subset=selected_antibiotics),
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    details_col: None, 
                    type_col: st.column_config.TextColumn("Type", width="small")
                }
            )

            # --- POPUP TRIGGER LOGIC ---
            # 1. Capture the selection and save to session state
            if event.selection.rows:
                selected_index = event.selection.rows[0]
                st.session_state.popup_data = comparison_df.iloc[selected_index]

            # 2. Show popup and then "consume" the event by clearing session state
            if st.session_state.popup_data is not None:
                row = st.session_state.popup_data
                # Clear the data BEFORE showing to prevent re-triggering on tab switch
                st.session_state.popup_data = None 
                show_bacteria_details(row[bacteria_col], row[type_col], row[details_col])
        else:
            for _ in range(10): st.write("")

    # --- TAB 2: SEARCH BACTERIA ---
    with tab2:
        st.subheader("What covers this bacterium?")
        selected_organism = st.selectbox(
            "Search for a bacterium:",
            options=df[bacteria_col].unique(),
            index=None,
            placeholder="Type bacteria name here...",
            key="tab2_select"
        )

        if selected_organism:
            row = df[df[bacteria_col] == selected_organism].iloc[0]
            
            st.markdown(f"**Classification:** {row[type_col]}")
            st.info(f"**Details:** {row[details_col]}")
            
            coverage = row[antibiotic_list].dropna()
            coverage = coverage[coverage.astype(str).str.lower() != 'none']
            
            if not coverage.empty:
                res_df = pd.DataFrame({
                    "Antib
