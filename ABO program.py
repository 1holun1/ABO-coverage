# --- 1. LOAD DATA (Updated for 3 fixed columns) ---
@st.cache_data
def load_data():
    file_name = "ABO_data.xlsx"
    try: 
        df = pd.read_excel(file_name, index_col=None, engine='openpyxl')
        # Assign names based on your new Excel order
        df.columns.values[0] = "Bacteria"
        df.columns.values[1] = "Type"
        df.columns.values[2] = "Information"
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# --- 2. TAB 1 LOGIC (Hiding the 'Information' column in the table) ---
with tab1:
    # Tell the code antibiotics start from the 4th column (index 3)
    antibiotic_list = df.columns[3:].tolist() 
    
    selected_antibiotics = st.multiselect(
        "Select antibiotics to compare:", 
        options=antibiotic_list, 
        key="t1"
    )
    
    if selected_antibiotics:
        mask = df[selected_antibiotics].notna().any(axis=1)
        
        # We explicitly exclude "Information" here to keep the table clean
        display_cols = ["Type", "Bacteria"] + selected_antibiotics
        comparison_df = df.loc[mask, display_cols].copy()
        
        st.dataframe(
            comparison_df.style.map(highlight_cells, subset=selected_antibiotics),
            use_container_width=True,
            hide_index=True,
            column_config={"Type": st.column_config.TextColumn("Type", width="small")}
        )
