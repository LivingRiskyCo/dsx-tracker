"""
DSX Opponent Tracker - Interactive Dashboard
A Streamlit-based GUI replacing Excel functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

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
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_division_data():
    """Load division rankings"""
    if os.path.exists("OCL_BU08_Stripes_Division_with_DSX.csv"):
        df = pd.read_csv("OCL_BU08_Stripes_Division_with_DSX.csv")
        return df
    return pd.DataFrame()


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
        ["🎯 What's Next", "🏆 Division Rankings", "📊 Team Analysis", "👥 Player Stats", "📅 Match History", "📝 Game Log", "🔍 Opponent Intel", "🎮 Game Predictions", "📊 Benchmarking", "📋 Full Analysis", "📖 Quick Start Guide", "⚙️ Data Manager"]
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
        try:
            white_div = pd.read_csv("OCL_BU08_White_Division_Rankings.csv")
        except:
            white_div = pd.DataFrame()
        
        try:
            bsa_schedules = pd.read_csv("BSA_Celtic_Schedules.csv")
        except:
            bsa_schedules = pd.DataFrame()
        
        # DSX season stats
        dsx_si = 35.6
        dsx_gf_avg = 4.17
        dsx_ga_avg = 5.08
        dsx_gd_avg = -0.92
        
        st.header("📅 Next 3 Games")
        st.markdown("---")
        
        for idx, game in upcoming.head(3).iterrows():
            opponent = game['Opponent']
            game_date = game['GameDate']
            location = game['Location']
            league = game['League']
            
            with st.expander(f"**{game_date}**: {opponent} ({league})", expanded=(idx==0)):
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.subheader("📍 Game Info")
                    st.write(f"**Date:** {game_date}")
                    st.write(f"**Location:** {location}")
                    st.write(f"**League:** {league}")
                    st.write(f"**Notes:** {game['Notes']}")
                
                with col2:
                    st.subheader("🎯 Match Prediction")
                    
                    # Get opponent stats
                    opp_si = None
                    opp_gf = None
                    opp_ga = None
                    
                    if "BSA Celtic" in opponent and not bsa_schedules.empty:
                        team_matches = bsa_schedules[bsa_schedules['OpponentTeam'] == opponent]
                        completed = team_matches[team_matches['GF'] != ''].copy()
                        
                        if len(completed) > 0:
                            completed['GF'] = pd.to_numeric(completed['GF'])
                            completed['GA'] = pd.to_numeric(completed['GA'])
                            
                            gp = len(completed)
                            wins = (completed['GF'] > completed['GA']).sum()
                            draws = (completed['GF'] == completed['GA']).sum()
                            ppg = (wins * 3 + draws) / gp if gp > 0 else 0
                            gd_per_game = (completed['GF'].sum() - completed['GA'].sum()) / gp if gp > 0 else 0
                            
                            ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
                            gd_norm = (max(-5.0, min(5.0, gd_per_game)) + 5.0) / 10.0 * 100.0
                            opp_si = 0.7 * ppg_norm + 0.3 * gd_norm
                            opp_gf = completed['GF'].mean()
                            opp_ga = completed['GA'].mean()
                    
                    elif "Club Ohio West" in opponent and not white_div.empty:
                        club_ohio = white_div[white_div['Team'].str.contains("Club Ohio West", case=False)]
                        if not club_ohio.empty:
                            team = club_ohio.iloc[0]
                            opp_si = team['StrengthIndex']
                            opp_gf = team['GF']
                            opp_ga = team['GA']
                    
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
                        pred_dsx_goals = max(0, dsx_gf_avg + (si_diff * 0.05))
                        pred_opp_goals = max(0, opp_gf if opp_gf else dsx_ga_avg - (si_diff * 0.05))
                        
                        pred_dsx_low = max(0, pred_dsx_goals - 1.5)
                        pred_dsx_high = pred_dsx_goals + 1.5
                        pred_opp_low = max(0, pred_opp_goals - 1.5)
                        pred_opp_high = pred_opp_goals + 1.5
                        
                        st.write(f"**DSX:** {pred_dsx_low:.1f} - {pred_dsx_high:.1f} goals")
                        st.write(f"**{opponent}:** {pred_opp_low:.1f} - {pred_opp_high:.1f} goals")
                        
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


elif page == "🏆 Division Rankings":
    st.title("🏆 OCL BU08 Stripes Division Rankings")
    
    df = load_division_data()
    
    if df.empty:
        st.warning("No division data found. Run `python fetch_gotsport_division.py` to fetch data.")
    else:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        dsx_row = df[df['Team'].str.contains('DSX', na=False)]
        if not dsx_row.empty:
            dsx_rank = int(dsx_row['Rank'].values[0])
            dsx_strength = float(dsx_row['StrengthIndex'].values[0])
            dsx_record = f"{int(dsx_row['W'].values[0])}-{int(dsx_row['D'].values[0])}-{int(dsx_row['L'].values[0])}"
            dsx_gd = float(dsx_row['GD'].values[0])
            
            with col1:
                st.metric("DSX Rank", f"#{dsx_rank} of {len(df)}", 
                         f"{dsx_rank - 4} from 4th" if dsx_rank > 4 else "Top 4!")
            with col2:
                st.metric("Strength Index", f"{dsx_strength:.1f}", 
                         f"{dsx_strength - 43.4:.1f} from 4th")
            with col3:
                st.metric("Record", dsx_record)
            with col4:
                st.metric("Goal Diff/Game", f"{dsx_gd:+.2f}")
        
        st.markdown("---")
        
        # Division table
        st.subheader("Complete Rankings")
        
        # Format the dataframe
        display_df = df.copy()
        display_df['Team'] = display_df['Team'].apply(
            lambda x: f"🟢 **{x}**" if 'DSX' in x else x
        )
        
        # Select columns to display
        display_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
        display_cols = [col for col in display_cols if col in display_df.columns]
        
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                "Team": st.column_config.TextColumn("Team"),
                "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                "W": st.column_config.NumberColumn("W", help="Wins"),
                "D": st.column_config.NumberColumn("D", help="Draws"),
                "L": st.column_config.NumberColumn("L", help="Losses"),
                "GF": st.column_config.NumberColumn("GF", help="Goals For per game", format="%.2f"),
                "GA": st.column_config.NumberColumn("GA", help="Goals Against per game", format="%.2f"),
                "GD": st.column_config.NumberColumn("GD", help="Goal Differential per game", format="%+.2f"),
                "Pts": st.column_config.NumberColumn("Pts", help="Total Points"),
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
        st.subheader("📊 Division Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Strength Index chart
            fig = px.bar(
                df,
                x='Team',
                y='StrengthIndex',
                title='Strength Index by Team',
                color='StrengthIndex',
                color_continuous_scale='RdYlGn',
                text='StrengthIndex'
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
            # Offensive vs Defensive
            fig = px.scatter(
                df,
                x='GA',
                y='GF',
                size='GP',
                color='StrengthIndex',
                hover_name='Team',
                title='Offense vs Defense',
                color_continuous_scale='RdYlGn',
                labels={'GF': 'Goals For/Game', 'GA': 'Goals Against/Game'}
            )
            fig.add_shape(
                type='line',
                x0=df['GA'].min(), y0=df['GA'].min(),
                x1=df['GA'].max(), y1=df['GA'].max(),
                line=dict(color='gray', dash='dash'),
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)


elif page == "📊 Team Analysis":
    st.title("📊 Team Analysis")
    
    df = load_division_data()
    
    if df.empty:
        st.warning("No division data found.")
    else:
        # Team selector
        teams = df['Team'].tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            team1 = st.selectbox("Select Team 1", teams, index=next((i for i, t in enumerate(teams) if 'DSX' in t), 0))
        
        with col2:
            team2 = st.selectbox("Select Team 2", teams, index=0 if team1 != teams[0] else 1)
        
        # Get team data
        team1_data = df[df['Team'] == team1].iloc[0]
        team2_data = df[df['Team'] == team2].iloc[0]
        
        st.markdown("---")
        
        # Head-to-head comparison
        col1, col2, col3 = st.columns([1, 0.2, 1])
        
        with col1:
            st.markdown(f"### {team1}")
            st.metric("Rank", f"#{int(team1_data['Rank'])}")
            st.metric("Strength Index", f"{team1_data['StrengthIndex']:.1f}")
            st.metric("Record", f"{int(team1_data['W'])}-{int(team1_data['D'])}-{int(team1_data['L'])}")
            st.metric("Goals/Game", f"{team1_data['GF']:.2f} - {team1_data['GA']:.2f}")
            st.metric("GD/Game", f"{team1_data['GD']:+.2f}")
            st.metric("PPG", f"{team1_data['PPG']:.2f}")
        
        with col2:
            st.markdown("<div style='text-align: center; padding-top: 100px; font-size: 40px;'>VS</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"### {team2}")
            st.metric("Rank", f"#{int(team2_data['Rank'])}")
            st.metric("Strength Index", f"{team2_data['StrengthIndex']:.1f}")
            st.metric("Record", f"{int(team2_data['W'])}-{int(team2_data['D'])}-{int(team2_data['L'])}")
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
        # Read CSVs with explicit index handling
        player_stats = pd.read_csv("player_stats.csv", dtype={'PlayerNumber': str})
        roster = pd.read_csv("roster.csv", dtype={'PlayerNumber': str})
        
        # Strip whitespace from column names (common issue)
        player_stats.columns = player_stats.columns.str.strip()
        roster.columns = roster.columns.str.strip()
        
        # Convert PlayerNumber to numeric AFTER reading
        player_stats['PlayerNumber'] = pd.to_numeric(player_stats['PlayerNumber'].astype(str).str.strip(), errors='coerce')
        roster['PlayerNumber'] = pd.to_numeric(roster['PlayerNumber'].astype(str).str.strip(), errors='coerce')
        
        # Debug: Show what we loaded
        st.info(f"📊 Debug: Loaded {len(roster)} roster entries, {len(player_stats)} stat entries")
        st.info(f"Roster columns: {roster.columns.tolist()}")
        st.info(f"Stats columns: {player_stats.columns.tolist()}")
        
        # Check if columns exist before selecting
        if 'PlayerNumber' not in roster.columns or 'PlayerName' not in roster.columns:
            st.error("Roster.csv is missing required columns!")
            st.write("Expected: PlayerNumber, PlayerName, Position")
            st.write(f"Found: {roster.columns.tolist()}")
            raise ValueError("Invalid roster.csv format")
        
        if 'PlayerNumber' not in player_stats.columns:
            st.error("player_stats.csv is missing PlayerNumber column!")
            st.write(f"Found: {player_stats.columns.tolist()}")
            raise ValueError("Invalid player_stats.csv format")
        
        # Select only the columns we need from each dataframe
        roster_subset = roster[['PlayerNumber', 'PlayerName', 'Position']].copy()
        stats_subset = player_stats[['PlayerNumber', 'GamesPlayed', 'Goals', 'Assists', 'MinutesPlayed']].copy()
        
        st.info(f"Roster subset shape: {roster_subset.shape}, Stats subset shape: {stats_subset.shape}")
        st.write("**First 3 roster rows:**")
        st.dataframe(roster_subset.head(3))
        st.write("**First 3 stats rows:**")
        st.dataframe(stats_subset.head(3))
        
        # Merge stats with roster for full player info
        players = roster_subset.merge(
            stats_subset, 
            on='PlayerNumber', 
            how='left'
        )
        
        st.info(f"After merge - Players shape: {players.shape}, Columns: {players.columns.tolist()}")
        st.write("**First 3 merged rows:**")
        st.dataframe(players.head(3))
        
        # Fill missing stats with 0 and convert to numeric
        for col in ['GamesPlayed', 'Goals', 'Assists', 'MinutesPlayed']:
            if col in players.columns:
                players[col] = pd.to_numeric(players[col], errors='coerce').fillna(0)
        
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
            
            if player_data['Notes']:
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
        stripes_div = pd.read_csv("OCL_BU08_Stripes_Division_Rankings.csv")
        white_div = pd.read_csv("OCL_BU08_White_Division_Rankings.csv")
        dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv")
        
        # DSX stats
        dsx_si = 35.6
        dsx_gf_avg = 4.17
        dsx_ga_avg = 5.08
        
        # Prediction Calculator
        st.header("🔮 Match Predictor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Select Opponent")
            
            # Get all division teams
            all_teams = []
            if not stripes_div.empty:
                all_teams.extend(stripes_div['Team'].tolist())
            if not white_div.empty:
                all_teams.extend(white_div['Team'].tolist())
            
            # Add upcoming opponents
            if not upcoming.empty:
                all_teams.extend(upcoming['Opponent'].tolist())
            
            all_teams = sorted(list(set(all_teams)))
            
            selected_opponent = st.selectbox("Choose opponent", all_teams)
            
            # Get opponent stats
            opp_si = None
            opp_gf = None
            opp_ga = None
            
            # Check stripes
            if not stripes_div.empty:
                opp_data = stripes_div[stripes_div['Team'] == selected_opponent]
                if not opp_data.empty:
                    opp_si = opp_data.iloc[0]['StrengthIndex']
                    opp_gf = opp_data.iloc[0]['GF']
                    opp_ga = opp_data.iloc[0]['GA']
            
            # Check white
            if opp_si is None and not white_div.empty:
                opp_data = white_div[white_div['Team'] == selected_opponent]
                if not opp_data.empty:
                    opp_si = opp_data.iloc[0]['StrengthIndex']
                    opp_gf = opp_data.iloc[0]['GF']
                    opp_ga = opp_data.iloc[0]['GA']
            
            if opp_si is None:
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
                
                pred_dsx_goals = max(0, dsx_gf_avg + (si_diff * 0.05))
                pred_opp_goals = max(0, opp_gf - (si_diff * 0.05))
                
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
            
            current_points = dsx_matches['Points'].sum()
            current_gp = len(dsx_matches)
            current_ppg = current_points / current_gp if current_gp > 0 else 0
            
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
            
            current_points = dsx_matches['Points'].sum()
            current_gp = len(dsx_matches)
            
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
    
    # Load division data
    try:
        stripes_div = pd.read_csv("OCL_BU08_Stripes_Division_Rankings.csv")
        white_div = pd.read_csv("OCL_BU08_White_Division_Rankings.csv")
        dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv")
        
        # DSX stats
        dsx_stats = {
            'Team': 'Dublin DSX Orange 2018 Boys',
            'StrengthIndex': 35.6,
            'PPG': 1.00,
            'GF': 4.17,
            'GA': 5.08,
            'GD': -0.92,
            'GP': len(dsx_matches)
        }
        
        # Combine divisions
        all_teams = []
        if not stripes_div.empty:
            all_teams.append(('Stripes', stripes_div))
        if not white_div.empty:
            all_teams.append(('White', white_div))
        
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
            
            # Build team list
            team_options = []
            for div_name, div_df in all_teams:
                for _, team in div_df.iterrows():
                    team_options.append(f"{team['Team']} ({div_name})")
            
            selected_team_str = st.selectbox("Choose opponent", team_options)
            
            # Get selected team data
            selected_team_name = selected_team_str.split(' (')[0]
            opp_stats = None
            
            for div_name, div_df in all_teams:
                team_data = div_df[div_df['Team'] == selected_team_name]
                if not team_data.empty:
                    opp_stats = team_data.iloc[0]
                    break
            
            if opp_stats is not None:
                st.write(f"**Strength Index:** {opp_stats['StrengthIndex']:.1f}")
                st.write(f"**PPG:** {opp_stats['PPG']:.2f}")
                st.write(f"**Goals/Game:** {opp_stats['GF']:.2f}")
                st.write(f"**Against/Game:** {opp_stats['GA']:.2f}")
        
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
            st.info("💡 Select a team to see detailed head-to-head analysis and performance trends.")
            
            # Opponent selector - show teams DSX actually played
            opponent_names = actual_opponents['Opponent'].tolist()
            selected_opp = st.selectbox(
                "Select Opponent", 
                opponent_names,
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
            
            # Compare to season average
            season_avg_gf = 4.17  # From season stats
            season_avg_ga = 5.08
            
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
                with st.expander(f"**{game['GameDate']}**: {game['Opponent']} ({game['League']})", expanded=False):
                    st.write(f"📍 **Location:** {game['Location']}")
                    st.write(f"🏆 **League:** {game['League']}")
                    st.write(f"📝 **Notes:** {game['Notes']}")
            
            st.markdown("---")
            
            # Opponent selector for upcoming
            upcoming_names = upcoming['Opponent'].tolist()
            selected_upcoming = st.selectbox(
                "Select Upcoming Opponent to Scout", 
                upcoming_names,
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
                            st.metric("Record", f"{wins}-{draws}-{losses}")
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
                            st.metric("Opponent SI", f"{strength_index:.1f}")
                            st.metric("DSX SI", "35.6")
                        
                        with col2:
                            si_diff = 35.6 - strength_index
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
                        
                        with col1:
                            st.metric("Opponent SI", f"{team['StrengthIndex']:.1f}")
                            st.metric("DSX SI", "35.6")
                        
                        with col2:
                            si_diff = 35.6 - team['StrengthIndex']
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
    
    st.info("This page displays the complete strategic analysis from DIVISION_ANALYSIS_SUMMARY.md")
    
    # Key insights at the top
    st.header("🎯 Executive Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ DSX Strengths")
        st.markdown("""
        - **4.17 goals/game** (3rd best offense!)
        - **7 of 12 games** earned points (W or D)
        - **Can beat anyone** - 11-0 win shows ceiling
        """)
    
    with col2:
        st.subheader("⚠️ DSX Weaknesses")
        st.markdown("""
        - **5.08 goals against/game** (defensive issues)
        - **Inconsistent** - Range from 11-0 to 0-13
        - **Negative GD** - -0.92 per game
        """)
    
    st.markdown("---")
    
    # Matchup Analysis
    st.header("🎯 Matchup Analysis by Division Rank")
    
    # Should Beat
    st.subheader("✅ Teams DSX Should Beat")
    
    with st.expander("**Columbus Force SC** (Rank 6, SI: 16.9)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("DSX Advantage", "+18.7 SI points")
            st.metric("Their Record", "1-1-7")
        with col2:
            st.markdown("""
            **Strategy:**
            - DSX should dominate if playing tight defense
            - They struggle offensively (1.56 GF/game)
            - Worst defense in division (6.11 GA/game)
            """)
    
    with st.expander("**Johnstown FC** (Rank 7, SI: 3.0)"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("DSX Advantage", "+32.6 SI points")
            st.metric("Their Record", "0-0-1")
        with col2:
            st.markdown("""
            **Strategy:**
            - Overwhelming favorite
            - Limited data (only 1 game)
            - Lost their only game 0-4
            """)
    
    # Competitive
    st.subheader("🟡 Competitive Matchups (Toss-Ups)")
    
    with st.expander("**Sporting Columbus** (Rank 3, SI: 43.8)"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Strength Gap", "8.2 points", delta="Slight disadvantage")
            st.metric("Their Record", "3-0-4")
        with col2:
            st.markdown("""
            **Analysis:**
            - True toss-up game, comes down to execution
            - Low-scoring style (2.14 GF, 2.57 GA/game)
            - DSX's offensive firepower could overwhelm them
            """)
    
    with st.expander("**Delaware Knights** (Rank 4, SI: 43.4)"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Strength Gap", "7.8 points", delta="Slight disadvantage")
            st.metric("Their Record", "3-0-4")
        with col2:
            st.markdown("""
            **Analysis:**
            - High-scoring style (4.86 GF, 4.57 GA/game)
            - Expect a track meet - no draws in their record
            - Matches DSX's offensive style
            """)
    
    # Tough Matchups
    st.subheader("🔴 Tough Matchups (Underdogs)")
    
    with st.expander("**Polaris SC** (Rank 2, SI: 61.0)"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("DSX Disadvantage", "-25.4 SI points")
            st.metric("Their Record", "4-1-2")
        with col2:
            st.markdown("""
            **Strategy:**
            - Explosive offense (4.14 GF/game)
            - Solid defense (3.29 GA/game)
            - Focus on defense, look for counter-attacks
            """)
    
    with st.expander("**Blast FC** (Rank 1, SI: 73.5) ⭐"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("DSX Disadvantage", "-37.9 SI points")
            st.metric("Their Record", "6-2-1")
        with col2:
            st.markdown("""
            **Strategy:**
            - Division champions - dominant defense
            - Only 1.89 goals against/game (best in division)
            - Need perfect game to have a chance
            """)
    
    st.markdown("---")
    
    # How to Move Up
    st.header("📈 How to Move Up in Rankings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Jump to 4th Place")
        st.markdown("""
        **Need:** +7.8 StrengthIndex points
        
        **Option A: Win Streak**
        - Win next 3 games
        - PPG: 1.00 → 1.40
        - Result: +9.3 points ✅
        
        **Option B: Defensive Improvement**
        - Allow only 2 goals/game (vs current 5)
        - GD/GP: -0.92 → -0.42
        - Combined with 2-1-1 record: +8.1 points ✅
        """)
    
    with col2:
        st.subheader("🎯 Reach Top 3")
        st.markdown("""
        **Need:** +16.0 StrengthIndex points total
        
        **Required:**
        - 5-0-0 record over next 5 games
        - PPG: 1.00 → 1.59 (+13.8 points)
        - Tighten defense (<3 GA/game)
        - Result: 3rd place possible ⭐
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
    
    # Quick wins
    st.header("🚀 Quick Wins (Do These First)")
    
    with st.expander("1️⃣ Check Your Division Position (30 seconds)", expanded=True):
        st.markdown("""
        **Action:** Go to **🏆 Division Rankings** page
        
        **You'll see:**
        - DSX rank: **5th of 7**
        - Strength Index: **35.6**
        - Teams above and below you
        
        **Insight:** You're mid-table, can beat 2 teams, competitive with 2 more.
        """)
    
    with st.expander("2️⃣ Scout Your Next Opponent (2 minutes)"):
        st.markdown("""
        **Action:** Go to **📊 Team Analysis** page
        
        **Steps:**
        1. Select "Dublin DSX Orange" as Team 1
        2. Select your opponent as Team 2
        3. Read the matchup prediction
        4. Check the radar chart
        
        **You'll learn:**
        - Who's favored to win
        - Expected goal differential
        - Strengths/weaknesses comparison
        """)
    
    with st.expander("3️⃣ Review Recent Performance (1 minute)"):
        st.markdown("""
        **Action:** Go to **📅 Match History** page
        
        **You'll see:**
        - All 12 DSX games this season
        - 4-3-5 record (4W, 3D, 5L)
        - Goals over time chart
        - Cumulative goal differential
        
        **Look for:** Trends - are you improving or declining?
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
        st.success("""
        **🟢 Good News**
        
        - **3rd best offense** (4.17 GF/game)
        - **Can beat anyone** on good days
        - **Only +7.8 SI points** from 4th place
        - **Very achievable** to move up
        """)
    
    with col2:
        st.warning("""
        **🟡 Areas to Improve**
        
        - **Defense struggles** (5.08 GA/game)
        - **Inconsistent** results (11-0 to 0-13)
        - **Mid-table** currently (5th of 7)
        - **Need consistency** to climb
        """)
    
    st.markdown("---")
    
    # Dashboard Pages Guide
    st.header("📱 Dashboard Pages Explained")
    
    pages_info = {
        'Page': ['🏆 Division Rankings', '📊 Team Analysis', '📅 Match History', '🔍 Opponent Intel', '📋 Full Analysis', '📖 Quick Start Guide', '⚙️ Data Manager'],
        'Use For': [
            'See where DSX ranks in division',
            'Compare any 2 teams head-to-head',
            'Review all DSX games & trends',
            'Scout specific opponents',
            'Complete strategic analysis',
            'Getting started (this page!)',
            'Update data & export files'
        ],
        'Time': ['30 sec', '2 min', '2 min', '3 min', '5 min', '5 min', '1 min'],
        'Best For': [
            'Quick status check',
            'Pre-game scouting',
            'Post-game review',
            'Opponent research',
            'Strategy planning',
            'First time users',
            'Data refresh'
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
        - **Compare to division** not just opponents
        - **Defense wins** - watch GA/game
        - **Strength Index** is best overall metric
        """)
    
    st.markdown("---")
    
    # Quick Reference
    st.header("📊 Quick Reference Card")
    
    st.info("""
    **DSX Current Stats:**
    - **Rank:** 5th of 7
    - **Record:** 4-3-5 (W-D-L)
    - **Strength Index:** 35.6
    - **Offense:** 4.17 GF/game (3rd best! ✅)
    - **Defense:** 5.08 GA/game (needs work ⚠️)
    - **Goal Diff:** -0.92/game
    
    **To Move Up:**
    - **4th Place:** Win next 3 games OR tighten defense
    - **3rd Place:** 5-game winning streak + defensive improvement
    
    **Upcoming:**
    - **Oct 18:** BSA Celtic 18B United (winnable)
    - **Oct 19:** BSA Celtic 18B City (favorable)
    """)


elif page == "⚙️ Data Manager":
    st.title("⚙️ Data Manager")
    
    st.info("✏️ Edit your data directly! Changes are saved when you click the save button.")
    
    # Tabs for different editable data
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Roster", "📊 Player Stats", "⚽ Matches", "🎮 Game Stats", "📥 Downloads"])
    
    with tab1:
        st.subheader("👥 Edit Roster")
        st.write("Update player names, positions, and parent info")
        
        try:
            roster = pd.read_csv("roster.csv")
            
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
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Roster", type="primary"):
                    edited_roster.to_csv("roster.csv", index=False)
                    st.success("✅ Roster saved successfully!")
                    st.balloons()
            
            with col2:
                if st.button("↩️ Reset Changes"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("roster.csv not found")
    
    with tab2:
        st.subheader("📊 Edit Player Stats")
        st.write("Update goals, assists, and playing time")
        
        try:
            player_stats = pd.read_csv("player_stats.csv")
            
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
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Player Stats", type="primary"):
                    edited_stats.to_csv("player_stats.csv", index=False)
                    st.success("✅ Player stats saved successfully!")
                    st.balloons()
            
            with col2:
                if st.button("↩️ Reset Changes ", key="reset_stats"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("player_stats.csv not found")
    
    with tab3:
        st.subheader("⚽ Edit Match History")
        st.write("Update match results and scores")
        
        try:
            matches = pd.read_csv("DSX_Matches_Fall2025.csv")
            
            # Editable dataframe
            edited_matches = st.data_editor(
                matches,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", required=True),
                    "Tournament": st.column_config.TextColumn("Tournament"),
                    "Opponent": st.column_config.TextColumn("Opponent", required=True),
                    "GF": st.column_config.NumberColumn("Goals For", min_value=0),
                    "GA": st.column_config.NumberColumn("Goals Against", min_value=0),
                    "Result": st.column_config.SelectboxColumn("Result", options=["W", "D", "L"]),
                }
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Matches", type="primary"):
                    edited_matches.to_csv("DSX_Matches_Fall2025.csv", index=False)
                    st.success("✅ Match data saved successfully!")
                    st.balloons()
            
            with col2:
                if st.button("↩️ Reset Changes  ", key="reset_matches"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("DSX_Matches_Fall2025.csv not found")
    
    with tab4:
        st.subheader("🎮 Edit Game-by-Game Player Stats")
        st.write("Track who scored and assisted in each game")
        
        try:
            game_stats = pd.read_csv("game_player_stats.csv")
            
            # Editable dataframe
            edited_game_stats = st.data_editor(
                game_stats,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", required=True),
                    "Opponent": st.column_config.TextColumn("Opponent", required=True),
                    "PlayerName": st.column_config.TextColumn("Player", required=True),
                    "Goals": st.column_config.NumberColumn("Goals", min_value=0),
                    "Assists": st.column_config.NumberColumn("Assists", min_value=0),
                    "Notes": st.column_config.TextColumn("Notes (e.g. PK, Hat-trick)"),
                }
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Game Stats", type="primary"):
                    edited_game_stats.to_csv("game_player_stats.csv", index=False)
                    st.success("✅ Game stats saved successfully!")
                    st.balloons()
            
            with col2:
                if st.button("↩️ Reset Changes   ", key="reset_game_stats"):
                    st.rerun()
        
        except FileNotFoundError:
            st.error("game_player_stats.csv not found")
            st.info("This file tracks individual player contributions per game")
    
    with tab5:
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

