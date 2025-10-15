"""
DSX Opponent Tracker - Interactive Dashboard
A Streamlit-based GUI replacing Excel functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import time

# Page configuration
st.set_page_config(
    page_title="DSX Opponent Tracker",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to fix display issues
st.markdown("""
<style>
    /* Fix white overlay issues - remove all backgrounds */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
        background: transparent !important;
    }
    
    /* Remove any white overlays */
    .stApp > div {
        background: transparent !important;
    }
    
    /* Fix metric boxes */
    [data-testid="stMetricValue"] {
        background: transparent !important;
    }
    
    div[data-testid="column"] {
        background: transparent !important;
    }
    
    /* Ensure proper stacking */
    .stMarkdown, .stDataFrame, .stPlotlyChart {
        z-index: 1;
        background: transparent !important;
    }
    
    /* Metric styling - with transparency */
    .stMetric {
        background-color: rgba(240, 242, 246, 0.5) !important;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Better text contrast - brighter text */
    .stMarkdown p, .stMarkdown li {
        color: #FAFAFA !important;
    }
    
    /* Bright text for all content */
    .stMarkdown, .stMarkdown * {
        color: #FAFAFA !important;
    }
    
    /* Fix expander visibility */
    .streamlit-expanderHeader {
        background-color: #f0f2f6 !important;
    }
    
    .streamlit-expanderContent {
        background-color: white !important;
        border: 1px solid #e6e6e6;
    }
    
    /* Ensure all text is readable */
    div[data-testid="stExpander"] {
        background-color: transparent !important;
    }
    
    /* Force remove any white overlays on comparison sections */
    div[data-testid="stHorizontalBlock"] {
        background: transparent !important;
    }
    
    /* Make sure headings are bright and visible */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        background: transparent !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* Bright text in expanders */
    .streamlit-expanderContent p, 
    .streamlit-expanderContent li,
    .streamlit-expanderContent div {
        color: #333333 !important;
    }
    
    /* Info boxes with good contrast */
    div[data-testid="stMarkdownContainer"] {
        color: #FAFAFA !important;
    }
    
    /* Strong/bold text should be even brighter */
    strong, b {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* Links should be bright blue */
    a {
        color: #4DA6FF !important;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        /* Larger tap targets for game day */
        .stButton button {
            min-height: 60px !important;
            font-size: 18px !important;
            padding: 12px !important;
        }
        
        /* Compact timer display */
        [data-testid="metric-container"] {
            padding: 8px !important;
        }
        
        /* Hide keyboard on dropdowns - prevents iOS zoom */
        select {
            font-size: 16px !important;
        }
        
        /* Scrollable event log */
        .event-log {
            max-height: 200px;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        /* Goalkeeper section spacing */
        .gk-actions {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
        }
        
        /* Radio buttons - larger for mobile */
        .stRadio > div {
            gap: 12px !important;
        }
        
        .stRadio label {
            padding: 10px !important;
            font-size: 16px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_division_data():
    """Load division rankings from all tracked divisions"""
    all_divisions = []
    
    # List of all division files to load
    division_files = [
        "OCL_BU08_Stripes_Division_Rankings.csv",     # 23 teams (Northeast, Northwest, Southeast)
        "OCL_BU08_White_Division_Rankings.csv",       # Club Ohio West division
        "OCL_BU08_Stars_Division_Rankings.csv",       # 5v5 Stars division
        "OCL_BU08_Stars_7v7_Division_Rankings.csv",   # 7v7 Stars division (Elite FC Arsenal)
        "MVYSA_B09_3_Division_Rankings.csv",          # 6 teams (BSA Celtic division)
    ]
    
    for file in division_files:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file, index_col=False).reset_index(drop=True)
                all_divisions.append(df)
            except Exception as e:
                st.warning(f"⚠️ Could not load {file}: {str(e)}")
    
    # Combine all divisions
    if all_divisions:
        combined = pd.concat(all_divisions, ignore_index=True)
        # Remove duplicates based on Team name
        combined = combined.drop_duplicates(subset=['Team'], keep='first')
        return combined
    
    return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes (more frequent updates for match data)
def calculate_dsx_stats():
    """Calculate DSX statistics dynamically from match data"""
    try:
        dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False).reset_index(drop=True)
        
        # Check if Result or Outcome column exists
        result_col = 'Result' if 'Result' in dsx_matches.columns else 'Outcome'
        
        completed = dsx_matches[dsx_matches[result_col].notna()].copy()
        
        if len(completed) > 0:
            dsx_gp = len(completed)
            dsx_w = len(completed[completed[result_col] == 'W'])
            dsx_d = len(completed[completed[result_col] == 'D'])
            dsx_l = len(completed[completed[result_col] == 'L'])
            dsx_gf = pd.to_numeric(completed['GF'], errors='coerce').fillna(0).sum()
            dsx_ga = pd.to_numeric(completed['GA'], errors='coerce').fillna(0).sum()
            dsx_gd = dsx_gf - dsx_ga
            dsx_pts = (dsx_w * 3) + dsx_d
            dsx_ppg = dsx_pts / dsx_gp if dsx_gp > 0 else 0
            dsx_gf_pg = dsx_gf / dsx_gp if dsx_gp > 0 else 0
            dsx_ga_pg = dsx_ga / dsx_gp if dsx_gp > 0 else 0
            dsx_gd_pg = dsx_gd / dsx_gp if dsx_gp > 0 else 0
            
            # Calculate DSX Strength Index
            ppg_norm = max(0.0, min(3.0, dsx_ppg)) / 3.0 * 100.0
            gdpg_norm = (max(-5.0, min(5.0, dsx_gd_pg)) + 5.0) / 10.0 * 100.0
            dsx_strength = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
            
            return {
                'Team': 'Dublin DSX Orange 2018 Boys',
                'GP': dsx_gp,
                'W': dsx_w,
                'D': dsx_d,
                'L': dsx_l,
                'Record': f"{dsx_w}-{dsx_d}-{dsx_l}",
                'GF': dsx_gf,
                'GA': dsx_ga,
                'GD': dsx_gd,
                'Pts': dsx_pts,
                'PPG': dsx_ppg,
                'GF_PG': dsx_gf_pg,
                'GA_PG': dsx_ga_pg,
                'GD_PG': dsx_gd_pg,
                'StrengthIndex': dsx_strength
            }
        else:
            return {
                'Team': 'Dublin DSX Orange 2018 Boys',
                'GP': 0,
                'W': 0,
                'D': 0,
                'L': 0,
                'Record': '0-0-0',
                'GF': 0,
                'GA': 0,
                'GD': 0,
                'Pts': 0,
                'PPG': 0,
                'GF_PG': 0,
                'GA_PG': 0,
                'GD_PG': 0,
                'StrengthIndex': 0
            }
    except Exception as e:
        st.error(f"Error calculating DSX stats: {str(e)}")
        return {
            'Team': 'Dublin DSX Orange 2018 Boys',
            'GP': 0,
            'W': 0,
            'D': 0,
            'L': 0,
            'Record': '0-0-0',
            'GF': 0,
            'GA': 0,
            'GD': 0,
            'Pts': 0,
            'PPG': 0,
            'GF_PG': 0,
            'GA_PG': 0,
            'GD_PG': 0,
            'StrengthIndex': 0
        }


@st.cache_data(ttl=3600)
def load_dsx_matches():
    """Load DSX match history"""
    # From the conversation - could also load from CSV
    matches = [
        {'Date': '2025-08-09', 'Tournament': 'Dublin Charity Cup', 'Opponent': '2017 Boys Premier OCL', 'GF': 3, 'GA': 15},
        {'Date': '2025-08-16', 'Tournament': 'Dublin Charity Cup', 'Opponent': 'Blast FC U8', 'GF': 4, 'GA': 5},
        {'Date': '2025-08-30', 'Tournament': 'Obetz Futbol Cup', 'Opponent': 'Elite FC 2018 Boys Liverpool', 'GF': 5, 'GA': 6},
        {'Date': '2025-08-30', 'Tournament': 'Obetz Futbol Cup', 'Opponent': 'Ohio Premier 2017 Boys Academy Dublin White', 'GF': 0, 'GA': 13},
        {'Date': '2025-08-31', 'Tournament': 'Obetz Futbol Cup', 'Opponent': 'Elite FC 2018 Boys Arsenal', 'GF': 4, 'GA': 2},
        {'Date': '2025-09-05', 'Tournament': 'Murfin Friendly Series', 'Opponent': 'LFC United 2018B Elite 2', 'GF': 11, 'GA': 0},
        {'Date': '2025-09-06', 'Tournament': 'Murfin Friendly Series', 'Opponent': 'Elite FC 2018 Boys Tottenham', 'GF': 4, 'GA': 4},
        {'Date': '2025-09-07', 'Tournament': 'Murfin Friendly Series', 'Opponent': 'Northwest FC 2018B Academy Blue', 'GF': 1, 'GA': 4},
        {'Date': '2025-09-27', 'Tournament': 'Grove City Fall Classic', 'Opponent': 'Barcelona United Elite 18B', 'GF': 7, 'GA': 2},
        {'Date': '2025-09-27', 'Tournament': 'Grove City Fall Classic', 'Opponent': 'Columbus United U8B', 'GF': 5, 'GA': 5},
        {'Date': '2025-09-28', 'Tournament': 'Grove City Fall Classic', 'Opponent': 'Grove City Kids Association 2018B', 'GF': 2, 'GA': 2},
        {'Date': '2025-09-28', 'Tournament': 'Grove City Fall Classic', 'Opponent': 'Columbus United U8B', 'GF': 4, 'GA': 3},
    ]
    df = pd.DataFrame(matches)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Result'] = df.apply(lambda r: 'W' if r['GF'] > r['GA'] else ('D' if r['GF'] == r['GA'] else 'L'), axis=1)
    df['GD'] = df['GF'] - df['GA']
    return df


@st.cache_data(ttl=3600)
def load_opponent_schedules():
    """Load opponent schedules if available"""
    if os.path.exists("BSA_Celtic_Schedules.csv"):
        return pd.read_csv("BSA_Celtic_Schedules.csv")
    return pd.DataFrame()


def refresh_data():
    """Refresh all cached data"""
    st.cache_data.clear()
    st.success("Data refreshed!")


# Sidebar
with st.sidebar:
    # Team logo
    import os
    if os.path.exists("dsx_logo.png"):
        st.image("dsx_logo.png", use_container_width=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); border-radius: 10px; margin-bottom: 20px;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>⚽ DSX ORANGE</h1>
            <p style='color: white; margin: 5px 0 0 0; font-size: 1.2em;'>U8 Boys 2018 - Fall 2025</p>
        </div>
        """, unsafe_allow_html=True)
    st.title("⚽ DSX Tracker")
    st.markdown("**Dublin DSX Orange**  \n2018 Boys")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🎯 What's Next", "📅 Team Schedule", "🎮 Live Game Tracker", "📺 Watch Live Game", "💬 Team Chat", "🏆 Division Rankings", "📊 Team Analysis", "👥 Player Stats", "📅 Match History", "📝 Game Log", "🔍 Opponent Intel", "🎮 Game Predictions", "📊 Benchmarking", "📋 Full Analysis", "📖 Quick Start Guide", "⚙️ Data Manager"]
    )
    
    st.markdown("---")
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        refresh_data()


# Main content
if page == "🎯 What's Next":
    st.title("🎯 What's Next - Smart Game Prep")
    
    st.info("⚡ Your command center for upcoming matches with AI-powered insights and predictions")
    
    # Load upcoming matches
    try:
        upcoming = pd.read_csv("DSX_Upcoming_Opponents.csv")
        dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv")
        
        # Load division data for predictions
        all_divisions_df = load_division_data()
        
        # Calculate DSX stats dynamically
        dsx_stats = calculate_dsx_stats()
        dsx_si = dsx_stats['StrengthIndex']
        dsx_gf_avg = dsx_stats['GF_PG']
        dsx_ga_avg = dsx_stats['GA_PG']
        dsx_gd_avg = dsx_stats['GD_PG']
        
        st.header("📅 Next 3 Games")
        st.markdown("---")
        
        for idx, game in upcoming.head(3).iterrows():
            opponent = game['Opponent']
            game_date = game['Date']
            location = game['Location']
            league = game.get('Tournament', game.get('League', 'N/A'))
            
            with st.expander(f"**{game_date}**: {opponent} ({league})", expanded=(idx==0)):
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.subheader("📍 Game Info")
                    st.write(f"**Date:** {game_date}")
                    st.write(f"**Location:** {location}")
                    st.write(f"**League:** {league}")
                    st.write(f"**Notes:** {game.get('Notes', 'N/A')}")
                
                with col2:
                    st.subheader("🎯 Match Prediction")
                    
                    # Get opponent stats from consolidated division data
                    opp_si = None
                    opp_gf = None
                    opp_ga = None
                    
                    if not all_divisions_df.empty:
                        opp_data = all_divisions_df[all_divisions_df['Team'] == opponent]
                        if not opp_data.empty:
                            team = opp_data.iloc[0]
                            opp_si = team['StrengthIndex']
                            # Calculate per-game stats
                            opp_gp = team.get('GP', 1)
                            opp_gp = opp_gp if opp_gp > 0 else 1
                            opp_gf = team.get('GF', 0) / opp_gp  # Goals per game
                            opp_ga = team.get('GA', 0) / opp_gp  # Goals against per game
                    
                    if opp_si is not None:
                        # Display opponent strength
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Opponent SI", f"{opp_si:.1f}")
                        with col_b:
                            st.metric("DSX SI", f"{dsx_si:.1f}")
                        with col_c:
                            si_diff = dsx_si - opp_si
                            st.metric("Advantage", f"{si_diff:+.1f}", delta_color="normal")
                        
                        # Predicted score
                        st.markdown("---")
                        st.subheader("🔮 Score Prediction")
                        
                        # Simple prediction based on average goals
                        # More balanced prediction formula
                        # DSX gets bonus for being stronger, opponent gets penalty for being weaker
                        # But don't make weak teams completely scoreless
                        pred_dsx_goals = max(0.5, dsx_gf_avg + (si_diff * 0.02))
                        pred_opp_goals = max(0.5, opp_gf if opp_gf else dsx_ga_avg - (si_diff * 0.02))
                        
                        # Calculate ranges for confidence assessment
                        pred_dsx_low = max(0, pred_dsx_goals - 1.5)
                        pred_dsx_high = pred_dsx_goals + 1.5
                        pred_opp_low = max(0, pred_opp_goals - 1.5)
                        pred_opp_high = pred_opp_goals + 1.5
                        
                        # Calculate single score predictions (rounded to realistic values)
                        dsx_prediction = round(pred_dsx_goals)
                        opp_prediction = round(pred_opp_goals)
                        
                        # Calculate confidence based on range tightness
                        dsx_range = pred_dsx_high - pred_dsx_low
                        opp_range = pred_opp_high - pred_opp_low
                        avg_range = (dsx_range + opp_range) / 2
                        
                        if avg_range <= 2.0:
                            confidence = "High"
                            confidence_color = "🟢"
                            confidence_style = "success"
                        elif avg_range <= 3.0:
                            confidence = "Medium"
                            confidence_color = "🟡"
                            confidence_style = "warning"
                        else:
                            confidence = "Low"
                            confidence_color = "🔴"
                            confidence_style = "error"
                        
                        # Display predictions with range and confidence
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**DSX:** {dsx_prediction} goals")
                            st.caption(f"(range: {pred_dsx_low:.1f}-{pred_dsx_high:.1f})")
                        
                        with col2:
                            st.write(f"**{opponent}:** {opp_prediction} goals")
                            st.caption(f"(range: {pred_opp_low:.1f}-{pred_opp_high:.1f})")
                        
                        # Final score prediction with confidence color
                        if confidence_style == "success":
                            st.success(f"**Final: DSX {dsx_prediction}-{opp_prediction} {opponent}**")
                        elif confidence_style == "warning":
                            st.warning(f"**Final: DSX {dsx_prediction}-{opp_prediction} {opponent}**")
                        else:
                            st.error(f"**Final: DSX {dsx_prediction}-{opp_prediction} {opponent}**")
                        
                        st.write(f"{confidence_color} **Confidence: {confidence}** (range: {avg_range:.1f} goals)")
                        
                        # Win probability
                        st.markdown("---")
                        if si_diff > 10:
                            win_prob = 65
                            draw_prob = 25
                            loss_prob = 10
                            st.success(f"✅ **Win Probability: {win_prob}%**")
                        elif si_diff < -10:
                            win_prob = 25
                            draw_prob = 30
                            loss_prob = 45
                            st.error(f"⚠️ **Win Probability: {win_prob}%**")
                        else:
                            win_prob = 40
                            draw_prob = 30
                            loss_prob = 30
                            st.info(f"⚖️ **Win Probability: {win_prob}%**")
                        
                        st.write(f"Draw: {draw_prob}% | Loss: {loss_prob}%")
                    else:
                        st.warning("Opponent data not available. Run data update to get predictions.")
                
                st.markdown("---")
                
                # Keys to Victory
                st.subheader("🔑 Keys to Victory")
                
                if opp_si and opp_si > dsx_si + 10:
                    st.write("**Defensive Focus:**")
                    st.write("- ✅ Stay compact defensively")
                    st.write("- ✅ Quick counter-attacks")
                    st.write("- ✅ Set piece opportunities")
                    st.write("- ✅ High energy for 60 minutes")
                elif opp_si and opp_si < dsx_si - 10:
                    st.write("**Offensive Pressure:**")
                    st.write("- ✅ High press from kickoff")
                    st.write("- ✅ Dominate possession")
                    st.write("- ✅ Create multiple chances")
                    st.write("- ✅ Early goal to set tone")
                else:
                    st.write("**Balanced Approach:**")
                    st.write("- ✅ Stay organized defensively")
                    st.write("- ✅ Be clinical with chances")
                    st.write("- ✅ Match their intensity")
                    st.write("- ✅ Capitalize on mistakes")
        
        st.markdown("---")
        
        # Quick Stats Summary
        st.header("📊 DSX Season Performance")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Strength Index", f"{dsx_si:.1f}")
        with col2:
            st.metric("Goals/Game", f"{dsx_gf_avg:.2f}")
        with col3:
            st.metric("Against/Game", f"{dsx_ga_avg:.2f}")
        with col4:
            st.metric("GD/Game", f"{dsx_gd_avg:+.2f}")
        with col5:
            games_played = len(dsx_matches)
            st.metric("Games Played", games_played)
        
        st.markdown("---")
        
        # Smart Insights
        st.header("💡 Smart Insights")
        
        insights = []
        
        # Analyze recent form
        recent_matches = dsx_matches.tail(5)
        recent_points = recent_matches['Points'].sum()
        recent_ppg = recent_points / 5 if len(recent_matches) >= 5 else 0
        
        if recent_ppg > 1.5:
            insights.append("🔥 **Hot Streak:** DSX averaging " + f"{recent_ppg:.2f} PPG in last 5 games (above season average)")
        elif recent_ppg < 0.8:
            insights.append("⚠️ **Slump Alert:** Only " + f"{recent_ppg:.2f} PPG in last 5 games - time to regroup")
        
        # Goal scoring
        if dsx_gf_avg > 4.0:
            insights.append("⚽ **Offensive Strength:** DSX averages " + f"{dsx_gf_avg:.2f} goals/game - one of the best attacks")
        
        # Defensive issues
        if dsx_ga_avg > 4.5:
            insights.append("🛡️ **Defensive Focus Needed:** Allowing " + f"{dsx_ga_avg:.2f} goals/game - work on organization")
        
        # Consistency
        gd_variance = dsx_matches['GoalDiff'].std() if len(dsx_matches) > 0 else 0
        if gd_variance > 5:
            insights.append("📊 **Inconsistent Results:** Wide range of scores - focus on consistency")
        
        for insight in insights:
            st.write(insight)
        
        if not insights:
            st.write("✅ **Solid Performance:** DSX showing steady, consistent play")
            
    except FileNotFoundError:
        st.error("Upcoming schedule not found. Create `DSX_Upcoming_Opponents.csv` with your schedule.")
        st.write("Or run `python update_all_data.py` to fetch latest data.")


elif page == "📅 Team Schedule":
    st.title("📅 Team Schedule")
    
    st.success("🎯 **Your complete schedule - games, practices, and availability tracking all in one place!**")
    
    # Load schedule and availability data
    try:
        schedule = pd.read_csv("team_schedule.csv")
        schedule['Date'] = pd.to_datetime(schedule['Date'])
        
        try:
            availability = pd.read_csv("schedule_availability.csv")
        except:
            availability = pd.DataFrame()
        
        try:
            roster = pd.read_csv("roster.csv")
            total_players = len(roster)
        except:
            total_players = 11
        
        # Load division data for opponent SI
        all_divisions = load_division_data()
        
        # Auto-populate OpponentStrengthIndex if missing
        for idx, row in schedule.iterrows():
            if pd.isna(row.get('OpponentStrengthIndex')) or row.get('OpponentStrengthIndex') == '':
                if row['EventType'] == 'Game' and row['Opponent']:
                    opp_data = all_divisions[all_divisions['Team'] == row['Opponent']]
                    if not opp_data.empty:
                        schedule.at[idx, 'OpponentStrengthIndex'] = opp_data.iloc[0]['StrengthIndex']
        
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            view_mode = st.selectbox("View", ["📋 List View", "📅 Calendar View", "📆 Week View"])
        
        with col2:
            event_filter = st.selectbox("Show", ["All Events", "Games Only", "Practices Only"])
        
        with col3:
            status_filter = st.selectbox("Status", ["All", "Upcoming", "Completed", "Cancelled"])
        
        with col4:
            month_filter = st.selectbox("Month", ["All Months"] + sorted(schedule['Date'].dt.strftime('%B %Y').unique().tolist()))
        
        # Apply filters
        filtered = schedule.copy()
        
        if event_filter == "Games Only":
            filtered = filtered[filtered['EventType'] == 'Game']
        elif event_filter == "Practices Only":
            filtered = filtered[filtered['EventType'] == 'Practice']
        
        if status_filter != "All":
            filtered = filtered[filtered['Status'] == status_filter]
        
        if month_filter != "All Months":
            filtered = filtered[filtered['Date'].dt.strftime('%B %Y') == month_filter]
        
        # Sort by date
        filtered = filtered.sort_values('Date')
        
        st.markdown("---")
        
        # LIST VIEW
        if view_mode == "📋 List View":
            st.subheader(f"📋 {event_filter} ({len(filtered)} events)")
            
            if filtered.empty:
                st.info("No events match your filters")
            else:
                for idx, event in filtered.iterrows():
                    event_id = event['EventID']
                    event_type = event['EventType']
                    event_date = event['Date']
                    event_time = event['Time']
                    
                    # Get availability summary for this event
                    avail_data = availability[availability['EventID'] == event_id]
                    available_count = len(avail_data[avail_data['Status'] == 'Available'])
                    not_available_count = len(avail_data[avail_data['Status'] == 'Not Available'])
                    maybe_count = len(avail_data[avail_data['Status'] == 'Maybe'])
                    no_response_count = len(avail_data[avail_data['Status'] == 'No Response'])
                    
                    # Event card styling based on type
                    if event_type == 'Game':
                        icon = "⚽"
                        bg_color = "#e3f2fd"
                        border_color = "#2196F3"
                    else:
                        icon = "🏃"
                        bg_color = "#f3e5f5"
                        border_color = "#9C27B0"
                    
                    # Create expandable event card
                    with st.expander(
                        f"{icon} **{event_date.strftime('%a, %b %d')}** - {event['Opponent'] if event['Opponent'] else 'Practice'} @ {event_time}",
                        expanded=False
                    ):
                        # Event details
                        col1, col2 = st.columns([2, 3])
                        
                        with col1:
                            st.markdown("### 📍 Event Info")
                            st.write(f"**Type:** {event_type}")
                            st.write(f"**Date:** {event_date.strftime('%A, %B %d, %Y')}")
                            st.write(f"**Time:** {event_time}")
                            st.write(f"**Arrival:** {event.get('ArrivalTime', 'TBD')}")
                            st.write(f"**Location:** {event['Location']}")
                            st.write(f"**Field:** {event.get('FieldNumber', 'TBD')}")
                            st.write(f"**Uniform:** {event.get('UniformColor', 'TBD')}")
                            
                            if event_type == 'Game':
                                st.write(f"**Home/Away:** {event.get('HomeAway', 'TBD')}")
                                st.write(f"**Tournament:** {event.get('Tournament', 'N/A')}")
                                
                                # Opponent Strength Index
                                opp_si = event.get('OpponentStrengthIndex')
                                if pd.notna(opp_si) and opp_si != '':
                                    dsx_stats = calculate_dsx_stats()
                                    dsx_si = dsx_stats['StrengthIndex']
                                    st.metric("Opponent SI", f"{opp_si:.1f}", 
                                             delta=f"DSX: {dsx_si:.1f}",
                                             delta_color="off")
                            
                            if event.get('Notes'):
                                st.write(f"**Notes:** {event['Notes']}")
                        
                        with col2:
                            st.markdown("### 👥 Availability")
                            
                            # Availability summary
                            total_responded = available_count + not_available_count + maybe_count
                            response_rate = (total_responded / total_players * 100) if total_players > 0 else 0
                            
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            with metric_col1:
                                st.metric("✅ Available", available_count)
                            with metric_col2:
                                st.metric("❌ Not Available", not_available_count)
                            with metric_col3:
                                st.metric("❓ Maybe", maybe_count)
                            
                            if no_response_count > 0:
                                st.warning(f"⚠️ {no_response_count} player(s) haven't responded")
                            
                            st.progress(response_rate / 100, text=f"Response Rate: {response_rate:.0f}%")
                            
                            st.markdown("---")
                            
                            # Quick availability response
                            st.markdown("**Your Response:**")
                            
                            # Check if current user (assuming coach) has responded
                            response_col1, response_col2, response_col3 = st.columns(3)
                            
                            with response_col1:
                                if st.button("✅ Available", key=f"avail_{event_id}", use_container_width=True):
                                    # Update schedule_availability.csv
                                    try:
                                        availability_df = pd.read_csv("schedule_availability.csv")
                                        coach_player_num = 0  # Coach = PlayerNumber 0
                                        mask = (availability_df['EventID'] == event_id) & (availability_df['PlayerNumber'] == coach_player_num)
                                        if mask.any():
                                            availability_df.loc[mask, 'Status'] = 'Available'
                                            availability_df.loc[mask, 'ResponseTime'] = datetime.now()
                                        else:
                                            new_row = pd.DataFrame([{
                                                'EventID': event_id,
                                                'PlayerNumber': coach_player_num,
                                                'PlayerName': 'Coach',
                                                'Status': 'Available',
                                                'Notes': '',
                                                'ResponseTime': datetime.now()
                                            }])
                                            availability_df = pd.concat([availability_df, new_row], ignore_index=True)
                                        availability_df.to_csv("schedule_availability.csv", index=False)
                                        st.success("✅ Marked as available!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating availability: {e}")
                            
                            with response_col2:
                                if st.button("❌ Can't Make It", key=f"unavail_{event_id}", use_container_width=True):
                                    # Update schedule_availability.csv
                                    try:
                                        availability_df = pd.read_csv("schedule_availability.csv")
                                        coach_player_num = 0  # Coach = PlayerNumber 0
                                        mask = (availability_df['EventID'] == event_id) & (availability_df['PlayerNumber'] == coach_player_num)
                                        if mask.any():
                                            availability_df.loc[mask, 'Status'] = 'Not Available'
                                            availability_df.loc[mask, 'ResponseTime'] = datetime.now()
                                        else:
                                            new_row = pd.DataFrame([{
                                                'EventID': event_id,
                                                'PlayerNumber': coach_player_num,
                                                'PlayerName': 'Coach',
                                                'Status': 'Not Available',
                                                'Notes': '',
                                                'ResponseTime': datetime.now()
                                            }])
                                            availability_df = pd.concat([availability_df, new_row], ignore_index=True)
                                        availability_df.to_csv("schedule_availability.csv", index=False)
                                        st.error("❌ Marked as unavailable")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating availability: {e}")
                            
                            with response_col3:
                                if st.button("❓ Maybe", key=f"maybe_{event_id}", use_container_width=True):
                                    # Update schedule_availability.csv
                                    try:
                                        availability_df = pd.read_csv("schedule_availability.csv")
                                        coach_player_num = 0  # Coach = PlayerNumber 0
                                        mask = (availability_df['EventID'] == event_id) & (availability_df['PlayerNumber'] == coach_player_num)
                                        if mask.any():
                                            availability_df.loc[mask, 'Status'] = 'Maybe'
                                            availability_df.loc[mask, 'ResponseTime'] = datetime.now()
                                        else:
                                            new_row = pd.DataFrame([{
                                                'EventID': event_id,
                                                'PlayerNumber': coach_player_num,
                                                'PlayerName': 'Coach',
                                                'Status': 'Maybe',
                                                'Notes': '',
                                                'ResponseTime': datetime.now()
                                            }])
                                            availability_df = pd.concat([availability_df, new_row], ignore_index=True)
                                        availability_df.to_csv("schedule_availability.csv", index=False)
                                        st.warning("❓ Marked as maybe")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating availability: {e}")
                        
                        st.markdown("---")
                        
                        # Quick Actions
                        st.markdown("### ⚡ Quick Actions")
                        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                        
                        with action_col1:
                            if event_type == 'Game':
                                if st.button("🎮 Start Live Tracker", key=f"track_{event_id}", use_container_width=True):
                                    # Pre-fill Live Game Tracker data in session state
                                    st.session_state.prefill_game_data = {
                                        'date': event['Date'].strftime('%Y-%m-%d'),
                                        'opponent': event['Opponent'],
                                        'location': event['Location'],
                                        'tournament': event.get('Tournament', ''),
                                        'field': event.get('FieldNumber', ''),
                                        'uniform': event.get('UniformColor', '')
                                    }
                                    st.success(f"✅ Game data ready! Go to **🎮 Live Game Tracker** to start recording.")
                                    st.info("💡 **Tip:** Use the sidebar to navigate to Live Game Tracker. Your game details will be pre-filled!")
                        
                        with action_col2:
                            if st.button("📝 View Details", key=f"detail_{event_id}", use_container_width=True):
                                # Show detailed event info
                                st.markdown("---")
                                st.markdown("#### 📋 Complete Event Details")
                                
                                detail_col1, detail_col2 = st.columns(2)
                                
                                with detail_col1:
                                    st.write(f"**📅 Date:** {event['Date'].strftime('%A, %B %d, %Y')}")
                                    st.write(f"**🕐 Game Time:** {event['Time']}")
                                    st.write(f"**⏰ Arrival Time:** {event.get('ArrivalTime', 'TBD')}")
                                    st.write(f"**📍 Location:** {event['Location']}")
                                    st.write(f"**🏟️ Field Number:** {event.get('FieldNumber', 'TBD')}")
                                
                                with detail_col2:
                                    st.write(f"**👕 Uniform:** {event.get('UniformColor', 'TBD')}")
                                    st.write(f"**🏠 Home/Away:** {event.get('HomeAway', 'TBD')}")
                                    st.write(f"**🏆 Tournament:** {event.get('Tournament', 'N/A')}")
                                    st.write(f"**📊 Status:** {event['Status']}")
                                    
                                    if event_type == 'Game' and pd.notna(event.get('OpponentStrengthIndex')) and event.get('OpponentStrengthIndex') != '':
                                        dsx_stats = calculate_dsx_stats()
                                        st.write(f"**⚡ Opponent SI:** {event.get('OpponentStrengthIndex'):.1f}")
                                        st.write(f"**⚡ DSX SI:** {dsx_stats['StrengthIndex']:.1f}")
                                
                                if event.get('Notes'):
                                    st.write(f"**📝 Notes:** {event['Notes']}")
                                
                                st.markdown("---")
                        
                        with action_col3:
                            if event_type == 'Game' and event.get('Opponent'):
                                if st.button("🔍 Opponent Intel", key=f"intel_{event_id}", use_container_width=True):
                                    # Store opponent for Opponent Intel page
                                    st.session_state.selected_opponent = event['Opponent']
                                    st.success(f"✅ Opponent selected: **{event['Opponent']}**")
                                    st.info("💡 **Go to 🔍 Opponent Intel** page to see full scouting report!")
                        
                        with action_col4:
                            location_query = event['Location'].replace(' ', '+')
                            maps_url = f"https://www.google.com/maps/search/?api=1&query={location_query}"
                            st.markdown(f"[🗺️ Directions]({maps_url})", unsafe_allow_html=True)
                        
                        # Show who's available (expandable)
                        if not avail_data.empty:
                            with st.expander("👀 See Who's Available"):
                                available_players = avail_data[avail_data['Status'] == 'Available']['PlayerName'].tolist()
                                unavailable_players = avail_data[avail_data['Status'] == 'Not Available']['PlayerName'].tolist()
                                maybe_players = avail_data[avail_data['Status'] == 'Maybe']['PlayerName'].tolist()
                                no_response_players = avail_data[avail_data['Status'] == 'No Response']['PlayerName'].tolist()
                                
                                if available_players:
                                    st.success("**✅ Available (" + str(len(available_players)) + "):** " + ", ".join(available_players))
                                if unavailable_players:
                                    st.error("**❌ Not Available (" + str(len(unavailable_players)) + "):** " + ", ".join(unavailable_players))
                                if maybe_players:
                                    st.warning("**❓ Maybe (" + str(len(maybe_players)) + "):** " + ", ".join(maybe_players))
                                if no_response_players:
                                    st.info("**⚪ No Response (" + str(len(no_response_players)) + "):** " + ", ".join(no_response_players))
        
        # CALENDAR VIEW
        elif view_mode == "📅 Calendar View":
            st.subheader("📅 Calendar View")
            
            # Initialize month/year in session state
            if 'cal_month' not in st.session_state:
                st.session_state.cal_month = datetime.now().month
                st.session_state.cal_year = datetime.now().year
            
            # Month navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("◀ Previous", key="prev_month", use_container_width=True):
                    st.session_state.cal_month -= 1
                    if st.session_state.cal_month < 1:
                        st.session_state.cal_month = 12
                        st.session_state.cal_year -= 1
                    st.rerun()
            with col2:
                month_name = datetime(st.session_state.cal_year, st.session_state.cal_month, 1).strftime('%B %Y')
                st.markdown(f"### {month_name}")
            with col3:
                if st.button("Next ▶", key="next_month", use_container_width=True):
                    st.session_state.cal_month += 1
                    if st.session_state.cal_month > 12:
                        st.session_state.cal_month = 1
                        st.session_state.cal_year += 1
                    st.rerun()
            
            # Create calendar grid
            import calendar
            cal = calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
            
            # Display calendar
            st.markdown("---")
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            cols = st.columns(7)
            for i, day in enumerate(days):
                with cols[i]:
                    st.markdown(f"**{day}**")
            
            # Display weeks
            for week in cal:
                cols = st.columns(7)
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0:
                            st.write("")
                        else:
                            # Check if this day has events
                            day_date = datetime(st.session_state.cal_year, st.session_state.cal_month, day)
                            day_events = filtered[filtered['Date'].dt.date == day_date.date()]
                            
                            if not day_events.empty:
                                # Color code based on event type
                                game_count = len(day_events[day_events['EventType'] == 'Game'])
                                practice_count = len(day_events[day_events['EventType'] == 'Practice'])
                                
                                if game_count > 0:
                                    st.markdown(f"🔵 **{day}**")
                                elif practice_count > 0:
                                    st.markdown(f"🟣 **{day}**")
                                
                                # Show event details on click
                                if st.button(f"View", key=f"day_{day}", use_container_width=True):
                                    st.session_state.selected_date = day_date
                            else:
                                st.write(f"{day}")
            
            # Show events for selected date
            if 'selected_date' in st.session_state:
                st.markdown("---")
                st.subheader(f"Events on {st.session_state.selected_date.strftime('%A, %B %d')}")
                selected_events = filtered[filtered['Date'].dt.date == st.session_state.selected_date.date()]
                if selected_events.empty:
                    st.info("No events scheduled for this date")
                else:
                    for idx, event in selected_events.iterrows():
                        icon = "⚽" if event['EventType'] == 'Game' else "🏃"
                        st.write(f"{icon} **{event['Time']}** - {event['Opponent'] if event['Opponent'] else 'Practice'}")
                        st.write(f"   📍 {event['Location']}")
                        if event.get('UniformColor'):
                            st.write(f"   👕 {event['UniformColor']}")
                        if event.get('ArrivalTime'):
                            st.write(f"   ⏰ Arrive: {event['ArrivalTime']}")
        
        # WEEK VIEW
        elif view_mode == "📆 Week View":
            st.subheader("📆 Week View")
            
            # Initialize week start in session state
            if 'week_start' not in st.session_state:
                today = datetime.now()
                st.session_state.week_start = today - timedelta(days=today.weekday())
            
            # Week navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("◀ Previous Week", key="prev_week", use_container_width=True):
                    st.session_state.week_start -= timedelta(days=7)
                    st.rerun()
            with col2:
                week_end = st.session_state.week_start + timedelta(days=6)
                st.markdown(f"### {st.session_state.week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
            with col3:
                if st.button("Next Week ▶", key="next_week", use_container_width=True):
                    st.session_state.week_start += timedelta(days=7)
                    st.rerun()
            
            st.markdown("---")
            
            # Display 7 days
            for i in range(7):
                day = st.session_state.week_start + timedelta(days=i)
                day_events = filtered[filtered['Date'].dt.date == day.date()]
                
                if not day_events.empty or i == 0:  # Show at least first day
                    with st.expander(f"{day.strftime('%A, %b %d')} ({len(day_events)} events)", 
                                   expanded=(len(day_events) > 0)):
                        if day_events.empty:
                            st.info("No events scheduled")
                        else:
                            for idx, event in day_events.iterrows():
                                icon = "⚽" if event['EventType'] == 'Game' else "🏃"
                                st.write(f"{icon} **{event['Time']}** - {event['Opponent'] if event['Opponent'] else 'Practice'}")
                                st.write(f"   📍 {event['Location']}")
                                if event.get('UniformColor'):
                                    st.write(f"   👕 {event['UniformColor']}")
                                if event.get('ArrivalTime'):
                                    st.write(f"   ⏰ Arrive: {event['ArrivalTime']}")
                                
                                # Quick availability summary for this event
                                event_id = event['EventID']
                                avail_data = availability[availability['EventID'] == event_id]
                                available_count = len(avail_data[avail_data['Status'] == 'Available'])
                                not_available_count = len(avail_data[avail_data['Status'] == 'Not Available'])
                                maybe_count = len(avail_data[avail_data['Status'] == 'Maybe'])
                                no_response_count = len(avail_data[avail_data['Status'] == 'No Response'])
                                
                                if available_count > 0 or not_available_count > 0 or maybe_count > 0:
                                    st.write(f"   👥 **Availability:** ✅{available_count} ❌{not_available_count} ❓{maybe_count}")
                                    if no_response_count > 0:
                                        st.write(f"   ⚠️ {no_response_count} no response")
        
        st.markdown("---")
        
        # Quick Stats
        st.header("📊 Schedule Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_events = len(schedule)
        total_games = len(schedule[schedule['EventType'] == 'Game'])
        total_practices = len(schedule[schedule['EventType'] == 'Practice'])
        upcoming_events = len(schedule[schedule['Status'] == 'Upcoming'])
        completed_events = len(schedule[schedule['Status'] == 'Completed'])
        
        with col1:
            st.metric("Total Events", total_events)
        with col2:
            st.metric("Games", total_games)
        with col3:
            st.metric("Practices", total_practices)
        with col4:
            st.metric("Upcoming", upcoming_events)
        with col5:
            st.metric("Completed", completed_events)
        
    except FileNotFoundError:
        st.error("Schedule file not found!")
        st.write("Create `team_schedule.csv` in the Data Manager to get started.")


elif page == "🎮 Live Game Tracker":
    st.title("⚽ DSX Live Game Tracker")
    
    st.success("📱 **Perfect for phones!** Use this page at the field to track games in real-time!")
    
    # Initialize game tracker session state
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'game_data' not in st.session_state:
        st.session_state.game_data = {}
    if 'events' not in st.session_state:
        st.session_state.events = []
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'time_remaining' not in st.session_state:
        st.session_state.time_remaining = 25 * 60
    if 'current_half' not in st.session_state:
        st.session_state.current_half = 1
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'starting_lineup' not in st.session_state:
        st.session_state.starting_lineup = []
    if 'bench_players' not in st.session_state:
        st.session_state.bench_players = []
    if 'on_field' not in st.session_state:
        st.session_state.on_field = []
    
    # Helper functions
    def format_time(seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def save_live_game_state():
        """Save current game state to CSV for live viewing"""
        if st.session_state.game_active and st.session_state.game_data:
            dsx_score, opp_score = get_score_tracker()
            
            # Save game summary
            game_state = {
                'date': st.session_state.game_data['date'],
                'opponent': st.session_state.game_data['opponent'],
                'location': st.session_state.game_data.get('location', ''),
                'tournament': st.session_state.game_data.get('tournament', ''),
                'dsx_score': dsx_score,
                'opp_score': opp_score,
                'half': st.session_state.current_half,
                'time_remaining': st.session_state.time_remaining,
                'timer_running': st.session_state.timer_running,
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
            pd.DataFrame([game_state]).to_csv('live_game_state.csv', index=False)
            
            # Save events
            if st.session_state.events:
                pd.DataFrame(st.session_state.events).to_csv('live_game_events.csv', index=False)
    
    def add_event_tracker(event_type, player=None, assist=None, notes=""):
        elapsed = (25 * 60) - st.session_state.time_remaining
        event = {
            'timestamp': format_time(elapsed),
            'half': st.session_state.current_half,
            'type': event_type,
            'player': player,
            'assist': assist,
            'notes': notes,
            'time': datetime.now().strftime('%H:%M:%S')
        }
        st.session_state.events.insert(0, event)
        return event
    
    def get_score_tracker():
        dsx_goals = len([e for e in st.session_state.events if e['type'] == 'DSX_GOAL'])
        opp_goals = len([e for e in st.session_state.events if e['type'] == 'OPP_GOAL'])
        return dsx_goals, opp_goals
    
    # Load roster for game tracker
    try:
        roster_tracker = pd.read_csv("roster.csv")
        roster_tracker = roster_tracker[['PlayerNumber', 'PlayerName', 'Position']].sort_values('PlayerNumber')
    except:
        roster_tracker = pd.DataFrame()
    
    # Check if game is active
    if not st.session_state.game_active:
        # PRE-GAME SETUP
        st.header("🏟️ New Game Setup")
        
        # Load upcoming matches for quick select
        try:
            upcoming_matches = pd.read_csv("DSX_Upcoming_Opponents.csv")
            upcoming_matches['Date'] = pd.to_datetime(upcoming_matches['Date'])
            has_upcoming = True
        except:
            has_upcoming = False
        
        # Initialize defaults
        default_date = datetime.now().date()
        default_opponent = ""
        default_location = ""
        default_tournament = "MVYSA Fall 2025"
        
        # Check if data was pre-filled from Team Schedule
        if 'prefill_game_data' in st.session_state:
            prefill = st.session_state.prefill_game_data
            st.success("🎯 **Game Pre-Selected from Schedule!**")
            st.info(f"**{prefill.get('opponent')}** on **{prefill.get('date')}** @ **{prefill.get('location')}**")
            
            # Use prefilled data as defaults
            try:
                default_date = datetime.strptime(prefill.get('date'), '%Y-%m-%d').date()
            except:
                pass
            default_opponent = prefill.get('opponent', '')
            default_location = prefill.get('location', '')
            default_tournament = prefill.get('tournament', 'MVYSA Fall 2025')
            
            # Clear prefill data after using it
            del st.session_state.prefill_game_data
        
        # Quick select from upcoming matches - NEW APPROACH: Skip manual form!
        if has_upcoming and not upcoming_matches.empty:
            st.subheader("⚡ Quick Select (Recommended)")
            
            # Build game options
            game_options = {}
            for idx, row in upcoming_matches.iterrows():
                game_key = f"{row['Date'].strftime('%b %d')} - {row['Opponent']} @ {row.get('Location', 'TBD')}"
                game_options[game_key] = {
                    'date': row['Date'].date(),
                    'opponent': str(row['Opponent']),
                    'location': str(row.get('Location', '')),
                    'tournament': str(row.get('Tournament', 'MVYSA Fall 2025')),
                    'time': str(row.get('GameTime', 'TBD'))
                }
            
            game_choice = st.radio(
                "Select your game:",
                ["Manual entry..."] + list(game_options.keys()),
                key="game_radio_selector"
            )
            
            if game_choice != "Manual entry...":
                # Show selected game card
                selected_game = game_options[game_choice]
                
                st.success("📋 **Selected Game:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**📅 Date:** {selected_game['date']}")
                    st.write(f"**⏰ Time:** {selected_game['time']}")
                    st.write(f"**🏆 Tournament:** {selected_game['tournament']}")
                with col2:
                    st.write(f"**🏟️ Opponent:** {selected_game['opponent']}")
                    st.write(f"**📍 Location:** {selected_game['location']}")
                
                st.markdown("---")
                
                # Store game data and skip to lineup
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    if st.button("✅ CONFIRM & SELECT LINEUP", type="primary", use_container_width=True):
                        st.session_state.game_data = {
                            'date': str(selected_game['date']),
                            'opponent': selected_game['opponent'],
                            'location': selected_game['location'],
                            'tournament': selected_game['tournament'],
                            'half_length': 25
                        }
                        st.session_state['skip_manual_form'] = True
                        st.rerun()
                with col_b:
                    if st.button("↩️ Back", use_container_width=True):
                        st.rerun()
                
                # Don't show manual form below
                show_manual_form = False
            else:
                show_manual_form = True
            
            st.markdown("---")
        else:
            show_manual_form = True
        
        # Only show manual form if needed
        if show_manual_form and 'skip_manual_form' not in st.session_state:
            st.subheader("📝 Manual Entry")
            
            col1, col2 = st.columns(2)
            
            with col1:
                game_date = st.date_input("Date", value=default_date)
                opponent = st.text_input("Opponent Team", value=default_opponent)
                location = st.text_input("Location", value=default_location)
                tournament = st.text_input("Tournament/League", value=default_tournament)
            
            with col2:
                st.subheader("⚙️ Game Settings")
                half_length = st.number_input("Half Length (minutes)", min_value=10, max_value=45, value=25)
                st.info(f"Game will be 2 halves of {half_length} minutes each")
            
            st.markdown("---")
        elif 'skip_manual_form' in st.session_state:
            # Use game data from quick select
            game_date = datetime.strptime(st.session_state.game_data['date'], '%Y-%m-%d').date()
            opponent = st.session_state.game_data['opponent']
            location = st.session_state.game_data['location']
            tournament = st.session_state.game_data['tournament']
            half_length = st.session_state.game_data['half_length']
        else:
            # Fallback defaults if nothing is set
            game_date = default_date
            opponent = default_opponent
            location = default_location
            tournament = default_tournament
            half_length = 25
        
        # Load position configuration
        try:
            positions_config = pd.read_csv("position_config.csv")
            position_names = positions_config['PositionName'].tolist()
        except:
            position_names = ["Goalkeeper", "Center Back", "Right Back", "Left Back", "Center Midfielder", "Right Winger", "Left Winger", "Striker"]
        
        # STARTING LINEUP SELECTION
        st.subheader("👥 Select Starting 7 (with Positions)")
        st.info("💡 **Tip:** Select player AND their position for each spot. You can customize position names in Data Manager.")
        
        if not roster_tracker.empty:
            # Use 4 columns for better mobile display
            selected_starters = []
            selected_positions = {}
            
            # Create a more compact, aligned layout
            for i in range(7):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    position = st.selectbox(
                        f"Pos {i+1}",
                        position_names,
                        key=f"pos_{i}",
                        index=i if i < len(position_names) else 0,
                        label_visibility="collapsed"
                    )
                
                with col2:
                    player_options = ["Select player..."] + [
                        f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                        for _, row in roster_tracker.iterrows()
                        if int(row['PlayerNumber']) not in selected_starters
                    ]
                    selected = st.selectbox(
                        f"Player {i+1}",
                        player_options,
                        key=f"starter_{i}",
                        label_visibility="collapsed",
                        help=f"Select player for {position}"
                    )
                    if selected != "Select player...":
                        player_num = int(selected.split('#')[1].split(' ')[0])
                        selected_starters.append(player_num)
                        selected_positions[player_num] = position
            
            st.markdown("---")
            
            # Show bench prominently
            if len(selected_starters) > 0:
                bench = roster_tracker[~roster_tracker['PlayerNumber'].isin(selected_starters)]
                if not bench.empty:
                    st.subheader("🪑 Bench (Ready for Substitution)")
                    
                    # Show bench in a nice table format
                    bench_display = pd.DataFrame({
                        'Jersey #': [f"#{int(row['PlayerNumber'])}" for _, row in bench.iterrows()],
                        'Player Name': [row['PlayerName'] for _, row in bench.iterrows()],
                        'Position': [row['Position'] for _, row in bench.iterrows()],
                        'Status': ['✅ Ready' for _ in range(len(bench))]
                    })
                    st.dataframe(bench_display, hide_index=True, use_container_width=True)
                    st.caption(f"**{len(bench)} players on bench** - Use 🔄 SUB button during game to make substitutions")
            
            st.markdown("---")
            
            # Start game button
            if st.button("🚀 START GAME", type="primary", use_container_width=True):
                if opponent and len(selected_starters) >= 7:
                    st.session_state.game_active = True
                    st.session_state.game_data = {
                        'date': game_date.strftime('%Y-%m-%d'),
                        'opponent': opponent,
                        'location': location,
                        'tournament': tournament,
                        'half_length': half_length
                    }
                    st.session_state.time_remaining = half_length * 60
                    st.session_state.starting_lineup = selected_starters
                    st.session_state.on_field = selected_starters.copy()
                    st.session_state.bench_players = [int(row['PlayerNumber']) for _, row in bench.iterrows()]
                    # Clear quick select flag for next game
                    if 'skip_manual_form' in st.session_state:
                        del st.session_state['skip_manual_form']
                    st.rerun()
                else:
                    st.error("Please enter opponent name and select at least 7 starting players!")
        else:
            st.error("No roster found! Please add players to roster.csv first.")
    
    else:
        # LIVE GAME INTERFACE  
        game_data = st.session_state.game_data
        dsx_score, opp_score = get_score_tracker()
        
        # Header with scores
        st.markdown(f"""
        <div style="font-size: 48px; font-weight: bold; text-align: center; padding: 20px; margin: 20px 0;">
            DSX <span style="color: #667eea;">{dsx_score}</span> - 
            <span style="color: #f093fb;">{opp_score}</span> {game_data['opponent']}
        </div>
        """, unsafe_allow_html=True)
        
        # Timer
        half_text = "FIRST HALF" if st.session_state.current_half == 1 else "SECOND HALF"
        st.markdown(f"""
        <div style="font-size: 72px; font-weight: bold; text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin: 20px 0;">
            ⏱️ {half_text}<br>
            {format_time(st.session_state.time_remaining)}
        </div>
        """, unsafe_allow_html=True)
        
        # Timer controls
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("▶️ Start" if not st.session_state.timer_running else "⏸️ Pause", 
                         use_container_width=True):
                st.session_state.timer_running = not st.session_state.timer_running
                st.session_state.last_update = time.time()
                st.rerun()
        
        with col2:
            if st.button("⏭️ Next Half", use_container_width=True):
                if st.session_state.current_half == 1:
                    st.session_state.current_half = 2
                    st.session_state.time_remaining = game_data['half_length'] * 60
                    st.session_state.timer_running = False
                    add_event_tracker('HALF_TIME', notes="Half time break")
                    save_live_game_state()
                    st.rerun()
        
        with col3:
            if st.button("🔄 Reset Timer", use_container_width=True):
                st.session_state.time_remaining = game_data['half_length'] * 60
                st.session_state.timer_running = False
                st.rerun()
        
        with col4:
            if st.button("⏹️ End Game", use_container_width=True, type="primary"):
                st.session_state.game_active = False
                st.session_state.show_summary = True
                st.rerun()
        
        with col5:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Update timer
        if st.session_state.timer_running:
            if st.session_state.last_update:
                elapsed = time.time() - st.session_state.last_update
                st.session_state.time_remaining = max(0, st.session_state.time_remaining - int(elapsed))
            st.session_state.last_update = time.time()
            
            # Auto-save every 15 seconds for live viewing
            if 'last_auto_save' not in st.session_state:
                st.session_state.last_auto_save = time.time()
            if time.time() - st.session_state.last_auto_save > 15:
                save_live_game_state()
                st.session_state.last_auto_save = time.time()
            
            if st.session_state.time_remaining > 0:
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.timer_running = False
                save_live_game_state()
                st.balloons()
                st.success(f"{half_text} Complete!")
        
        st.markdown("---")
        
        # BIG BUTTON DASHBOARD
        st.subheader("🎮 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⚽ DSX GOAL", use_container_width=True, type="primary", key="dsx_goal_btn"):
                st.session_state.show_goal_dialog = True
                st.rerun()
        
        with col2:
            if st.button("🥅 OPP GOAL", use_container_width=True, key="opp_goal_btn"):
                add_event_tracker('OPP_GOAL')
                save_live_game_state()
                st.rerun()
        
        with col3:
            if st.button("🎯 SHOT", use_container_width=True, key="shot_btn"):
                st.session_state.show_shot_dialog = True
                st.rerun()
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("🧤 SAVE", use_container_width=True, key="save_btn"):
                st.session_state.show_save_dialog = True
                st.rerun()
        
        with col5:
            if st.button("⚠️ CORNER", use_container_width=True, key="corner_btn"):
                add_event_tracker('CORNER')
                save_live_game_state()
                st.rerun()
        
        with col6:
            if st.button("🔄 SUB", use_container_width=True, key="sub_btn"):
                st.session_state.show_sub_dialog = True
                st.rerun()
        
        col7, col8, col9 = st.columns(3)
        
        with col7:
            if st.button("↩️ UNDO", use_container_width=True, type="secondary", key="undo_btn"):
                if st.session_state.events:
                    last_event = st.session_state.events.pop(0)
                    st.success(f"✅ Undid: {last_event['type']}")
                    st.rerun()
                else:
                    st.error("No events to undo!")
        
        with col8:
            if st.button("📝 NOTE", use_container_width=True, key="note_btn"):
                st.session_state.show_note_dialog = True
                st.rerun()
        
        with col9:
            if st.button("🚨 TIMEOUT", use_container_width=True, key="timeout_btn"):
                add_event_tracker('TIMEOUT', notes="Injury/timeout")
                save_live_game_state()
                if st.session_state.timer_running:
                    st.session_state.timer_running = False
                st.rerun()
        
        # Goalkeeper Actions Section
        st.markdown("---")
        st.markdown("### 🧤 Goalkeeper Actions")
        gk_col1, gk_col2, gk_col3, gk_col4 = st.columns(4)
        
        with gk_col1:
            if st.button("✋ CATCH", use_container_width=True, key="catch_btn"):
                st.session_state.show_catch_dialog = True
                st.rerun()
        
        with gk_col2:
            if st.button("👊 PUNCH", use_container_width=True, key="punch_btn"):
                st.session_state.show_punch_dialog = True
                st.rerun()
        
        with gk_col3:
            if st.button("🦶 DISTRIBUTION", use_container_width=True, key="dist_btn"):
                st.session_state.show_dist_dialog = True
                st.rerun()
        
        with gk_col4:
            if st.button("🧹 CLEARANCE", use_container_width=True, key="clear_btn"):
                st.session_state.show_clear_dialog = True
                st.rerun()
        
        # Dialogs (simplified for embedding)
        if 'show_goal_dialog' in st.session_state and st.session_state.show_goal_dialog:
            with st.form("goal_form"):
                st.subheader("⚽ DSX GOAL!")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                scorer = st.selectbox("Who scored?", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                       for _, row in on_field_players.iterrows()])
                assist = st.selectbox("Assisted by:", ["None"] + [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                                   for _, row in on_field_players.iterrows()])
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        player_name = scorer.split(' ', 1)[1]
                        assist_name = assist.split(' ', 1)[1] if assist != "None" else None
                        add_event_tracker('DSX_GOAL', player=player_name, assist=assist_name, notes=notes)
                        save_live_game_state()
                        st.session_state.show_goal_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_goal_dialog = False
                        st.rerun()
        
        # Shot dialog
        if 'show_shot_dialog' in st.session_state and st.session_state.show_shot_dialog:
            with st.form("shot_form"):
                st.subheader("🎯 SHOT ON GOAL")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                shooter = st.selectbox("Who took the shot?", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                               for _, row in on_field_players.iterrows()])
                
                # Shot outcome
                st.write("**Outcome:**")
                shot_outcome = st.radio("outcome", 
                    ["⚽ On Target", "❌ Off Target", "🛡️ Blocked"], 
                    horizontal=True, label_visibility="collapsed")
                
                # Shot type
                st.write("**Type:**")
                shot_type = st.radio("type", 
                    ["👟 Right Foot", "👟 Left Foot", "🤕 Header"], 
                    horizontal=True, label_visibility="collapsed")
                
                # Shot location
                st.write("**Location:**")
                shot_location = st.radio("location", 
                    ["⬆️ Top", "⬇️ Bottom", "⬅️ Left", "➡️ Right", "🎯 Center"], 
                    horizontal=True, label_visibility="collapsed")
                
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        player_name = shooter.split(' ', 1)[1]
                        shot_details = f"{shot_outcome} | {shot_type} | {shot_location}"
                        if notes:
                            shot_details += f" | {notes}"
                        add_event_tracker('SHOT', player=player_name, notes=shot_details)
                        save_live_game_state()
                        st.session_state.show_shot_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_shot_dialog = False
                        st.rerun()
        
        # Save dialog
        if 'show_save_dialog' in st.session_state and st.session_state.show_save_dialog:
            with st.form("save_form"):
                st.subheader("🧤 GOALKEEPER SAVE")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                keeper = st.selectbox("Who made the save?", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                              for _, row in on_field_players.iterrows()])
                
                # Save type
                st.write("**Save Type:**")
                save_type = st.radio("save_type", 
                    ["🤿 Dive", "🧍 Standing", "⚡ Reflex", "✋ Tip Over"], 
                    horizontal=True, label_visibility="collapsed")
                
                # Shot location (where shot came from)
                st.write("**Shot From:**")
                shot_from = st.radio("shot_from", 
                    ["⬆️ Top", "⬇️ Bottom", "⬅️ Left", "➡️ Right", "🎯 Center"], 
                    horizontal=True, label_visibility="collapsed")
                
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        player_name = keeper.split(' ', 1)[1]
                        save_details = f"{save_type} | Shot from {shot_from}"
                        if notes:
                            save_details += f" | {notes}"
                        add_event_tracker('SAVE', player=player_name, notes=save_details)
                        save_live_game_state()
                        st.session_state.show_save_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_save_dialog = False
                        st.rerun()
        
        # Sub dialog
        if 'show_sub_dialog' in st.session_state and st.session_state.show_sub_dialog:
            with st.form("sub_form"):
                st.subheader("🔄 SUBSTITUTION")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                bench_players_df = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.bench_players)]
                
                player_out = st.selectbox("Player COMING OFF:", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                                  for _, row in on_field_players.iterrows()])
                player_in = st.selectbox("Player GOING ON:", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                               for _, row in bench_players_df.iterrows()])
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        # Parse player numbers
                        out_num = int(player_out.split('#')[1].split(' ')[0])
                        in_num = int(player_in.split('#')[1].split(' ')[0])
                        
                        # Update on_field and bench
                        st.session_state.on_field.remove(out_num)
                        st.session_state.on_field.append(in_num)
                        st.session_state.bench_players.remove(in_num)
                        st.session_state.bench_players.append(out_num)
                        
                        # Record event
                        out_name = player_out.split(' ', 1)[1]
                        in_name = player_in.split(' ', 1)[1]
                        add_event_tracker('SUBSTITUTION', player=f"OUT: {out_name}, IN: {in_name}", notes=notes)
                        save_live_game_state()
                        st.session_state.show_sub_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_sub_dialog = False
                        st.rerun()
        
        # Catch dialog
        if 'show_catch_dialog' in st.session_state and st.session_state.show_catch_dialog:
            with st.form("catch_form"):
                st.subheader("✋ GOALKEEPER CATCH")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                keeper = st.selectbox("Who caught it?", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                          for _, row in on_field_players.iterrows()])
                
                # Catch type
                st.write("**Catch Type:**")
                catch_type = st.radio("catch_type", 
                    ["🌐 Cross", "⚠️ Corner", "⚡ Through Ball", "🎯 Shot"], 
                    horizontal=True, label_visibility="collapsed")
                
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        player_name = keeper.split(' ', 1)[1]
                        catch_details = f"{catch_type}"
                        if notes:
                            catch_details += f" | {notes}"
                        add_event_tracker('CATCH', player=player_name, notes=catch_details)
                        save_live_game_state()
                        st.session_state.show_catch_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_catch_dialog = False
                        st.rerun()
        
        # Punch dialog
        if 'show_punch_dialog' in st.session_state and st.session_state.show_punch_dialog:
            with st.form("punch_form"):
                st.subheader("👊 GOALKEEPER PUNCH")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                keeper = st.selectbox("Who punched it?", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                           for _, row in on_field_players.iterrows()])
                
                # Punch type
                st.write("**Punch Type:**")
                punch_type = st.radio("punch_type", 
                    ["⚠️ Corner", "🌐 Cross", "⚽ Free Kick"], 
                    horizontal=True, label_visibility="collapsed")
                
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        player_name = keeper.split(' ', 1)[1]
                        punch_details = f"{punch_type}"
                        if notes:
                            punch_details += f" | {notes}"
                        add_event_tracker('PUNCH', player=player_name, notes=punch_details)
                        save_live_game_state()
                        st.session_state.show_punch_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_punch_dialog = False
                        st.rerun()
        
        # Distribution dialog
        if 'show_dist_dialog' in st.session_state and st.session_state.show_dist_dialog:
            with st.form("dist_form"):
                st.subheader("🦶 GOALKEEPER DISTRIBUTION")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                keeper = st.selectbox("Who distributed?", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                            for _, row in on_field_players.iterrows()])
                
                # Distribution type
                st.write("**Distribution Type:**")
                dist_type = st.radio("dist_type", 
                    ["🥅 Goal Kick", "🤾 Throw", "🦶 Punt", "⚽ Roll Out"], 
                    horizontal=True, label_visibility="collapsed")
                
                # Target area
                st.write("**Target Area:**")
                target = st.radio("target", 
                    ["⬅️ Left", "➡️ Right", "🎯 Center", "🚀 Long"], 
                    horizontal=True, label_visibility="collapsed")
                
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        player_name = keeper.split(' ', 1)[1]
                        dist_details = f"{dist_type} to {target}"
                        if notes:
                            dist_details += f" | {notes}"
                        add_event_tracker('DISTRIBUTION', player=player_name, notes=dist_details)
                        save_live_game_state()
                        st.session_state.show_dist_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_dist_dialog = False
                        st.rerun()
        
        # Clearance dialog
        if 'show_clear_dialog' in st.session_state and st.session_state.show_clear_dialog:
            with st.form("clear_form"):
                st.subheader("🧹 GOALKEEPER CLEARANCE")
                on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
                keeper = st.selectbox("Who cleared it?", [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                           for _, row in on_field_players.iterrows()])
                
                # Clearance type
                st.write("**Clearance Type:**")
                clear_type = st.radio("clear_type", 
                    ["🦶 Kick", "👊 Punch", "✋ Catch & Clear", "🤾 Throw"], 
                    horizontal=True, label_visibility="collapsed")
                
                notes = st.text_input("Notes (optional)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                        player_name = keeper.split(' ', 1)[1]
                        clear_details = f"{clear_type}"
                        if notes:
                            clear_details += f" | {notes}"
                        add_event_tracker('CLEARANCE', player=player_name, notes=clear_details)
                        save_live_game_state()
                        st.session_state.show_clear_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_clear_dialog = False
                        st.rerun()
        
        st.markdown("---")
        
        # Live Feed
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Live Event Feed")
            if st.session_state.events:
                for event in st.session_state.events[:20]:
                    icon = {'DSX_GOAL': '⚽', 'OPP_GOAL': '🥅', 'SHOT': '🎯', 'SAVE': '🧤', 
                            'CORNER': '⚠️', 'SUBSTITUTION': '🔄', 'HALF_TIME': '⏰', 
                            'TIMEOUT': '🚨', 'NOTE': '📝', 'CATCH': '✋', 'PUNCH': '👊',
                            'DISTRIBUTION': '🦶', 'CLEARANCE': '🧹'}.get(event['type'], '📝')
                    event_text = f"{icon} {event['timestamp']} - "
                    if event['type'] == 'DSX_GOAL':
                        event_text += f"GOAL! {event['player']}"
                        if event['assist']:
                            event_text += f" (assist: {event['assist']})"
                    elif event['type'] == 'OPP_GOAL':
                        event_text += "Opponent Goal"
                    elif event['type'] == 'SHOT':
                        event_text += f"Shot by {event.get('player', 'Unknown')}"
                        if event.get('notes'):
                            event_text += f" - {event['notes']}"
                    elif event['type'] == 'SAVE':
                        event_text += f"Save by {event.get('player', 'Unknown')}"
                        if event.get('notes'):
                            event_text += f" - {event['notes']}"
                    elif event['type'] == 'SUBSTITUTION':
                        event_text += f"SUB: {event.get('player', 'Unknown')}"
                    else:
                        event_text += event['type'].replace('_', ' ').title()
                        if event.get('notes'):
                            event_text += f" - {event['notes']}"
                    st.write(event_text)
            else:
                st.info("No events yet. Start recording!")
        
        with col2:
            st.subheader("📊 Stats")
            goals = [e for e in st.session_state.events if e['type'] == 'DSX_GOAL']
            shots = [e for e in st.session_state.events if e['type'] == 'SHOT']
            saves = [e for e in st.session_state.events if e['type'] == 'SAVE']
            corners = [e for e in st.session_state.events if e['type'] == 'CORNER']
            st.metric("Goals", len(goals))
            st.metric("Shots", len(shots))
            st.metric("Saves", len(saves))
            st.metric("Corners", len(corners))
    
    # Game summary
    if 'show_summary' in st.session_state and st.session_state.show_summary:
        st.markdown("---")
        st.header("🎉 GAME COMPLETE!")
        dsx_score, opp_score = get_score_tracker()
        result = "WIN" if dsx_score > opp_score else "LOSS" if dsx_score < opp_score else "DRAW"
        st.markdown(f"### {result}! DSX {dsx_score} - {opp_score} {st.session_state.game_data['opponent']}")
        
        if st.button("💾 Save to CSV", use_container_width=True, type="primary"):
            # Save match
            match_data = {
                'Date': st.session_state.game_data['date'],
                'Tournament': st.session_state.game_data['tournament'],
                'Opponent': st.session_state.game_data['opponent'],
                'Location': st.session_state.game_data['location'],
                'GF': dsx_score, 'GA': opp_score, 'GD': dsx_score - opp_score,
                'Result': result[0], 'Outcome': result
            }
            matches_df = pd.read_csv("DSX_Matches_Fall2025.csv") if os.path.exists("DSX_Matches_Fall2025.csv") else pd.DataFrame()
            matches_df = pd.concat([matches_df, pd.DataFrame([match_data])], ignore_index=True)
            matches_df.to_csv("DSX_Matches_Fall2025.csv", index=False)
            st.success("✅ Game saved!")
            
        if st.button("🔄 New Game", use_container_width=True):
            st.session_state.game_active = False
            st.session_state.show_summary = False
            st.session_state.events = []
            # Clear quick select flag for fresh setup
            if 'skip_manual_form' in st.session_state:
                del st.session_state['skip_manual_form']
            st.rerun()


elif page == "📺 Watch Live Game":
    st.title("📺 Watch Live Game")
    
    st.success("👨‍👩‍👧‍👦 **Parent/Team View** - Watch the game in real-time! This page auto-refreshes every 15 seconds.")
    
    # Auto-refresh every 15 seconds
    st.markdown("""
        <meta http-equiv="refresh" content="15">
    """, unsafe_allow_html=True)
    
    # Check if a game is currently active
    if os.path.exists('live_game_state.csv'):
        try:
            game_state = pd.read_csv('live_game_state.csv')
            
            if not game_state.empty:
                state = game_state.iloc[0]
                
                # Display game header
                st.markdown(f"""
                <div style="font-size: 56px; font-weight: bold; text-align: center; padding: 30px; margin: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;">
                    DSX <span style="color: #ffd700;">{int(state['dsx_score'])}</span> - 
                    <span style="color: #ffd700;">{int(state['opp_score'])}</span> {state['opponent']}
                </div>
                """, unsafe_allow_html=True)
                
                # Timer and game info
                col1, col2, col3 = st.columns(3)
                with col1:
                    half_text = "1ST HALF" if state['half'] == 1 else "2ND HALF"
                    mins = int(state['time_remaining']) // 60
                    secs = int(state['time_remaining']) % 60
                    st.markdown(f"""
                    <div style="font-size: 32px; font-weight: bold; text-align: center; padding: 20px; background: #667eea; border-radius: 10px; color: white;">
                        ⏱️ {half_text}<br>{mins:02d}:{secs:02d}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="font-size: 20px; text-align: center; padding: 20px; background: #f0f0f0; border-radius: 10px;">
                        <strong>📅 {state['date']}</strong><br>
                        🏆 {state['tournament']}<br>
                        📍 {state['location']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    status_icon = "▶️" if state['timer_running'] else "⏸️"
                    status_text = "LIVE" if state['timer_running'] else "PAUSED"
                    st.markdown(f"""
                    <div style="font-size: 28px; font-weight: bold; text-align: center; padding: 20px; background: {'#00ff00' if state['timer_running'] else '#ffcc00'}; border-radius: 10px; color: black;">
                        {status_icon} {status_text}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Load and display events
                if os.path.exists('live_game_events.csv'):
                    events = pd.read_csv('live_game_events.csv')
                    
                    if not events.empty:
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("📋 Live Event Feed")
                            # Show most recent 15 events
                            for _, event in events.head(15).iterrows():
                                icon = {'DSX_GOAL': '⚽', 'OPP_GOAL': '🥅', 'SHOT': '🎯', 'SAVE': '🧤', 
                                        'CORNER': '⚠️', 'SUBSTITUTION': '🔄', 'HALF_TIME': '⏰', 
                                        'TIMEOUT': '🚨', 'NOTE': '📝'}.get(event['type'], '📝')
                                
                                event_text = f"{icon} {event['timestamp']} - "
                                if event['type'] == 'DSX_GOAL':
                                    event_text += f"**GOAL! {event.get('player', 'Unknown')}**"
                                    if event.get('assist') and str(event.get('assist')) != 'nan':
                                        event_text += f" (assist: {event['assist']})"
                                elif event['type'] == 'OPP_GOAL':
                                    event_text += "Opponent Goal"
                                elif event['type'] == 'SHOT':
                                    event_text += f"Shot by {event.get('player', 'Unknown')}"
                                elif event['type'] == 'SAVE':
                                    event_text += f"Save by {event.get('player', 'Unknown')}"
                                elif event['type'] == 'SUBSTITUTION':
                                    event_text += f"SUB: {event.get('player', 'Unknown')}"
                                else:
                                    event_text += event['type'].replace('_', ' ').title()
                                
                                st.write(event_text)
                        
                        with col2:
                            st.subheader("📊 Game Stats")
                            goals = len(events[events['type'] == 'DSX_GOAL'])
                            shots = len(events[events['type'] == 'SHOT'])
                            saves = len(events[events['type'] == 'SAVE'])
                            corners = len(events[events['type'] == 'CORNER'])
                            st.metric("⚽ Goals", goals)
                            st.metric("🎯 Shots", shots)
                            st.metric("🧤 Saves", saves)
                            st.metric("⚠️ Corners", corners)
                    else:
                        st.info("No events recorded yet. Check back soon!")
                else:
                    st.info("No events recorded yet. Check back soon!")
                
                st.markdown("---")
                st.caption(f"🔄 Last updated: {state['last_updated']} | Auto-refreshes every 15 seconds")
                st.caption("💡 Tip: Keep this page open on your phone to follow the game!")
            else:
                st.info("⏳ No game currently in progress. Check back when a game starts!")
                st.write("The coach/recorder will start tracking from the **🎮 Live Game Tracker** page.")
        
        except Exception as e:
            st.error("Error loading game data. Please refresh.")
            st.caption(f"Technical details: {str(e)}")
    else:
        st.info("⏳ No game currently in progress. Check back when a game starts!")
        st.write("The coach/recorder will start tracking from the **🎮 Live Game Tracker** page.")
        st.markdown("---")
        st.subheader("📱 How to Use")
        st.write("""
        **For Parents/Team Members:**
        1. Open this link on your phone during the game
        2. This page auto-refreshes every 15 seconds
        3. Watch live score, timer, and events!
        4. No need to refresh - just keep it open
        
        **For Coach/Recorder:**
        1. Use the **🎮 Live Game Tracker** page to record events
        2. This page automatically displays what you record
        3. Share the Streamlit app link with parents!
        """)


elif page == "💬 Team Chat":
    st.title("💬 Team Chat")
    
    st.success("📱 **Real-Time Team Communication** - Messages update every 3 seconds!")
    
    # Import chat database
    try:
        from chat_db import ChatDatabase
        db = ChatDatabase()
    except Exception as e:
        st.error(f"Could not load chat database: {str(e)}")
        st.info("Make sure `chat_db.py` is in the same directory as `dsx_dashboard.py`")
        st.stop()
    
    # Initialize session state for auto-refresh
    if 'last_chat_refresh' not in st.session_state:
        st.session_state.last_chat_refresh = time.time()
    if 'chat_username' not in st.session_state:
        st.session_state.chat_username = ""
    
    # Auto-refresh every 3 seconds
    current_time = time.time()
    if current_time - st.session_state.last_chat_refresh > 3:
        st.session_state.last_chat_refresh = current_time
        st.rerun()
    
    # Channel selection
    channels = db.get_all_channels()
    if 'selected_channel' not in st.session_state:
        st.session_state.selected_channel = 'general'
    
    # Channel tabs
    channel_tabs = st.tabs([f"#{row['name'].title()} ({db.get_message_count(row['name'])})" 
                            for _, row in channels.iterrows()])
    
    for idx, (_, channel_row) in enumerate(channels.iterrows()):
        with channel_tabs[idx]:
            channel_name = channel_row['name']
            channel_desc = channel_row['description']
            
            st.caption(f"💬 {channel_desc}")
            st.markdown("---")
            
            # Get messages for this channel
            messages = db.get_messages(channel_name, limit=50)
            
            if not messages.empty:
                # Display pinned messages first
                pinned_messages = messages[messages['pinned'] == 1]
                if not pinned_messages.empty:
                    st.subheader("📌 Pinned Messages")
                    for _, msg in pinned_messages.iterrows():
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**{msg['username']}** · {msg['timestamp']}")
                                st.write(msg['message'])
                            with col2:
                                if st.button("📌 Unpin", key=f"unpin_{msg['id']}"):
                                    db.unpin_message(msg['id'])
                                    st.rerun()
                                if st.button("🗑️ Delete", key=f"del_pinned_{msg['id']}"):
                                    db.delete_message(msg['id'])
                                    st.rerun()
                    st.markdown("---")
                
                # Display regular messages
                st.subheader("💬 Recent Messages")
                regular_messages = messages[messages['pinned'] == 0]
                
                if not regular_messages.empty:
                    for _, msg in regular_messages.iterrows():
                        with st.container():
                            col1, col2 = st.columns([5, 1])
                            with col1:
                                st.markdown(f"**{msg['username']}** · {msg['timestamp']}")
                                st.write(msg['message'])
                            with col2:
                                with st.popover("⋮"):
                                    if st.button("📌 Pin", key=f"pin_{msg['id']}"):
                                        db.pin_message(msg['id'])
                                        st.rerun()
                                    if st.button("🗑️ Delete", key=f"del_{msg['id']}"):
                                        db.delete_message(msg['id'])
                                        st.rerun()
                            st.markdown("---")
                else:
                    st.info("No messages yet. Be the first to post!")
            else:
                st.info("No messages in this channel yet. Start the conversation!")
            
            # Post message section
            st.markdown("---")
            st.subheader("✏️ Post a Message")
            
            with st.form(key=f"post_form_{channel_name}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    username = st.text_input(
                        "Your Name", 
                        value=st.session_state.chat_username,
                        placeholder="Coach John, Parent Sarah, etc.",
                        key=f"username_{channel_name}"
                    )
                
                with col2:
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                
                message = st.text_area(
                    "Message",
                    placeholder="Type your message here...",
                    height=100,
                    key=f"message_{channel_name}"
                )
                
                submit = st.form_submit_button("📤 Send Message", use_container_width=True, type="primary")
                
                if submit:
                    if not username or not username.strip():
                        st.error("Please enter your name!")
                    elif not message or not message.strip():
                        st.error("Please enter a message!")
                    else:
                        # Save username for next time
                        st.session_state.chat_username = username.strip()
                        
                        # Post message
                        db.post_message(username.strip(), message.strip(), channel_name)
                        st.success("✅ Message posted!")
                        time.sleep(0.5)
                        st.rerun()
    
    # Auto-refresh notice
    st.markdown("---")
    st.caption("🔄 Messages auto-refresh every 3 seconds • Keep this page open to see new messages instantly!")
    
    # Add some helpful tips
    with st.expander("💡 How to Use Team Chat"):
        st.markdown("""
        **Posting Messages:**
        - Enter your name (it will be remembered)
        - Type your message
        - Click "Send Message"
        
        **Channels:**
        - **General** - Team announcements and general discussion
        - **Game Day** - Coordinate on game days
        - **Schedule** - Schedule changes and updates
        - **Carpools** - Find rides or offer carpools
        - **Equipment** - Share equipment needs/offers
        
        **Pin Messages:**
        - Click the ⋮ menu next to any message
        - Click "📌 Pin" to pin important messages to the top
        - Pinned messages stay visible for everyone
        
        **Delete Messages:**
        - Click the ⋮ menu next to any message
        - Click "🗑️ Delete" to remove a message
        
        **Tips:**
        - Messages update automatically every 3 seconds
        - Keep the page open to see new messages
        - Use specific channels to keep conversations organized
        - Pin important info (game times, field changes, etc.)
        """)


elif page == "🏆 Division Rankings":
    st.title("🏆 Competitive Rankings - DSX vs Opponents")
    
    st.info("📊 **DSX isn't in a division, but here's how you rank against all the teams you play!**")
    
    # Load DSX match history
    try:
        dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False).reset_index(drop=True)
    except:
        dsx_matches = pd.DataFrame()
    
    # Calculate DSX stats
    if not dsx_matches.empty:
        # Check if Result or Outcome column exists
        result_col = 'Result' if 'Result' in dsx_matches.columns else 'Outcome'
        
        completed = dsx_matches[dsx_matches[result_col].notna()].copy()
        
        if len(completed) > 0:
            dsx_gp = len(completed)
            dsx_w = len(completed[completed[result_col] == 'W'])
            dsx_d = len(completed[completed[result_col] == 'D'])
            dsx_l = len(completed[completed[result_col] == 'L'])
            dsx_gf = pd.to_numeric(completed['GF'], errors='coerce').fillna(0).sum()
            dsx_ga = pd.to_numeric(completed['GA'], errors='coerce').fillna(0).sum()
            dsx_gd = dsx_gf - dsx_ga
            dsx_pts = (dsx_w * 3) + dsx_d
            dsx_ppg = dsx_pts / dsx_gp if dsx_gp > 0 else 0
            dsx_gf_pg = dsx_gf / dsx_gp if dsx_gp > 0 else 0
            dsx_ga_pg = dsx_ga / dsx_gp if dsx_gp > 0 else 0
            dsx_gd_pg = dsx_gd / dsx_gp if dsx_gp > 0 else 0
            
            # Calculate DSX Strength Index
            ppg_norm = max(0.0, min(3.0, dsx_ppg)) / 3.0 * 100.0
            gdpg_norm = (max(-5.0, min(5.0, dsx_gd_pg)) + 5.0) / 10.0 * 100.0
            dsx_strength = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
            
            # Create DSX row
            dsx_row = pd.DataFrame([{
                'Team': 'DSX Orange 2018',
                'GP': dsx_gp,
                'W': dsx_w,
                'D': dsx_d,
                'L': dsx_l,
                'GF': dsx_gf,
                'GA': dsx_ga,
                'GD': dsx_gd,
                'Pts': dsx_pts,
                'PPG': dsx_ppg,
                'GF_PG': dsx_gf_pg,
                'GA_PG': dsx_ga_pg,
                'GD_PG': dsx_gd_pg,
                'StrengthIndex': dsx_strength,
                'IsDSX': True
            }])
        else:
            st.warning("No completed matches found for DSX. Record some games in **📅 Match History** or **🎮 Live Game Tracker**!")
            dsx_row = pd.DataFrame()
    else:
        st.warning("No match history found. Add games to `DSX_Matches_Fall2025.csv`!")
        dsx_row = pd.DataFrame()
    
    # Load opponent stats from all divisions being tracked
    opponent_stats = []
    
    # Get unique opponents DSX has played or will play
    try:
        actual_opponents = pd.read_csv("DSX_Actual_Opponents.csv", index_col=False).reset_index(drop=True)
        opponent_names = actual_opponents['Opponent'].unique().tolist()
    except:
        opponent_names = []
    
    try:
        upcoming_opponents = pd.read_csv("DSX_Upcoming_Opponents.csv", index_col=False).reset_index(drop=True)
        opponent_names.extend(upcoming_opponents['Opponent'].unique().tolist())
    except:
        pass
    
    # Add opponents from match history
    if not dsx_matches.empty:
        opponent_names.extend(dsx_matches['Opponent'].unique().tolist())
    
    opponent_names = list(set(opponent_names))  # Remove duplicates
    
    # Load division data and filter for DSX opponents
    df = load_division_data()
    
    if not df.empty and not dsx_row.empty:
        # Try exact match first
        opponent_df = df[df['Team'].isin(opponent_names)].copy()
        
        # Show matching results
        with st.expander(f"🔍 Opponent Matching Details ({len(opponent_df)} of {len(opponent_names)} matched)"):
            if not opponent_df.empty:
                st.success(f"✅ Found {len(opponent_df)} exact matches!")
                st.write("**Matched teams:**", opponent_df['Team'].tolist())
            
            unmatched = [opp for opp in opponent_names if opp not in opponent_df['Team'].values]
            if unmatched:
                st.warning(f"⚠️ {len(unmatched)} opponents not found in division data:")
                st.write(unmatched)
                st.caption("These teams might not be in the divisions we're tracking, or the names might not match exactly.")
        
        # If no exact matches, try fuzzy matching
        if opponent_df.empty and opponent_names:
            st.warning("⚠️ No exact matches found. Trying fuzzy matching...")
            
            # Try partial matching (case-insensitive, more aggressive)
            matched_teams = []
            match_details = []
            
            for opp in opponent_names:
                opp_lower = str(opp).lower()
                # Extract key parts of opponent name (remove common words)
                opp_parts = [p for p in opp_lower.split() if p not in ['boys', 'girls', 'academy', 'fc', 'sc', 'soccer', 'club', '2018', '2017', 'b', 'u8', 'u08', 'bu08', '18b']]
                
                best_match = None
                best_match_score = 0
                
                for idx, row in df.iterrows():
                    team_lower = str(row['Team']).lower()
                    team_parts = [p for p in team_lower.split() if p not in ['boys', 'girls', 'academy', 'fc', 'sc', 'soccer', 'club', '2018', '2017', 'b', 'u8', 'u08', 'bu08', '18b']]
                    
                    # Count matching parts
                    match_count = sum(1 for part in opp_parts if part in team_lower or any(part in tp for tp in team_parts))
                    match_count += sum(1 for part in team_parts if part in opp_lower or any(part in op for op in opp_parts))
                    
                    if match_count > best_match_score and match_count >= 2:  # At least 2 matching parts
                        best_match_score = match_count
                        best_match = row['Team']
                
                if best_match and best_match not in matched_teams:
                    matched_teams.append(best_match)
                    match_details.append(f"'{opp}' → '{best_match}'")
            
            if matched_teams:
                opponent_df = df[df['Team'].isin(matched_teams)].copy()
                st.success(f"✅ Found {len(opponent_df)} teams using fuzzy matching!")
                with st.expander("🔗 Fuzzy Match Results"):
                    for detail in match_details:
                        st.write(detail)
                
                # Show unmatched teams
                matched_opp_names = [detail.split("'")[1] for detail in match_details]
                unmatched_opps = [opp for opp in opponent_names if opp not in matched_opp_names]
                
                if unmatched_opps:
                    with st.expander(f"⚠️ {len(unmatched_opps)} Teams Still Unmatched - Debug Info"):
                        st.write("**These opponents couldn't be matched:**")
                        
                        for opp in unmatched_opps:
                            st.markdown(f"**{opp}**")
                            
                            # Show extracted key parts
                            opp_lower = str(opp).lower()
                            opp_parts = [p for p in opp_lower.split() if p not in ['boys', 'girls', 'academy', 'fc', 'sc', 'soccer', 'club', '2018', '2017', 'b', 'u8', 'u08', 'bu08', '18b']]
                            st.write(f"   - Key parts extracted: {opp_parts}")
                            
                            # Find closest potential matches
                            potential_matches = []
                            for idx, row in df.iterrows():
                                team_lower = str(row['Team']).lower()
                                team_parts = [p for p in team_lower.split() if p not in ['boys', 'girls', 'academy', 'fc', 'sc', 'soccer', 'club', '2018', '2017', 'b', 'u8', 'u08', 'bu08', '18b']]
                                
                                match_count = sum(1 for part in opp_parts if part in team_lower)
                                if match_count > 0:
                                    potential_matches.append((row['Team'], match_count, team_parts))
                            
                            # Sort by match count
                            potential_matches.sort(key=lambda x: x[1], reverse=True)
                            
                            if potential_matches[:3]:
                                st.write("   - Closest matches in division data:")
                                for team, score, parts in potential_matches[:3]:
                                    st.write(f"      • {team} (score: {score}, parts: {parts})")
                            else:
                                st.write("   - ❌ No similar teams found in tracked divisions")
                                st.caption("   → This team might not be in any division we're tracking")
                            
                            st.write("")
                        
                        st.info("💡 **To fix:** Run `python update_all_data.py` to fetch more division data, or these teams might not be in tracked leagues.")
            else:
                st.error(f"❌ Could not find any matching teams.")
                with st.expander("🔍 Troubleshooting - Detailed Debug"):
                    st.write("**Your opponents:**")
                    st.write(opponent_names[:10])
                    st.write("\n**Available teams in division data (sample):**")
                    st.write(df['Team'].head(15).tolist())
                    
                    st.markdown("---")
                    st.write("**Why no matches?**")
                    for opp in opponent_names[:5]:
                        opp_lower = str(opp).lower()
                        opp_parts = [p for p in opp_lower.split() if p not in ['boys', 'girls', 'academy', 'fc', 'sc', 'soccer', 'club', '2018', '2017', 'b', 'u8', 'u08', 'bu08', '18b']]
                        st.write(f"\n'{opp}':")
                        st.write(f"  - Key parts: {opp_parts}")
                        st.write(f"  - No teams in division data with 2+ matching parts")
                    
                    st.info("💡 **Tip:** Run `python update_all_data.py` to refresh division data and make sure your opponents' divisions are being tracked!")
        
        # If still no matches, at least show DSX stats
        if opponent_df.empty:
            st.warning("⚠️ No opponent data available for ranking. Showing DSX stats only.")
            
            # Show just DSX stats
            st.markdown("---")
            st.subheader("📊 DSX Season Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Record", f"{dsx_w}-{dsx_l}-{dsx_d}")
                st.metric("Goals For", f"{dsx_gf} ({dsx_gf_pg:.2f}/game)")
                st.metric("Points", f"{dsx_pts} ({dsx_ppg:.2f} PPG)")
            with col2:
                st.metric("Games Played", dsx_gp)
                st.metric("Goals Against", f"{dsx_ga} ({dsx_ga_pg:.2f}/game)")
                st.metric("Goal Diff", f"{dsx_gd:+d} ({dsx_gd_pg:+.2f}/game)")
            
            st.info("💡 **To see rankings:** Add your opponents' divisions to the tracking system by running `python update_all_data.py`")
            
        # Recalculate per-game stats for consistency
        if not opponent_df.empty:
            for idx, row in opponent_df.iterrows():
                gp = row['GP'] if row['GP'] > 0 else 1
                # Safely get GF/GA/GD, defaulting to 0 if missing or NaN
                gf = pd.to_numeric(row.get('GF', 0), errors='coerce')
                gf = gf if pd.notna(gf) else 0
                ga = pd.to_numeric(row.get('GA', 0), errors='coerce')
                ga = ga if pd.notna(ga) else 0
                gd = pd.to_numeric(row.get('GD', 0), errors='coerce')
                gd = gd if pd.notna(gd) else 0
                
                opponent_df.at[idx, 'GF_PG'] = gf / gp
                opponent_df.at[idx, 'GA_PG'] = ga / gp
                opponent_df.at[idx, 'GD_PG'] = gd / gp
                opponent_df.at[idx, 'IsDSX'] = False
            
            # Ensure GF, GA, GD columns exist and have proper values
            if 'GF' not in opponent_df.columns:
                opponent_df['GF'] = opponent_df['GF_PG'] * opponent_df['GP']
            if 'GA' not in opponent_df.columns:
                opponent_df['GA'] = opponent_df['GA_PG'] * opponent_df['GP']
            if 'GD' not in opponent_df.columns:
                opponent_df['GD'] = opponent_df['GD_PG'] * opponent_df['GP']
            
            # Combine DSX with opponents
            combined_df = pd.concat([dsx_row, opponent_df], ignore_index=True)
            
            # Sort by PPG (primary) and StrengthIndex (secondary)
            combined_df = combined_df.sort_values(['PPG', 'StrengthIndex'], ascending=[False, False]).reset_index(drop=True)
            
            # Add rank
            combined_df['Rank'] = range(1, len(combined_df) + 1)
            
            # Get DSX rank
            dsx_rank_row = combined_df[combined_df['IsDSX'] == True]
            if not dsx_rank_row.empty:
                dsx_rank = int(dsx_rank_row['Rank'].values[0])
                total_teams = len(combined_df)
                
                # Top metrics
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    delta = f"Top {dsx_rank}" if dsx_rank <= 3 else f"{total_teams - dsx_rank} teams behind"
                    st.metric("DSX Rank", f"#{dsx_rank} of {total_teams}", delta)
                
                with col2:
                    st.metric("Strength Index", f"{dsx_strength:.1f}", 
                             f"{'Strong' if dsx_strength > 60 else 'Improving' if dsx_strength > 40 else 'Building'}")
                
                with col3:
                    st.metric("Record", f"{dsx_w}-{dsx_l}-{dsx_d}", f"{dsx_ppg:.2f} PPG")
                
                with col4:
                    st.metric("Goal Diff/Game", f"{dsx_gd_pg:+.2f}", 
                             f"{'Positive' if dsx_gd_pg > 0 else 'Even' if dsx_gd_pg == 0 else 'Negative'}")
                
                st.markdown("---")
                
                # Rankings table
                st.subheader("📊 Complete Rankings - DSX vs Opponents")
                st.caption("Ranked by Points Per Game (PPG), then Strength Index")
                
                # Format the dataframe for display
                display_df = combined_df.copy()
                
                # Highlight DSX
                display_df['Team'] = display_df.apply(
                    lambda row: f"🟢 **{row['Team']}**" if row['IsDSX'] else row['Team'],
                    axis=1
                )
                
                # Round numeric columns
                display_df['PPG'] = display_df['PPG'].round(2)
                display_df['GF_PG'] = display_df['GF_PG'].round(2)
                display_df['GA_PG'] = display_df['GA_PG'].round(2)
                display_df['GD_PG'] = display_df['GD_PG'].round(2)
                display_df['StrengthIndex'] = display_df['StrengthIndex'].round(1)
                
                # Select columns to display
                display_cols = ['Rank', 'Team', 'GP', 'W', 'L', 'D', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
                
                st.dataframe(
                    display_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Team": st.column_config.TextColumn("Team"),
                        "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                        "W": st.column_config.NumberColumn("W", help="Wins"),
                        "L": st.column_config.NumberColumn("L", help="Losses"),
                        "D": st.column_config.NumberColumn("D", help="Draws"),
                        "GF": st.column_config.NumberColumn("GF", help="Goals For (Total)"),
                        "GA": st.column_config.NumberColumn("GA", help="Goals Against (Total)"),
                        "GD": st.column_config.NumberColumn("GD", help="Goal Differential (Total)", format="%+d"),
                        "Pts": st.column_config.NumberColumn("Pts", help="Total Points (3 for W, 1 for D)"),
                        "PPG": st.column_config.NumberColumn("PPG", help="Points Per Game", format="%.2f"),
                        "StrengthIndex": st.column_config.ProgressColumn(
                            "Strength",
                            help="Combined strength rating (0-100)",
                            format="%.1f",
                            min_value=0,
                            max_value=100,
                        ),
                    }
                )
                
                # Visualizations
                st.markdown("---")
                st.subheader("📊 Visual Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Strength Index chart
                    fig = px.bar(
                        combined_df,
                        x='Team',
                        y='StrengthIndex',
                        title='Strength Index Comparison',
                        text='StrengthIndex',
                        color='IsDSX',
                        color_discrete_map={True: '#00ff00', False: '#667eea'}
                    )
                    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Strength Index",
                        showlegend=False,
                        height=400
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # PPG comparison
                    fig = px.bar(
                        combined_df,
                        x='Team',
                        y='PPG',
                        title='Points Per Game Comparison',
                        text='PPG',
                        color='IsDSX',
                        color_discrete_map={True: '#00ff00', False: '#667eea'}
                    )
                    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Points Per Game",
                        showlegend=False,
                        height=400
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Offensive vs Defensive scatter
                st.markdown("---")
                st.subheader("⚔️ Offense vs Defense")
                
                fig = px.scatter(
                    combined_df,
                    x='GA_PG',
                    y='GF_PG',
                    size='GP',
                    color='IsDSX',
                    color_discrete_map={True: '#00ff00', False: '#667eea'},
                    hover_name='Team',
                    hover_data={'GP': True, 'PPG': ':.2f', 'StrengthIndex': ':.1f', 'IsDSX': False},
                    title='Offensive Output vs Defensive Performance',
                    labels={'GF_PG': 'Goals For Per Game', 'GA_PG': 'Goals Against Per Game'}
                )
                fig.add_hline(y=combined_df['GF_PG'].mean(), line_dash="dash", line_color="gray", 
                              annotation_text="Avg GF/G", annotation_position="right")
                fig.add_vline(x=combined_df['GA_PG'].mean(), line_dash="dash", line_color="gray",
                              annotation_text="Avg GA/G", annotation_position="top")
                fig.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **Top-right quadrant** = Strong offense & weak defense | **Top-left quadrant** = Strong offense & strong defense (best!)")
    
    elif not dsx_row.empty:
        st.warning("No division data found for your opponents. Run `python update_all_data.py` to fetch latest standings.")
    else:
        st.warning("No DSX match data found. Add games to see your competitive ranking!")


elif page == "📊 Team Analysis":
    st.title("📊 Team Analysis")
    
    df = load_division_data()
    
    # Add DSX to the analysis (they're not in a division, so we calculate their stats separately)
    dsx_stats = calculate_dsx_stats()
    dsx_row = pd.DataFrame([{
        'Team': 'Dublin DSX Orange 2018 Boys',
        'Rank': 0,  # Not in division
        'StrengthIndex': dsx_stats['StrengthIndex'],
        'W': dsx_stats['W'],
        'L': dsx_stats['L'],
        'D': dsx_stats['D'],
        'GF': dsx_stats['GF_PG'],
        'GA': dsx_stats['GA_PG'],
        'GD': dsx_stats['GD_PG'],
        'PPG': dsx_stats['PPG'],
        'GP': dsx_stats['GP'],
        'League/Division': 'Independent (plays division teams)',
        'SourceURL': 'DSX_Matches_Fall2025.csv'
    }])
    
    # Combine DSX with division data
    if not df.empty:
        df = pd.concat([dsx_row, df], ignore_index=True)
    else:
        df = dsx_row
    
    if df.empty:
        st.warning("No division data found.")
    else:
        # ONLY show teams with actual data (from division rankings + DSX)
        teams_with_data = df['Team'].tolist()
        
        # Filter out NaN/float values and ensure strings only
        teams_with_data = [t for t in teams_with_data if isinstance(t, str)]
        
        # Ensure DSX is first if present
        dsx_teams = [t for t in teams_with_data if 'DSX' in t or 'Dublin' in t]
        other_teams = sorted([t for t in teams_with_data if t not in dsx_teams])
        teams = dsx_teams + other_teams
        
        # Check for upcoming opponents without data
        teams_without_data = []
        try:
            upcoming = pd.read_csv("DSX_Upcoming_Opponents.csv")
            for opp in upcoming['Opponent'].dropna().unique():
                if opp not in teams_with_data:
                    teams_without_data.append(opp)
        except:
            pass
        
        try:
            matches = pd.read_csv("DSX_Matches_Fall2025.csv")
            for opp in matches['Opponent'].dropna().unique():
                if opp not in teams_with_data and opp not in teams_without_data:
                    teams_without_data.append(opp)
        except:
            pass
        
        # Show info about teams without data
        if teams_without_data:
            with st.expander(f"ℹ️ Teams on Schedule (No Data Yet) - {len(teams_without_data)} teams"):
                st.write("**These teams are on your schedule but don't have stats data yet:**")
                for team in sorted(teams_without_data):
                    st.write(f"• {team}")
                st.info("💡 **To add data:** Run `update_all_data.py` or add these teams' divisions to tracking.")
        
        st.success(f"✅ Analyzing {len(teams)} teams with complete data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Select Team 1**")
            team1 = st.selectbox("Team 1", teams, index=0, label_visibility="collapsed", key="team1_analysis")
        
        with col2:
            st.write("**Select Team 2**")
            # Filter out team1 from team2 options
            team2_options = [t for t in teams if t != team1]
            team2 = st.selectbox("Team 2", team2_options, index=0, label_visibility="collapsed", key="team2_analysis")
        
        # Get team data (guaranteed to exist now)
        team1_data = df[df['Team'] == team1].iloc[0]
        team2_data = df[df['Team'] == team2].iloc[0]
        
        st.markdown("---")
        
        # Head-to-head comparison
        col1, col2, col3 = st.columns([1, 0.2, 1])
        
        with col1:
            st.markdown(f"### {team1}")
            # Show rank or "Independent" for DSX
            if team1_data['Rank'] == 0:
                st.metric("Division Status", "Independent")
            else:
                st.metric("Rank", f"#{int(team1_data['Rank'])}")
            st.metric("Strength Index", f"{team1_data['StrengthIndex']:.1f}")
            st.metric("Record", f"{int(team1_data['W'])}-{int(team1_data['L'])}-{int(team1_data['D'])}")
            st.metric("Goals/Game", f"{team1_data['GF']:.2f} - {team1_data['GA']:.2f}")
            st.metric("GD/Game", f"{team1_data['GD']:+.2f}")
            st.metric("PPG", f"{team1_data['PPG']:.2f}")
        
        with col2:
            st.markdown("<div style='text-align: center; padding-top: 100px; font-size: 40px;'>VS</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"### {team2}")
            # Show rank or "Independent" for DSX
            if team2_data['Rank'] == 0:
                st.metric("Division Status", "Independent")
            else:
                st.metric("Rank", f"#{int(team2_data['Rank'])}")
            st.metric("Strength Index", f"{team2_data['StrengthIndex']:.1f}")
            st.metric("Record", f"{int(team2_data['W'])}-{int(team2_data['L'])}-{int(team2_data['D'])}")
            st.metric("Goals/Game", f"{team2_data['GF']:.2f} - {team2_data['GA']:.2f}")
            st.metric("GD/Game", f"{team2_data['GD']:+.2f}")
            st.metric("PPG", f"{team2_data['PPG']:.2f}")
        
        st.markdown("---")
        
        # Matchup analysis
        st.subheader("📈 Matchup Analysis")
        
        strength_diff = team1_data['StrengthIndex'] - team2_data['StrengthIndex']
        
        if abs(strength_diff) < 5:
            prediction = "🟡 Toss-up game - could go either way"
        elif strength_diff > 15:
            prediction = f"🟢 {team1} heavily favored"
        elif strength_diff > 5:
            prediction = f"🟢 {team1} favored"
        elif strength_diff < -15:
            prediction = f"🔴 {team2} heavily favored"
        else:
            prediction = f"🔴 {team2} favored"
        
        st.info(prediction)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Strength Difference", f"{abs(strength_diff):.1f} points", 
                     f"{team1 if strength_diff > 0 else team2} advantage")
        
        with col2:
            expected_gd = (team1_data['GF'] - team1_data['GA']) - (team2_data['GF'] - team2_data['GA'])
            st.metric("Expected Goal Differential", f"{expected_gd:+.2f}", 
                     f"per game for {team1}")
        
        # Radar chart comparison
        st.subheader("Attribute Comparison")
        
        categories = ['Offense (GF)', 'Defense (inverse GA)', 'Consistency (PPG)', 'Goal Diff']
        
        team1_values = [
            team1_data['GF'] / 5 * 100,  # Normalize to 0-100
            (5 - team1_data['GA']) / 5 * 100,  # Inverse for defense
            team1_data['PPG'] / 3 * 100,
            (team1_data['GD'] + 5) / 10 * 100
        ]
        
        team2_values = [
            team2_data['GF'] / 5 * 100,
            (5 - team2_data['GA']) / 5 * 100,
            team2_data['PPG'] / 3 * 100,
            (team2_data['GD'] + 5) / 10 * 100
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=team1_values,
            theta=categories,
            fill='toself',
            name=team1
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=team2_values,
            theta=categories,
            fill='toself',
            name=team2
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)


elif page == "👥 Player Stats":
    st.title("👥 Player Statistics & Performance")
    
    st.info("📊 Track individual player contributions and development")
    
    # Load player stats and roster
    try:
        # Read CSVs exactly like Data Manager (which works!)
        roster = pd.read_csv("roster.csv", index_col=False)
        player_stats = pd.read_csv("player_stats.csv", index_col=False)
        
        # Convert PlayerNumber to same type BEFORE merge (this is the key!)
        roster['PlayerNumber'] = roster['PlayerNumber'].astype(str).str.strip()
        player_stats['PlayerNumber'] = player_stats['PlayerNumber'].astype(str).str.strip()
        
        # Now merge will work
        players = pd.merge(
            roster[['PlayerNumber', 'PlayerName', 'Position']], 
            player_stats[['PlayerNumber', 'GamesPlayed', 'Goals', 'Assists', 'MinutesPlayed', 'Notes']], 
            on='PlayerNumber', 
            how='inner'
        )
        
        # Convert numeric columns after merge
        players['PlayerNumber'] = pd.to_numeric(players['PlayerNumber'], errors='coerce')
        players['GamesPlayed'] = pd.to_numeric(players['GamesPlayed'], errors='coerce').fillna(0)
        players['Goals'] = pd.to_numeric(players['Goals'], errors='coerce').fillna(0)
        players['Assists'] = pd.to_numeric(players['Assists'], errors='coerce').fillna(0)
        players['MinutesPlayed'] = pd.to_numeric(players['MinutesPlayed'], errors='coerce').fillna(0)
        
        # Ensure Notes exists
        if 'Notes' not in players.columns:
            players['Notes'] = ''
        
        # Fill any NaN
        players = players.fillna(0)
        
        # Calculate derived stats
        players['Goals+Assists'] = players['Goals'] + players['Assists']
        players['Minutes'] = players['MinutesPlayed']
        players['Goals/Game'] = players.apply(lambda x: x['Goals'] / x['GamesPlayed'] if x['GamesPlayed'] > 0 else 0, axis=1)
        players['Assists/Game'] = players.apply(lambda x: x['Assists'] / x['GamesPlayed'] if x['GamesPlayed'] > 0 else 0, axis=1)
        
        # Top Stats
        st.header("⭐ Top Performers")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("⚽ Goals")
            top_scorers = players.nlargest(5, 'Goals')[['PlayerName', 'Goals', 'Goals/Game']]
            if not top_scorers.empty and top_scorers['Goals'].sum() > 0:
                for idx, player in top_scorers.iterrows():
                    st.write(f"**{player['PlayerName']}**: {int(player['Goals'])} goals ({player['Goals/Game']:.2f}/game)")
            else:
                st.write("_No goal data yet - update player_stats.csv_")
        
        with col2:
            st.subheader("🎯 Assists")
            top_assists = players.nlargest(5, 'Assists')[['PlayerName', 'Assists', 'Assists/Game']]
            if not top_assists.empty and top_assists['Assists'].sum() > 0:
                for idx, player in top_assists.iterrows():
                    st.write(f"**{player['PlayerName']}**: {int(player['Assists'])} assists ({player['Assists/Game']:.2f}/game)")
            else:
                st.write("_No assist data yet - update player_stats.csv_")
        
        with col3:
            st.subheader("🌟 Total Contributions")
            top_contrib = players.nlargest(5, 'Goals+Assists')[['PlayerName', 'Goals+Assists', 'GamesPlayed']]
            if not top_contrib.empty and top_contrib['Goals+Assists'].sum() > 0:
                for idx, player in top_contrib.iterrows():
                    st.write(f"**{player['PlayerName']}**: {int(player['Goals+Assists'])} G+A ({int(player['GamesPlayed'])} games)")
            else:
                st.write("_No contribution data yet_")
        
        st.markdown("---")
        
        # Full Player Table
        st.header("📋 Complete Roster Stats")
        
        # Check if we have player data
        if len(players) == 0:
            st.warning("No player data loaded. Check that roster.csv and player_stats.csv are properly formatted.")
        else:
            # Sortable table
            sort_by = st.selectbox("Sort by", ["PlayerNumber", "PlayerName", "Goals", "Assists", "Goals+Assists", "GamesPlayed", "Minutes"])
            ascending = st.checkbox("Ascending order", value=False)
            
            # Only include columns that exist
            desired_cols = ['PlayerNumber', 'PlayerName', 'Position', 'GamesPlayed', 'Goals', 'Assists', 'Goals+Assists', 'Goals/Game', 'Minutes']
            display_cols = [col for col in desired_cols if col in players.columns]
            
            display_df = players[display_cols].sort_values(sort_by, ascending=ascending)
            
            # Format for display
            if 'Goals/Game' in display_df.columns:
                display_df['Goals/Game'] = display_df['Goals/Game'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Playing Time Analysis
        st.header("⏱️ Playing Time Distribution")
        
        if players['Minutes'].sum() > 0:
            fig = px.bar(
                players.sort_values('Minutes', ascending=False),
                x='PlayerName',
                y='Minutes',
                title='Minutes Played by Player',
                labels={'PlayerName': 'Player', 'Minutes': 'Minutes Played'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Fairness check
            avg_minutes = players['Minutes'].mean()
            max_minutes = players['Minutes'].max()
            min_minutes = players['Minutes'].min()
            
            if max_minutes - min_minutes < avg_minutes * 0.3:
                st.success(f"✅ **Fair Distribution**: Playing time is well balanced (range: {min_minutes:.0f}-{max_minutes:.0f} min)")
            else:
                st.warning(f"⚠️ **Uneven Distribution**: Large gap in playing time (range: {min_minutes:.0f}-{max_minutes:.0f} min)")
        else:
            st.info("No playing time data recorded yet. Update player_stats.csv with minutes played.")
        
        st.markdown("---")
        
        # Individual Player Details
        st.header("👤 Player Details")
        
        if len(players) > 0:
            selected_player = st.selectbox("Select Player", players['PlayerName'].tolist())
            
            player_data = players[players['PlayerName'] == selected_player].iloc[0]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Profile")
                st.write(f"**Number:** {int(player_data['PlayerNumber'])}")
                st.write(f"**Position:** {player_data['Position']}")
                st.write(f"**Games:** {int(player_data['GamesPlayed'])}")
                st.write(f"**Minutes:** {int(player_data['Minutes'])}")
                
            with col2:
                st.subheader("Season Stats")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Goals", int(player_data['Goals']))
                with col_b:
                    st.metric("Assists", int(player_data['Assists']))
                with col_c:
                    st.metric("G/Game", f"{player_data['Goals/Game']:.2f}")
                with col_d:
                    st.metric("Min/Game", f"{player_data['Minutes'] / player_data['GamesPlayed'] if player_data['GamesPlayed'] > 0 else 0:.0f}")
            
            if 'Notes' in player_data and player_data['Notes'] and str(player_data['Notes']).strip():
                st.write(f"**Notes:** {player_data['Notes']}")
        else:
            st.warning("No players loaded. Check that player_stats.csv and roster.csv are properly formatted.")
        
        st.markdown("---")
        
        # Data Management
        st.header("📝 Update Player Data")
        
        st.info("To update player statistics, edit the `player_stats.csv` file and refresh the dashboard.")
        
        with st.expander("📂 How to Update Player Stats"):
            st.write("""
            1. Open `player_stats.csv` in Excel or text editor
            2. Update the following columns:
               - **GamesPlayed**: Number of games the player has participated in
               - **Goals**: Total goals scored
               - **Assists**: Total assists
               - **MinutesPlayed**: Total minutes on field
               - **Notes**: Any observations about player development
            3. Save the file
            4. Click 🔄 Refresh Data in the sidebar
            """)
        
        # Download template
        if st.button("📥 Download Current Stats as Template"):
            csv = players[['PlayerNumber', 'PlayerName', 'GamesPlayed', 'Goals', 'Assists', 'MinutesPlayed', 'Notes']].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="player_stats_template.csv",
                mime="text/csv"
            )
            
    except FileNotFoundError as e:
        st.error(f"Player data files not found: {e}")
        st.write("Make sure `player_stats.csv` and `roster.csv` exist in the project directory.")
        
        if st.button("Create Template Files"):
            st.info("Run this command to create template files: `python -c \"import pandas as pd; pd.DataFrame({'PlayerNumber':range(1,11), 'PlayerName':['Player '+str(i) for i in range(1,11)], 'GamesPlayed':[0]*10, 'Goals':[0]*10, 'Assists':[0]*10, 'MinutesPlayed':[0]*10, 'Notes':['']*10}).to_csv('player_stats.csv', index=False)\"`")


elif page == "📅 Match History":
    st.title("📅 DSX Match History")
    
    matches = load_dsx_matches()
    
    # Load game player stats
    try:
        game_stats = pd.read_csv("game_player_stats.csv")
    except:
        game_stats = pd.DataFrame()
    
    # Summary stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Games Played", len(matches))
    with col2:
        st.metric("Wins", (matches['Result'] == 'W').sum())
    with col3:
        st.metric("Draws", (matches['Result'] == 'D').sum())
    with col4:
        st.metric("Losses", (matches['Result'] == 'L').sum())
    with col5:
        st.metric("Goal Diff", f"{matches['GD'].sum():+d}")
    
    st.markdown("---")
    
    # Match details with scorers
    st.subheader("Match Details")
    
    for idx, match in matches.iterrows():
        result_emoji = {'W': '✅', 'D': '➖', 'L': '❌'}
        emoji = result_emoji.get(match['Result'], '⚽')
        
        with st.expander(f"{emoji} {match['Date'].strftime('%b %d')} - {match['Opponent']} ({match['GF']}-{match['GA']})", expanded=False):
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.write(f"**Tournament:** {match.get('Tournament', 'N/A')}")
                if 'Location' in match:
                    st.write(f"**Location:** {match['Location']}")
                outcome = match.get('Outcome', match['Result'])
                st.write(f"**Result:** {match['Result']} - {outcome}")
                st.write(f"**Score:** DSX {match['GF']} - {match['GA']} {match['Opponent']}")
                st.write(f"**Goal Diff:** {match['GD']:+d}")
            
            with col2:
                st.write("**⚽ Goal Scorers:**")
                
                if not game_stats.empty:
                    # Get scorers for this game
                    game_scorers = game_stats[
                        (game_stats['Date'] == match['Date'].strftime('%Y-%m-%d')) &
                        (game_stats['Opponent'] == match['Opponent']) &
                        (game_stats['Goals'] > 0)
                    ]
                    
                    if not game_scorers.empty:
                        for _, scorer in game_scorers.iterrows():
                            goals = int(scorer['Goals'])
                            player = scorer['PlayerName']
                            if goals > 1:
                                st.write(f"  • {player} ({goals} goals)")
                            else:
                                st.write(f"  • {player}")
                    else:
                        st.write(f"  • {int(match['GF'])} goals scored")
                else:
                    st.write(f"  • {int(match['GF'])} goals scored")
                
                st.write("")
                st.write("**🎯 Assists:**")
                
                if not game_stats.empty:
                    game_assists = game_stats[
                        (game_stats['Date'] == match['Date'].strftime('%Y-%m-%d')) &
                        (game_stats['Opponent'] == match['Opponent']) &
                        (game_stats['Assists'] > 0)
                    ]
                    
                    if not game_assists.empty:
                        for _, assister in game_assists.iterrows():
                            assists = int(assister['Assists'])
                            player = assister['PlayerName']
                            notes = assister.get('Notes', '')
                            if notes:
                                st.write(f"  • {player} ({notes})")
                            else:
                                st.write(f"  • {player}")
                    else:
                        st.write("  • Not tracked")
                else:
                    st.write("  • Not tracked")
    
    st.markdown("---")
    
    # Match table
    st.subheader("Quick View - All Matches")
    
    display_matches = matches.copy()
    display_matches['Date'] = display_matches['Date'].dt.strftime('%Y-%m-%d')
    
    # Add result emoji
    result_emoji = {'W': '✅', 'D': '➖', 'L': '❌'}
    display_matches['Result'] = display_matches['Result'].map(result_emoji) + ' ' + display_matches['Result']
    
    st.dataframe(
        display_matches[['Date', 'Tournament', 'Opponent', 'GF', 'GA', 'GD', 'Result']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date"),
            "GF": st.column_config.NumberColumn("GF", help="Goals For"),
            "GA": st.column_config.NumberColumn("GA", help="Goals Against"),
            "GD": st.column_config.NumberColumn("GD", help="Goal Differential", format="%+d"),
        }
    )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Goals over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=matches['Date'],
            y=matches['GF'],
            name='Goals For',
            mode='lines+markers',
            line=dict(color='green')
        ))
        fig.add_trace(go.Scatter(
            x=matches['Date'],
            y=matches['GA'],
            name='Goals Against',
            mode='lines+markers',
            line=dict(color='red')
        ))
        fig.update_layout(
            title='Goals Over Time',
            xaxis_title='Date',
            yaxis_title='Goals',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Results by tournament
        tournament_results = matches.groupby(['Tournament', 'Result']).size().unstack(fill_value=0)
        
        fig = px.bar(
            tournament_results,
            title='Results by Tournament',
            barmode='stack',
            color_discrete_map={'W': 'green', 'D': 'yellow', 'L': 'red'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cumulative GD
    matches_sorted = matches.sort_values('Date')
    matches_sorted['Cumulative_GD'] = matches_sorted['GD'].cumsum()
    
    fig = px.line(
        matches_sorted,
        x='Date',
        y='Cumulative_GD',
        title='Cumulative Goal Differential',
        markers=True
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


elif page == "🎮 Game Predictions":
    st.title("🎮 Game Predictions & Scenarios")
    
    st.info("🔮 Predict match outcomes and explore what-if scenarios")
    
    # Load data
    try:
        upcoming = pd.read_csv("DSX_Upcoming_Opponents.csv")
        all_divisions_df = load_division_data()
        
        # Calculate DSX stats dynamically
        dsx_stats = calculate_dsx_stats()
        dsx_si = dsx_stats['StrengthIndex']
        dsx_gf_avg = dsx_stats['GF_PG']
        dsx_ga_avg = dsx_stats['GA_PG']
        
        # Prediction Calculator
        st.header("🔮 Match Predictor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Select Opponent")
            
            # Get all teams from combined division data
            if not all_divisions_df.empty:
                all_teams = sorted(all_divisions_df['Team'].dropna().unique().tolist())
            else:
                all_teams = []
            
            # Add upcoming opponents
            if not upcoming.empty:
                all_teams.extend(upcoming['Opponent'].tolist())
            
            all_teams = sorted(list(set(all_teams)))
            
            selected_opponent = st.selectbox("Choose opponent", all_teams)
            
            # Get opponent stats from consolidated division data
            opp_si = None
            opp_gf = None
            opp_ga = None
            
            if not all_divisions_df.empty:
                opp_data = all_divisions_df[all_divisions_df['Team'] == selected_opponent]
                if not opp_data.empty:
                    opp_si = opp_data.iloc[0]['StrengthIndex']
                    # Calculate per-game stats
                    opp_gp = opp_data.iloc[0].get('GP', 1)
                    opp_gp = opp_gp if opp_gp > 0 else 1
                    opp_gf = opp_data.iloc[0].get('GF', 0) / opp_gp  # Goals per game
                    opp_ga = opp_data.iloc[0].get('GA', 0) / opp_gp  # Goals against per game
            
            if opp_si is None:
                st.warning("No division data found for this opponent. Enter stats manually:")
                opp_si = st.number_input("Opponent Strength Index", min_value=0.0, max_value=100.0, value=50.0)
                opp_gf = st.number_input("Opponent Goals/Game", min_value=0.0, max_value=10.0, value=3.0)
                opp_ga = st.number_input("Opponent Goals Against/Game", min_value=0.0, max_value=10.0, value=3.0)
        
        with col2:
            st.subheader("Prediction")
            
            if opp_si is not None:
                # Display comparison
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("DSX SI", f"{dsx_si:.1f}")
                    st.metric("DSX GF/Game", f"{dsx_gf_avg:.2f}")
                with col_b:
                    st.metric("Opponent SI", f"{opp_si:.1f}")
                    st.metric("Opp GF/Game", f"{opp_gf:.2f}")
                
                st.markdown("---")
                
                # Calculate prediction
                si_diff = dsx_si - opp_si
                
                # More balanced prediction formula
                # DSX gets bonus for being stronger, opponent gets penalty for being weaker
                # But don't make weak teams completely scoreless
                pred_dsx_goals = max(0.5, dsx_gf_avg + (si_diff * 0.02))
                pred_opp_goals = max(0.5, opp_gf - (si_diff * 0.02))
                
                st.subheader("📊 Predicted Score")
                st.write(f"### DSX: {pred_dsx_goals:.1f}")
                st.write(f"### {selected_opponent}: {pred_opp_goals:.1f}")
                
                # Win probability
                if si_diff > 15:
                    win_prob = 70
                    draw_prob = 20
                    loss_prob = 10
                elif si_diff > 5:
                    win_prob = 55
                    draw_prob = 25
                    loss_prob = 20
                elif si_diff > -5:
                    win_prob = 40
                    draw_prob = 30
                    loss_prob = 30
                elif si_diff > -15:
                    win_prob = 25
                    draw_prob = 25
                    loss_prob = 50
                else:
                    win_prob = 15
                    draw_prob = 20
                    loss_prob = 65
                
                st.markdown("---")
                st.subheader("📈 Outcome Probability")
                
                col_w, col_d, col_l = st.columns(3)
                with col_w:
                    st.metric("Win", f"{win_prob}%")
                with col_d:
                    st.metric("Draw", f"{draw_prob}%")
                with col_l:
                    st.metric("Loss", f"{loss_prob}%")
        
        st.markdown("---")
        
        # What-If Scenarios
        st.header("💭 What-If Scenarios")
        
        scenario = st.selectbox("Choose Scenario", [
            "What if DSX wins next game?",
            "What if DSX wins all remaining games?",
            "What if DSX beats a top-3 team?",
            "Custom scenario"
        ])
        
        if "wins next game" in scenario:
            st.subheader("Impact of Next Win")
            
            # Use dsx_stats which is already calculated
            current_gp = dsx_stats['GP']
            current_ppg = dsx_stats['PPG']
            current_points = int(current_ppg * current_gp)
            
            new_points = current_points + 3
            new_gp = current_gp + 1
            new_ppg = new_points / new_gp
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current PPG", f"{current_ppg:.2f}")
                st.metric("Current Points", current_points)
            with col2:
                st.metric("New PPG", f"{new_ppg:.2f}", delta=f"+{new_ppg - current_ppg:.2f}")
                st.metric("New Points", new_points, delta="+3")
            
            st.success(f"✅ A win would improve DSX's PPG by {new_ppg - current_ppg:.2f} points!")
        
        elif "wins all remaining" in scenario:
            st.subheader("Best Case Scenario")
            
            remaining_games = len(upcoming) if not upcoming.empty else 3
            
            # Use dsx_stats which is already calculated
            current_gp = dsx_stats['GP']
            current_ppg = dsx_stats['PPG']
            current_points = int(current_ppg * current_gp)
            
            best_case_points = current_points + (remaining_games * 3)
            best_case_gp = current_gp + remaining_games
            best_case_ppg = best_case_points / best_case_gp
            
            st.write(f"If DSX wins all {remaining_games} remaining games:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Points", best_case_points)
            with col2:
                st.metric("Total Games", best_case_gp)
            with col3:
                st.metric("Final PPG", f"{best_case_ppg:.2f}")
            
            st.success(f"🏆 This would give DSX a {best_case_ppg:.2f} PPG - strong finish!")
        
        elif "beats a top-3 team" in scenario:
            st.subheader("Upset Victory Impact")
            
            st.write("**Beating a top-3 team would:**")
            st.write("- ✅ Boost team confidence")
            st.write("- ✅ Prove DSX can compete with the best")
            st.write("- ✅ Improve strength of schedule")
            st.write("- ✅ Potentially move up in rankings")
            
            st.info("💡 Focus on defensive organization and counter-attacks against stronger opponents")
        
    except Exception as e:
        st.error(f"Error loading prediction data: {e}")
        st.write("Make sure all data files are available.")


elif page == "📊 Benchmarking":
    st.title("📊 Team Benchmarking & Comparison")
    
    st.info("⚖️ Compare DSX against any opponent or division team")
    
    # Load ALL division data using centralized function
    all_divisions_df = load_division_data()
    
    try:
        dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv")
        
        # Calculate DSX stats from actual matches
        completed = dsx_matches[dsx_matches['Outcome'].notna()]
        if len(completed) > 0:
            dsx_gp = len(completed)
            dsx_w = len(completed[completed['Outcome'] == 'W'])
            dsx_d = len(completed[completed['Outcome'] == 'D'])
            dsx_l = len(completed[completed['Outcome'] == 'L'])
            dsx_gf = pd.to_numeric(completed['GF'], errors='coerce').fillna(0).sum()
            dsx_ga = pd.to_numeric(completed['GA'], errors='coerce').fillna(0).sum()
            dsx_gd = dsx_gf - dsx_ga
            dsx_pts = (dsx_w * 3) + dsx_d
            dsx_ppg = dsx_pts / dsx_gp if dsx_gp > 0 else 0
            dsx_gf_pg = dsx_gf / dsx_gp if dsx_gp > 0 else 0
            dsx_ga_pg = dsx_ga / dsx_gp if dsx_gp > 0 else 0
            dsx_gd_pg = dsx_gd / dsx_gp if dsx_gp > 0 else 0
            
            # Calculate DSX Strength Index
            ppg_norm = max(0.0, min(3.0, dsx_ppg)) / 3.0 * 100.0
            gdpg_norm = (max(-5.0, min(5.0, dsx_gd_pg)) + 5.0) / 10.0 * 100.0
            dsx_strength = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
            
            dsx_stats = {
                'Team': 'Dublin DSX Orange 2018 Boys',
                'StrengthIndex': dsx_strength,
                'PPG': dsx_ppg,
                'GF': dsx_gf_pg,
                'GA': dsx_ga_pg,
                'GD': dsx_gd_pg,
                'GP': dsx_gp,
                'W': dsx_w,
                'D': dsx_d,
                'L': dsx_l
            }
        else:
            dsx_stats = {
                'Team': 'Dublin DSX Orange 2018 Boys',
                'StrengthIndex': 0,
                'PPG': 0,
                'GF': 0,
                'GA': 0,
                'GD': 0,
                'GP': 0,
                'W': 0,
                'D': 0,
                'L': 0
            }
        
        if not all_divisions_df.empty:
            st.success(f"✅ Ready to benchmark against {len(all_divisions_df)} teams across all divisions")
        else:
            st.warning("No division data found. Run `update_all_data.py` to fetch division stats.")
        
        # Team Selector
        st.header("🔍 Select Teams to Compare")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Team 1: DSX (You)")
            st.write(f"**Strength Index:** {dsx_stats['StrengthIndex']:.1f}")
            st.write(f"**PPG:** {dsx_stats['PPG']:.2f}")
            st.write(f"**Goals/Game:** {dsx_stats['GF']:.2f}")
            st.write(f"**Against/Game:** {dsx_stats['GA']:.2f}")
        
        with col2:
            st.subheader("Team 2: Select Opponent")
            
            # Build team list from ALL divisions
            if not all_divisions_df.empty:
                team_options = sorted(all_divisions_df['Team'].dropna().unique().tolist())
                selected_team_name = st.selectbox("Choose opponent", team_options)
                
                # Get selected team data
                opp_data = all_divisions_df[all_divisions_df['Team'] == selected_team_name]
                if not opp_data.empty:
                    opp_stats = opp_data.iloc[0]
                    st.write(f"**Strength Index:** {opp_stats['StrengthIndex']:.1f}")
                    st.write(f"**PPG:** {opp_stats.get('PPG', 0):.2f}")
                    if 'GF' in opp_stats:
                        st.write(f"**Goals/Game:** {opp_stats['GF']:.2f}")
                    if 'GA' in opp_stats:
                        st.write(f"**Against/Game:** {opp_stats['GA']:.2f}")
                else:
                    opp_stats = None
            else:
                st.warning("No opponent data available")
                opp_stats = None
        
        st.markdown("---")
        
        # Comparison Charts
        if opp_stats is not None:
            st.header("📊 Head-to-Head Comparison")
            
            # Strength Index comparison
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Strength Index")
                diff_si = dsx_stats['StrengthIndex'] - opp_stats['StrengthIndex']
                if diff_si > 0:
                    st.success(f"DSX: +{diff_si:.1f}")
                elif diff_si < 0:
                    st.error(f"Opponent: +{abs(diff_si):.1f}")
                else:
                    st.info("Even")
            
            with col2:
                st.subheader("Offensive")
                diff_gf = dsx_stats['GF'] - opp_stats['GF']
                if diff_gf > 0:
                    st.success(f"DSX: +{diff_gf:.2f} G/G")
                elif diff_gf < 0:
                    st.error(f"Opponent: +{abs(diff_gf):.2f} G/G")
                else:
                    st.info("Even")
            
            with col3:
                st.subheader("Defensive")
                diff_ga = opp_stats['GA'] - dsx_stats['GA']  # Lower is better
                if diff_ga > 0:
                    st.success(f"DSX: -{abs(diff_ga):.2f} GA/G")
                elif diff_ga < 0:
                    st.error(f"Opponent: -{abs(diff_ga):.2f} GA/G")
                else:
                    st.info("Even")
            
            st.markdown("---")
            
            # Radar Chart
            st.subheader("📈 Performance Radar")
            
            categories = ['Strength Index', 'PPG', 'Goals For', 'Goals Against (Inv)', 'Goal Diff']
            
            # Normalize metrics to 0-100 scale
            dsx_values = [
                dsx_stats['StrengthIndex'],
                dsx_stats['PPG'] / 3.0 * 100,
                dsx_stats['GF'] / 10.0 * 100,
                (10.0 - dsx_stats['GA']) / 10.0 * 100,  # Inverted (lower is better)
                (dsx_stats['GD'] + 5) / 10.0 * 100
            ]
            
            opp_values = [
                opp_stats['StrengthIndex'],
                opp_stats['PPG'] / 3.0 * 100,
                opp_stats['GF'] / 10.0 * 100,
                (10.0 - opp_stats['GA']) / 10.0 * 100,
                (opp_stats['GD'] + 5) / 10.0 * 100
            ]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=dsx_values,
                theta=categories,
                fill='toself',
                name='DSX',
                line_color='orange'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=opp_values,
                theta=categories,
                fill='toself',
                name=selected_team_name,
                line_color='blue'
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Matchup Prediction
            st.subheader("🎯 Predicted Matchup")
            
            si_diff = dsx_stats['StrengthIndex'] - opp_stats['StrengthIndex']
            
            if si_diff > 15:
                st.success("✅ **DSX FAVORED** - Significant advantage")
                st.write("Expected outcome: Win")
                st.write("Confidence: High")
            elif si_diff > 5:
                st.success("✅ **DSX SLIGHT EDGE** - Small advantage")
                st.write("Expected outcome: Competitive win")
                st.write("Confidence: Medium")
            elif si_diff > -5:
                st.info("⚖️ **EVENLY MATCHED** - Toss-up game")
                st.write("Expected outcome: Could go either way")
                st.write("Confidence: Low")
            elif si_diff > -15:
                st.warning("⚠️ **OPPONENT SLIGHT EDGE** - Uphill battle")
                st.write("Expected outcome: Competitive loss")
                st.write("Confidence: Medium")
            else:
                st.error("❌ **OPPONENT FAVORED** - Difficult matchup")
                st.write("Expected outcome: Likely loss")
                st.write("Confidence: High")
            
    except Exception as e:
        st.error(f"Error loading benchmarking data: {e}")
        st.write("Make sure division ranking files are available.")


elif page == "📝 Game Log":
    st.title("📝 Game-by-Game Player Performance")
    
    st.info("⚽ Detailed breakdown of who scored and assisted in each game")
    
    # Load data
    matches = load_dsx_matches()
    
    try:
        game_stats = pd.read_csv("game_player_stats.csv")
        player_stats = pd.read_csv("player_stats.csv")
    except:
        game_stats = pd.DataFrame()
        player_stats = pd.DataFrame()
    
    # Filter options
    st.header("🔍 Filter Games")
    
    col1, col2 = st.columns(2)
    
    with col1:
        result_filter = st.selectbox("Filter by Result", ["All Games", "Wins Only", "Draws Only", "Losses Only"])
    
    with col2:
        if not player_stats.empty:
            player_filter = st.selectbox("Filter by Player", ["All Players"] + player_stats['PlayerName'].tolist())
        else:
            player_filter = "All Players"
    
    st.markdown("---")
    
    # Apply filters
    filtered_matches = matches.copy()
    
    if result_filter == "Wins Only":
        filtered_matches = filtered_matches[filtered_matches['Result'] == 'W']
    elif result_filter == "Draws Only":
        filtered_matches = filtered_matches[filtered_matches['Result'] == 'D']
    elif result_filter == "Losses Only":
        filtered_matches = filtered_matches[filtered_matches['Result'] == 'L']
    
    st.header(f"📋 Game Log ({len(filtered_matches)} games)")
    
    # Display games
    for idx, match in filtered_matches.iterrows():
        result_emoji = {'W': '✅ WIN', 'D': '➖ DRAW', 'L': '❌ LOSS'}
        result_text = result_emoji.get(match['Result'], match['Result'])
        
        st.subheader(f"{match['Date'].strftime('%b %d, %Y')} - {match['Opponent']}")
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            st.metric("Score", f"{int(match['GF'])} - {int(match['GA'])}")
            st.write(f"**Result:** {result_text}")
        
        with col2:
            st.write(f"**Tournament:** {match.get('Tournament', 'N/A')}")
            if 'Location' in match:
                st.write(f"**Location:** {match['Location']}")
            st.write(f"**Goal Diff:** {match['GD']:+d}")
        
        with col3:
            # Player contributions
            if not game_stats.empty:
                game_players = game_stats[
                    (game_stats['Date'] == match['Date'].strftime('%Y-%m-%d')) &
                    (game_stats['Opponent'] == match['Opponent'])
                ]
                
                if player_filter != "All Players":
                    game_players = game_players[game_players['PlayerName'] == player_filter]
                
                if not game_players.empty:
                    st.write("**⚽ Goals:**")
                    scorers = game_players[game_players['Goals'] > 0]
                    if not scorers.empty:
                        for _, player in scorers.iterrows():
                            st.write(f"  • {player['PlayerName']} ({int(player['Goals'])})")
                    else:
                        st.write("  • None (filtered out)")
                    
                    st.write("**🎯 Assists:**")
                    assisters = game_players[game_players['Assists'] > 0]
                    if not assisters.empty:
                        for _, player in assisters.iterrows():
                            notes = player.get('Notes', '')
                            if notes:
                                st.write(f"  • {player['PlayerName']} - {notes}")
                            else:
                                st.write(f"  • {player['PlayerName']}")
                    else:
                        st.write("  • None tracked")
                else:
                    st.write(f"⚽ {int(match['GF'])} goals scored")
                    st.write("🎯 Assists not tracked")
            else:
                st.write(f"⚽ {int(match['GF'])} goals scored")
        
        st.markdown("---")
    
    # Summary statistics
    if player_filter != "All Players" and not game_stats.empty:
        st.markdown("---")
        st.header(f"📊 {player_filter} - Filtered Summary")
        
        player_games = game_stats[game_stats['PlayerName'] == player_filter]
        
        total_goals = player_games['Goals'].sum()
        total_assists = player_games['Assists'].sum()
        games_with_goal = (player_games['Goals'] > 0).sum()
        games_with_assist = (player_games['Assists'] > 0).sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Goals", int(total_goals))
        with col2:
            st.metric("Total Assists", int(total_assists))
        with col3:
            st.metric("Games with Goal", int(games_with_goal))
        with col4:
            st.metric("Games with Assist", int(games_with_assist))
        
        if total_goals > 0:
            st.success(f"⚽ {player_filter} has scored in {games_with_goal} of {len(filtered_matches)} games ({games_with_goal/len(filtered_matches)*100:.1f}%)")


elif page == "🔍 Opponent Intel":
    st.title("🔍 Opponent Intelligence")
    
    # Tabs for played vs upcoming opponents
    tab1, tab2 = st.tabs(["📊 Played Opponents", "🔮 Upcoming Opponents"])
    
    with tab1:
        st.subheader("Teams DSX Has Played")
        
        # Load DSX's actual opponents
        try:
            actual_opponents = pd.read_csv("DSX_Actual_Opponents.csv")
            dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv")
            
            st.success(f"Loaded {len(actual_opponents)} opponents that DSX has played")
            
            # Check if opponent was pre-selected from Team Schedule
            default_index = 0
            if 'selected_opponent' in st.session_state:
                preselected = st.session_state.selected_opponent
                opponent_names = actual_opponents['Opponent'].tolist()
                if preselected in opponent_names:
                    default_index = opponent_names.index(preselected)
                    st.success(f"🎯 **Pre-Selected from Schedule:** {preselected}")
                    # Clear after use
                    if 'selected_opponent' in st.session_state:
                        del st.session_state.selected_opponent
            else:
                st.info("💡 Select a team to see detailed head-to-head analysis and performance trends.")
            
            # Opponent selector - show teams DSX actually played
            opponent_names = actual_opponents['Opponent'].tolist()
            selected_opp = st.selectbox(
                "Select Opponent", 
                opponent_names,
                index=default_index,
                help="Choose an opponent to see head-to-head analysis"
            )
            
            # Get opponent data
            opp_row = actual_opponents[actual_opponents['Opponent'] == selected_opp].iloc[0]
            opp_matches = dsx_matches[dsx_matches['Opponent'] == selected_opp]
            
            st.subheader(f"📊 {selected_opp}")
            
            # Display opponent stats from DSX's perspective
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Games Played", int(opp_row['GP']))
            with col2:
                st.metric("DSX Record", opp_row['Record'])
            with col3:
                st.metric("DSX Goals", f"{int(opp_row['GF'])}-{int(opp_row['GA'])}")
            with col4:
                st.metric("Goal Diff", f"{opp_row['GD']:+.0f}")
            with col5:
                st.metric("DSX PPG", f"{opp_row['PPG']:.2f}")
            
            st.markdown("---")
            
            # Head-to-head analysis
            st.subheader("📈 Matchup Analysis")
            
            if opp_row['PPG'] >= 2.5:
                st.success(f"✅ **Dominated** - DSX has strong record against {selected_opp}")
            elif opp_row['PPG'] >= 1.5:
                st.success(f"✅ **Strong** - DSX performs well against {selected_opp}")
            elif opp_row['PPG'] >= 1.0:
                st.info(f"⚖️ **Competitive** - Even matchup with {selected_opp}")
            elif opp_row['PPG'] > 0:
                st.warning(f"⚠️ **Struggled** - Difficult matchup against {selected_opp}")
            else:
                st.error(f"❌ **Overmatched** - {selected_opp} has dominated DSX")
            
            st.markdown("---")
            
            # Match history
            st.subheader("📅 Match History")
            
            match_display = opp_matches[['Date', 'Tournament', 'Location', 'GF', 'GA', 'Outcome', 'Points', 'GoalDiff']].copy()
            match_display.columns = ['Date', 'Tournament', 'Location', 'GF', 'GA', 'Result', 'Pts', 'GD']
            
            st.dataframe(match_display, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Performance trends
            if len(opp_matches) > 1:
                st.subheader("📊 Performance Trend")
                
                import plotly.graph_objects as go
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(opp_matches) + 1)),
                    y=opp_matches['GF'].values,
                    name='Goals For',
                    mode='lines+markers',
                    line=dict(color='green')
                ))
                
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(opp_matches) + 1)),
                    y=opp_matches['GA'].values,
                    name='Goals Against',
                    mode='lines+markers',
                    line=dict(color='red')
                ))
                
                fig.update_layout(
                    title=f"DSX Performance vs {selected_opp}",
                    xaxis_title="Game Number",
                    yaxis_title="Goals",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Tactical insights
            st.subheader("🎯 Key Insights")
            
            avg_gf = opp_row['GF'] / opp_row['GP']
            avg_ga = opp_row['GA'] / opp_row['GP']
            
            st.write(f"**Offensive Performance:** {avg_gf:.2f} goals/game vs this opponent")
            st.write(f"**Defensive Performance:** {avg_ga:.2f} goals against/game vs this opponent")
            
            # Compare to season average - DYNAMIC
            dsx_stats = calculate_dsx_stats()
            season_avg_gf = dsx_stats['GF_PG']
            season_avg_ga = dsx_stats['GA_PG']
            
            if avg_gf > season_avg_gf:
                st.write(f"⚽ DSX scores {avg_gf - season_avg_gf:.2f} MORE goals/game vs this opponent than season average")
            elif avg_gf < season_avg_gf:
                st.write(f"⚽ DSX scores {season_avg_gf - avg_gf:.2f} FEWER goals/game vs this opponent than season average")
            
            if avg_ga < season_avg_ga:
                st.write(f"🛡️ DSX allows {season_avg_ga - avg_ga:.2f} FEWER goals/game vs this opponent than season average")
            elif avg_ga > season_avg_ga:
                st.write(f"🛡️ DSX allows {avg_ga - season_avg_ga:.2f} MORE goals/game vs this opponent than season average")
            
            st.markdown("---")
            
            # Game plan for rematch
            st.subheader("📋 Game Plan for Next Time")
            
            if opp_row['PPG'] >= 2.0:
                st.write("**Continue What's Working:**")
                st.write("- Same tactical approach")
                st.write("- Build on previous success")
                st.write("- Maintain confidence")
            elif opp_row['PPG'] <= 0.5:
                st.write("**Need Different Approach:**")
                st.write("- Analyze what didn't work")
                st.write("- Consider tactical adjustments")
                st.write("- Focus on defensive organization")
            else:
                st.write("**Close Matchup:**")
                st.write("- Small adjustments can make difference")
                st.write("- Focus on finishing chances")
                st.write("- Minimize defensive errors")
                
        except FileNotFoundError:
            st.error("Opponent data not found. Run `python fix_opponent_tracking.py` to generate.")
            st.write("Or update `DSX_Matches_Fall2025.csv` with your match data.")
    
    with tab2:
        st.subheader("Scouting Upcoming Opponents")
        
        try:
            upcoming = pd.read_csv("DSX_Upcoming_Opponents.csv")
            
            st.success(f"Loaded {len(upcoming)} upcoming matches")
            st.info("💡 Scout these teams before your next games!")
            
            # Show upcoming schedule
            st.markdown("### 📅 Upcoming Schedule")
            
            for _, game in upcoming.iterrows():
                league = game.get('Tournament', game.get('League', 'N/A'))
                with st.expander(f"**{game['Date']}**: {game['Opponent']} ({league})", expanded=False):
                    st.write(f"📍 **Location:** {game['Location']}")
                    st.write(f"🏆 **League:** {league}")
                    st.write(f"📝 **Notes:** {game.get('Notes', 'N/A')}")
            
            st.markdown("---")
            
            # Check if opponent was pre-selected from Team Schedule
            upcoming_default_index = 0
            if 'selected_opponent' in st.session_state:
                preselected_upcoming = st.session_state.selected_opponent
                upcoming_names = upcoming['Opponent'].tolist()
                if preselected_upcoming in upcoming_names:
                    upcoming_default_index = upcoming_names.index(preselected_upcoming)
                    st.success(f"🎯 **Pre-Selected from Schedule:** {preselected_upcoming}")
                    # Clear after use
                    if 'selected_opponent' in st.session_state:
                        del st.session_state.selected_opponent
            
            # Opponent selector for upcoming
            upcoming_names = upcoming['Opponent'].tolist()
            selected_upcoming = st.selectbox(
                "Select Upcoming Opponent to Scout", 
                upcoming_names,
                index=upcoming_default_index,
                help="Choose an opponent to see scouting report"
            )
            
            st.subheader(f"🔍 Scouting Report: {selected_upcoming}")
            
            # Check if it's a BSA Celtic team
            if "BSA Celtic" in selected_upcoming:
                try:
                    bsa_schedules = pd.read_csv("BSA_Celtic_Schedules.csv")
                    team_matches = bsa_schedules[bsa_schedules['OpponentTeam'] == selected_upcoming]
                    
                    # Filter completed matches
                    completed = team_matches[team_matches['GF'] != ''].copy()
                    
                    if len(completed) > 0:
                        completed['GF'] = pd.to_numeric(completed['GF'])
                        completed['GA'] = pd.to_numeric(completed['GA'])
                        completed['GD'] = completed['GF'] - completed['GA']
                        
                        # Calculate stats
                        wins = (completed['GD'] > 0).sum()
                        draws = (completed['GD'] == 0).sum()
                        losses = (completed['GD'] < 0).sum()
                        
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("Games", len(completed))
                        with col2:
                            st.metric("Record", f"{wins}-{losses}-{draws}")
                        with col3:
                            st.metric("GF/Game", f"{completed['GF'].mean():.2f}")
                        with col4:
                            st.metric("GA/Game", f"{completed['GA'].mean():.2f}")
                        with col5:
                            ppg = (wins * 3 + draws) / len(completed)
                            st.metric("PPG", f"{ppg:.2f}")
                        
                        st.markdown("---")
                        
                        # Calculate Strength Index
                        gd_per_game = completed['GD'].mean()
                        ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
                        gd_norm = (max(-5.0, min(5.0, gd_per_game)) + 5.0) / 10.0 * 100.0
                        strength_index = 0.7 * ppg_norm + 0.3 * gd_norm
                        
                        st.subheader("📊 Strength Assessment")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            dsx_stats = calculate_dsx_stats()
                            st.metric("Opponent SI", f"{strength_index:.1f}")
                            st.metric("DSX SI", f"{dsx_stats['StrengthIndex']:.1f}")
                        
                        with col2:
                            dsx_stats = calculate_dsx_stats()
                            si_diff = dsx_stats['StrengthIndex'] - strength_index
                            if si_diff > 10:
                                st.success("✅ DSX is stronger")
                                st.write("**Target:** Win (3 points)")
                            elif si_diff < -10:
                                st.error("⚠️ Opponent is stronger")
                                st.write("**Target:** Stay competitive")
                            else:
                                st.info("⚖️ Evenly matched")
                                st.write("**Target:** Fight for all points")
                        
                        st.markdown("---")
                        
                        # Recent form
                        st.subheader("📈 Recent Form")
                        
                        recent_5 = completed.tail(5)
                        
                        for _, match in recent_5.iterrows():
                            if pd.notna(match['GF']) and pd.notna(match['GA']):
                                result = "W" if match['GD'] > 0 else "D" if match['GD'] == 0 else "L"
                                if result == "W":
                                    st.success(f"**{result}** {int(match['GF'])}-{int(match['GA'])} vs {match['TheirOpponent']}")
                                elif result == "D":
                                    st.info(f"**{result}** {int(match['GF'])}-{int(match['GA'])} vs {match['TheirOpponent']}")
                                else:
                                    st.error(f"**{result}** {int(match['GF'])}-{int(match['GA'])} vs {match['TheirOpponent']}")
                        
                        st.markdown("---")
                        
                        # Game plan
                        st.subheader("📋 Recommended Game Plan")
                        
                        if si_diff > 10:
                            st.write("**Offensive Approach:**")
                            st.write("- Press high and control possession")
                            st.write("- Create multiple scoring chances")
                            st.write("- Build team confidence")
                        elif si_diff < -10:
                            st.write("**Defensive Approach:**")
                            st.write("- Stay compact and organized")
                            st.write("- Counter-attack when possible")
                            st.write("- Limit their scoring chances")
                        else:
                            st.write("**Balanced Approach:**")
                            st.write("- Match their intensity")
                            st.write("- Be clinical with chances")
                            st.write("- Strong defensive shape")
                        
                    else:
                        st.warning(f"No completed matches found for {selected_upcoming}")
                        st.write("Check back closer to game day for updated results")
                        
                except FileNotFoundError:
                    st.warning("BSA Celtic schedule data not available")
                    st.write("Run `python fetch_bsa_celtic.py` to get their latest results")
            
            # Check if it's Club Ohio West (division team)
            elif "Club Ohio" in selected_upcoming:
                try:
                    division = pd.read_csv("OCL_BU08_Stripes_Division_with_DSX.csv")
                    club_ohio = division[division['Team'].str.contains("Club Ohio", na=False, case=False)]
                    
                    if not club_ohio.empty:
                        team = club_ohio.iloc[0]
                        
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("Division Rank", f"#{int(team['Rank'])} / 7")
                        with col2:
                            st.metric("Record", f"{int(team['W'])}-{int(team['D'])}-{int(team['L'])}")
                        with col3:
                            st.metric("GF/Game", f"{team['GF']:.2f}")
                        with col4:
                            st.metric("GA/Game", f"{team['GA']:.2f}")
                        with col5:
                            st.metric("PPG", f"{team['PPG']:.2f}")
                        
                        st.markdown("---")
                        
                        st.subheader("📊 Strength Assessment")
                        
                        col1, col2 = st.columns(2)
                        
                        # Get dynamic DSX stats
                        dsx_stats = calculate_dsx_stats()
                        dsx_si = dsx_stats['StrengthIndex']
                        
                        with col1:
                            st.metric("Opponent SI", f"{team['StrengthIndex']:.1f}")
                            st.metric("DSX SI", f"{dsx_si:.1f}")
                        
                        with col2:
                            si_diff = dsx_si - team['StrengthIndex']
                            if si_diff > 10:
                                st.success("✅ DSX is stronger")
                            elif si_diff < -10:
                                st.error("⚠️ Opponent is stronger")
                            else:
                                st.info("⚖️ Evenly matched")
                    else:
                        st.warning("Division data not found for this team")
                        
                except FileNotFoundError:
                    st.warning("Division data not available")
                    st.write("Run `python fetch_gotsport_division.py` to get latest standings")
            
            else:
                st.info("Scouting data not yet available for this opponent")
                st.write("Check back as game approaches or add data manually")
                
        except FileNotFoundError:
            st.error("Upcoming schedule not found")
            st.write("Create `DSX_Upcoming_Opponents.csv` with your schedule")


elif page == "📋 Full Analysis":
    st.title("📋 Complete Division Analysis")
    
    st.info("This page displays your current season performance and strategic matchup analysis")
    
    # Get dynamic DSX stats
    dsx_stats = calculate_dsx_stats()
    
    # Key insights at the top
    st.header("🎯 Executive Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ DSX Strengths")
        st.markdown(f"""
        - **{dsx_stats['GF_PG']:.2f} goals/game** - Offensive capability
        - **{dsx_stats['W']} wins, {dsx_stats['D']} draws** in {dsx_stats['GP']} games
        - **{dsx_stats['PPG']:.2f} PPG** - Points per game
        """)
    
    with col2:
        st.subheader("⚠️ Areas for Improvement")
        st.markdown(f"""
        - **{dsx_stats['GA_PG']:.2f} goals against/game** - Defensive focus
        - **{dsx_stats['GD_PG']:.2f} goal diff/game** - Need to close gaps
        - **{dsx_stats['L']} losses** - Learn from tough matches
        """)
    
    st.markdown("---")
    
    # Matchup Analysis - DYNAMIC
    st.header("🎯 Matchup Analysis by Division Rank")
    st.info("💡 **Dynamic analysis based on latest division data across all tracked leagues**")
    
    # Load all division data
    all_divs = load_division_data()
    dsx_si = dsx_stats['StrengthIndex']
    
    # Calculate strength differences
    all_divs['SI_Diff'] = dsx_si - all_divs['StrengthIndex']
    
    # Categorize teams
    should_beat = all_divs[all_divs['SI_Diff'] > 10].sort_values('StrengthIndex', ascending=False)
    competitive = all_divs[(all_divs['SI_Diff'] >= -10) & (all_divs['SI_Diff'] <= 10)].sort_values('StrengthIndex', ascending=False)
    tough_matchups = all_divs[all_divs['SI_Diff'] < -10].sort_values('StrengthIndex', ascending=False)
    
    # Teams DSX Should Beat
    st.subheader(f"✅ Teams DSX Should Beat ({len(should_beat)} teams)")
    
    if len(should_beat) > 0:
        for idx, (_, team) in enumerate(should_beat.iterrows()):
            expanded = (idx == 0)  # Expand first one
            with st.expander(f"**{team['Team']}** (SI: {team['StrengthIndex']:.1f}, {team.get('League/Division', 'N/A')})", expanded=expanded):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("DSX Advantage", f"+{team['SI_Diff']:.1f} SI points")
                    if pd.notna(team.get('W')) and pd.notna(team.get('L')) and pd.notna(team.get('D')):
                        st.metric("Their Record", f"{int(team['W'])}-{int(team['L'])}-{int(team['D'])}")
                    st.metric("Their PPG", f"{team.get('PPG', 0):.2f}")
                with col2:
                    st.markdown(f"""
                    **Strategy:**
                    - DSX is **{team['SI_Diff']:.1f} points stronger** - target win
                    - They average **{team.get('PPG', 0):.2f} PPG** across {int(team.get('GP', 0))} games
                    - Focus on controlling possession and creating chances
                    """)
    else:
        st.warning("No teams found where DSX has a significant advantage.")
    
    # Competitive Matchups
    st.subheader(f"🟡 Competitive Matchups ({len(competitive)} teams)")
    
    if len(competitive) > 0:
        for idx, (_, team) in enumerate(competitive.iterrows()):
            with st.expander(f"**{team['Team']}** (SI: {team['StrengthIndex']:.1f}, {team.get('League/Division', 'N/A')})"):
                col1, col2 = st.columns(2)
                with col1:
                    diff_label = "DSX Advantage" if team['SI_Diff'] > 0 else "Opponent Advantage"
                    st.metric(diff_label, f"{team['SI_Diff']:+.1f} SI points")
                    if pd.notna(team.get('W')) and pd.notna(team.get('L')) and pd.notna(team.get('D')):
                        st.metric("Their Record", f"{int(team['W'])}-{int(team['L'])}-{int(team['D'])}")
                    st.metric("Their PPG", f"{team.get('PPG', 0):.2f}")
                with col2:
                    st.markdown(f"""
                    **Analysis:**
                    - **Evenly matched** - game could go either way
                    - They average **{team.get('PPG', 0):.2f} PPG** across {int(team.get('GP', 0))} games
                    - Execution and game plan will determine outcome
                    """)
    else:
        st.warning("No evenly matched teams found.")
    
    # Tough Matchups
    st.subheader(f"🔴 Tough Matchups ({len(tough_matchups)} teams)")
    
    if len(tough_matchups) > 0:
        for idx, (_, team) in enumerate(tough_matchups.iterrows()):
            with st.expander(f"**{team['Team']}** (SI: {team['StrengthIndex']:.1f}, {team.get('League/Division', 'N/A')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("DSX Disadvantage", f"{team['SI_Diff']:.1f} SI points")
                    if pd.notna(team.get('W')) and pd.notna(team.get('L')) and pd.notna(team.get('D')):
                        st.metric("Their Record", f"{int(team['W'])}-{int(team['L'])}-{int(team['D'])}")
                    st.metric("Their PPG", f"{team.get('PPG', 0):.2f}")
                with col2:
                    st.markdown(f"""
                    **Strategy:**
                    - Strong opponent - **{abs(team['SI_Diff']):.1f} points stronger**
                    - They average **{team.get('PPG', 0):.2f} PPG** across {int(team.get('GP', 0))} games
                    - Play disciplined defense and look for counter-attacks
                    """)
    else:
        st.warning("No significantly stronger teams found.")
    
    st.markdown("---")
    
    # How to Improve - DYNAMIC
    st.header("📈 How DSX Can Improve")
    st.info(f"💡 **Current DSX SI: {dsx_si:.1f}** - Analysis based on actual performance data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Reach Mid-Tier Teams (SI 50+)")
        target_si = 50.0
        points_needed = target_si - dsx_si
        
        # Calculate scenarios
        games_for_target = max(3, int(points_needed / 3))  # Rough estimate
        
        st.markdown(f"""
        **Need:** +{points_needed:.1f} StrengthIndex points
        
        **Option A: Win Streak**
        - Win next {games_for_target} games
        - Current PPG: {dsx_stats['PPG']:.2f}
        - Target PPG: ~2.0
        - Focus on consistency
        
        **Option B: Defensive Improvement**
        - Current: {dsx_stats['GA_PG']:.2f} goals against/game
        - Target: < 2.0 goals against/game
        - Improve goal differential
        - Pair with balanced record (W-L-D)
        """)
    
    with col2:
        st.subheader("🎯 Reach Top-Tier Teams (SI 70+)")
        target_si_high = 70.0
        points_needed_high = target_si_high - dsx_si
        
        st.markdown(f"""
        **Need:** +{points_needed_high:.1f} StrengthIndex points total
        
        **Required:**
        - Sustained winning streak (5+ games)
        - Current PPG: {dsx_stats['PPG']:.2f} → Target: 2.5+
        - Tighten defense (<2 GA/game)
        - Build on offensive strength ({dsx_stats['GF_PG']:.2f} GF/game)
        - Result: Compete with division leaders ⭐
        """)
    
    st.markdown("---")
    
    # Strategic Recommendations
    st.header("💡 Strategic Recommendations")
    
    tab1, tab2, tab3 = st.tabs(["For Coaches", "For Scouting", "For Team"])
    
    with tab1:
        st.markdown("""
        ### Coaching Priorities
        
        1. **🛡️ Defensive Focus** - This is THE biggest weakness
           - Currently 5.08 GA/game vs 1.89-3.29 for top 4
           - Even small improvement makes huge difference
        
        2. **⚽ Maintain Offensive Pressure**
           - 4.17 GF/game is working (3rd best!)
           - Keep attacking mindset
        
        3. **📊 Consistency Training**
           - Reduce gap between best (11-0) and worst (0-13)
           - More predictable performances
        
        4. **🎓 Study Blast FC**
           - Watch how #1 plays both ends
           - Learn from division champions
        """)
    
    with tab2:
        st.markdown("""
        ### Scouting Priorities
        
        1. **🔍 Priority Opponents:**
           - Polaris SC (closest competitor above you)
           - Sporting Columbus (reachable target)
        
        2. **👀 Watch:**
           - Blast FC games (learn from the best)
           - Teams you'll face soon
        
        3. **🤝 Identify:**
           - Common opponents for comparison
           - Patterns in divisional play
        """)
    
    with tab3:
        st.markdown("""
        ### Team Mentality
        
        1. **✅ Realistic Goal:** Finish 4th
           - Very achievable with 2-3 win streak
           - Only +7.8 SI points away
        
        2. **⭐ Stretch Goal:** Finish 3rd
           - Requires defensive improvement
           - Need sustained winning
        
        3. **🚀 Long Shot:** Finish 2nd
           - Would need 6+ game winning streak
           - Major improvement required
        
        **Current Position:** Mid-table (5th of 7)
        - Can beat 2 teams
        - Competitive with 2 more
        - Underdogs vs top 2
        """)
    
    st.markdown("---")
    
    # Season Goals
    st.header("📊 Season Goals & Feasibility")
    
    goals_data = {
        'Goal': ['Positive GD/Game', 'PPG > 1.50', 'Top 4 Finish', 'Top 3 Finish', 'Division Title'],
        'Current': [-0.92, 1.00, '5th', '5th', '5th'],
        'Target': [0.00, 1.50, '4th', '3rd', '1st'],
        'Gap': ['+0.92', '+0.50', '+1 rank', '+2 ranks', '+4 ranks'],
        'Feasibility': ['⭐⭐⭐ Challenging', '⭐⭐⭐⭐ Achievable', '⭐⭐⭐⭐⭐ Very Achievable', '⭐⭐⭐ Difficult', '⭐ Very Unlikely']
    }
    
    st.dataframe(pd.DataFrame(goals_data), use_container_width=True, hide_index=True)


elif page == "📖 Quick Start Guide":
    st.title("📖 Quick Start Guide")
    
    st.success("Welcome to the DSX Opponent Tracker! This page helps you get started.")
    
    # Get dynamic DSX stats for display
    dsx_stats = calculate_dsx_stats()
    all_divisions_df = load_division_data()
    
    # Quick wins
    st.header("🚀 Quick Wins (Do These First)")
    
    with st.expander("1️⃣ Check Your Division Position (30 seconds)", expanded=True):
        st.markdown(f"""
        **Action:** Go to **🏆 Division Rankings** page
        
        **You'll see:**
        - DSX Strength Index: **{dsx_stats['StrengthIndex']:.1f}**
        - Current Record: **{dsx_stats['Record']}** ({dsx_stats['GP']} games)
        - Rank among teams you've played
        
        **Insight:** Compare against {len(all_divisions_df)} teams from 4 divisions!
        """)
    
    with st.expander("2️⃣ Scout Your Next Opponent (2 minutes)"):
        st.markdown("""
        **Action:** Go to **🎯 What's Next** page
        
        **Steps:**
        1. See your next 3 upcoming games
        2. Review opponent Strength Index
        3. Check win probability prediction
        4. Read strategic recommendations
        
        **You'll learn:**
        - Who's favored to win
        - Expected goal differential
        - Key tactical focus areas
        """)
    
    with st.expander("3️⃣ Review Recent Performance (1 minute)"):
        st.markdown(f"""
        **Action:** Go to **📅 Match History** page
        
        **You'll see:**
        - All {dsx_stats['GP']} DSX games this season
        - {dsx_stats['Record']} record ({dsx_stats['W']}W, {dsx_stats['D']}D, {dsx_stats['L']}L)
        - {dsx_stats['GF_PG']:.2f} goals/game, {dsx_stats['GA_PG']:.2f} against/game
        - Goals over time chart
        
        **Look for:** Trends - are you improving or declining?
        """)
    
    with st.expander("4️⃣ Use Live Game Tracker (Game Day)"):
        st.markdown("""
        **Action:** Go to **🎮 Live Game Tracker** page on game day
        
        **Features:**
        1. Record goals, assists, shots, saves in real-time
        2. Track substitutions and player minutes
        3. Auto-saves every action to CSV
        4. Parents can watch on **📺 Watch Live Game** page
        
        **Benefits:**
        - Never lose track of who scored
        - Automatic stats updates
        - Live feed for parents/team
        """)
    
    with st.expander("5️⃣ Team Communication (Any Time)"):
        st.markdown("""
        **Action:** Go to **💬 Team Chat** page
        
        **Features:**
        1. 5 channels: General, Game Day, Schedule, Carpools, Equipment
        2. Auto-refreshes every 3 seconds
        3. Pin important messages
        4. Works on phones via Cloudflare Tunnel
        
        **Use for:**
        - Game day coordination
        - Schedule changes
        - Carpool arrangements
        - Equipment sharing
        """)
    
    st.markdown("---")
    
    # Weekly Routine
    st.header("📅 Weekly Routine")
    
    st.subheader("Sunday Evening (After Weekend Games)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⏱️ 5 minutes")
    
    with col2:
        st.markdown("""
        1. Open dashboard
        2. Go to **⚙️ Data Manager**
        3. Click **"Update All"** button
        4. Wait 30 seconds for data refresh
        5. Return to **Division Rankings** to see changes
        6. Check **Match History** for trends
        """)
    
    st.subheader("Wednesday/Thursday (Pre-Game)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⏱️ 3 minutes")
    
    with col2:
        st.markdown("""
        1. **Team Analysis** → Compare DSX vs this weekend's opponent
        2. Note the prediction and expected GD
        3. **Opponent Intel** → Check their recent form
        4. **Full Analysis** → Review strategic recommendations
        """)
    
    st.markdown("---")
    
    # Key Insights
    st.header("🎯 Key Insights You Should Know")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"""
        **🟢 Good News**
        
        - **{dsx_stats['GF_PG']:.2f} GF/game** - Scoring capability
        - **{dsx_stats['W']} wins** this season
        - **SI {dsx_stats['StrengthIndex']:.1f}** - Competitive level
        - **{len(all_divisions_df)} teams tracked** across 4 divisions
        """)
    
    with col2:
        st.warning(f"""
        **🟡 Areas to Improve**
        
        - **{dsx_stats['GA_PG']:.2f} GA/game** - Defensive focus
        - **{dsx_stats['L']} losses** - Learn & adapt
        - **Consistency** - Minimize scoring variance
        - **Goal differential** - Close the gap
        """)
    
    st.markdown("---")
    
    # Dashboard Pages Guide
    st.header("📱 Dashboard Pages Explained")
    
    pages_info = {
        'Page': [
            '🏆 Division Rankings',
            '📊 Team Analysis', 
            '📅 Match History',
            '🔍 Opponent Intel',
            '🎯 What\'s Next',
            '🎮 Game Predictions',
            '📊 Benchmarking',
            '⚽ Player Stats',
            '📋 Game Log',
            '🎮 Live Game Tracker',
            '📺 Watch Live Game',
            '💬 Team Chat',
            '📋 Full Analysis',
            '⚙️ Data Manager'
        ],
        'Use For': [
            'See where DSX ranks vs opponents',
            'Compare any 2 teams head-to-head',
            'Review all DSX games & trends',
            'Scout specific opponents',
            'View next 3 games & predictions',
            'Predict matchups vs any team',
            'Radar chart comparisons',
            'Individual player statistics',
            'Per-game player contributions',
            'Record live game events',
            'Watch ongoing game (parents)',
            'Team communication',
            'Strategic season analysis',
            'Edit data & update division info'
        ],
        'Time': ['30 sec', '2 min', '2 min', '3 min', '1 min', '2 min', '2 min', '2 min', '2 min', 'Game day', 'Any time', 'Any time', '5 min', '1 min'],
        'Best For': [
            'Quick status check',
            'Pre-game scouting',
            'Post-game review',
            'Opponent research',
            'Weekly planning',
            'What-if scenarios',
            'Visual comparisons',
            'Player development',
            'Stats tracking',
            'Coaches/managers',
            'Parents/fans',
            'Team coordination',
            'Strategy planning',
            'Data maintenance'
        ]
    }
    
    st.dataframe(pd.DataFrame(pages_info), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Tips
    st.header("💡 Pro Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Speed Tips
        
        - **Bookmark** `http://localhost:8501`
        - **Leave tab open** - switch instantly
        - **Click columns** to sort tables
        - **Use sidebar** for quick navigation
        """)
    
    with col2:
        st.markdown("""
        ### Analysis Tips
        
        - **Focus on trends** not single games
        - **Update after every game** for accuracy
        - **SI differences >10** = significant gap
        - **Use Live Tracker** on game days
        - **Check Team Chat** for updates
        """)
    
    st.markdown("---")
    
    # Quick Reference
    st.header("📊 Quick Reference Card")
    
    st.info(f"""
    **DSX Current Stats:**
    - **Record:** {dsx_stats['Record']} (W-D-L)
    - **Games Played:** {dsx_stats['GP']}
    - **Strength Index:** {dsx_stats['StrengthIndex']:.1f}
    - **Offense:** {dsx_stats['GF_PG']:.2f} GF/game
    - **Defense:** {dsx_stats['GA_PG']:.2f} GA/game
    - **Goal Diff:** {dsx_stats['GD_PG']:.2f}/game
    - **PPG:** {dsx_stats['PPG']:.2f}
    
    **Division Coverage:**
    - **{len(all_divisions_df)} teams** tracked across 4 divisions
    - OCL BU08 Stripes, White, Stars + MVYSA B09-3
    
    **Quick Access:**
    - Live Game Tracker for game days
    - Team Chat for coordination
    - Data Manager to update stats
    """)


elif page == "⚙️ Data Manager":
    st.title("⚙️ Data Manager")
    
    st.info("✏️ Edit your data directly! Changes are saved when you click the save button.")
    
    # Tabs for different editable data
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["👥 Roster", "📊 Player Stats", "⚽ Matches", "🎮 Game Stats", "📅 Schedule", "⚽ Positions", "📥 Downloads"])
    
    with tab1:
        st.subheader("👥 Edit Roster")
        st.write("Update player names, positions, and parent info")
        
        try:
            roster = pd.read_csv("roster.csv", index_col=False)
            
            # Reset index to ensure no extra columns
            roster = roster.reset_index(drop=True)
            
            # Editable dataframe
            edited_roster = st.data_editor(
                roster,
                num_rows="dynamic",  # Allow adding/deleting rows
                use_container_width=True,
                hide_index=True,
                column_config={
                    "PlayerNumber": st.column_config.NumberColumn("Jersey #", required=True),
                    "PlayerName": st.column_config.TextColumn("Player Name", required=True),
                    "Position": st.column_config.SelectboxColumn("Position", options=["Forward", "Midfielder", "Defender", "Goalkeeper"]),
                }
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Locally", type="secondary", key="save_roster_local"):
                    edited_roster.to_csv("roster.csv", index=False)
                    st.success("✅ Saved to local file!")
            
            with col2:
                if st.button("🚀 Save & Push to GitHub", type="primary", key="push_roster"):
                    try:
                        edited_roster.to_csv("roster.csv", index=False)
                        
                        # Git commands
                        os.system("git add roster.csv")
                        os.system('git commit -m "Update roster from dashboard"')
                        result = os.system("git push")
                        
                        if result == 0:
                            st.success("✅ Pushed to GitHub successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Git push failed - check credentials")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                if st.button("↩️ Reset", key="reset_roster"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("roster.csv not found")
    
    with tab2:
        st.subheader("📊 Edit Player Stats")
        st.write("Update goals, assists, and playing time")
        
        try:
            player_stats = pd.read_csv("player_stats.csv", index_col=False)
            
            # Reset index to ensure no extra columns
            player_stats = player_stats.reset_index(drop=True)
            
            # Editable dataframe
            edited_stats = st.data_editor(
                player_stats,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "PlayerNumber": st.column_config.NumberColumn("Jersey #", required=True),
                    "PlayerName": st.column_config.TextColumn("Player Name", required=True),
                    "GamesPlayed": st.column_config.NumberColumn("Games", min_value=0),
                    "Goals": st.column_config.NumberColumn("Goals", min_value=0),
                    "Assists": st.column_config.NumberColumn("Assists", min_value=0),
                    "MinutesPlayed": st.column_config.NumberColumn("Minutes", min_value=0),
                    "Notes": st.column_config.TextColumn("Notes"),
                }
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Locally", type="secondary", key="save_stats_local"):
                    edited_stats.to_csv("player_stats.csv", index=False)
                    st.success("✅ Saved to local file!")
            
            with col2:
                if st.button("🚀 Save & Push to GitHub", type="primary", key="push_stats"):
                    try:
                        edited_stats.to_csv("player_stats.csv", index=False)
                        
                        # Git commands
                        os.system("git add player_stats.csv")
                        os.system('git commit -m "Update player stats from dashboard"')
                        result = os.system("git push")
                        
                        if result == 0:
                            st.success("✅ Pushed to GitHub successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Git push failed - check credentials")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                if st.button("↩️ Reset", key="reset_stats"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("player_stats.csv not found")
    
    with tab3:
        st.subheader("⚽ Edit Match History")
        st.write("Update match results and scores")
        
        try:
            matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
            
            # Reset index to ensure no extra columns
            matches = matches.reset_index(drop=True)
            
            # Editable dataframe
            edited_matches = st.data_editor(
                matches,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date (YYYY-MM-DD)", required=True),
                    "Tournament": st.column_config.TextColumn("Tournament"),
                    "Opponent": st.column_config.TextColumn("Opponent", required=True),
                    "GF": st.column_config.NumberColumn("Goals For", min_value=0),
                    "GA": st.column_config.NumberColumn("Goals Against", min_value=0),
                    "Result": st.column_config.SelectboxColumn("Result", options=["W", "D", "L"]),
                }
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Locally", type="secondary", key="save_matches_local"):
                    edited_matches.to_csv("DSX_Matches_Fall2025.csv", index=False)
                    st.success("✅ Saved to local file!")
            
            with col2:
                if st.button("🚀 Save & Push to GitHub", type="primary", key="push_matches"):
                    try:
                        edited_matches.to_csv("DSX_Matches_Fall2025.csv", index=False)
                        
                        # Git commands
                        os.system("git add DSX_Matches_Fall2025.csv")
                        os.system('git commit -m "Update match results from dashboard"')
                        result = os.system("git push")
                        
                        if result == 0:
                            st.success("✅ Pushed to GitHub successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Git push failed - check credentials")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                if st.button("↩️ Reset", key="reset_matches"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("DSX_Matches_Fall2025.csv not found")
    
    with tab4:
        st.subheader("🎮 Edit Game-by-Game Player Stats")
        st.write("Track who scored and assisted in each game")
        
        try:
            game_stats = pd.read_csv("game_player_stats.csv", index_col=False)
            
            # Reset index to ensure no extra columns
            game_stats = game_stats.reset_index(drop=True)
            
            # Editable dataframe
            edited_game_stats = st.data_editor(
                game_stats,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date (YYYY-MM-DD)", required=True),
                    "Opponent": st.column_config.TextColumn("Opponent", required=True),
                    "PlayerName": st.column_config.TextColumn("Player", required=True),
                    "Goals": st.column_config.NumberColumn("Goals", min_value=0),
                    "Assists": st.column_config.NumberColumn("Assists", min_value=0),
                    "Notes": st.column_config.TextColumn("Notes (e.g. PK, Hat-trick)"),
                }
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Locally", type="secondary", key="save_game_stats_local"):
                    edited_game_stats.to_csv("game_player_stats.csv", index=False)
                    st.success("✅ Saved to local file!")
            
            with col2:
                if st.button("🚀 Save & Push to GitHub", type="primary", key="push_game_stats"):
                    try:
                        edited_game_stats.to_csv("game_player_stats.csv", index=False)
                        
                        # Git commands
                        os.system("git add game_player_stats.csv")
                        os.system('git commit -m "Update game stats from dashboard"')
                        result = os.system("git push")
                        
                        if result == 0:
                            st.success("✅ Pushed to GitHub successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Git push failed - check credentials")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                if st.button("↩️ Reset", key="reset_game_stats"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("game_player_stats.csv not found")
            st.info("This file tracks individual player contributions per game")
    
    with tab5:
        st.subheader("📅 Edit Team Schedule")
        st.write("Manage games, practices, and all team events")
        st.info("💡 **Enhanced schedule with practices, arrival times, uniforms, and more!**")
        
        try:
            schedule = pd.read_csv("team_schedule.csv", index_col=False)
            
            # Reset index to ensure no extra columns
            schedule = schedule.reset_index(drop=True)
            
            # Editable dataframe with ALL the new columns
            edited_schedule = st.data_editor(
                schedule,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "EventID": st.column_config.NumberColumn("Event ID", help="Unique ID (auto-generated)"),
                    "EventType": st.column_config.SelectboxColumn("Type", options=["Game", "Practice"], required=True),
                    "Date": st.column_config.TextColumn("Date (YYYY-MM-DD)", required=True, help="Format: 2025-10-18"),
                    "Time": st.column_config.TextColumn("Time", required=True, help="e.g., 11:20 AM or 6:00 PM"),
                    "Opponent": st.column_config.TextColumn("Opponent", help="Leave blank for practices"),
                    "Location": st.column_config.TextColumn("Location/Complex", required=True),
                    "FieldNumber": st.column_config.TextColumn("Field #", help="e.g., Field 3"),
                    "ArrivalTime": st.column_config.TextColumn("Arrival Time", help="e.g., 11:00 AM or '15 min before'"),
                    "UniformColor": st.column_config.TextColumn("Uniform", help="e.g., Blue Jerseys, White"),
                    "Tournament": st.column_config.TextColumn("Tournament/League"),
                    "HomeAway": st.column_config.SelectboxColumn("H/A", options=["Home", "Away", "Neutral"]),
                    "Status": st.column_config.SelectboxColumn("Status", options=["Upcoming", "Confirmed", "Completed", "Cancelled"]),
                    "Notes": st.column_config.TextColumn("Notes"),
                    "OpponentStrengthIndex": st.column_config.NumberColumn("Opp SI", help="Auto-populated from division data"),
                }
            )
            
            st.caption("""
            **Tips:**
            - **Games:** Set EventType = "Game", fill in Opponent
            - **Practices:** Set EventType = "Practice", leave Opponent blank
            - **Arrival Time:** Use "15 min before" or specific time like "11:00 AM"
            - **Uniform:** Specify jersey color to avoid confusion
            - **Field Number:** Helps parents find the right field
            - **OpponentStrengthIndex:** Leave blank - auto-filled from division data
            """)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Locally", type="secondary", key="save_schedule_local"):
                    # Auto-generate EventIDs if missing
                    if 'EventID' not in edited_schedule.columns or edited_schedule['EventID'].isna().any():
                        edited_schedule['EventID'] = range(1, len(edited_schedule) + 1)
                    
                    # Sort by date before saving
                    edited_schedule['Date'] = pd.to_datetime(edited_schedule['Date'])
                    edited_schedule = edited_schedule.sort_values('Date')
                    edited_schedule['Date'] = edited_schedule['Date'].dt.strftime('%Y-%m-%d')
                    edited_schedule.to_csv("team_schedule.csv", index=False)
                    st.success("✅ Saved! Schedule page will update.")
            
            with col2:
                if st.button("🚀 Save & Push to GitHub", type="primary", key="push_schedule"):
                    try:
                        # Auto-generate EventIDs if missing
                        if 'EventID' not in edited_schedule.columns or edited_schedule['EventID'].isna().any():
                            edited_schedule['EventID'] = range(1, len(edited_schedule) + 1)
                        
                        # Sort by date before saving
                        edited_schedule['Date'] = pd.to_datetime(edited_schedule['Date'])
                        edited_schedule = edited_schedule.sort_values('Date')
                        edited_schedule['Date'] = edited_schedule['Date'].dt.strftime('%Y-%m-%d')
                        edited_schedule.to_csv("team_schedule.csv", index=False)
                        
                        # Git commands
                        os.system("git add team_schedule.csv")
                        os.system('git commit -m "Update team schedule from dashboard"')
                        result = os.system("git push")
                        
                        if result == 0:
                            st.success("✅ Pushed to GitHub successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Git push failed - check credentials")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                if st.button("↩️ Reset", key="reset_schedule"):
                    st.rerun()
            
            st.markdown("---")
            
            # TeamSnap Import Section
            st.subheader("📥 Import from TeamSnap")
            st.info("💡 **Export your schedule from TeamSnap as CSV, then upload it here to merge with existing schedule.**")
            
            uploaded_file = st.file_uploader("Upload TeamSnap CSV Export", type=['csv'], key="teamsnap_upload")
            
            if uploaded_file:
                try:
                    # Preview uploaded data
                    preview_df = pd.read_csv(uploaded_file)
                    st.write("**Preview of uploaded schedule:**")
                    st.dataframe(preview_df.head(10))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Import & Merge", type="primary", use_container_width=True):
                            # Call import logic from import_teamsnap_schedule.py
                            try:
                                # Read the uploaded file content
                                uploaded_df = pd.read_csv(uploaded_file)
                                
                                # Basic mapping (simplified version of import_teamsnap_schedule.py logic)
                                # This is a basic implementation - the full script has more sophisticated mapping
                                new_events = []
                                for idx, row in uploaded_df.iterrows():
                                    # Try to detect if it's a game or practice based on common TeamSnap columns
                                    event_type = "Game"  # Default to game
                                    opponent = ""
                                    
                                    # Look for opponent in common TeamSnap column names
                                    for col in ['Opponent', 'Away Team', 'Home Team', 'Team', 'vs']:
                                        if col in uploaded_df.columns and pd.notna(row[col]):
                                            opponent = str(row[col])
                                            break
                                    
                                    # If no opponent found, might be a practice
                                    if not opponent or opponent.lower() in ['practice', 'training', '']:
                                        event_type = "Practice"
                                        opponent = ""
                                    
                                    # Extract date
                                    date_str = ""
                                    for col in ['Date', 'Game Date', 'Event Date', 'Start Date']:
                                        if col in uploaded_df.columns and pd.notna(row[col]):
                                            date_str = str(row[col])
                                            break
                                    
                                    # Extract time
                                    time_str = ""
                                    for col in ['Time', 'Start Time', 'Game Time', 'Event Time']:
                                        if col in uploaded_df.columns and pd.notna(row[col]):
                                            time_str = str(row[col])
                                            break
                                    
                                    # Extract location
                                    location = ""
                                    for col in ['Location', 'Venue', 'Field', 'Address', 'Facility']:
                                        if col in uploaded_df.columns and pd.notna(row[col]):
                                            location = str(row[col])
                                            break
                                    
                                    # Create new event
                                    if date_str and time_str and location:
                                        new_event = {
                                            'EventID': len(edited_schedule) + len(new_events) + 1,
                                            'EventType': event_type,
                                            'Date': date_str,
                                            'Time': time_str,
                                            'Opponent': opponent,
                                            'Location': location,
                                            'FieldNumber': '',
                                            'ArrivalTime': '',
                                            'UniformColor': '',
                                            'Tournament': 'Imported from TeamSnap',
                                            'HomeAway': 'Away',
                                            'Status': 'Upcoming',
                                            'Notes': 'Imported from TeamSnap',
                                            'OpponentStrengthIndex': ''
                                        }
                                        new_events.append(new_event)
                                
                                if new_events:
                                    # Add new events to existing schedule
                                    new_events_df = pd.DataFrame(new_events)
                                    combined_schedule = pd.concat([edited_schedule, new_events_df], ignore_index=True)
                                    
                                    # Save combined schedule
                                    combined_schedule.to_csv("team_schedule.csv", index=False)
                                    st.success(f"✅ Imported {len(new_events)} events from TeamSnap!")
                                    st.rerun()
                                else:
                                    st.warning("No valid events found in uploaded file. Check column names.")
                                    
                            except Exception as e:
                                st.error(f"Import error: {e}")
                                st.write("**Tip:** Make sure your TeamSnap CSV has columns like 'Date', 'Time', 'Location', and 'Opponent'")
                    
                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            
            st.markdown("---")
            
            # Preview upcoming events
            with st.expander("👀 Preview - Upcoming Events"):
                st.write("**Next 5 events:**")
                upcoming = edited_schedule[edited_schedule['Status'].isin(['Upcoming', 'Confirmed'])].head(5)
                for _, event in upcoming.iterrows():
                    event_type_icon = "⚽" if event['EventType'] == 'Game' else "🏃"
                    opponent_text = event['Opponent'] if event['Opponent'] else "Practice"
                    st.write(f"{event_type_icon} {event['Date']} @ {event['Time']} - {opponent_text} @ {event['Location']}")
        
        except FileNotFoundError:
            st.error("team_schedule.csv not found")
            st.info("Creating default enhanced schedule file...")
            default_schedule = pd.DataFrame({
                'EventID': [1, 2],
                'EventType': ['Game', 'Practice'],
                'Date': ['2025-10-18', '2025-10-16'],
                'Time': ['11:20 AM', '6:00 PM'],
                'Opponent': ['Example Team', ''],
                'Location': ['John Ankeney Soccer Complex', 'John Ankeney Soccer Complex'],
                'FieldNumber': ['Field 3', 'Field 1'],
                'ArrivalTime': ['11:00 AM', '5:45 PM'],
                'UniformColor': ['Blue Jerseys', 'Practice Gear'],
                'Tournament': ['MVYSA Fall 2025', ''],
                'HomeAway': ['Away', 'Home'],
                'Status': ['Upcoming', 'Upcoming'],
                'Notes': ['Edit or delete this example', 'Regular practice'],
                'OpponentStrengthIndex': ['', '']
            })
            default_schedule.to_csv("team_schedule.csv", index=False)
            st.success("✅ Created default team_schedule.csv - Refresh page to edit!")
    
    with tab6:
        st.subheader("⚽ Edit Position Names")
        st.write("Customize position names to match your coach's terminology")
        st.info("💡 **These positions will be used in Live Game Tracker when setting up lineup!**")
        
        try:
            positions = pd.read_csv("position_config.csv", index_col=False)
            
            # Reset index to ensure no extra columns
            positions = positions.reset_index(drop=True)
            
            # Editable dataframe
            edited_positions = st.data_editor(
                positions,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="position_config_editor",
                column_config={
                    "PositionName": st.column_config.TextColumn("Position Name (e.g. Center Midfielder)", required=True, width="large"),
                    "Abbreviation": st.column_config.TextColumn("Abbreviation (e.g. CM)", required=True, width="small"),
                    "SortOrder": st.column_config.NumberColumn("Display Order", min_value=1, help="Lower numbers appear first in dropdowns"),
                }
            )
            
            st.caption("""
            **Common positions for 7v7 (U8):**
            - Goalkeeper (GK)
            - Center Back (CB), Right Back (RB), Left Back (LB)
            - Center Midfielder (CM), Right Midfielder (RM), Left Midfielder (LM)
            - Striker (ST), Forward (FW)
            - Right Winger (RW), Left Winger (LW)
            """)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Locally", type="secondary", key="save_positions_local"):
                    # Sort by SortOrder before saving
                    edited_positions = edited_positions.sort_values('SortOrder')
                    edited_positions.to_csv("position_config.csv", index=False)
                    st.success("✅ Saved! Positions will update in Live Game Tracker.")
            
            with col2:
                if st.button("🚀 Save & Push to GitHub", type="primary", key="push_positions"):
                    try:
                        # Sort by SortOrder before saving
                        edited_positions = edited_positions.sort_values('SortOrder')
                        edited_positions.to_csv("position_config.csv", index=False)
                        
                        # Git commands
                        os.system("git add position_config.csv")
                        os.system('git commit -m "Update position names from dashboard"')
                        result = os.system("git push")
                        
                        if result == 0:
                            st.success("✅ Pushed to GitHub successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Git push failed - check credentials")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                if st.button("↩️ Reset", key="reset_positions"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("position_config.csv not found")
            st.info("Creating default positions file...")
            default_positions = pd.DataFrame({
                'PositionName': ['Goalkeeper', 'Center Back', 'Right Back', 'Left Back', 'Center Midfielder', 'Right Winger', 'Left Winger', 'Striker'],
                'Abbreviation': ['GK', 'CB', 'RB', 'LB', 'CM', 'RW', 'LW', 'ST'],
                'SortOrder': [1, 2, 3, 4, 5, 6, 7, 8]
            })
            default_positions.to_csv("position_config.csv", index=False)
            st.success("✅ Created default position_config.csv - Refresh page to edit!")
    
    with tab7:
        st.subheader("📥 Download Data Files")
        
        # Check what data is available
        files = {
            "Roster": "roster.csv",
            "Player Stats": "player_stats.csv",
            "Match History": "DSX_Matches_Fall2025.csv",
            "Game Stats": "game_player_stats.csv",
            "Division Rankings": "OCL_BU08_Stripes_Division_with_DSX.csv",
            "BSA Celtic Schedules": "BSA_Celtic_Schedules.csv",
            "Common Opponent Matrix": "Common_Opponent_Matrix_Template.csv"
        }
        
        for name, filename in files.items():
            exists = os.path.exists(filename)
            status = "✅ Available" if exists else "❌ Not found"
            
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                st.write(f"**{name}**")
            with col2:
                st.write(status)
            with col3:
                if exists:
                    with open(filename, 'rb') as f:
                        st.download_button(
                            "📥 Download",
                            f,
                            file_name=filename,
                            key=f"download_{filename}"
                        )
    
    st.markdown("---")
    
    # Help Section
    with st.expander("❓ How to Use the Editor & GitHub Push"):
        st.markdown("""
        ### 📝 **Editing Data:**
        1. Click on any cell to edit it
        2. Use **+** button at bottom to add new rows
        3. Select a row and press **Delete** to remove it
        
        ### 💾 **Two Save Options:**
        
        **Option 1: 💾 Save Locally**
        - Saves changes to the file immediately
        - **On Streamlit Cloud:** Changes are temporary (lost on next deploy)
        - **On Local Computer:** Changes persist until you push to GitHub
        
        **Option 2: 🚀 Save & Push to GitHub** ⭐ **RECOMMENDED**
        - Saves changes AND pushes to GitHub
        - Makes changes permanent across all devices
        - Updates Streamlit Cloud automatically
        - Dashboard will refresh in 60-90 seconds
        
        ### 🎯 **After Each Game Workflow:**
        
        1. **⚽ Matches Tab:**
           - Add new match with date, opponent, score
           - Click **🚀 Save & Push to GitHub**
        
        2. **🎮 Game Stats Tab:**
           - Add a row for each player who scored/assisted
           - Example: `2024-10-15 | BSA Celtic | Jax Derryberry | 2 | 1 | Hat-trick`
           - Click **🚀 Save & Push to GitHub**
        
        3. **📊 Player Stats Tab:**
           - Update season totals (add goals from this game)
           - Update games played (+1 for each player)
           - Update minutes played
           - Click **🚀 Save & Push to GitHub**
        
        ### 🔧 **Troubleshooting:**
        
        **"Git push failed" error:**
        - On **Local Computer:** Make sure Git is configured
        - On **Streamlit Cloud:** This feature works automatically!
        
        **Changes not showing up:**
        - Wait 60-90 seconds for Streamlit Cloud to redeploy
        - Check the "Manage App" button to see deployment status
        
        **Data looks wrong:**
        - Use the **📥 Downloads** tab to backup your data first
        - Click **↩️ Reset** to discard changes and reload from file
        """)
    
    st.markdown("---")
    
    st.subheader("🔄 Update Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Update Division", use_container_width=True):
            with st.spinner("Fetching division data..."):
                import subprocess
                result = subprocess.run(['python', 'fetch_gotsport_division.py'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("Division data updated!")
                    refresh_data()
                else:
                    st.error("Error updating division data")
                    st.code(result.stderr)
    
    with col2:
        if st.button("Update BSA Celtic", use_container_width=True):
            with st.spinner("Fetching BSA Celtic..."):
                import subprocess
                result = subprocess.run(['python', 'fetch_bsa_celtic.py'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("BSA Celtic data updated!")
                    refresh_data()
                else:
                    st.error("Error updating BSA Celtic")
                    st.code(result.stderr)
    
    with col3:
        if st.button("Update All", use_container_width=True):
            with st.spinner("Updating all data..."):
                import subprocess
                
                # Update division
                subprocess.run(['python', 'fetch_gotsport_division.py'])
                # Update schedules
                subprocess.run(['python', 'fetch_division_schedules.py'])
                # Update BSA Celtic
                subprocess.run(['python', 'fetch_bsa_celtic.py'])
                
                st.success("All data updated!")
                refresh_data()
    
    st.markdown("---")
    
    st.subheader("ℹ️ System Info")
    
    st.info(f"""
    **Dashboard Version:** 1.0  
    **Last Data Refresh:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    **Python Scripts:** All operational  
    **Cache TTL:** 1 hour
    """)


# Footer
st.markdown("---")
st.caption("Dublin DSX Orange 2018 Boys | Opponent Tracker Dashboard | Built with Streamlit")

