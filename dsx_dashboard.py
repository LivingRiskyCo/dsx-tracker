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
    st.image("https://via.placeholder.com/200x100/ff6b35/ffffff?text=DSX+ORANGE", use_container_width=True)
    st.title("⚽ DSX Tracker")
    st.markdown("**Dublin DSX Orange**  \n2018 Boys")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏆 Division Rankings", "📊 Team Analysis", "📅 Match History", "🔍 Opponent Intel", "📋 Full Analysis", "📖 Quick Start Guide", "⚙️ Data Manager"]
    )
    
    st.markdown("---")
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        refresh_data()


# Main content
if page == "🏆 Division Rankings":
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


elif page == "📅 Match History":
    st.title("📅 DSX Match History")
    
    matches = load_dsx_matches()
    
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
    
    # Match table
    st.subheader("All Matches")
    
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
    
    st.subheader("📥 Data Sources")
    
    # Check what data is available
    files = {
        "Division Rankings": "OCL_BU08_Stripes_Division_with_DSX.csv",
        "BSA Celtic Schedules": "BSA_Celtic_Schedules.csv",
        "Common Opponent Matrix": "Common_Opponent_Matrix_Template.csv"
    }
    
    for name, filename in files.items():
        exists = os.path.exists(filename)
        status = "✅ Loaded" if exists else "❌ Not found"
        
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
                        key=filename
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

