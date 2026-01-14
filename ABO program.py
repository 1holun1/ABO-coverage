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
def show_bacteria_details(name, classification, details):
    st.markdown(f"### {name}")
    st.write(details if pd.notna(details) else "No additional details available for this organism.")
    
    # When this button is clicked, we clear the selection and rerun
    if st.button("Close and Clear Selection"):
        if 'tab1_df_key' in st.session_state:
            # This effectively "reboots" the dataframe component
            st.session_state.tab1_df_key += 1 
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
        # Initialize a counter in session state if it doesn't exist
        if 'tab1_df_key' not in st.session_state:
            st.session_state.tab1_df_key = 0

        # ... (your multiselect code) ...

        if selected_antibiotics:
            # ... (your masking and display_cols code) ...

            event = st.dataframe(
                comparison_df.style.map(highlight_tab1, subset=selected_antibiotics),
                use_container_width=True,
                hide_index=True,
                on_select="rerun", 
                selection_mode="single-row",
                # ADD THIS LINE: It uses the counter to reset the table on close
                key=f"data_table_{st.session_state.tab1_df_key}",
                column_config={
                    details_col: None,
                    type_col: st.column_config.TextColumn("Type", width="small")
                }
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                row_data = comparison_df.iloc[selected_index]
                show_bacteria_details(
                    row_data[bacteria_col], 
                    row_data[type_col], 
                    row_data[details_col]
                )
            # --- POPUP TRIGGER LOGIC ---
            if event.selection.rows:
                selected_index = event.selection.rows[0]
                st.session_state.popup_data = comparison_df.iloc[selected_index]

            if st.session_state.popup_data is not None:
                row = st.session_state.popup_data
                st.session_state.popup_data = None 
                show_bacteria_details(row[bacteria_col], row[type_col], row[details_col])
        else:
            for _ in range(10): st.write("")
        st.info("💡 **Tip:** Click the tick box to see common infections.")

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
                # FIXED STRING LITERAL HERE
                res_df = pd.DataFrame({
                    "Antibiotic": coverage.index,
                    "Effectiveness": coverage.values
                })

                def highlight_tab2(val):
                    if str(val).upper() == 'V':
                        return 'background-color: #ffeeba; color: black'
                    return 'background-color: #d4edda; color: black'

                st.table(res_df.style.map(highlight_tab2, subset=['Effectiveness']))
            else:
                st.warning("No antibiotic data found for this organism.")
        else:
            for _ in range(10): st.write("")

# 4. SIDEBAR
with st.sidebar:
    st.write("### Legend")
    st.info("**Green (✔)**: Susceptible\n\n**Yellow (V)**: Variable \n\n**Gray**: No data/ Resistant")



