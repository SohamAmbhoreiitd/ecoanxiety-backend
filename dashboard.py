import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Import the database URL from your existing config
from app.config import DATABASE_URL

# --- Page Configuration ---
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Database Connection ---
@st.cache_resource
def get_db_engine():
    """Creates and caches a database engine connection."""
    return create_engine(DATABASE_URL)

@st.cache_data
def load_data():
    """Loads conversation data from the database and caches it."""
    engine = get_db_engine()
    try:
        # SQL query to fetch all conversations
        query = "SELECT * FROM conversations ORDER BY timestamp DESC"
        df = pd.read_sql(query, engine)
        # Convert timestamp to a more readable format and set it as the index
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Failed to load data from the database: {e}")
        return pd.DataFrame() # Return empty dataframe on error

# --- Main Dashboard ---
st.title("📊 Eco-Anxiety Chatbot Analytics")
st.markdown("This dashboard provides insights into the chatbot's usage and interactions.")

# Load the data
data = load_data()

if not data.empty:
    # --- Key Metrics ---
    total_conversations = len(data)
    avg_query_length = data['user_query'].str.len().mean()
    avg_response_length = data['ai_response'].str.len().mean()

    st.header("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Conversations", f"{total_conversations}")
    col2.metric("Avg. Query Length", f"{avg_query_length:.0f} chars")
    col3.metric("Avg. Response Length", f"{avg_response_length:.0f} chars")

    # --- Conversations Over Time ---
    st.header("Conversations Over Time")
    # Resample data by day to count conversations per day
    daily_conversations = data.set_index('timestamp').resample('D').size()
    st.bar_chart(daily_conversations)

    # --- Raw Data View ---
    st.header("Recent Conversations Log")
    st.dataframe(data)
else:
    st.warning("No conversation data found in the database yet.")