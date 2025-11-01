"""
DSX Parent Availability Page
Simple, public-facing page for parents to mark player availability
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="DSX Team Availability",
    page_icon="⚽",
    layout="centered"
)

# Custom CSS for mobile-friendly design
st.markdown("""
<style>
    /* Mobile-first design */
    .stButton button {
        min-height: 50px !important;
        font-size: 16px !important;
    }
    
    /* Prevent iOS zoom on select */
    select {
        font-size: 16px !important;
    }
    
    /* Compact layout */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ DSX Orange 2018 - Player Availability")
st.write("Mark your player's availability for upcoming games and practices")

# Load schedule and roster
try:
    schedule = pd.read_csv("team_schedule.csv")
    schedule['Date'] = pd.to_datetime(schedule['Date'])
    roster = pd.read_csv("roster.csv")
    availability = pd.read_csv("schedule_availability.csv")
except Exception as e:
    st.error("Unable to load schedule data. Please contact coach.")
    st.caption(f"Technical details: {str(e)}")
    st.stop()

# Filter upcoming events only
upcoming = schedule[schedule['Date'] >= datetime.now()].sort_values('Date')

if upcoming.empty:
    st.info("No upcoming events scheduled")
    st.stop()

# Player selection
st.subheader("1️⃣ Select Your Player")
player_names = roster['PlayerName'].tolist()
selected_player = st.selectbox("Player Name", [""] + player_names, key="player_select")

if not selected_player:
    st.info("👆 Please select your player to continue")
    st.stop()

# Get player number
player_row = roster[roster['PlayerName'] == selected_player].iloc[0]
player_number = player_row['PlayerNumber']

st.success(f"✅ Selected: #{player_number} {selected_player}")

# Show upcoming events
st.markdown("---")
st.subheader("2️⃣ Mark Availability")

for idx, event in upcoming.iterrows():
    event_id = event['EventID']
    event_type = event['EventType']
    event_date = event['Date']
    event_time = event['Time']
    
    # Get current availability status
    current_status = availability[
        (availability['EventID'] == event_id) & 
        (availability['PlayerNumber'] == player_number)
    ]
    
    if not current_status.empty:
        status = current_status.iloc[0]['Status']
    else:
        status = "No Response"
    
    # Event card
    with st.expander(
        f"{'⚽' if event_type == 'Game' else '🏃'} {event_date.strftime('%a, %b %d')} - {event['Opponent'] if event['Opponent'] else 'Practice'} @ {event_time}",
        expanded=True
    ):
        st.write(f"**Location:** {event['Location']}")
        if event.get('ArrivalTime'):
            st.write(f"**Arrival Time:** {event['ArrivalTime']}")
        if event.get('UniformColor'):
            st.write(f"**Uniform:** {event['UniformColor']}")
        
        # Current status
        if status == "Available":
            st.success(f"✅ Current Status: **{status}**")
        elif status == "Not Available":
            st.error(f"❌ Current Status: **{status}**")
        elif status == "Maybe":
            st.warning(f"❓ Current Status: **{status}**")
        else:
            st.info(f"⚪ Current Status: **{status}**")
        
        # Response buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Available", key=f"avail_{event_id}", use_container_width=True):
                # Update availability
                mask = (availability['EventID'] == event_id) & (availability['PlayerNumber'] == player_number)
                if mask.any():
                    availability.loc[mask, 'Status'] = 'Available'
                    availability.loc[mask, 'ResponseTime'] = datetime.now()
                else:
                    new_row = pd.DataFrame([{
                        'EventID': event_id,
                        'PlayerNumber': player_number,
                        'PlayerName': selected_player,
                        'Status': 'Available',
                        'Notes': '',
                        'ResponseTime': datetime.now()
                    }])
                    availability = pd.concat([availability, new_row], ignore_index=True)
                
                availability.to_csv("schedule_availability.csv", index=False)
                st.success("✅ Marked as available!")
                st.rerun()
        
        with col2:
            if st.button("❌ Can't Make It", key=f"unavail_{event_id}", use_container_width=True):
                # Update availability
                mask = (availability['EventID'] == event_id) & (availability['PlayerNumber'] == player_number)
                if mask.any():
                    availability.loc[mask, 'Status'] = 'Not Available'
                    availability.loc[mask, 'ResponseTime'] = datetime.now()
                else:
                    new_row = pd.DataFrame([{
                        'EventID': event_id,
                        'PlayerNumber': player_number,
                        'PlayerName': selected_player,
                        'Status': 'Not Available',
                        'Notes': '',
                        'ResponseTime': datetime.now()
                    }])
                    availability = pd.concat([availability, new_row], ignore_index=True)
                
                availability.to_csv("schedule_availability.csv", index=False)
                st.error("❌ Marked as unavailable")
                st.rerun()
        
        with col3:
            if st.button("❓ Maybe", key=f"maybe_{event_id}", use_container_width=True):
                # Update availability
                mask = (availability['EventID'] == event_id) & (availability['PlayerNumber'] == player_number)
                if mask.any():
                    availability.loc[mask, 'Status'] = 'Maybe'
                    availability.loc[mask, 'ResponseTime'] = datetime.now()
                else:
                    new_row = pd.DataFrame([{
                        'EventID': event_id,
                        'PlayerNumber': player_number,
                        'PlayerName': selected_player,
                        'Status': 'Maybe',
                        'Notes': '',
                        'ResponseTime': datetime.now()
                    }])
                    availability = pd.concat([availability, new_row], ignore_index=True)
                
                availability.to_csv("schedule_availability.csv", index=False)
                st.warning("❓ Marked as maybe")
                st.rerun()

st.markdown("---")
st.caption("Questions? Contact Coach via team chat or text")
st.caption("💡 **Tip:** Bookmark this page on your phone for quick access!")





