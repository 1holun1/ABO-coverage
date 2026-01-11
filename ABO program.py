import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Antibiotic Coverage Search", page_icon="💊")

# -----------------------------------------------------------------------------
# 2. LOAD DATA
# -----------------------------------------------------------------------------
@st.cache_data # This caches the data so it doesn't reload on every click
def load_data():
    # Replace 'antibiotics_data.xlsx' with your actual file name
    # We assume index_col=0 so the first column (Bacteria names) becomes the index
    try: 
        df = pd.read_excel("ABO_data.xlsx", index_col=0)
        
        # Clean the data: replace NaN (empty cells) with a placeholder if needed,
        # or we will just filter them out later.
        return df
    except FileNotFoundError:
        st.error("File 'antibiotics_data.xlsx' not found. Please ensure the file is in the same folder.")
        print("Error!!!")
        return pd.DataFrame() # Return empty if failed
        

df = load_data()

# -----------------------------------------------------------------------------
# 3. THE UI AND SEARCH LOGIC
# -----------------------------------------------------------------------------
st.title("💊 Antibiotic Susceptibility Search")
st.markdown("Search for an antibiotic to see which bacteria it covers.")

if not df.empty:
    # --- The Search Feature ---
    # st.selectbox automatically provides the "type-ahead" suggestion feature.
    # If a user types "penici", it will filter the list to "Penicillin G", "Penicillin V", etc.
    antibiotic_list = df.columns.tolist()
    selected_antibiotic = st.selectbox("Type to search antibiotic:", antibiotic_list, index=None, placeholder="e.g. Penicillin...")

    # --- Display Results ---
    if selected_antibiotic:
        st.divider()
        st.subheader(f"Coverage for: {selected_antibiotic}")

        # Filter logic:
        # We want rows where the selected column is NOT empty (NaN).
        # We select the bacteria name (index) and the value (V, Checkmark, etc.)
        coverage_data = df[df[selected_antibiotic].notna()][[selected_antibiotic]]
        
        if coverage_data.empty:
            st.warning(f"No susceptible bacteria data found for {selected_antibiotic}.")
        else:
            # Let's rename the column for a cleaner display
            coverage_data.columns = ["Susceptibility Status"]
            
            # Optional: formatting "V" vs others
            # We can create a styled dataframe to highlight "V" in yellow and others in green
            def highlight_status(val):
                if str(val).upper() == 'V':
                    return 'background-color: #ffeeba; color: black' # Yellowish for Variable
                return 'background-color: #d4edda; color: black' # Greenish for Susceptible
            
            # Display the data
            st.dataframe(coverage_data.style.applymap(highlight_status), use_container_width=True)

else:
    st.info("Please add your 'antibiotics_data.xlsx' file to the directory.")

# -----------------------------------------------------------------------------
# 4. SIDEBAR INFO (Optional)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.write("### Legend")
    st.markdown("- **V**: Variable response")

    st.markdown("- **✔ / S**: Susceptible")
