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
import sys

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
            min-height: 80px !important;
            font-size: 20px !important;
            padding: 16px !important;
        }
        
        /* Compact timer display */
        [data-testid="metric-container"] {
            padding: 8px !important;
        }
        
        /* Hide keyboard on dropdowns - prevents iOS zoom */
        select {
            font-size: 18px !important;
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
            padding: 12px !important;
            font-size: 18px !important;
            min-height: 60px !important;
        }
        
        /* Large buttons in dialogs - mobile optimized */
        .live-game-dialog button {
            min-height: 80px !important;
            font-size: 20px !important;
            padding: 16px !important;
        }
        
        /* Player selection buttons - grid layout */
        .player-select-btn {
            min-height: 80px !important;
            font-size: 18px !important;
            padding: 12px !important;
        }
    }
    
    /* Large buttons for desktop too - better game day experience */
    .live-game-dialog button {
        min-height: 70px !important;
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)


def load_game_config():
    """Load game configuration settings"""
    config_file = "game_config.csv"
    if os.path.exists(config_file):
        try:
            config_df = pd.read_csv(config_file, index_col=False)
            if not config_df.empty and 'GameLockMode' in config_df.columns:
                return config_df.iloc[0]['GameLockMode'] == True
        except:
            pass
    # Default: disabled (testing mode)
    return False

def save_game_config(game_lock_enabled):
    """Save game configuration settings"""
    config_file = "game_config.csv"
    config_df = pd.DataFrame([{'GameLockMode': game_lock_enabled}])
    config_df.to_csv(config_file, index=False)

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
        "Haunted_Classic_B08Orange_Division_Rankings.csv",  # 2025 Haunted Classic Orange division
        "Haunted_Classic_B08Black_Division_Rankings.csv",   # 2025 Haunted Classic Black division
        "CU_Fall_Finale_2025_Division_Rankings.csv",   # 2025 CU Fall Finale U8 Boys Platinum
        "Club_Ohio_Fall_Classic_2025_Division_Rankings.csv",   # 2025 Club Ohio Fall Classic U09B Select III
        "CPL_Fall_2025_Division_Rankings.csv",                # CPL Fall 2025 U9 divisions (multiple groups consolidated)
        # Note: OCL_BU09_7v7_Stripes_Benchmarking_2017.csv is NOT included here - it's for benchmarking only (2017 boys teams)
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
        
        # Exclude DSX from division data - DSX stats should come from match history, not division files
        # (Division files may have tournament-only stats for DSX, which would be misleading)
        combined = combined[~combined['Team'].str.contains('DSX', case=False, na=False)]
        
        # Prioritize tournament data for teams DSX has played in tournaments
        # Load DSX match history to identify tournament opponents
        tournament_opponents = set()
        tournament_files = [
            "Haunted_Classic_B08Orange_Division_Rankings.csv",
            "Haunted_Classic_B08Black_Division_Rankings.csv",
            "CU_Fall_Finale_2025_Division_Rankings.csv",
            "Club_Ohio_Fall_Classic_2025_Division_Rankings.csv",
        ]
        
        try:
            matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
            if not matches.empty and 'Tournament' in matches.columns:
                # Get opponents from tournament games
                tournament_matches = matches[matches['Tournament'].notna()]
                if not tournament_matches.empty:
                    tournament_opponents = set([resolve_alias(str(opp)) for opp in tournament_matches['Opponent'].dropna().unique()])
        except:
            pass
        
        # If we have tournament opponents, prioritize tournament file data for those teams
        if tournament_opponents:
            # Split into tournament and non-tournament rows
            tournament_rows = []
            non_tournament_rows = []
            
            for idx, row in combined.iterrows():
                team_name = str(row.get('Team', ''))
                team_resolved = resolve_alias(team_name)
                
                # Check if this team is a tournament opponent
                is_tournament_opponent = False
                for opp in tournament_opponents:
                    if normalize_name(opp) == normalize_name(team_resolved):
                        is_tournament_opponent = True
                        break
                
                # Check if this row is from a tournament file
                source_file = str(row.get('League', '')) + str(row.get('SourceURL', ''))
                is_tournament_file = any(tf in source_file for tf in ['Haunted Classic', 'CU Fall Finale', 'Club Ohio Fall Classic'])
                
                if is_tournament_opponent and is_tournament_file:
                    tournament_rows.append((idx, row))
                else:
                    non_tournament_rows.append((idx, row))
            
            # Combine: tournament rows first, then non-tournament
            # When duplicates are removed, tournament rows take precedence
            if tournament_rows:
                tournament_df = pd.DataFrame([r for _, r in tournament_rows])
                non_tournament_df = pd.DataFrame([r for _, r in non_tournament_rows])
                
                # Combine with tournament data first (so it's kept when removing duplicates)
                combined = pd.concat([tournament_df, non_tournament_df], ignore_index=True)
        
        # Remove duplicates based on Team name (keeping first = tournament data if prioritized)
        combined = combined.drop_duplicates(subset=['Team'], keep='first')
        return combined
    
    return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes (more frequent updates for match data)

# ----------- Team Name Aliases (normalize cross-league names) -----------
def normalize_name(name):
    if pd.isna(name):
        return ""
    return ' '.join(str(name).strip().split()).lower()

TEAM_NAME_ALIASES = {
    # CPL naming vs local/tournament naming
    normalize_name("Lakota FC 2018 Red"): "Lakota Futbol Club Lakota FC B17 Red",
    normalize_name("Lakota FC 2018 Black"): "Lakota Futbol Club Lakota FC B17 Black",
    normalize_name("TFA B18 Elite"): "Total Futbol Academy(OH) TFA B17 Elite",
    # BSA Celtic City aliases (for MVYSA B09-3 division)
    normalize_name("BSA Celtic City"): "BSA Celtic City",
    normalize_name("BSA Celtic City 2018"): "BSA Celtic City",
    # Worthington United name variations
    normalize_name("Worthington United Worthington United 94 2018 Boys White"): "Worthington United Worthington United 2018 Boys White",
    normalize_name("Worthington United 94 2018 Boys White"): "Worthington United Worthington United 2018 Boys White",
}

def resolve_alias(team_name: str) -> str:
    key = normalize_name(team_name)
    return TEAM_NAME_ALIASES.get(key, team_name)

def get_opponent_three_stat_snapshot(opponent_name, all_divisions_df, dsx_matches):
    """
    Generate a three-stat snapshot for an opponent:
    1. League Season Stats (from division data)
    2. Tournament Stats (if we played them in a tournament)
    3. Head-to-Head vs DSX
    
    Returns: dict with keys 'league', 'tournament', 'h2h' or None if no data
    """
    if all_divisions_df.empty and (dsx_matches is None or dsx_matches.empty):
        return None
    
    snapshot = {
        'league': None,
        'tournament': None,
        'h2h': None
    }
    
    # Helper function to normalize team names for matching
    def normalize_name_for_match(name):
        if pd.isna(name):
            return ""
        return ' '.join(str(name).strip().split()).lower()
    
    # Try to find opponent in division data (League Season Stats)
    # IMPORTANT: Filter out tournament files to get league/division season stats
    resolved_opp_name = resolve_alias(opponent_name)
    opp_division_row = pd.DataFrame()
    
    if not all_divisions_df.empty:
        # Filter out tournament data for League Season stats
        # Tournament files: Haunted Classic, CU Fall Finale, Club Ohio Fall Classic
        league_divisions_df = all_divisions_df.copy()
        
        # Identify tournament rows
        tournament_keywords = ['Haunted Classic', 'CU Fall Finale', 'Club Ohio Fall Classic']
        is_tournament = league_divisions_df.apply(
            lambda row: any(kw in str(row.get('League', '')) + str(row.get('SourceURL', '')) 
                           for kw in tournament_keywords), 
            axis=1
        )
        
        # Prefer league/division data over tournament data for "League Season" section
        league_only_df = league_divisions_df[~is_tournament].copy()
        tournament_only_df = league_divisions_df[is_tournament].copy()
        
        # First try to find in league/division data
        if not league_only_df.empty:
            # Try exact match first
            opp_division_row = league_only_df[league_only_df['Team'] == resolved_opp_name].copy()
            
            # If no exact match, try case-insensitive
            if opp_division_row.empty:
                opp_normalized = normalize_name_for_match(resolved_opp_name)
                for idx, row in league_only_df.iterrows():
                    team_normalized = normalize_name_for_match(row['Team'])
                    if team_normalized == opp_normalized:
                        opp_division_row = league_only_df.iloc[[idx]]
                        break
            
            # If still no match, try fuzzy matching
            if opp_division_row.empty:
                opp_normalized = normalize_name_for_match(resolved_opp_name)
                opp_words = [w for w in opp_normalized.split() if len(w) > 3]
                matches = []
                for idx, row in league_only_df.iterrows():
                    team_normalized = normalize_name_for_match(row['Team'])
                    match_score = sum(1 for word in opp_words if word in team_normalized)
                    if match_score >= 2:
                        matches.append((match_score, idx, row['Team']))
                if matches:
                    matches.sort(reverse=True)
                    best_match_idx = matches[0][1]
                    opp_division_row = league_only_df.iloc[[best_match_idx]]
        
        # If still no match in league data, fall back to tournament data (for teams that only exist in tournaments)
        if opp_division_row.empty and not tournament_only_df.empty:
            # Try exact match first
            opp_division_row = tournament_only_df[tournament_only_df['Team'] == resolved_opp_name].copy()
            
            # If no exact match, try case-insensitive
            if opp_division_row.empty:
                opp_normalized = normalize_name_for_match(resolved_opp_name)
                for idx, row in tournament_only_df.iterrows():
                    team_normalized = normalize_name_for_match(row['Team'])
                    if team_normalized == opp_normalized:
                        opp_division_row = tournament_only_df.iloc[[idx]]
                        break
            
            # If still no match, try fuzzy matching
            if opp_division_row.empty:
                opp_normalized = normalize_name_for_match(resolved_opp_name)
                opp_words = [w for w in opp_normalized.split() if len(w) > 3]
                matches = []
                for idx, row in tournament_only_df.iterrows():
                    team_normalized = normalize_name_for_match(row['Team'])
                    match_score = sum(1 for word in opp_words if word in team_normalized)
                    if match_score >= 2:
                        matches.append((match_score, idx, row['Team']))
                if matches:
                    matches.sort(reverse=True)
                    best_match_idx = matches[0][1]
                    opp_division_row = tournament_only_df.iloc[[best_match_idx]]
    
    if not opp_division_row.empty:
        opp_full = opp_division_row.iloc[0]
        
        # Safely convert W/L/D to int, handling NaN and various types
        def safe_int(value, default=0):
            if pd.isna(value):
                return default
            try:
                if hasattr(value, 'iloc'):
                    # It's a Series, get first value
                    value = value.iloc[0] if len(value) > 0 else default
                if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                    # It's an iterable, get first value
                    value = value[0] if len(value) > 0 else default
                # Convert to float first (handles string numbers), then int
                # NaN check: NaN != NaN is True, so if value != value, it's NaN
                if value != value:  # This is True for NaN
                    return default
                return int(float(value))
            except (ValueError, TypeError, IndexError):
                return default
        
        def safe_float(value, default=0.0):
            """Safely convert value to float, handling NaN"""
            if pd.isna(value):
                return default
            try:
                if hasattr(value, 'iloc'):
                    value = value.iloc[0] if len(value) > 0 else default
                if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                    value = value[0] if len(value) > 0 else default
                if value != value:  # NaN check
                    return default
                return float(value)
            except (ValueError, TypeError, IndexError):
                return default
        
        def safe_str(value, default='Unknown'):
            """Safely convert value to string, handling NaN"""
            if pd.isna(value):
                return default
            try:
                return str(value).strip() if str(value).strip() else default
            except:
                return default
        
        # Safely get GP, handling NaN
        gp = safe_int(opp_full.get('GP', 1), default=1)
        gp = gp if gp > 0 else 1
        
        # Handle both totals and per-game for GF/GA
        opp_gf_raw = opp_full.get('GF', 0)
        opp_ga_raw = opp_full.get('GA', 0)
        opp_gf = safe_float(opp_gf_raw, 0)
        opp_ga = safe_float(opp_ga_raw, 0)
        
        if opp_gf > 10:  # Heuristic: if > 10, it's likely total
            opp_gf_pg = opp_gf / gp if gp > 0 else 0
        else:
            opp_gf_pg = opp_gf
        
        if opp_ga > 10:
            opp_ga_pg = opp_ga / gp if gp > 0 else 0
        else:
            opp_ga_pg = opp_ga
        
        # Get GD, handling NaN
        opp_gd_raw = opp_full.get('GD', opp_gf - opp_ga)
        opp_gd = safe_float(opp_gd_raw, opp_gf - opp_ga)
        
        if abs(opp_gd) > 10:
            opp_gd_pg = opp_gd / gp if gp > 0 else 0
        else:
            opp_gd_pg = opp_gd
        
        w = safe_int(opp_full.get('W', 0))
        l = safe_int(opp_full.get('L', 0))
        d = safe_int(opp_full.get('D', 0))
        pts = (w * 3) + d
        opp_ppg = pts / gp if gp > 0 else 0
        
        # Safely get league/division names, handling NaN
        league_name = safe_str(opp_full.get('League', opp_full.get('League/Division', 'Unknown')), 'Unknown')
        division_name = safe_str(opp_full.get('Division', opp_full.get('League/Division', 'Unknown')), 'Unknown')
        
        # Safely get Rank and StrengthIndex
        rank_val = opp_full.get('Rank', 'N/A')
        if pd.isna(rank_val):
            rank_display = 'N/A'
        else:
            try:
                rank_display = int(float(rank_val))
            except:
                rank_display = 'N/A'
        
        strength_val = opp_full.get('StrengthIndex', 0)
        strength = safe_float(strength_val, 0)
        
        snapshot['league'] = {
            'record': f"{w}-{l}-{d}",
            'gp': gp,
            'ppg': round(opp_ppg, 2),
            'gf_pg': round(opp_gf_pg, 2) if not pd.isna(opp_gf_pg) else 0.0,
            'ga_pg': round(opp_ga_pg, 2) if not pd.isna(opp_ga_pg) else 0.0,
            'gd_pg': round(opp_gd_pg, 2) if not pd.isna(opp_gd_pg) else 0.0,
            'rank': rank_display,
            'strength': strength,
            'league': league_name,
            'division': division_name,
            'team_name': safe_str(opp_full.get('Team', opponent_name), opponent_name)
        }
    
    # Get Head-to-Head vs DSX stats
    if dsx_matches is not None and not dsx_matches.empty:
        h2h_games = dsx_matches[dsx_matches['Opponent'] == opponent_name].copy()
        
        if not h2h_games.empty:
            h2h_gp = len(h2h_games)
            # From opponent's perspective: goals they scored = DSX's GA
            h2h_gf = pd.to_numeric(h2h_games['GA'], errors='coerce').fillna(0).sum()
            # Goals they allowed = DSX's GF
            h2h_ga = pd.to_numeric(h2h_games['GF'], errors='coerce').fillna(0).sum()
            h2h_gd = h2h_gf - h2h_ga
            
            h2h_w = len(h2h_games[h2h_games['Outcome'] == 'L'])  # Opp wins = DSX losses
            h2h_l = len(h2h_games[h2h_games['Outcome'] == 'W'])  # Opp losses = DSX wins
            h2h_d = len(h2h_games[h2h_games['Outcome'] == 'D'])
            h2h_pts = (h2h_w * 3) + h2h_d
            h2h_ppg = h2h_pts / h2h_gp if h2h_gp > 0 else 0
            h2h_gf_pg = h2h_gf / h2h_gp if h2h_gp > 0 else 0
            h2h_ga_pg = h2h_ga / h2h_gp if h2h_gp > 0 else 0
            h2h_gd_pg = h2h_gd / h2h_gp if h2h_gp > 0 else 0
            
            # Tournament-specific stats from tournament division files (full tournament stats, not just H2H)
            tournaments_played = {}
            tournament_files_map = {
                '2025 Haunted Classic': ['Haunted_Classic_B08Orange_Division_Rankings.csv', 'Haunted_Classic_B08Black_Division_Rankings.csv'],
                '2025 Club Ohio Fall Classic': ['Club_Ohio_Fall_Classic_2025_Division_Rankings.csv'],
                'CU Fall Finale 2025': ['CU_Fall_Finale_2025_Division_Rankings.csv'],
                'Grove City Fall Classic': []  # Add file if available
            }
            
            # Get tournaments where DSX played this opponent
            for tour_name in h2h_games['Tournament'].unique():
                if pd.notna(tour_name) and tour_name != 'N/A':
                    # Look for tournament division file
                    tour_files = tournament_files_map.get(tour_name, [])
                    
                    # Try to find opponent in tournament division files
                    tour_stats_found = False
                    for tour_file in tour_files:
                        if os.path.exists(tour_file):
                            try:
                                tour_df = pd.read_csv(tour_file, index_col=False)
                                if not tour_df.empty:
                                    # Try to match opponent in tournament file
                                    opp_tour_row = tour_df[tour_df['Team'] == resolved_opp_name].copy()
                                    if opp_tour_row.empty:
                                        # Try normalized matching
                                        opp_normalized = normalize_name_for_match(resolved_opp_name)
                                        for idx, row in tour_df.iterrows():
                                            if normalize_name_for_match(row['Team']) == opp_normalized:
                                                opp_tour_row = tour_df.iloc[[idx]]
                                                break
                                    
                                    if not opp_tour_row.empty:
                                        tour_row = opp_tour_row.iloc[0]
                                        tour_gp = safe_int(tour_row.get('GP', 0))
                                        tour_w = safe_int(tour_row.get('W', 0))
                                        tour_l = safe_int(tour_row.get('L', 0))
                                        tour_d = safe_int(tour_row.get('D', 0))
                                        
                                        # Get GF/GA - handle totals vs per-game
                                        tour_gf = float(tour_row.get('GF', 0))
                                        tour_ga = float(tour_row.get('GA', 0))
                                        if tour_gf > 10 or tour_gp > 2:  # Likely totals
                                            tour_gf_pg = tour_gf / tour_gp if tour_gp > 0 else 0
                                            tour_ga_pg = tour_ga / tour_gp if tour_gp > 0 else 0
                                        else:
                                            tour_gf_pg = tour_gf
                                            tour_ga_pg = tour_ga
                                        
                                        tour_gd_pg = (tour_gf_pg - tour_ga_pg)
                                        tour_pts = (tour_w * 3) + tour_d
                                        tour_ppg = tour_pts / tour_gp if tour_gp > 0 else 0
                                        
                                        tournaments_played[tour_name] = {
                                            'record': f"{tour_w}-{tour_l}-{tour_d}",
                                            'gp': tour_gp,
                                            'ppg': round(tour_ppg, 2),
                                            'gf_pg': round(tour_gf_pg, 2),
                                            'ga_pg': round(tour_ga_pg, 2),
                                            'gd_pg': round(tour_gd_pg, 2)
                                        }
                                        tour_stats_found = True
                                        break
                            except Exception as e:
                                continue
                    
                    # If no tournament file found, fall back to H2H stats for that tournament
                    if not tour_stats_found:
                        tour_games = h2h_games[h2h_games['Tournament'] == tour_name]
                        tour_gp = len(tour_games)
                        tour_gf = pd.to_numeric(tour_games['GA'], errors='coerce').fillna(0).sum()
                        tour_ga = pd.to_numeric(tour_games['GF'], errors='coerce').fillna(0).sum()
                        tour_w = len(tour_games[tour_games['Outcome'] == 'L'])
                        tour_l = len(tour_games[tour_games['Outcome'] == 'W'])
                        tour_d = len(tour_games[tour_games['Outcome'] == 'D'])
                        tour_pts = (tour_w * 3) + tour_d
                        tour_ppg = tour_pts / tour_gp if tour_gp > 0 else 0
                        
                        tournaments_played[tour_name] = {
                            'record': f"{tour_w}-{tour_l}-{tour_d}",
                            'gp': tour_gp,
                            'ppg': round(tour_ppg, 2),
                            'gf_pg': round(tour_gf / tour_gp if tour_gp > 0 else 0, 2),
                            'ga_pg': round(tour_ga / tour_gp if tour_gp > 0 else 0, 2),
                            'gd_pg': round((tour_gf - tour_ga) / tour_gp if tour_gp > 0 else 0, 2)
                        }
            
            snapshot['h2h'] = {
                'record': f"{h2h_w}-{h2h_l}-{h2h_d}",
                'gp': h2h_gp,
                'ppg': round(h2h_ppg, 2),
                'gf_pg': round(h2h_gf_pg, 2),
                'ga_pg': round(h2h_ga_pg, 2),
                'gd_pg': round(h2h_gd_pg, 2),
                'tournaments': tournaments_played
            }
            
            # If there's only one tournament, set it as the tournament stat
            if len(tournaments_played) == 1:
                tour_name = list(tournaments_played.keys())[0]
                snapshot['tournament'] = {
                    'tournament_name': tour_name,
                    **tournaments_played[tour_name]
                }
    
    return snapshot if any(snapshot.values()) else None

def display_opponent_three_stat_snapshot(snapshot, opponent_name):
    """
    Display the three-stat snapshot in Streamlit:
    - League Season Stats
    - Tournament Stats (if available)
    - Head-to-Head vs DSX
    """
    if not snapshot or not any(snapshot.values()):
        st.info(f"📊 Scouting data not yet available for {opponent_name}")
        return
    
    st.markdown("---")
    st.subheader("📊 Three-Stat Snapshot")
    
    # Create three columns for the three stats
    col1, col2, col3 = st.columns(3)
    
    # Column 1: League Season Stats
    with col1:
        st.markdown("### 🏆 League Season")
        if snapshot.get('league'):
            league = snapshot['league']
            st.write(f"**{league.get('league', 'Unknown')}**")
            st.write(f"*{league.get('division', 'Unknown')}*")
            st.write(f"**Record:** {league['record']}")
            st.write(f"**GP:** {league['gp']}")
            st.write(f"**PPG:** {league['ppg']:.2f}")
            st.write(f"**GF/GA:** {league['gf_pg']:.1f} / {league['ga_pg']:.1f}")
            st.write(f"**GD:** {league['gd_pg']:+.1f}")
            if league['rank'] != 'N/A':
                st.write(f"**Rank:** #{int(league['rank'])}")
            st.write(f"**Strength:** {league['strength']:.1f}")
        else:
            st.info("No league data available")
    
    # Column 2: Tournament Stats
    with col2:
        st.markdown("### 🏅 Tournament")
        if snapshot.get('tournament'):
            tour = snapshot['tournament']
            st.write(f"**{tour.get('tournament_name', 'Tournament')}**")
            st.write(f"**Record:** {tour['record']}")
            st.write(f"**GP:** {tour['gp']}")
            st.write(f"**PPG:** {tour['ppg']:.2f}")
            st.write(f"**GF/GA:** {tour['gf_pg']:.1f} / {tour['ga_pg']:.1f}")
            st.write(f"**GD:** {tour['gd_pg']:+.1f}")
        elif snapshot.get('h2h') and snapshot['h2h'].get('tournaments'):
            # Show first tournament if multiple
            tournaments = snapshot['h2h']['tournaments']
            tour_name = list(tournaments.keys())[0]
            tour = tournaments[tour_name]
            st.write(f"**{tour_name}**")
            st.write(f"**Record:** {tour['record']}")
            st.write(f"**GP:** {tour['gp']}")
            st.write(f"**PPG:** {tour['ppg']:.2f}")
            st.write(f"**GF/GA:** {tour['gf_pg']:.1f} / {tour['ga_pg']:.1f}")
            st.write(f"**GD:** {tour['gd_pg']:+.1f}")
        else:
            st.info("No tournament data available")
    
    # Column 3: Head-to-Head vs DSX
    with col3:
        st.markdown("### ⚔️ H2H vs DSX")
        if snapshot.get('h2h'):
            h2h = snapshot['h2h']
            st.write(f"**Record:** {h2h['record']}")
            st.write(f"**GP:** {h2h['gp']}")
            st.write(f"**PPG:** {h2h['ppg']:.2f}")
            st.write(f"**GF/GA:** {h2h['gf_pg']:.1f} / {h2h['ga_pg']:.1f}")
            st.write(f"**GD:** {h2h['gd_pg']:+.1f}")
            if h2h.get('tournaments') and len(h2h['tournaments']) > 1:
                st.caption(f"({len(h2h['tournaments'])} tournaments)")
        else:
            st.info("No H2H data available")

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
    """Load DSX match history from CSV file"""
    try:
        # Try to load from CSV first (preferred - supports Data Manager updates)
        if os.path.exists("DSX_Matches_Fall2025.csv"):
            df = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False).reset_index(drop=True)
            # Ensure Date is datetime
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            # Calculate Result if not present
            if 'Result' not in df.columns and 'GF' in df.columns and 'GA' in df.columns:
                df['Result'] = df.apply(lambda r: 'W' if r['GF'] > r['GA'] else ('D' if r['GF'] == r['GA'] else 'L'), axis=1)
            # Calculate GD if not present
            if 'GD' not in df.columns and 'GF' in df.columns and 'GA' in df.columns:
                df['GD'] = df['GF'] - df['GA']
            return df
    except Exception as e:
        pass
    
    # Fallback: hardcoded matches (only used if CSV doesn't exist or fails)
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
        
        # Helper function to normalize team names for matching
        def normalize_name(name):
            """Normalize team name for matching (strip, lower, remove extra spaces)"""
            if pd.isna(name):
                return ""
            return ' '.join(str(name).strip().split()).lower()
        
        # Calculate DSX stats dynamically
        dsx_stats = calculate_dsx_stats()
        dsx_si = dsx_stats['StrengthIndex']
        dsx_gf_avg = dsx_stats['GF_PG']
        dsx_ga_avg = dsx_stats['GA_PG']
        dsx_gd_avg = dsx_stats['GD_PG']
        
        # Show recent completed games first
        st.header("📊 Recent Results")
        st.markdown("---")
        
        # Get recent completed games from match history
        # Filter to only completed games (those with Outcome) and sort by date descending
        completed_games = dsx_matches[dsx_matches['Outcome'].notna()].copy()
        
        if not completed_games.empty:
            # Convert date to datetime for proper sorting
            try:
                completed_games['Date_Parsed'] = pd.to_datetime(completed_games['Date'], errors='coerce')
                completed_games = completed_games.sort_values('Date_Parsed', ascending=False)
            except:
                # If date parsing fails, try sorting by index (newest at bottom)
                completed_games = completed_games.sort_index(ascending=False)
            
            # Get last 3 (most recent) completed games
            recent_games = completed_games.head(3)
        
        if not recent_games.empty:
            for idx, game in recent_games.iterrows():
                opponent = game['Opponent']
                game_date = game['Date']
                tournament = game['Tournament']
                actual_gf = game['GF']
                actual_ga = game['GA']
                actual_outcome = game['Outcome']
                
                # Determine outcome color and icon
                if actual_outcome == 'W':
                    outcome_color = "success"
                    outcome_icon = "✅"
                    outcome_text = "WIN"
                elif actual_outcome == 'D':
                    outcome_color = "info"
                    outcome_icon = "➖"
                    outcome_text = "DRAW"
                else:
                    outcome_color = "error"
                    outcome_icon = "❌"
                    outcome_text = "LOSS"
                
                with st.expander(f"{outcome_icon} **{game_date}**: {opponent} - DSX {actual_gf}-{actual_ga} ({outcome_text})", expanded=(idx==0)):
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.subheader("📍 Game Info")
                        st.write(f"**Date:** {game_date}")
                        st.write(f"**Tournament:** {tournament}")
                        st.write(f"**Result:** DSX {actual_gf}-{actual_ga}")
                        st.write(f"**Outcome:** {outcome_text}")
                    
                    with col2:
                        st.subheader("📈 Performance Analysis")
                        
                        # Get opponent stats for analysis
                        opp_si = None
                        if not all_divisions_df.empty:
                            opp_data = all_divisions_df[all_divisions_df['Team'] == opponent]
                            if not opp_data.empty:
                                opp_si = opp_data.iloc[0]['StrengthIndex']
                        
                        if opp_si is not None:
                            si_diff = dsx_si - opp_si
                            
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                st.markdown("### 🏆 DSX Performance")
                                st.markdown(f"**Strength Index: {dsx_si:.1f}**")
                                st.caption(f"Goals: {actual_gf}")
                                st.caption(f"Against: {actual_ga}")
                            
                            with col_b:
                                st.markdown("### ⚔️ " + opponent)
                                st.markdown(f"**Strength Index: {opp_si:.1f}**")
                                st.caption(f"Expected Challenge")
                            
                            with col_c:
                                if si_diff > 0:
                                    st.markdown("### 🎯 DSX Advantage")
                                    st.markdown(f"**+{si_diff:.1f} Points**")
                                    if actual_outcome == 'W':
                                        st.success("✅ Expected Win!")
                                    else:
                                        st.warning("⚠️ Upset Loss")
                                elif si_diff < 0:
                                    st.markdown("### ⚠️ Underdog")
                                    st.markdown(f"**{si_diff:.1f} Points**")
                                    if actual_outcome == 'W':
                                        st.success("✅ Upset Win!")
                                    else:
                                        st.info("ℹ️ Expected Result")
                                else:
                                    st.markdown("### ⚖️ Even Match")
                                    st.markdown("**0.0 Points**")
                                    st.info("🤝 Fair Result")
                        else:
                            st.info("No division data available for opponent analysis")
        
        st.markdown("---")
        
        # Show upcoming games
        st.header("📅 Upcoming Games")
        st.markdown("---")
        
        # Form Trend Analysis Section
        st.header("📈 Form Trend Analysis")
        st.markdown("---")
        
        # Analyze last 7 games for form trends (tournaments typically 3-4 games)
        if len(dsx_matches) >= 3:
            # Sort by date descending (most recent first) before taking last 7
            dsx_matches_sorted = dsx_matches.sort_values('Date', ascending=False).reset_index(drop=True)
            last_7_games = dsx_matches_sorted.head(7)  # Get most recent 7 (head because sorted descending)
            
            # Calculate form metrics
            form_wins = len(last_7_games[last_7_games['Outcome'] == 'W'])
            form_draws = len(last_7_games[last_7_games['Outcome'] == 'D'])
            form_losses = len(last_7_games[last_7_games['Outcome'] == 'L'])
            form_points = (form_wins * 3) + form_draws
            form_ppg = form_points / len(last_7_games)
            
            # Goals trend
            form_gf = last_7_games['GF'].sum()
            form_ga = last_7_games['GA'].sum()
            form_gf_pg = form_gf / len(last_7_games)
            form_ga_pg = form_ga / len(last_7_games)
            form_gd_pg = form_gf_pg - form_ga_pg
            
            # Compare to season average
            season_ppg = dsx_stats['PPG']
            season_gf_pg = dsx_stats['GF_PG']
            season_ga_pg = dsx_stats['GA_PG']
            season_gd_pg = dsx_stats['GD_PG']
            
            # Form indicators
            ppg_trend = "📈 Improving" if form_ppg > season_ppg else "📉 Declining" if form_ppg < season_ppg else "➡️ Stable"
            gf_trend = "📈 Improving" if form_gf_pg > season_gf_pg else "📉 Declining" if form_gf_pg < season_gf_pg else "➡️ Stable"
            ga_trend = "📈 Improving" if form_ga_pg < season_ga_pg else "📉 Declining" if form_ga_pg > season_ga_pg else "➡️ Stable"
            gd_trend = "📈 Improving" if form_gd_pg > season_gd_pg else "📉 Declining" if form_gd_pg < season_gd_pg else "➡️ Stable"
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Last 7 Games", f"{form_wins}-{form_losses}-{form_draws}", 
                         f"{ppg_trend} ({form_ppg:.2f} PPG)")
            
            with col2:
                st.metric("Goals For/Game", f"{form_gf_pg:.1f}", 
                         f"{gf_trend} (Season: {season_gf_pg:.1f})")
            
            with col3:
                st.metric("Goals Against/Game", f"{form_ga_pg:.1f}", 
                         f"{ga_trend} (Season: {season_ga_pg:.1f})")
            
            with col4:
                st.metric("Goal Difference/Game", f"{form_gd_pg:+.1f}", 
                         f"{gd_trend} (Season: {season_gd_pg:+.1f})")
            
            # Form analysis insights
            st.subheader("🎯 Form Analysis")
            
            if form_ppg > season_ppg + 0.3:
                st.success("🔥 **Hot Form!** DSX is playing better than season average. Keep the momentum!")
            elif form_ppg < season_ppg - 0.3:
                st.warning("⚠️ **Cold Form** - DSX needs to turn things around. Focus on fundamentals.")
            else:
                st.info("📊 **Consistent Form** - DSX is performing at season average. Look for small improvements.")
            
            # Specific recommendations based on trends
            recommendations = []
            
            if form_gf_pg < season_gf_pg - 0.5:
                recommendations.append("🎯 **Offensive Focus**: Goals per game down. Work on finishing and attacking patterns.")
            
            if form_ga_pg > season_ga_pg + 0.5:
                recommendations.append("🛡️ **Defensive Focus**: Goals against up. Tighten up defensive shape and communication.")
            
            if form_gd_pg < -1.0:
                recommendations.append("⚖️ **Balance Needed**: Goal difference negative. Focus on both ends of the field.")
            
            if form_wins == 0 and len(last_7_games) >= 3:
                recommendations.append("💪 **Confidence Building**: No wins in recent games. Focus on small victories and team morale.")
            
            if form_wins >= 3:
                recommendations.append("🚀 **Momentum Building**: Great recent form! Keep the same intensity and focus.")
            
            if recommendations:
                st.subheader("💡 Strategic Recommendations")
                for rec in recommendations:
                    st.write(rec)
            
            # Recent games breakdown
            st.subheader("📋 Last 7 Games Breakdown")
            st.caption("💡 Shows last 7 games to capture full tournament results (3-4 games per tournament)")
            
            for idx, game in last_7_games.iterrows():
                opponent = game['Opponent']
                gf = game['GF']
                ga = game['GA']
                outcome = game['Outcome']
                date = game['Date']
                tournament = game.get('Tournament', 'N/A')
                
                # Format date for display
                if pd.notna(date):
                    if isinstance(date, str):
                        date_str = date
                    else:
                        date_str = pd.to_datetime(date).strftime('%m/%d/%Y')
                else:
                    date_str = 'N/A'
                
                # Color coding
                if outcome == 'W':
                    color = "🟢"
                    result_text = "WIN"
                elif outcome == 'D':
                    color = "🟡"
                    result_text = "DRAW"
                else:
                    color = "🔴"
                    result_text = "LOSS"
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"{color} **{date_str}**: {opponent}")
                    st.caption(f"{tournament}")
                
                with col2:
                    st.write(f"**{gf}-{ga}**")
                
                with col3:
                    st.write(f"**{result_text}**")
                
                with col4:
                    if gf > ga:
                        st.write("✅ Good")
                    elif gf == ga:
                        st.write("➖ Even")
                    else:
                        st.write("❌ Tough")
        
        else:
            st.info("📊 **Form Analysis Available After 3+ Games** - Play more games to see trend analysis.")
            st.caption("💡 Once you have 7+ games, you'll see analysis covering 2+ tournaments!")
        
        st.markdown("---")
        
        # Season Trajectory Analysis
        st.header("📈 Season Trajectory")
        st.markdown("---")
        
        if len(dsx_matches) >= 4:
            # Calculate trajectory over time
            matches_with_dates = dsx_matches.copy()
            matches_with_dates['Date'] = pd.to_datetime(matches_with_dates['Date'])
            matches_with_dates = matches_with_dates.sort_values('Date')
            
            # Calculate rolling averages
            matches_with_dates['Cumulative_PPG'] = matches_with_dates['Outcome'].map({'W': 3, 'D': 1, 'L': 0}).cumsum() / (matches_with_dates.index + 1)
            matches_with_dates['Cumulative_GF'] = matches_with_dates['GF'].cumsum() / (matches_with_dates.index + 1)
            matches_with_dates['Cumulative_GA'] = matches_with_dates['GA'].cumsum() / (matches_with_dates.index + 1)
            matches_with_dates['Cumulative_GD'] = matches_with_dates['Cumulative_GF'] - matches_with_dates['Cumulative_GA']
            
            # Calculate trajectory trends
            recent_games = 3
            if len(matches_with_dates) >= recent_games:
                early_ppg = matches_with_dates.iloc[:recent_games]['Cumulative_PPG'].iloc[-1]
                recent_ppg = matches_with_dates.iloc[-recent_games:]['Cumulative_PPG'].iloc[-1]
                ppg_trend = recent_ppg - early_ppg
                
                early_gd = matches_with_dates.iloc[:recent_games]['Cumulative_GD'].iloc[-1]
                recent_gd = matches_with_dates.iloc[-recent_games:]['Cumulative_GD'].iloc[-1]
                gd_trend = recent_gd - early_gd
                
                # Trajectory analysis
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if ppg_trend > 0.2:
                        st.success("📈 **Improving**")
                        st.write(f"PPG: +{ppg_trend:.2f}")
                        st.caption("Getting better!")
                    elif ppg_trend < -0.2:
                        st.error("📉 **Declining**")
                        st.write(f"PPG: {ppg_trend:.2f}")
                        st.caption("Need to turn around")
                    else:
                        st.info("➡️ **Stable**")
                        st.write(f"PPG: {ppg_trend:+.2f}")
                        st.caption("Consistent performance")
                
                with col2:
                    if gd_trend > 0.3:
                        st.success("📈 **Improving**")
                        st.write(f"GD: +{gd_trend:.2f}")
                        st.caption("Better goal difference")
                    elif gd_trend < -0.3:
                        st.error("📉 **Declining**")
                        st.write(f"GD: {gd_trend:.2f}")
                        st.caption("Goal difference slipping")
                    else:
                        st.info("➡️ **Stable**")
                        st.write(f"GD: {gd_trend:+.2f}")
                        st.caption("Steady goal difference")
                
                with col3:
                    # Overall trajectory assessment
                    if ppg_trend > 0.2 and gd_trend > 0.3:
                        st.success("🚀 **Strong Upward**")
                        st.write("Both PPG & GD improving")
                        st.caption("Excellent trajectory!")
                    elif ppg_trend < -0.2 and gd_trend < -0.3:
                        st.error("⚠️ **Concerning**")
                        st.write("Both PPG & GD declining")
                        st.caption("Need immediate attention")
                    elif ppg_trend > 0.1 or gd_trend > 0.1:
                        st.info("📈 **Positive**")
                        st.write("Some improvement")
                        st.caption("Moving in right direction")
                    else:
                        st.warning("➡️ **Flat**")
                        st.write("No clear trend")
                        st.caption("Room for improvement")
            
            # Season progression chart
            st.subheader("📊 Season Progression")
            
            # Create a simple trajectory chart
            fig = go.Figure()
            
            # Add PPG line
            fig.add_trace(go.Scatter(
                x=matches_with_dates['Date'],
                y=matches_with_dates['Cumulative_PPG'],
                mode='lines+markers',
                name='Points Per Game',
                line=dict(color='#2E8B57', width=3),
                marker=dict(size=6)
            ))
            
            # Add Goal Difference line
            fig.add_trace(go.Scatter(
                x=matches_with_dates['Date'],
                y=matches_with_dates['Cumulative_GD'],
                mode='lines+markers',
                name='Goal Difference',
                line=dict(color='#FF6B35', width=3),
                marker=dict(size=6),
                yaxis='y2'
            ))
            
            # Update layout
            fig.update_layout(
                title="DSX Season Trajectory",
                xaxis_title="Date",
                yaxis_title="Points Per Game",
                yaxis2=dict(title="Goal Difference", overlaying="y", side="right"),
                hovermode='x unified',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Season insights
            st.subheader("💡 Season Insights")
            
            current_ppg = matches_with_dates['Cumulative_PPG'].iloc[-1]
            current_gd = matches_with_dates['Cumulative_GD'].iloc[-1]
            
            insights = []
            
            if current_ppg >= 2.0:
                insights.append("🎯 **Strong Season**: PPG above 2.0 indicates excellent performance")
            elif current_ppg >= 1.5:
                insights.append("👍 **Good Season**: PPG above 1.5 shows solid performance")
            elif current_ppg >= 1.0:
                insights.append("📊 **Average Season**: PPG around 1.0 is competitive")
            else:
                insights.append("⚠️ **Challenging Season**: PPG below 1.0 needs improvement")
            
            if current_gd > 0:
                insights.append("⚽ **Positive GD**: Scoring more than conceding - great sign!")
            elif current_gd == 0:
                insights.append("⚖️ **Even GD**: Balanced scoring and defending")
            else:
                insights.append("🛡️ **Negative GD**: Need to tighten defense or improve attack")
            
            # Recent form vs season average
            if len(matches_with_dates) >= 3:
                recent_3_ppg = matches_with_dates.tail(3)['Outcome'].map({'W': 3, 'D': 1, 'L': 0}).mean()
                if recent_3_ppg > current_ppg + 0.5:
                    insights.append("🔥 **Hot Finish**: Recent form much better than season average")
                elif recent_3_ppg < current_ppg - 0.5:
                    insights.append("❄️ **Cold Finish**: Recent form below season average")
            
            for insight in insights:
                st.write(insight)
        
        else:
            st.info("📊 **Season Trajectory Available After 4+ Games** - Play more games to see trajectory analysis.")
        
        st.markdown("---")
        
        # Filter to only upcoming games (robust: trim, handle NaN, future dates)
        try:
            status_series = upcoming['Status'].astype(str).str.strip().str.upper()
        except Exception:
            status_series = pd.Series([], dtype=str)

        upcoming_games = upcoming[status_series == 'UPCOMING'].copy()

        # Also exclude games that are already in match history (double-check even if status says UPCOMING)
        if not dsx_matches.empty and not upcoming_games.empty:
            # Normalize opponent names for matching
            def normalize_opponent_name(name):
                if pd.isna(name):
                    return ""
                return ' '.join(str(name).strip().split()).lower()
            
            # Create set of completed match dates + opponents for fast lookup
            completed_match_keys = set()
            for _, match in dsx_matches.iterrows():
                match_date = pd.to_datetime(match.get('Date'), errors='coerce')
                if pd.notna(match_date):
                    opp_name = normalize_opponent_name(str(match.get('Opponent', '')))
                    completed_match_keys.add((match_date.date(), opp_name))
            
            # Filter out games where date + opponent matches a completed match
            def is_already_played(row):
                game_date = pd.to_datetime(row.get('Date'), errors='coerce')
                if pd.notna(game_date):
                    opp_name = normalize_opponent_name(str(row.get('Opponent', '')))
                    if (game_date.date(), opp_name) in completed_match_keys:
                        return False
                    # Also check fuzzy match by opponent name only (same date, similar opponent name)
                    for match_date, match_opp in completed_match_keys:
                        if match_date == game_date.date():
                            # Check if opponent names are similar (70% word overlap)
                            opp_words = set(opp_name.split())
                            match_words = set(match_opp.split())
                            if opp_words and match_words:
                                overlap = len(opp_words & match_words) / max(len(opp_words), len(match_words))
                                if overlap > 0.7:
                                    return False
                return True
            
            try:
                upcoming_games = upcoming_games[upcoming_games.apply(is_already_played, axis=1)]
            except Exception:
                pass  # If filtering fails, continue with status-based filter

        # Ensure dates parse and filter to future dates (>= today)
        try:
            upcoming_games['Date_Parsed'] = pd.to_datetime(upcoming_games['Date'], errors='coerce')
            today = pd.to_datetime(pd.Timestamp.today().date())
            upcoming_games = upcoming_games[upcoming_games['Date_Parsed'].notna()]
            upcoming_games = upcoming_games[upcoming_games['Date_Parsed'] >= today]
        except Exception:
            pass
        
        if not upcoming_games.empty:
            # Sort by date for proper chronological order
            try:
                if 'Date_Parsed' not in upcoming_games.columns:
                    upcoming_games['Date_Parsed'] = pd.to_datetime(upcoming_games['Date'], errors='coerce')
                upcoming_games = upcoming_games.sort_values('Date_Parsed', ascending=True)
            except Exception:
                # If date parsing fails, keep original order
                pass
            
            for idx, game in upcoming_games.head(5).iterrows():
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
                        st.subheader("🎯 Head-to-Head Prediction")
                        
                        # Get opponent stats from consolidated division data (with alias + fuzzy matching)
                        opp_si = None
                        opp_gf = None
                        opp_ga = None
                        opp_gp = 1
                        
                        if not all_divisions_df.empty:
                            # Apply alias first
                            opponent_alias = resolve_alias(opponent)
                            # Try exact match first
                            opp_data = all_divisions_df[all_divisions_df['Team'] == opponent_alias]
                            
                            # If no exact match, try case-insensitive
                            if opp_data.empty:
                                opp_normalized = normalize_name(opponent_alias)
                                for jdx, row in all_divisions_df.iterrows():
                                    team_normalized = normalize_name(row['Team'])
                                    if team_normalized == opp_normalized:
                                        opp_data = all_divisions_df.iloc[[jdx]]
                                        break
                            
                            # If still no match, try fuzzy matching
                            if opp_data.empty:
                                opp_normalized = normalize_name(opponent_alias)
                                opp_words = [w for w in opp_normalized.split() if len(w) > 3]
                                
                                best_match = None
                                best_score = 0
                                
                                for jdx, row in all_divisions_df.iterrows():
                                    team_normalized = normalize_name(row['Team'])
                                    team_words = [w for w in team_normalized.split() if len(w) > 3]
                                    
                                    match_score = sum(1 for word in opp_words if word in team_normalized)
                                    match_score += sum(1 for word in team_words if word in opp_normalized)
                                    
                                    if match_score >= 2 and match_score > best_score:
                                        best_score = match_score
                                        best_match = row['Team']
                                
                                if best_match:
                                    opp_data = all_divisions_df[all_divisions_df['Team'] == best_match]
                            
                        if not opp_data.empty:
                            team = opp_data.iloc[0]
                            opp_si = team['StrengthIndex']
                            # Calculate per-game stats
                            opp_gp = team.get('GP', 1)
                            opp_gp = opp_gp if opp_gp > 0 else 1
                            
                            # Check if GF/GA are totals or per-game already
                            gf_val = team.get('GF', 0)
                            ga_val = team.get('GA', 0)
                            
                            # If GF > 10, likely totals (divide by GP), otherwise might be per-game
                            if gf_val > 10:
                                opp_gf = gf_val / opp_gp if opp_gp > 0 else 0
                            else:
                                opp_gf = gf_val
                            
                            if ga_val > 10:
                                opp_ga = ga_val / opp_gp if opp_gp > 0 else 0
                            else:
                                opp_ga = ga_val
                    
                    if opp_si is not None:
                        # Enhanced Strength Index display
                        st.markdown("---")
                        st.subheader("⚡ Strength Index Analysis")
                        
                        # Create a more prominent SI display
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.markdown("### 🏆 DSX Orange")
                            st.markdown(f"**Strength Index: {dsx_si:.1f}**")
                            st.caption(f"Goals/Game: {dsx_gf_avg:.1f}")
                            st.caption(f"Goals Against: {dsx_ga_avg:.1f}")
                        
                        with col_b:
                            st.markdown("### ⚔️ " + opponent)
                            st.markdown(f"**Strength Index: {opp_si:.1f}**")
                            if opp_gf is not None:
                                st.caption(f"Goals/Game: {opp_gf:.1f}")
                            if opp_ga is not None:
                                st.caption(f"Goals Against: {opp_ga:.1f}")
                        
                        with col_c:
                            si_diff = dsx_si - opp_si
                            if si_diff > 0:
                                st.markdown("### 🎯 DSX Advantage")
                                st.markdown(f"**+{si_diff:.1f} Points**")
                                st.success("✅ We're Stronger")
                            elif si_diff < 0:
                                st.markdown("### ⚠️ Opponent Advantage")
                                st.markdown(f"**{si_diff:.1f} Points**")
                                st.warning("⚠️ They're Stronger")
                            else:
                                st.markdown("### ⚖️ Even Match")
                                st.markdown("**0.0 Points**")
                                st.info("🤝 Dead Even")
                        
                        # Predicted score
                        st.markdown("---")
                        st.subheader("🔮 Score Prediction")
                        
                        # Improved prediction logic that properly accounts for strength differences
                        # When opponent is stronger (negative si_diff), they should score more, we should score less
                        # When we're stronger (positive si_diff), we should score more, they should score less
                        
                        # Base predictions on each team's offensive capability
                        # Use more aggressive SI impact for realistic predictions
                        si_impact = si_diff * 0.08  # Even stronger impact
                        
                        pred_dsx_goals = max(0.5, dsx_gf_avg + si_impact)
                        pred_opp_goals = max(0.5, (opp_gf if opp_gf else dsx_ga_avg) - si_impact)
                        
                        # Track if we swapped the predictions
                        swapped = False
                        
                        # Ensure the stronger team actually scores more goals
                        if si_diff < -5:  # Opponent is significantly stronger
                            if pred_dsx_goals >= pred_opp_goals:
                                # Swap the predictions so stronger team scores more
                                pred_dsx_goals, pred_opp_goals = pred_opp_goals, pred_dsx_goals
                                swapped = True
                            # If they're much stronger, give them at least 1 more goal
                            elif pred_dsx_goals == pred_opp_goals and si_diff < -10:
                                pred_opp_goals = pred_dsx_goals + 1
                        elif si_diff > 5:  # We are significantly stronger
                            if pred_opp_goals >= pred_dsx_goals:
                                # Swap the predictions so stronger team scores more
                                pred_dsx_goals, pred_opp_goals = pred_opp_goals, pred_dsx_goals
                                swapped = True
                            # If we're much stronger, give us at least 1 more goal
                            elif pred_dsx_goals == pred_opp_goals and si_diff > 10:
                                pred_dsx_goals = pred_opp_goals + 1
                        
                        # Calculate ranges for confidence assessment
                        pred_dsx_low = max(0, pred_dsx_goals - 1.5)
                        pred_dsx_high = pred_dsx_goals + 1.5
                        pred_opp_low = max(0, pred_opp_goals - 1.5)
                        pred_opp_high = pred_opp_goals + 1.5
                        
                        # Calculate single score predictions (rounded to realistic values)
                        dsx_prediction = round(pred_dsx_goals)
                        opp_prediction = round(pred_opp_goals)
                        
                        # Calculate confidence based on range tightness and strength difference
                        dsx_range = pred_dsx_high - pred_dsx_low
                        opp_range = pred_opp_high - pred_opp_low
                        avg_range = (dsx_range + opp_range) / 2
                        
                        # Calculate percentage confidence based on multiple factors
                        range_factor = max(0, 1 - (avg_range / 4.0))  # Tighter range = higher confidence
                        strength_factor = min(1.0, abs(si_diff) / 20.0)  # Bigger strength difference = higher confidence
                        data_factor = min(1.0, opp_gp / 5.0)  # More opponent data = higher confidence
                        
                        # Weighted confidence calculation
                        confidence_pct = (range_factor * 0.4 + strength_factor * 0.4 + data_factor * 0.2) * 100
                        confidence_pct = max(25, min(95, confidence_pct))  # Clamp between 25% and 95%
                        
                        if confidence_pct >= 75:
                            confidence = "High"
                            confidence_color = "🟢"
                            confidence_style = "success"
                        elif confidence_pct >= 60:
                            confidence = "Medium"
                            confidence_color = "🟡"
                            confidence_style = "warning"
                        else:
                            confidence = "Low"
                            confidence_color = "🔴"
                            confidence_style = "error"
                        
                        # Enhanced score prediction display
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 🏆 DSX Orange")
                            st.markdown(f"## **{dsx_prediction} Goals**")
                            st.caption(f"Range: {pred_dsx_low:.1f} - {pred_dsx_high:.1f}")
                        
                        with col2:
                            st.markdown("### ⚔️ " + opponent)
                            st.markdown(f"## **{opp_prediction} Goals**")
                            st.caption(f"Range: {pred_opp_low:.1f} - {pred_opp_high:.1f}")
                        
                        # Final score prediction with confidence color - better sized
                        st.markdown("---")
                        if confidence_style == "success":
                            st.markdown(f"### 🎯 **Final Score: DSX {dsx_prediction}-{opp_prediction} {opponent}**")
                                st.success(f"**{confidence_color} Confidence: {confidence} ({confidence_pct:.0f}%)** - Based on strength difference and data quality")
                        elif confidence_style == "warning":
                            st.markdown(f"### 🎯 **Final Score: DSX {dsx_prediction}-{opp_prediction} {opponent}**")
                                st.warning(f"**{confidence_color} Confidence: {confidence} ({confidence_pct:.0f}%)** - Based on strength difference and data quality")
                        else:
                            st.markdown(f"### 🎯 **Final Score: DSX {dsx_prediction}-{opp_prediction} {opponent}**")
                                st.error(f"**{confidence_color} Confidence: {confidence} ({confidence_pct:.0f}%)** - Based on strength difference and data quality")
                        
                        # Win probability based on final predicted score
                        st.markdown("---")
                        
                        # Calculate win probability using rounded final score shown to user
                        if dsx_prediction > opp_prediction:
                            # We're predicted to win
                            goal_diff = dsx_prediction - opp_prediction
                            if goal_diff >= 2:
                                win_prob = 75
                                draw_prob = 15
                                loss_prob = 10
                                st.success(f"✅ **Win Probability: {win_prob}%**")
                            else:
                                win_prob = 60
                                draw_prob = 25
                                loss_prob = 15
                                st.success(f"✅ **Win Probability: {win_prob}%**")
                        elif dsx_prediction < opp_prediction:
                            # We're predicted to lose
                            goal_diff = opp_prediction - dsx_prediction
                            if goal_diff >= 2:
                                win_prob = 15
                                draw_prob = 20
                                loss_prob = 65
                                st.error(f"⚠️ **Win Probability: {win_prob}%**")
                            else:
                                win_prob = 25
                                draw_prob = 30
                                loss_prob = 45
                                st.error(f"⚠️ **Win Probability: {win_prob}%**")
                        else:
                            # Predicted draw
                            win_prob = 35
                            draw_prob = 40
                            loss_prob = 25
                            st.info(f"⚖️ **Win Probability: {win_prob}%**")
                        
                        st.write(f"Draw: {draw_prob}% | Loss: {loss_prob}%")
                            
                            # Opponent's Three-Stat Snapshot (League Season + Tournament + H2H vs DSX)
                            try:
                                dsx_matches_for_snapshot = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
                            except:
                                dsx_matches_for_snapshot = pd.DataFrame()
                            
                            opponent_snapshot = get_opponent_three_stat_snapshot(opponent, all_divisions_df, dsx_matches_for_snapshot)
                            if opponent_snapshot:
                                display_opponent_three_stat_snapshot(opponent_snapshot, opponent)
                            else:
                                st.info(f"📊 Scouting data not yet available for {opponent}")
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
        elif 'Status' in upcoming.columns:
            # Debug info to help identify missing upcoming items
            with st.expander("ℹ️ Troubleshooting: Upcoming schedule (no upcoming detected)"):
                try:
                    st.write("Loaded rows:", len(upcoming))
                    st.write("Status values:", sorted(list(set(upcoming['Status'].astype(str).str.strip().str.upper().tolist()))))
                    st.dataframe(upcoming, use_container_width=True, hide_index=True)
                except Exception:
                    st.write("Unable to display upcoming CSV contents.")
        
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
        
        # Win/Loss streaks
        if len(dsx_matches) >= 3:
            recent_results = dsx_matches.tail(3)['Points'].tolist()
            if recent_results == [3, 3, 3]:
                insights.append("🏆 **Perfect Streak:** 3 wins in a row - keep the momentum!")
            elif recent_results == [0, 0, 0]:
                insights.append("😤 **Bounce Back Time:** 3 losses in a row - time to dig deep")
            elif recent_results.count(3) >= 2:
                insights.append("💪 **Strong Form:** Multiple wins in last 3 games")
        
        # Goal scoring trends
        if len(dsx_matches) >= 3:
            recent_gf = dsx_matches.tail(3)['GF'].mean()
            if recent_gf > dsx_gf_avg + 1:
                insights.append("🚀 **Scoring Surge:** " + f"{recent_gf:.1f} goals/game in last 3 (up from {dsx_gf_avg:.1f})")
            elif recent_gf < dsx_gf_avg - 1:
                insights.append("🎯 **Scoring Slump:** " + f"{recent_gf:.1f} goals/game in last 3 (down from {dsx_gf_avg:.1f})")
        
        # Defensive trends
        if len(dsx_matches) >= 3:
            recent_ga = dsx_matches.tail(3)['GA'].mean()
            if recent_ga < dsx_ga_avg - 1:
                insights.append("🛡️ **Defensive Improvement:** " + f"{recent_ga:.1f} goals allowed in last 3 (down from {dsx_ga_avg:.1f})")
            elif recent_ga > dsx_ga_avg + 1:
                insights.append("⚠️ **Defensive Concerns:** " + f"{recent_ga:.1f} goals allowed in last 3 (up from {dsx_ga_avg:.1f})")
        
        # Home vs Away performance
        if 'HomeAway' in dsx_matches.columns:
            home_matches = dsx_matches[dsx_matches['HomeAway'] == 'Home']
            away_matches = dsx_matches[dsx_matches['HomeAway'] == 'Away']
            
            if len(home_matches) >= 2 and len(away_matches) >= 2:
                home_ppg = home_matches['Points'].mean()
                away_ppg = away_matches['Points'].mean()
                
                if home_ppg > away_ppg + 0.5:
                    insights.append("🏠 **Home Field Advantage:** " + f"{home_ppg:.1f} PPG at home vs {away_ppg:.1f} away")
                elif away_ppg > home_ppg + 0.5:
                    insights.append("✈️ **Road Warriors:** " + f"{away_ppg:.1f} PPG away vs {home_ppg:.1f} at home")
        
        # Tournament performance
        if 'Tournament' in dsx_matches.columns:
            tournament_performance = dsx_matches.groupby('Tournament')['Points'].mean()
            best_tournament = tournament_performance.idxmax()
            best_ppg = tournament_performance.max()
            
            if len(tournament_performance) > 1 and best_ppg > dsx_matches['Points'].mean() + 0.5:
                insights.append("🏆 **Tournament Specialist:** " + f"{best_ppg:.1f} PPG in {best_tournament} (your best league)")
        
        # Comeback ability
        comeback_wins = dsx_matches[(dsx_matches['Points'] == 3) & (dsx_matches['GF'] < dsx_matches['GA'])]
        if len(comeback_wins) > 0:
            insights.append("💪 **Comeback Kings:** " + f"{len(comeback_wins)} comeback wins this season - never give up!")
        
        # Blowout wins
        blowout_wins = dsx_matches[(dsx_matches['Points'] == 3) & (dsx_matches['GoalDiff'] >= 3)]
        if len(blowout_wins) > 0:
            insights.append("💥 **Blowout Specialists:** " + f"{len(blowout_wins)} wins by 3+ goals - when you're on, you're ON!")
        
        # Close games
        close_games = dsx_matches[abs(dsx_matches['GoalDiff']) <= 1]
        if len(close_games) >= 3:
            close_win_pct = len(close_games[close_games['Points'] == 3]) / len(close_games) * 100
            if close_win_pct >= 60:
                insights.append("🎯 **Clutch Performers:** " + f"{close_win_pct:.0f}% win rate in close games - ice in your veins!")
            elif close_win_pct <= 30:
                insights.append("😰 **Close Game Struggles:** " + f"{close_win_pct:.0f}% win rate in close games - work on finishing")
        
        # Goal difference trends
        if len(dsx_matches) >= 5:
            first_half_gd = dsx_matches.head(len(dsx_matches)//2)['GoalDiff'].mean()
            second_half_gd = dsx_matches.tail(len(dsx_matches)//2)['GoalDiff'].mean()
            
            if second_half_gd > first_half_gd + 1:
                insights.append("📈 **Improving Form:** " + f"{second_half_gd:.1f} avg goal diff recently (up from {first_half_gd:.1f})")
            elif second_half_gd < first_half_gd - 1:
                insights.append("📉 **Form Dip:** " + f"{second_half_gd:.1f} avg goal diff recently (down from {first_half_gd:.1f})")
        
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
    if 'timer_start_time' not in st.session_state:
        st.session_state.timer_start_time = None
    if 'total_paused_time' not in st.session_state:
        st.session_state.total_paused_time = 0
    if 'pause_start_time' not in st.session_state:
        st.session_state.pause_start_time = None
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
    
    def update_player_stats_live(event_type, player=None, assist=None, pass_to=None, pass_complete=None):
        """Update player_stats.csv in real-time during game"""
        try:
            # Read current stats
            if os.path.exists("player_stats.csv"):
                stats_df = pd.read_csv("player_stats.csv", index_col=False)
            else:
                # Create empty stats file if doesn't exist
                stats_df = pd.DataFrame(columns=['PlayerNumber', 'PlayerName', 'GamesPlayed', 'Goals', 'Assists', 'Shots', 'PassesComplete', 'PassesIncomplete', 'MinutesPlayed', 'Notes'])
            
            # Get roster to map player names to numbers
            if os.path.exists("roster.csv"):
                roster_df = pd.read_csv("roster.csv", index_col=False)
            else:
                roster_df = pd.DataFrame()
            
            # Helper to find player number from name
            def get_player_number(player_name):
                if player_name and not pd.isna(player_name):
                    # Try to extract number from "#5 Name" format
                    if '#' in str(player_name):
                        try:
                            num = int(str(player_name).split('#')[1].split(' ')[0])
                            return num
                        except:
                            pass
                    # Try direct match on PlayerName
                    if not roster_df.empty:
                        player_name_str = str(player_name).split(' ')[-1] if ' ' in str(player_name) else str(player_name)
                        match = roster_df[roster_df['PlayerName'].str.contains(player_name_str, case=False, na=False)]
                        if not match.empty:
                            return int(match.iloc[0]['PlayerNumber'])
                return None
            
            # Update stats based on event type
            players_to_update = []
            
            if event_type == 'DSX_GOAL' and player:
                player_num = get_player_number(player)
                if player_num:
                    players_to_update.append({'num': player_num, 'stat': 'Goals', 'value': 1})
            
            if assist and event_type == 'DSX_GOAL':
                assist_num = get_player_number(assist)
                if assist_num:
                    players_to_update.append({'num': assist_num, 'stat': 'Assists', 'value': 1})
            
            if event_type == 'SHOT' and player:
                player_num = get_player_number(player)
                if player_num:
                    players_to_update.append({'num': player_num, 'stat': 'Shots', 'value': 1})
            
            if event_type in ['PASS_COMPLETE', 'PASS_INCOMPLETE'] and player:
                player_num = get_player_number(player)
                if player_num:
                    if event_type == 'PASS_COMPLETE':
                        players_to_update.append({'num': player_num, 'stat': 'PassesComplete', 'value': 1})
                    else:
                        players_to_update.append({'num': player_num, 'stat': 'PassesIncomplete', 'value': 1})
            
            # Update stats for each player
            for update in players_to_update:
                player_num = update['num']
                stat_name = update['stat']
                stat_value = update['value']
                
                # Ensure player exists in stats
                if 'PlayerNumber' in stats_df.columns:
                    stats_df['PlayerNumber'] = stats_df['PlayerNumber'].astype(str).str.strip()
                else:
                    stats_df['PlayerNumber'] = ''
                
                player_row = stats_df[stats_df['PlayerNumber'].astype(str) == str(player_num)]
                
                if player_row.empty:
                    # Create new row for player
                    player_name = ""
                    if not roster_df.empty:
                        player_match = roster_df[roster_df['PlayerNumber'].astype(str) == str(player_num)]
                        if not player_match.empty:
                            player_name = player_match.iloc[0]['PlayerName']
                    
                    new_row = {
                        'PlayerNumber': str(player_num),
                        'PlayerName': player_name,
                        'GamesPlayed': 1,  # Assume this game
                        'Goals': 0,
                        'Assists': 0,
                        'Shots': 0,
                        'PassesComplete': 0,
                        'PassesIncomplete': 0,
                        'MinutesPlayed': 0,
                        'Notes': ''
                    }
                    new_row[stat_name] = stat_value
                    stats_df = pd.concat([stats_df, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    # Update existing row
                    idx = player_row.index[0]
                    # Ensure stat column exists
                    if stat_name not in stats_df.columns:
                        stats_df[stat_name] = 0
                    # Update stat
                    current_value = pd.to_numeric(stats_df.at[idx, stat_name], errors='coerce') or 0
                    stats_df.at[idx, stat_name] = current_value + stat_value
            
            # Ensure all stat columns exist (add if missing, fill NaN with 0)
            required_cols = ['Shots', 'PassesComplete', 'PassesIncomplete']
            for col in required_cols:
                if col not in stats_df.columns:
                    stats_df[col] = 0
                # Fill NaN with 0 for existing rows
                stats_df[col] = pd.to_numeric(stats_df[col], errors='coerce').fillna(0).astype(int)
            
            # Ensure other numeric columns are properly typed
            numeric_cols = ['GamesPlayed', 'Goals', 'Assists', 'MinutesPlayed']
            for col in numeric_cols:
                if col in stats_df.columns:
                    stats_df[col] = pd.to_numeric(stats_df[col], errors='coerce').fillna(0).astype(int)
            
            # Write updated stats back to CSV
            stats_df.to_csv("player_stats.csv", index=False)
            
        except Exception as e:
            # Don't break game tracking if stats update fails
            st.warning(f"⚠️ Stats update failed: {str(e)}")
    
    def _update_last_shot_event():
        """Update the most recent shot event with current shot details"""
        if not st.session_state.shot_player or not st.session_state.events:
            return
        # Find most recent SHOT event
        for event in st.session_state.events:
            if event.get('type') == 'SHOT' and event.get('player'):
                player_name = st.session_state.shot_player.split(' ', 1)[1] if ' ' in st.session_state.shot_player else st.session_state.shot_player
                if player_name in str(event.get('player', '')):
                    # Update notes with current selections
                    shot_details_parts = []
                    if st.session_state.shot_outcome:
                        shot_details_parts.append(st.session_state.shot_outcome)
                    if st.session_state.shot_type:
                        shot_details_parts.append(st.session_state.shot_type)
                    if st.session_state.shot_location:
                        shot_details_parts.append(st.session_state.shot_location)
                    if st.session_state.get('shot_notes'):
                        shot_details_parts.append(st.session_state.shot_notes)
                    event['notes'] = " | ".join(shot_details_parts) if shot_details_parts else ""
                    break
    
    def _update_last_pass_event():
        """Update the most recent pass event with current pass details"""
        if not st.session_state.pass_from_player or not st.session_state.pass_to_player or not st.session_state.events:
            return
        # Find most recent PASS event
        for event in st.session_state.events:
            if event.get('type') == 'PASS' and event.get('player') and event.get('pass_to'):
                player_from_name = st.session_state.pass_from_player.split(' ', 1)[1] if ' ' in st.session_state.pass_from_player else st.session_state.pass_from_player
                player_to_name = st.session_state.pass_to_player.split(' ', 1)[1] if ' ' in st.session_state.pass_to_player else st.session_state.pass_to_player
                if player_from_name in str(event.get('player', '')) and player_to_name in str(event.get('pass_to', '')):
                    # Update pass_complete status
                    if st.session_state.pass_complete_status:
                        event['pass_complete'] = (st.session_state.pass_complete_status == "Complete")
                    # Update notes
                    pass_notes_parts = [f"To: {player_to_name}"]
                    if st.session_state.pass_complete_status:
                        status_text = "Complete" if event.get('pass_complete') else "Incomplete"
                        pass_notes_parts.append(status_text)
                    if st.session_state.get('pass_notes'):
                        pass_notes_parts.append(st.session_state.pass_notes)
                    event['notes'] = " | ".join(pass_notes_parts)
                    break
    
    def log_to_chat(event_type, event_data, channel='game-day'):
        """Auto-log game events to team chat (TeamSnap-style)"""
        try:
            from chat_db import ChatDatabase
            db = ChatDatabase()
            
            # Format messages based on event type
            username = "🎮 Game Tracker"
            message = ""
            
            if event_type == 'GAME_START':
                game_info = event_data.get('game_data', {})
                message = f"🚀 **Game Started!**\n"
                message += f"⚽ **Opponent:** {game_info.get('opponent', 'Unknown')}\n"
                message += f"📅 **Date:** {game_info.get('date', 'Unknown')}\n"
                message += f"📍 **Location:** {game_info.get('location', 'TBD')}\n"
                message += f"🏆 **Tournament:** {game_info.get('tournament', 'Unknown')}"
            
            elif event_type == 'DSX_GOAL':
                player = event_data.get('player', 'Unknown')
                assist = event_data.get('assist')
                timestamp = event_data.get('timestamp', '')
                half = event_data.get('half', 1)
                dsx_score, opp_score = get_score_tracker()
                message = f"⚽ **GOAL!** {player} ({timestamp} - {half}H) - DSX {dsx_score}-{opp_score}"
                if assist and assist != 'nan' and assist != '':
                    message += f"\n🎯 Assist: {assist}"
            
            elif event_type == 'OPP_GOAL':
                timestamp = event_data.get('timestamp', '')
                half = event_data.get('half', 1)
                dsx_score, opp_score = get_score_tracker()
                message = f"🥅 Opponent Goal ({timestamp} - {half}H) - DSX {dsx_score}-{opp_score}"
            
            elif event_type == 'SHOT':
                player = event_data.get('player', 'Unknown')
                timestamp = event_data.get('timestamp', '')
                notes = event_data.get('notes', '')
                message = f"🎯 Shot by {player} ({timestamp})"
                if notes:
                    message += f" - {notes}"
            
            elif event_type == 'SAVE':
                player = event_data.get('player', 'Unknown')
                timestamp = event_data.get('timestamp', '')
                notes = event_data.get('notes', '')
                message = f"🧤 Save by {player} ({timestamp})"
                if notes:
                    message += f" - {notes}"
            
            elif event_type == 'SUBSTITUTION':
                player = event_data.get('player', 'Unknown')
                timestamp = event_data.get('timestamp', '')
                message = f"🔄 Substitution ({timestamp}): {player}"
            
            elif event_type == 'HALF_TIME':
                dsx_score, opp_score = get_score_tracker()
                message = f"⏰ **HALF TIME** - DSX {dsx_score}-{opp_score}"
            
            elif event_type == 'TIMEOUT':
                timestamp = event_data.get('timestamp', '')
                message = f"🚨 Timeout called ({timestamp})"
            
            elif event_type == 'CORNER':
                timestamp = event_data.get('timestamp', '')
                message = f"⚠️ Corner kick ({timestamp})"
            
            elif event_type == 'PASS':
                player_from = event_data.get('player', 'Unknown')
                player_to = event_data.get('pass_to', 'Unknown')
                complete = event_data.get('pass_complete', True)
                timestamp = event_data.get('timestamp', '')
                status = "✅" if complete else "❌"
                message = f"{status} Pass: {player_from} → {player_to} ({timestamp})"
            
            if message:
                db.post_message(username, message, channel)
        except Exception as e:
            # Don't break game tracking if chat logging fails
            pass
    
    def add_event_tracker(event_type, player=None, assist=None, notes="", pass_to=None, pass_complete=None):
        # Calculate elapsed time from game start (more accurate)
        if 'game_data' in st.session_state and st.session_state.game_data:
            half_length = st.session_state.game_data.get('half_length', 25) * 60
        else:
            half_length = 25 * 60
        
        # Calculate elapsed time in current half
        elapsed = (half_length - st.session_state.time_remaining)
        
        # If in second half, add first half time
        if st.session_state.current_half == 2:
            elapsed += half_length
        
        event = {
            'timestamp': format_time(elapsed),
            'half': st.session_state.current_half,
            'type': event_type,
            'player': player,
            'assist': assist,
            'notes': notes,
            'time': datetime.now().strftime('%H:%M:%S'),
            'time_remaining': st.session_state.time_remaining
        }
        
        # Add pass-specific fields
        if pass_to:
            event['pass_to'] = pass_to
        if pass_complete is not None:
            event['pass_complete'] = pass_complete
        
        st.session_state.events.insert(0, event)
        
        # Auto-log major events to chat (TeamSnap-style)
        major_events = ['GAME_START', 'DSX_GOAL', 'OPP_GOAL', 'SHOT', 'SAVE', 'SUBSTITUTION', 'HALF_TIME', 'TIMEOUT', 'CORNER']
        if event_type in major_events:
            log_to_chat(event_type, event)
        elif event_type == 'PASS' and pass_to:  # Only log completed passes or important ones
            log_to_chat('PASS', event)
        
        # Update player stats immediately
        update_player_stats_live(event_type, player, assist, pass_to, pass_complete)
        
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
            
            # Check if game lock is enabled and game is active (for disabling manual entry)
            game_lock_enabled = load_game_config()
            game_active_and_locked = st.session_state.game_active and game_lock_enabled and not st.session_state.get('game_unlocked', False)
            
            with col1:
                game_date = st.date_input("Date", value=default_date, disabled=game_active_and_locked)
                opponent = st.text_input("Opponent Team", value=default_opponent, disabled=game_active_and_locked)
                location = st.text_input("Location", value=default_location, disabled=game_active_and_locked)
                tournament = st.text_input("Tournament/League", value=default_tournament, disabled=game_active_and_locked)
            
            with col2:
                st.subheader("⚙️ Game Settings")
                half_length = st.number_input("Half Length (minutes)", min_value=10, max_value=45, value=25, disabled=game_active_and_locked)
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
        
        # Check if game lock is enabled (for when starting a new game)
        game_lock_enabled = load_game_config()
        game_active_and_locked = st.session_state.game_active and game_lock_enabled and not st.session_state.get('game_unlocked', False)
        
        # ENHANCED LINEUP SELECTION WITH FORMATIONS
        st.subheader("👥 Select Starting Lineup")
        st.info("💡 **Choose your formation and select players for each position!**")
        
        if not roster_tracker.empty:
            # Formation selector (disabled if game is active and locked)
            formation = st.selectbox(
                "Formation:",
                ["2-2-2 (Recommended)", "2-3-1", "3-2-1", "1-3-2"],
                help="Choose your team formation",
                disabled=game_active_and_locked
            )
            
            st.markdown("---")
            
            # Position assignments based on formation
            if "2-2-2" in formation:
                positions = ["GK", "D1", "D2", "M1", "M2", "F1", "F2"]
                position_names = ["Goalkeeper", "Defender 1", "Defender 2", "Midfielder 1", "Midfielder 2", "Forward 1", "Forward 2"]
            elif "2-3-1" in formation:
                positions = ["GK", "D1", "D2", "M1", "M2", "M3", "F1"]
                position_names = ["Goalkeeper", "Defender 1", "Defender 2", "Midfielder 1", "Midfielder 2", "Midfielder 3", "Forward 1"]
            elif "3-2-1" in formation:
                positions = ["GK", "D1", "D2", "D3", "M1", "M2", "F1"]
                position_names = ["Goalkeeper", "Defender 1", "Defender 2", "Defender 3", "Midfielder 1", "Midfielder 2", "Forward 1"]
            else:  # 1-3-2
                positions = ["GK", "D1", "M1", "M2", "M3", "F1", "F2"]
                position_names = ["Goalkeeper", "Defender 1", "Midfielder 1", "Midfielder 2", "Midfielder 3", "Forward 1", "Forward 2"]
            
            # Initialize lineup session state
            if 'lineup' not in st.session_state:
                st.session_state.lineup = {pos: None for pos in positions}
                st.session_state.lineup['subs'] = []
            
            # Get available players (not already selected)
            selected_players = [p for p in st.session_state.lineup.values() if p and p != "Empty"]
            available_players = [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" for _, row in roster_tracker.iterrows() 
                               if f"#{int(row['PlayerNumber'])} {row['PlayerName']}" not in selected_players]
            
            # Create lineup form
            lineup_form = {}
            
            for i, (pos, pos_name) in enumerate(zip(positions, position_names)):
                # Get current player for this position
                current_player = st.session_state.lineup.get(pos, None)
                
                # Create options list
                options = ["Select Player..."] + available_players
                if current_player and current_player != "Empty":
                    options = [current_player] + [p for p in available_players if p != current_player]
                
                # Player selector (disabled if game is active and locked)
                selected = st.selectbox(
                    f"{pos_name} ({pos})",
                    options,
                    key=f"lineup_{pos}",
                    help=f"Select player for {pos_name}",
                    disabled=game_active_and_locked
                )
                
                if selected and selected != "Select Player...":
                    lineup_form[pos] = selected
                else:
                    lineup_form[pos] = "Empty"
            
            # Build selected_starters from session state (not form state)
            selected_starters = []
            for pos in positions:
                player = st.session_state.lineup.get(pos)
                if player and player != "Empty" and player != "Select Player...":
                    try:
                        player_num = int(player.split('#')[1].split(' ')[0])
                        selected_starters.append(player_num)
                    except:
                        pass
            
                        # Opponent Season History
                        st.markdown("---")
                        st.subheader("📊 Opponent's Full Season History")
                        opp_div_row = all_divisions_df[all_divisions_df['Team'] == opponent] if not all_divisions_df.empty else pd.DataFrame()
                        if not opp_div_row.empty:
                            opp_full = opp_div_row.iloc[0]
                            colh1, colh2, colh3, colh4, colh5 = st.columns(5)
                            with colh1:
                                st.metric("Record", f"{int(opp_full.get('W',0))}-{int(opp_full.get('L',0))}-{int(opp_full.get('D',0))}")
                                st.caption(f"GP: {int(opp_full.get('GP',0))}")
                            with colh2:
                                opp_ppg = float(opp_full.get('PPG', opp_full.get('Pts',0)/max(1, opp_full.get('GP',1))))
                                st.metric("PPG", f"{opp_ppg:.2f}")
                            with colh3:
                                ogf = float(opp_full.get('GF',0)); oga = float(opp_full.get('GA',0))
                                st.metric("GF/GA", f"{ogf:.1f} - {oga:.1f}")
                            with colh4:
                                ogd = float(opp_full.get('GD', ogf-oga))
                                st.metric("GD", f"{ogd:+.1f}")
                            with colh5:
                                orank = opp_full.get('Rank', opp_full.get('rank','N/A'))
                                osi = float(opp_full.get('StrengthIndex', opp_full.get('strength_index',0)))
                                st.metric("Rank", f"#{int(orank)}" if orank!='N/A' else "N/A")
                                st.caption(f"SI: {osi:.1f}")
                        else:
                            st.info("ℹ️ No division season stats found for this opponent in tracked files.")
            
            # Update session state (disabled if game is active and locked)
            game_active_and_locked = st.session_state.game_active and game_lock_enabled and not st.session_state.get('game_unlocked', False)
            if st.button("✅ Update Lineup", type="primary", use_container_width=True, disabled=game_active_and_locked):
                for pos, player in lineup_form.items():
                    st.session_state.lineup[pos] = player
                st.success("Lineup updated!")
                st.rerun()
            
            # Show lock warning if game is active and locked
            if game_active_and_locked:
                st.warning("🔒 **Lineup is locked** - Game is active. Unlock game to edit lineup.")
            
            # Display current lineup summary
            st.markdown("---")
            st.markdown("**Current Lineup:**")
            for pos, player in st.session_state.lineup.items():
                if pos != 'subs' and player and player != "Empty":
                    st.write(f"**{pos}:** {player}")
                elif pos != 'subs':
                    st.write(f"**{pos}:** *Empty*")
            
            st.markdown("---")
            
            # Show bench players
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
            
            # Quick actions
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("💾 Save Lineup", use_container_width=True):
                    # Save lineup to CSV with formation info
                    lineup_data = []
                    for pos, player in st.session_state.lineup.items():
                        if pos != 'subs' and player and player != "Empty" and player != "Select Player...":
                            lineup_data.append({
                                'Position': pos,
                                'Player': player,
                                'Status': 'Starting',
                                'Formation': formation  # Save formation too
                            })
                    
                    if lineup_data:
                    lineup_df = pd.DataFrame(lineup_data)
                    lineup_df.to_csv("current_lineup.csv", index=False)
                        st.success(f"✅ Lineup saved! ({len(lineup_data)} players)")
                    else:
                        st.warning("⚠️ No players selected to save!")
            
            with col_b:
                if st.button("📂 Load Lineup", use_container_width=True, disabled=game_active_and_locked):
                    try:
                        saved_lineup = pd.read_csv("current_lineup.csv")
                        
                        if saved_lineup.empty:
                            st.warning("⚠️ Saved lineup file is empty!")
                        else:
                            # Clear current lineup first
                            for pos in positions:
                                st.session_state.lineup[pos] = None
                            
                            # Load saved players into their saved positions
                            loaded_count = 0
                            saved_positions = saved_lineup['Position'].tolist() if 'Position' in saved_lineup.columns else []
                            
                        for _, row in saved_lineup.iterrows():
                                if row.get('Status') == 'Starting' or 'Status' not in row:
                                    saved_pos = str(row.get('Position', ''))
                                    saved_player = str(row.get('Player', ''))
                                    
                                    # If saved position exists in current formation, use it
                                    if saved_pos in positions:
                                        st.session_state.lineup[saved_pos] = saved_player
                                        loaded_count += 1
                                    else:
                                        # Position doesn't exist in current formation - find first empty position
                                for pos in positions:
                                    if st.session_state.lineup.get(pos) is None:
                                                st.session_state.lineup[pos] = saved_player
                                                loaded_count += 1
                                        break
                            
                            if loaded_count > 0:
                                # Check if saved formation matches current formation
                                saved_formation = saved_lineup['Formation'].iloc[0] if 'Formation' in saved_lineup.columns else None
                                if saved_formation and saved_formation != formation:
                                    st.warning(f"⚠️ Saved lineup was from '{saved_formation}' formation. Positions may not match perfectly.")
                                st.success(f"✅ Lineup loaded! ({loaded_count} players) - Refresh page to see changes.")
                                st.rerun()
                            else:
                                st.error("❌ No players loaded. Check saved lineup file.")
                    except FileNotFoundError:
                        st.warning("⚠️ No saved lineup found. Save a lineup first!")
                    except Exception as e:
                        st.error(f"❌ Error loading lineup: {str(e)}")
            
            with col_c:
                if st.button("🔄 Reset Lineup", use_container_width=True, disabled=game_active_and_locked):
                    for pos in positions:
                        st.session_state.lineup[pos] = None
                    st.session_state.lineup['subs'] = []
                    st.success("Lineup reset!")
                    st.rerun()
            
            st.markdown("---")
            
            # Debug info
            st.markdown("---")
            st.markdown(f"**Debug Info:** Selected {len(selected_starters)}/7 players: {selected_starters}")
            
            # Start game button (disabled if game already active and locked)
            if st.button("🚀 START GAME", type="primary", use_container_width=True, disabled=game_active_and_locked):
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
                    
                    # Auto-log game start to chat (TeamSnap-style)
                    log_to_chat('GAME_START', {'game_data': st.session_state.game_data})
                    
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
        
        # Check if game lock mode is enabled
        game_lock_enabled = load_game_config()
        game_is_locked = game_lock_enabled and st.session_state.game_active and not st.session_state.get('game_unlocked', False)
        
        # Initialize unlock request if not set
        if 'unlock_requested' not in st.session_state:
            st.session_state.unlock_requested = False
        
        # Header with scores
        st.markdown(f"""
        <div style="font-size: 48px; font-weight: bold; text-align: center; padding: 20px; margin: 20px 0;">
            DSX <span style="color: #667eea;">{dsx_score}</span> - 
            <span style="color: #f093fb;">{opp_score}</span> {game_data['opponent']}
        </div>
        """, unsafe_allow_html=True)
        
        # Timer
        half_text = "FIRST HALF" if st.session_state.current_half == 1 else "SECOND HALF"
        
        # Create a placeholder for the timer that can be updated
        timer_placeholder = st.empty()

        # Calculate current time remaining (based on elapsed time since start)
        current_time = time.time()
        if st.session_state.timer_running and st.session_state.timer_start_time:
            # Calculate elapsed time since timer started, minus paused time
            elapsed = current_time - st.session_state.timer_start_time - st.session_state.total_paused_time
            if st.session_state.pause_start_time:
                # Currently paused, subtract current pause time
                elapsed -= (current_time - st.session_state.pause_start_time)
            st.session_state.time_remaining = max(0, int((game_data['half_length'] * 60) - elapsed))

        # Display timer with current state
        timer_status = "running" if st.session_state.timer_running else "paused"
        timer_color = "#667eea" if st.session_state.timer_running else "#ff6b6b"

        timer_html = f"""
        <div style="font-size: 72px; font-weight: bold; text-align: center; padding: 30px; background: linear-gradient(135deg, {timer_color} 0%, #764ba2 100%); border-radius: 20px; color: white; margin: 20px 0; transition: background 0.3s ease;">
            ⏱️ {half_text}<br>
            <span id="timer-display">{format_time(st.session_state.time_remaining)}</span>
        </div>

        <script>
        (function() {{
            // Initialize timer state in window object (persists across Streamlit reruns)
            if (typeof window.dsxTimerState === 'undefined') {{
                window.dsxTimerState = {{
                    timeRemaining: {st.session_state.time_remaining},
                    timerStatus: "{timer_status}",
                    startTime: null,
                    lastSyncTime: Date.now(),
                    syncInterval: 15000  // Sync with Python every 15 seconds
                }};
            }} else {{
                // Update from Python state (when status changes or after sync interval)
                const timeSinceSync = Date.now() - window.dsxTimerState.lastSyncTime;
                if (timeSinceSync >= window.dsxTimerState.syncInterval || 
                    window.dsxTimerState.timerStatus !== "{timer_status}") {{
                    window.dsxTimerState.timeRemaining = {st.session_state.time_remaining};
                    window.dsxTimerState.timerStatus = "{timer_status}";
                    window.dsxTimerState.lastSyncTime = Date.now();
                    
                    // Reset start time if timer just started
                    if ("{timer_status}" === "running" && window.dsxTimerState.timerStatus !== "running") {{
                        window.dsxTimerState.startTime = Date.now();
                    }}
                }}
            }}
            
            const timerDisplay = document.getElementById('timer-display');
            const timerContainer = timerDisplay.parentElement;
            let lastMinuteAlerted = false;
            let halftimeAlerted = false;
            
            function formatTime(seconds) {{
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return mins.toString().padStart(2, '0') + ':' + secs.toString().padStart(2, '0');
            }}
            
            function updateTimer() {{
                const state = window.dsxTimerState;
                
                // Update time remaining if timer is running
                if (state.timerStatus === "running" && state.timeRemaining > 0) {{
                    // Decrement by 1 second (setInterval runs every 1000ms)
                    state.timeRemaining = Math.max(0, state.timeRemaining - 1);
                }}
                
                // Update display
                timerDisplay.textContent = formatTime(state.timeRemaining);
                
                // Visual feedback when time is low
                if (state.timeRemaining <= 60) {{
                    timerContainer.style.background = "linear-gradient(135deg, #ff4757 0%, #ff3838 100%)";
                    timerContainer.style.animation = "pulse 1s infinite";
                    
                    if (!lastMinuteAlerted) {{
                        lastMinuteAlerted = true;
                        // Optional: play alert sound
                    }}
                }} else if (state.timeRemaining <= 300) {{
                    timerContainer.style.background = "linear-gradient(135deg, #ffa726 0%, #fb8c00 100%)";
                }} else {{
                    timerContainer.style.background = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
                }}
                
                // Auto-sync with Python periodically (triggers Streamlit rerun)
                if (state.timerStatus === "running" && state.timeRemaining > 0) {{
                    const timeSinceSync = Date.now() - state.lastSyncTime;
                    if (timeSinceSync >= state.syncInterval) {{
                        // Trigger Streamlit rerun to sync with Python state
                        setTimeout(function() {{
                            // Use Streamlit's rerun mechanism
                            if (window.parent.streamlitApi) {{
                                window.parent.streamlitApi.rerun();
                            }} else {{
                                // Fallback: reload page for sync
                                window.location.reload();
                            }}
                        }}, 100);
                    }}
                }}
                
                // Check for end of half/game
                if (state.timeRemaining === 0 && state.timerStatus === "running") {{
                    // Trigger Streamlit rerun to handle end of half
                    setTimeout(function() {{
                        window.location.reload();
                    }}, 1000);
                }}
            }}
            
            // Update display immediately
            timerDisplay.textContent = formatTime(window.dsxTimerState.timeRemaining);
            
            // Start smooth countdown interval (updates every second)
            setInterval(updateTimer, 1000);
            
            // Add CSS for pulse animation
            if (!document.getElementById('dsx-timer-styles')) {{
                const style = document.createElement('style');
                style.id = 'dsx-timer-styles';
                style.textContent = `
                    @keyframes pulse {{
                        0% {{ transform: scale(1); opacity: 1; }}
                        50% {{ transform: scale(1.03); opacity: 0.95; }}
                        100% {{ transform: scale(1); opacity: 1; }}
                    }}
                `;
                document.head.appendChild(style);
            }}
        }})();
        </script>
        """

        timer_placeholder.markdown(timer_html, unsafe_allow_html=True)
        
        # Timer controls
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("▶️ Start" if not st.session_state.timer_running else "⏸️ Pause", 
                         use_container_width=True):
                if not st.session_state.timer_running:
                    # Starting timer
                    st.session_state.timer_running = True
                    if not st.session_state.timer_start_time:
                        # First start - initialize
                        st.session_state.timer_start_time = current_time
                        st.session_state.total_paused_time = 0
                        st.session_state.pause_start_time = None
                    else:
                        # Resuming from pause
                        if st.session_state.pause_start_time:
                            st.session_state.total_paused_time += (current_time - st.session_state.pause_start_time)
                            st.session_state.pause_start_time = None
                else:
                    # Pausing timer
                    st.session_state.timer_running = False
                    st.session_state.pause_start_time = current_time
                save_live_game_state()
                st.rerun()
        
        # Show timer status
        if st.session_state.timer_running:
            st.success("⏱️ Timer running - Enter details while clock continues")
        
        with col2:
            if st.button("⏭️ Next Half", use_container_width=True, disabled=game_is_locked):
                if st.session_state.current_half == 1:
                    st.session_state.current_half = 2
                    st.session_state.time_remaining = game_data['half_length'] * 60
                    st.session_state.timer_running = False
                    st.session_state.timer_start_time = None
                    st.session_state.total_paused_time = 0
                    st.session_state.pause_start_time = None
                    add_event_tracker('HALF_TIME', notes="Half time break")
                    save_live_game_state()
                    st.rerun()
        
        with col3:
            if st.button("🔄 Reset Timer", use_container_width=True, disabled=game_is_locked):
                st.session_state.time_remaining = game_data['half_length'] * 60
                st.session_state.timer_running = False
                st.session_state.timer_start_time = None
                st.session_state.total_paused_time = 0
                st.session_state.pause_start_time = None
                st.rerun()
        
        with col4:
            if st.button("⏹️ End Game", use_container_width=True, type="primary"):
                st.session_state.game_active = False
                st.session_state.show_summary = True
                st.rerun()
        
        with col5:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Show lock status and unlock option
        if game_is_locked:
            st.warning("🔒 **Game Locked** - Lineup and timer settings are locked. Only game actions can be recorded.")
            
            # Unlock button with confirmation
            if not st.session_state.unlock_requested:
                if st.button("🔓 Unlock Game (Testing)", use_container_width=True, type="secondary"):
                    st.session_state.unlock_requested = True
                    st.rerun()
            else:
                st.error("⚠️ **Unlock Confirmation**")
                st.write("Unlocking allows editing game settings and lineup. Are you sure?")
                col_unlock1, col_unlock2 = st.columns(2)
                with col_unlock1:
                    if st.button("✅ Yes, Unlock", use_container_width=True, type="primary"):
                        st.session_state.game_unlocked = True  # Flag to bypass lock
                        st.session_state.unlock_requested = False
                        st.success("✅ Game unlocked for this session")
                        st.rerun()
                with col_unlock2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.unlock_requested = False
                        st.rerun()
            
            # Update game_is_locked if unlocked
            if st.session_state.get('game_unlocked', False):
                game_is_locked = False
        
        # Auto-save every 15 seconds for live viewing (non-blocking)
            if 'last_auto_save' not in st.session_state:
            st.session_state.last_auto_save = current_time
        if current_time - st.session_state.last_auto_save > 15:
                save_live_game_state()
            st.session_state.last_auto_save = current_time
        
        # Check if half is complete
        if st.session_state.timer_running and st.session_state.time_remaining <= 0:
                st.session_state.timer_running = False
            st.session_state.timer_start_time = None
            st.session_state.total_paused_time = 0
            st.session_state.pause_start_time = None
                save_live_game_state()
                st.balloons()
                st.success(f"{half_text} Complete!")
        
        # Auto-sync timer state with Python (JavaScript handles smooth countdown)
        # Only sync periodically to avoid excessive Streamlit reruns
        # JavaScript timer updates display every second, Python syncs every 15 seconds
        if st.session_state.timer_running and st.session_state.time_remaining > 0:
            # Track last sync to avoid excessive reruns
            if 'last_timer_sync' not in st.session_state:
                st.session_state.last_timer_sync = current_time
            
            # Sync every 15 seconds (JavaScript handles smooth countdown between syncs)
            time_since_sync = current_time - st.session_state.last_timer_sync
            sync_interval = 15.0  # 15 seconds - Python syncs, JavaScript updates smoothly
            
            # Only sync if interval passed (JavaScript timer handles the smooth countdown)
            if time_since_sync >= sync_interval:
                st.session_state.last_timer_sync = current_time
                # Save state before sync
                save_live_game_state()
                # Trigger sync (JavaScript will update from Python state)
                st.rerun()
        
        st.markdown("---")
        
        # BIG BUTTON DASHBOARD
        st.subheader("🎮 Quick Actions")
        
        # Row 1: DSX GOAL, OPP GOAL
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⚽ DSX GOAL", use_container_width=True, type="primary", key="dsx_goal_btn"):
                st.session_state.show_goal_dialog = True
                # Reset timer refresh to prevent auto-refresh during dialog
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with col2:
            if st.button("🥅 OPP GOAL", use_container_width=True, key="opp_goal_btn"):
                add_event_tracker('OPP_GOAL')
                # Reset timer refresh
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        # Row 2: SHOT, PASS
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🎯 SHOT", use_container_width=True, key="shot_btn"):
                st.session_state.show_shot_dialog = True
                # Reset timer refresh
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with col4:
            if st.button("➡️ PASS", use_container_width=True, key="pass_btn"):
                st.session_state.show_pass_dialog = True
                # Reset timer refresh
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        # Player selection area - appears between SHOT/PASS and SAVE/CORNER/SUB rows
        # SHOT and PASS dialogs appear here (below their buttons)
        if 'show_shot_dialog' in st.session_state and st.session_state.show_shot_dialog:
            st.markdown('<div class="live-game-dialog">', unsafe_allow_html=True)
            st.subheader("🎯 SHOT ON GOAL")
            on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
            
            # Initialize shot selections if not set
            if 'shot_player' not in st.session_state:
                st.session_state.shot_player = None
            if 'shot_outcome' not in st.session_state:
                st.session_state.shot_outcome = None
            if 'shot_type' not in st.session_state:
                st.session_state.shot_type = None
            if 'shot_location' not in st.session_state:
                st.session_state.shot_location = None
            
            # Shooter - Large Button Grid (AUTO-SAVES on selection)
            st.write("**Who took the shot?**")
            if on_field_players.empty:
                st.warning("No players on field!")
            else:
                num_cols = min(3, len(on_field_players))
                shooter_cols = st.columns(num_cols)
                for idx, (_, row) in enumerate(on_field_players.iterrows()):
                    with shooter_cols[idx % num_cols]:
                        player_display = f"#{int(row['PlayerNumber'])} {row['PlayerName']}"
                        if st.button(player_display, use_container_width=True,
                                   type="primary" if st.session_state.shot_player == player_display else "secondary",
                                   key=f"shot_player_{int(row['PlayerNumber'])}"):
                            st.session_state.shot_player = player_display
                            # Auto-save immediately when player is selected
                            player_name = player_display.split(' ', 1)[1] if ' ' in player_display else player_display
                            add_event_tracker('SHOT', player=player_name, notes="")
                            update_player_stats_live('SHOT', player=player_name)
                save_live_game_state()
                st.rerun()
        
            if st.session_state.shot_player:
                st.success(f"✅ Shooter: {st.session_state.shot_player}")
            
            st.markdown("---")
            
            # Shot Outcome - Large Box Buttons (OPTIONAL - AUTO-SAVES on selection)
            st.write("**Outcome (Optional):**")
            outcome_cols = st.columns(3)
            with outcome_cols[0]:
                if st.button("⚽ ON TARGET", use_container_width=True,
                           type="primary" if st.session_state.shot_outcome == "⚽ On Target" else "secondary",
                           key="shot_outcome_target"):
                    st.session_state.shot_outcome = "⚽ On Target"
                    # Auto-update existing shot event notes
                    _update_last_shot_event()
                    save_live_game_state()
                    st.rerun()
            with outcome_cols[1]:
                if st.button("❌ OFF TARGET", use_container_width=True,
                           type="primary" if st.session_state.shot_outcome == "❌ Off Target" else "secondary",
                           key="shot_outcome_off"):
                    st.session_state.shot_outcome = "❌ Off Target"
                    # Auto-update existing shot event notes
                    _update_last_shot_event()
                    save_live_game_state()
                    st.rerun()
            with outcome_cols[2]:
                if st.button("🛡️ BLOCKED", use_container_width=True,
                           type="primary" if st.session_state.shot_outcome == "🛡️ Blocked" else "secondary",
                           key="shot_outcome_blocked"):
                    st.session_state.shot_outcome = "🛡️ Blocked"
                    # Auto-update existing shot event notes
                    _update_last_shot_event()
                    save_live_game_state()
                    st.rerun()
            
            if st.session_state.shot_outcome:
                st.success(f"✅ Outcome: {st.session_state.shot_outcome}")
            
            st.markdown("---")
            
            # Shot Type - Large Box Buttons (OPTIONAL - AUTO-SAVES on selection)
            st.write("**Type (Optional):**")
            type_cols = st.columns(3)
            with type_cols[0]:
                if st.button("👟 RIGHT FOOT", use_container_width=True,
                           type="primary" if st.session_state.shot_type == "👟 Right Foot" else "secondary",
                           key="shot_type_right"):
                    st.session_state.shot_type = "👟 Right Foot"
                    # Auto-update existing shot event notes
                    _update_last_shot_event()
                    save_live_game_state()
                    st.rerun()
            with type_cols[1]:
                if st.button("👟 LEFT FOOT", use_container_width=True,
                           type="primary" if st.session_state.shot_type == "👟 Left Foot" else "secondary",
                           key="shot_type_left"):
                    st.session_state.shot_type = "👟 Left Foot"
                    # Auto-update existing shot event notes
                    _update_last_shot_event()
                    save_live_game_state()
                    st.rerun()
            with type_cols[2]:
                if st.button("🤕 HEADER", use_container_width=True,
                           type="primary" if st.session_state.shot_type == "🤕 Header" else "secondary",
                           key="shot_type_header"):
                    st.session_state.shot_type = "🤕 Header"
                    # Auto-update existing shot event notes
                    _update_last_shot_event()
                    save_live_game_state()
                st.rerun()
        
            if st.session_state.shot_type:
                st.success(f"✅ Type: {st.session_state.shot_type}")
            
            st.markdown("---")
            
            # Shot Location - Large Box Buttons (OPTIONAL)
            st.write("**Location (Optional):**")
            loc_cols = st.columns(5)
            locations = [
                ("⬆️ TOP", "⬆️ Top"),
                ("⬇️ BOTTOM", "⬇️ Bottom"),
                ("⬅️ LEFT", "⬅️ Left"),
                ("➡️ RIGHT", "➡️ Right"),
                ("🎯 CENTER", "🎯 Center")
            ]
            for idx, (btn_text, display_text) in enumerate(locations):
                with loc_cols[idx]:
                    if st.button(btn_text, use_container_width=True,
                               type="primary" if st.session_state.shot_location == display_text else "secondary",
                               key=f"shot_location_{idx}"):
                        st.session_state.shot_location = display_text
                        # Auto-update existing shot event notes
                        _update_last_shot_event()
                save_live_game_state()
                st.rerun()
        
            if st.session_state.shot_location:
                st.success(f"✅ Location: {st.session_state.shot_location}")
            
        st.markdown("---")
            
            # Notes (optional)
            if 'shot_notes' not in st.session_state:
                st.session_state.shot_notes = ""
            notes = st.text_input("Notes (optional)", value=st.session_state.shot_notes, key="shot_notes_input")
            if notes != st.session_state.shot_notes:
                st.session_state.shot_notes = notes
            
            st.markdown("---")
            
            # Close button (no RECORD button needed - auto-saves on each selection)
            if st.button("✅ Done / Close", use_container_width=True, type="primary", key="close_shot_btn"):
                # Final update before closing
                if st.session_state.shot_player:
                    _update_last_shot_event()
                    save_live_game_state()
                # Reset selections
                st.session_state.shot_player = None
                st.session_state.shot_outcome = None
                st.session_state.shot_type = None
                st.session_state.shot_location = None
                st.session_state.shot_notes = ""
                st.session_state.show_shot_dialog = False
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = time.time()
                st.rerun()
        
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Pass dialog
        if 'show_pass_dialog' in st.session_state and st.session_state.show_pass_dialog:
            st.markdown('<div class="live-game-dialog">', unsafe_allow_html=True)
            st.subheader("➡️ PASS")
            on_field_players = roster_tracker[roster_tracker['PlayerNumber'].isin(st.session_state.on_field)]
            
            # Initialize selected players if not set
            if 'pass_from_player' not in st.session_state:
                st.session_state.pass_from_player = None
            if 'pass_to_player' not in st.session_state:
                st.session_state.pass_to_player = None
            if 'pass_complete_status' not in st.session_state:
                st.session_state.pass_complete_status = None
            
            # From Player - Large Button Grid
            st.write("**From Player:**")
            if on_field_players.empty:
                st.warning("No players on field!")
            else:
                # Create grid of large player buttons (2-3 columns on mobile)
                num_cols = min(3, len(on_field_players))
                from_cols = st.columns(num_cols)
                for idx, (_, row) in enumerate(on_field_players.iterrows()):
                    with from_cols[idx % num_cols]:
                        player_display = f"#{int(row['PlayerNumber'])} {row['PlayerName']}"
                        if st.button(player_display, use_container_width=True, 
                                   type="primary" if st.session_state.pass_from_player == player_display else "secondary",
                                   key=f"pass_from_{int(row['PlayerNumber'])}"):
                            st.session_state.pass_from_player = player_display
                            # Auto-save will happen when "To Player" is selected
                st.rerun()
        
            # Show selected from player
            if st.session_state.pass_from_player:
                st.success(f"✅ From: {st.session_state.pass_from_player}")
            
            st.markdown("---")
            
            # To Player - Large Button Grid
            st.write("**To Player:**")
            if on_field_players.empty:
                st.warning("No players on field!")
            else:
                # Create grid of large player buttons
                to_cols = st.columns(num_cols)
                for idx, (_, row) in enumerate(on_field_players.iterrows()):
                    with to_cols[idx % num_cols]:
                        player_display = f"#{int(row['PlayerNumber'])} {row['PlayerName']}"
                        # Don't allow same player for from and to
                        if st.session_state.pass_from_player and player_display == st.session_state.pass_from_player:
                            st.button(f"⚠️ {player_display}", use_container_width=True, disabled=True, 
                                    key=f"pass_to_disabled_{int(row['PlayerNumber'])}")
                        else:
                            if st.button(player_display, use_container_width=True,
                                       type="primary" if st.session_state.pass_to_player == player_display else "secondary",
                                       key=f"pass_to_{int(row['PlayerNumber'])}"):
                                st.session_state.pass_to_player = player_display
                                # Auto-save immediately when both players are selected
                                if st.session_state.pass_from_player and st.session_state.pass_to_player:
                                    player_from_name = st.session_state.pass_from_player.split(' ', 1)[1] if ' ' in st.session_state.pass_from_player else st.session_state.pass_from_player
                                    player_to_name = player_display.split(' ', 1)[1] if ' ' in player_display else player_display
                                    pass_complete = None
                                    if st.session_state.pass_complete_status:
                                        pass_complete = (st.session_state.pass_complete_status == "Complete")
                                    pass_notes = f"To: {player_to_name}"
                                    add_event_tracker('PASS', player=player_from_name, pass_to=player_to_name, 
                                                     pass_complete=pass_complete, notes=pass_notes)
                                    update_player_stats_live('PASS', player=player_from_name, pass_to=player_to_name, pass_complete=pass_complete)
                                    save_live_game_state()
                st.rerun()
        
            # Show selected to player
            if st.session_state.pass_to_player:
                st.success(f"✅ To: {st.session_state.pass_to_player}")
            
            st.markdown("---")
            
            # Complete/Incomplete - Large Box Buttons (OPTIONAL)
            st.write("**Pass Result (Optional):**")
            result_col1, result_col2 = st.columns(2)
            with result_col1:
                if st.button("✅ COMPLETE", use_container_width=True, 
                           type="primary" if st.session_state.pass_complete_status == "Complete" else "secondary",
                           key="pass_complete_btn"):
                    st.session_state.pass_complete_status = "Complete"
                    # Auto-update existing pass event
                    _update_last_pass_event()
                    save_live_game_state()
                st.rerun()
        
            with result_col2:
                if st.button("❌ INCOMPLETE", use_container_width=True,
                           type="primary" if st.session_state.pass_complete_status == "Incomplete" else "secondary",
                           key="pass_incomplete_btn"):
                    st.session_state.pass_complete_status = "Incomplete"
                    # Auto-update existing pass event
                    _update_last_pass_event()
                        save_live_game_state()
                        st.rerun()
        
            # Show selected status
            if st.session_state.pass_complete_status:
                status_text = "✅ Complete" if st.session_state.pass_complete_status == "Complete" else "❌ Incomplete"
                st.success(f"✅ Result: {status_text}")
            
            st.markdown("---")
            
            # Notes (optional)
            if 'pass_notes' not in st.session_state:
                st.session_state.pass_notes = ""
            notes = st.text_input("Notes (optional)", value=st.session_state.pass_notes, 
                                 placeholder="e.g., through ball, cross, etc.",
                                 key="pass_notes_input")
            if notes != st.session_state.pass_notes:
                st.session_state.pass_notes = notes
            
            st.markdown("---")
            
            # Close button (no RECORD button needed - auto-saves on each selection)
            if st.button("✅ Done / Close", use_container_width=True, type="primary", key="close_pass_btn"):
                # Final update before closing
                if st.session_state.pass_from_player and st.session_state.pass_to_player:
                    _update_last_pass_event()
                        save_live_game_state()
                # Reset selections
                st.session_state.pass_from_player = None
                st.session_state.pass_to_player = None
                st.session_state.pass_complete_status = None
                st.session_state.pass_notes = ""
                st.session_state.show_pass_dialog = False
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = time.time()
                        st.rerun()
        
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Save dialog - appears above SAVE/CORNER/SUB buttons
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
        
        # Sub dialog - appears above SAVE/CORNER/SUB buttons
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
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            if st.button("🧤 SAVE", use_container_width=True, key="save_btn"):
                st.session_state.show_save_dialog = True
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with col6:
            if st.button("⚠️ CORNER", use_container_width=True, key="corner_btn"):
                add_event_tracker('CORNER')
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with col7:
            if st.button("🔄 SUB", use_container_width=True, key="sub_btn"):
                st.session_state.show_sub_dialog = True
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        col7, col8, col9 = st.columns(3)
        
        with col7:
            if st.button("↩️ UNDO", use_container_width=True, type="secondary", key="undo_btn"):
                if st.session_state.events:
                    last_event = st.session_state.events.pop(0)
                    st.success(f"✅ Undid: {last_event['type']}")
                    if 'last_timer_refresh' in st.session_state:
                        st.session_state.last_timer_refresh = current_time
                    save_live_game_state()
                    st.rerun()
                else:
                    st.error("No events to undo!")
        
        with col8:
            if st.button("📝 NOTE", use_container_width=True, key="note_btn"):
                st.session_state.show_note_dialog = True
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with col9:
            if st.button("🚨 TIMEOUT", use_container_width=True, key="timeout_btn"):
                add_event_tracker('TIMEOUT', notes="Injury/timeout")
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                if st.session_state.timer_running:
                    st.session_state.timer_running = False
                    st.session_state.pause_start_time = current_time
                st.rerun()
        
        # Goalkeeper Actions Section
        st.markdown("---")
        st.markdown("### 🧤 Goalkeeper Actions")
        gk_col1, gk_col2, gk_col3, gk_col4 = st.columns(4)
        
        with gk_col1:
            if st.button("✋ CATCH", use_container_width=True, key="catch_btn"):
                st.session_state.show_catch_dialog = True
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with gk_col2:
            if st.button("👊 PUNCH", use_container_width=True, key="punch_btn"):
                st.session_state.show_punch_dialog = True
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with gk_col3:
            if st.button("🦶 DISTRIBUTION", use_container_width=True, key="dist_btn"):
                st.session_state.show_dist_dialog = True
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
                st.rerun()
        
        with gk_col4:
            if st.button("🧹 CLEARANCE", use_container_width=True, key="clear_btn"):
                st.session_state.show_clear_dialog = True
                if 'last_timer_refresh' in st.session_state:
                    st.session_state.last_timer_refresh = current_time
                save_live_game_state()
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
                        player_name = scorer.split(' ', 1)[1] if ' ' in scorer else scorer
                        assist_name = assist.split(' ', 1)[1] if assist != "None" and ' ' in assist else (None if assist == "None" else assist)
                        add_event_tracker('DSX_GOAL', player=player_name, assist=assist_name, notes=notes)
                        # Stats are updated automatically in add_event_tracker()
                        if 'last_timer_refresh' in st.session_state:
                            st.session_state.last_timer_refresh = time.time()
                        save_live_game_state()
                        st.session_state.show_goal_dialog = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_goal_dialog = False
                        st.rerun()
        
        # Dialogs have been moved to appear between button rows for better UX
        # SHOT, PASS, SAVE, SUB dialogs now appear between their respective button rows
        # Only Goalkeeper dialogs (Catch, Punch, Distribution, Clearance) remain below
        
        # Goalkeeper Actions Section - Dialogs appear below
        
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
    
    # Show comprehensive rankings option
    col1, col2 = st.columns(2)
    with col1:
        st.info("📊 **See how DSX ranks among your peers - teams that also play tournament schedules like DSX.**")
    with col2:
        if st.button("🔄 Refresh Rankings Data", use_container_width=True):
            # Run the ranking generation script
            import subprocess
            import sys
            try:
                result = subprocess.run([sys.executable, "create_comprehensive_rankings.py"], 
                                       capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    st.success("✅ Rankings updated successfully!")
                    st.cache_data.clear()  # Clear cache to reload data
                    st.rerun()
                else:
                    st.error(f"Error updating rankings: {result.stderr}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Show comprehensive rankings section
    st.markdown("---")
    st.header("📊 Comprehensive Rankings")
    
    # Load comprehensive rankings - separated by year
    ranking_tabs = st.tabs(["2018 Teams (3+ games)", "2018 Teams (6+ games)", "2017 Teams (3+ games)", "All Teams Combined"])
    
    with ranking_tabs[0]:  # 2018 Teams (3+ games)
        if os.path.exists("Rankings_2018_Teams_3Plus_Games.csv"):
            try:
                rankings_2018 = pd.read_csv("Rankings_2018_Teams_3Plus_Games.csv", index_col=False)
                
                # Find DSX position
                dsx_row = rankings_2018[rankings_2018['Team'].str.contains('DSX', case=False, na=False)]
                if not dsx_row.empty:
                    dsx_rank = int(dsx_row.iloc[0]['Rank'])
                    total_teams = len(rankings_2018)
                    
                    st.metric("DSX Position", f"#{dsx_rank} of {total_teams} teams", 
                             f"PPG: {dsx_row.iloc[0]['PPG']:.2f}, SI: {dsx_row.iloc[0]['StrengthIndex']:.1f}")
                    st.caption("2018 teams with 3+ games (includes tournament teams)")
                
                # Display rankings table
                st.subheader(f"📋 2018 Teams Rankings ({len(rankings_2018)} teams)")
                
                # Format for display
                display_df = rankings_2018.copy()
                display_df['Team'] = display_df.apply(
                    lambda row: f"🟢 **{row['Team']}**" if 'DSX' in str(row['Team']) else row['Team'],
                    axis=1
                )
                
                st.dataframe(
                    display_df[['Rank', 'Team', 'GP', 'W', 'L', 'D', 'GF', 'GA', 'GD', 'PPG', 'StrengthIndex']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Team": st.column_config.TextColumn("Team"),
                        "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                        "PPG": st.column_config.NumberColumn("PPG", help="Points Per Game", format="%.2f"),
                        "StrengthIndex": st.column_config.ProgressColumn("Strength", format="%.1f", min_value=0, max_value=100),
                    }
                )
            except Exception as e:
                st.error(f"Error loading 2018 rankings: {e}")
        else:
            st.warning("2018 rankings file not found. Click 'Refresh Rankings Data' to generate it.")
    
    with ranking_tabs[1]:  # 2018 Teams (6+ games)
        if os.path.exists("Rankings_2018_Teams_6Plus_Games.csv"):
            try:
                rankings_2018_6plus = pd.read_csv("Rankings_2018_Teams_6Plus_Games.csv", index_col=False)
                
                # Find DSX position
                dsx_row = rankings_2018_6plus[rankings_2018_6plus['Team'].str.contains('DSX', case=False, na=False)]
                if not dsx_row.empty:
                    dsx_rank = int(dsx_row.iloc[0]['Rank'])
                    total_teams = len(rankings_2018_6plus)
                    
                    st.metric("DSX Position", f"#{dsx_rank} of {total_teams} teams", 
                             f"PPG: {dsx_row.iloc[0]['PPG']:.2f}, SI: {dsx_row.iloc[0]['StrengthIndex']:.1f}")
                    st.caption("2018 teams with 6+ games (most accurate - full league seasons)")
                
                # Display rankings table
                st.subheader(f"🏆 2018 Teams Rankings - 6+ Games ({len(rankings_2018_6plus)} teams)")
                
                # Format for display
                display_df = rankings_2018_6plus.copy()
                display_df['Team'] = display_df.apply(
                    lambda row: f"🟢 **{row['Team']}**" if 'DSX' in str(row['Team']) else row['Team'],
                    axis=1
                )
                
                st.dataframe(
                    display_df[['Rank', 'Team', 'GP', 'W', 'L', 'D', 'GF', 'GA', 'GD', 'PPG', 'StrengthIndex']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Team": st.column_config.TextColumn("Team"),
                        "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                        "PPG": st.column_config.NumberColumn("PPG", help="Points Per Game", format="%.2f"),
                        "StrengthIndex": st.column_config.ProgressColumn("Strength", format="%.1f", min_value=0, max_value=100),
                    }
                )
            except Exception as e:
                st.error(f"Error loading 2018 rankings (6+ games): {e}")
        else:
            st.warning("2018 rankings (6+ games) file not found. Click 'Refresh Rankings Data' to generate it.")
    
    with ranking_tabs[2]:  # 2017 Teams (3+ games)
        if os.path.exists("Rankings_2017_Teams_3Plus_Games.csv"):
            try:
                rankings_2017 = pd.read_csv("Rankings_2017_Teams_3Plus_Games.csv", index_col=False)
                
                st.metric("Total Teams", len(rankings_2017), "2017 and 17/18 teams")
                st.caption("2017 teams with 3+ games (includes 17/18 mixed-age teams)")
                
                # Display rankings table
                st.subheader(f"📋 2017 Teams Rankings ({len(rankings_2017)} teams)")
                
                st.dataframe(
                    rankings_2017[['Rank', 'Team', 'GP', 'W', 'L', 'D', 'GF', 'GA', 'GD', 'PPG', 'StrengthIndex']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Team": st.column_config.TextColumn("Team"),
                        "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                        "PPG": st.column_config.NumberColumn("PPG", help="Points Per Game", format="%.2f"),
                        "StrengthIndex": st.column_config.ProgressColumn("Strength", format="%.1f", min_value=0, max_value=100),
                    }
                )
            except Exception as e:
                st.error(f"Error loading 2017 rankings: {e}")
        else:
            st.warning("2017 rankings file not found. Click 'Refresh Rankings Data' to generate it.")
    
    with ranking_tabs[3]:  # All Teams Combined
        if os.path.exists("Comprehensive_All_Teams_Rankings.csv"):
            try:
                all_rankings = pd.read_csv("Comprehensive_All_Teams_Rankings.csv", index_col=False)
                
                # Find DSX position
                dsx_row = all_rankings[all_rankings['Team'].str.contains('DSX', case=False, na=False)]
                if not dsx_row.empty:
                    dsx_rank = int(dsx_row.iloc[0]['Rank'])
                    total_teams = len(all_rankings)
                    
                    st.metric("DSX Position", f"#{dsx_rank} of {total_teams} teams", 
                             f"PPG: {dsx_row.iloc[0]['PPG']:.2f}, SI: {dsx_row.iloc[0]['StrengthIndex']:.1f}")
                    st.caption("All teams (2018 + 2017) with 3+ games")
                
                # Display rankings table
                st.subheader(f"📋 All Teams Rankings ({len(all_rankings)} teams)")
                
                # Format for display
                display_df = all_rankings.copy()
                display_df['Team'] = display_df.apply(
                    lambda row: f"🟢 **{row['Team']}**" if 'DSX' in str(row['Team']) else row['Team'],
                    axis=1
                )
                
                st.dataframe(
                    display_df[['Rank', 'Team', 'GP', 'W', 'L', 'D', 'GF', 'GA', 'GD', 'PPG', 'StrengthIndex']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Team": st.column_config.TextColumn("Team"),
                        "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                        "PPG": st.column_config.NumberColumn("PPG", help="Points Per Game", format="%.2f"),
                        "StrengthIndex": st.column_config.ProgressColumn("Strength", format="%.1f", min_value=0, max_value=100),
                    }
                )
            except Exception as e:
                st.error(f"Error loading comprehensive rankings: {e}")
        else:
            st.warning("Comprehensive rankings file not found. Click 'Refresh Rankings Data' to generate it.")
    
    st.markdown("---")
    
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
            
            # Create DSX row (use per-game averages to match other teams)
            dsx_row = pd.DataFrame([{
                'Team': 'DSX Orange 2018',
                'GP': dsx_gp,
                'W': dsx_w,
                'D': dsx_d,
                'L': dsx_l,
                'GF': round(dsx_gf_pg, 2),  # Per-game average (not total)
                'GA': round(dsx_ga_pg, 2),  # Per-game average (not total)
                'GD': round(dsx_gd_pg, 2),  # Per-game average (not total)
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
    
    # Get unique opponents DSX has played or will play
        opponent_names = []
    
    # Load from match history
    if not dsx_matches.empty:
        opponent_names.extend([resolve_alias(n) for n in dsx_matches['Opponent'].unique().tolist()])
    
    # Load from upcoming opponents
    try:
        upcoming_opponents = pd.read_csv("DSX_Upcoming_Opponents.csv", index_col=False).reset_index(drop=True)
        # Filter for upcoming games only
        upcoming = upcoming_opponents[upcoming_opponents['Status'].str.lower() == 'upcoming']
        opponent_names.extend([resolve_alias(n) for n in upcoming['Opponent'].unique().tolist()])
    except:
        pass
    
    opponent_names = list(set(opponent_names))  # Remove duplicates
    
    # ===== PEER RANKINGS - Tournament Teams =====
    # Build peer group from tournament divisions and similar-strength teams
    peer_teams = []
    
    if not dsx_row.empty:
        st.markdown("---")
        st.header("🎯 Peer Rankings - Tournament Teams")
        st.info("💡 **This shows how DSX ranks among similar teams - those playing tournament schedules like DSX.**")
        
        # Load tournament division files (teams that play tournaments like DSX)
        tournament_files = [
            "Haunted_Classic_B08Orange_Division_Rankings.csv",
            "Haunted_Classic_B08Black_Division_Rankings.csv",
            "Club_Ohio_Fall_Classic_2025_Division_Rankings.csv",
            "CU_Fall_Finale_2025_Division_Rankings.csv",
        ]
        
        tournament_teams = []
        for tour_file in tournament_files:
            if os.path.exists(tour_file):
                try:
                    tour_df = pd.read_csv(tour_file, index_col=False)
                    if not tour_df.empty:
                        tournament_teams.append(tour_df)
                except:
                    pass
        
        if tournament_teams:
            tournament_df = pd.concat(tournament_teams, ignore_index=True)
            # Reset index to ensure no duplicates
            tournament_df = tournament_df.reset_index(drop=True)
            # Normalize column names (handle lowercase/capitalized variations)
            col_mapping = {}
            for col in tournament_df.columns:
                col_lower = col.lower()
                if col_lower == 'team':
                    col_mapping[col] = 'Team'
                elif col_lower == 'rank':
                    col_mapping[col] = 'Rank'
                elif col_lower == 'gp':
                    col_mapping[col] = 'GP'
                elif col_lower in ['w', 'l', 'd', 'gf', 'ga', 'gd', 'pts', 'ppg']:
                    col_mapping[col] = col.upper()
                elif col_lower in ['strengthindex', 'strength_index']:
                    col_mapping[col] = 'StrengthIndex'
                # Keep other columns as-is
            
            # Apply column name normalization
            if col_mapping:
                tournament_df = tournament_df.rename(columns=col_mapping)
            
            # Ensure 'Team' column exists and is string type
            if 'Team' not in tournament_df.columns:
                # Try to find a team-like column
                team_cols = [col for col in tournament_df.columns if 'team' in col.lower()]
                if team_cols:
                    tournament_df = tournament_df.rename(columns={team_cols[0]: 'Team'})
                else:
                    # Skip filtering if no Team column exists
                    pass
            
            # Remove DSX from tournament data (we'll add our own stats)
            if 'Team' in tournament_df.columns:
                try:
                    # Reset index first to avoid duplicate index issues
                    tournament_df = tournament_df.reset_index(drop=True)
                    # Convert Team column to string, handling all edge cases
                    # First ensure it's a proper Series
                    team_series = tournament_df['Team'].copy()
                    # Fill NaN and convert to string
                    team_series = team_series.fillna('').astype(str)
                    # Now try to filter
                    if len(team_series) > 0:
                        mask = team_series.str.contains('DSX', case=False, na=False)
                        tournament_df = tournament_df[~mask].copy()
                        # Reset index after filtering
                        tournament_df = tournament_df.reset_index(drop=True)
                except Exception as e:
                    # If anything goes wrong, skip DSX filtering but continue
                    # The app should still work without this filter
                    pass
            
            # Filter out teams with empty or missing team names
            if 'Team' in tournament_df.columns:
                try:
                    # Reset index to avoid duplicate index issues
                    tournament_df = tournament_df.reset_index(drop=True)
                    tournament_df = tournament_df[tournament_df['Team'].notna()].copy()
                    tournament_df = tournament_df.reset_index(drop=True)
                    tournament_df = tournament_df[tournament_df['Team'].astype(str).str.strip() != ''].copy()
                    tournament_df = tournament_df.reset_index(drop=True)
                except Exception as e:
                    # If filtering fails, continue with original data
                    pass
            
            # Filter out teams with zero games played (they haven't started tournament yet)
            try:
                if 'GP' in tournament_df.columns and len(tournament_df) > 0:
                    # Ensure GP column is a Series before converting
                    gp_series = tournament_df['GP'].copy()
                    tournament_df['GP'] = pd.to_numeric(gp_series, errors='coerce').fillna(0)
                    # Reset index before filtering
                    tournament_df = tournament_df.reset_index(drop=True)
                    tournament_df = tournament_df[tournament_df['GP'] > 0].copy()
                    tournament_df = tournament_df.reset_index(drop=True)
                else:
                    # If no GP column, create one with 1 to keep all teams
                    tournament_df['GP'] = 1
            except Exception as e:
                # If GP processing fails, just set GP to 1 for all teams
                tournament_df['GP'] = 1
            
            # Double-check: remove any rows where GP is still 0 or team name is empty
            try:
                tournament_df = tournament_df.reset_index(drop=True)
                if 'Team' in tournament_df.columns and 'GP' in tournament_df.columns and len(tournament_df) > 0:
                    tournament_df = tournament_df[
                        (tournament_df['GP'] > 0) & 
                        (tournament_df['Team'].notna()) & 
                        (tournament_df['Team'].astype(str).str.strip() != '')
                    ].copy()
                    tournament_df = tournament_df.reset_index(drop=True)
            except Exception as e:
                # If filtering fails, just continue with what we have
                pass
            
            # Get DSX strength for peer filtering
            dsx_si = dsx_row.iloc[0]['StrengthIndex'] if not dsx_row.empty else 0
            
            # Filter for peer teams (similar strength: within 25 points of DSX)
            # Also include all tournament teams regardless of strength (they're tournament players like DSX)
            if not tournament_df.empty:
                # Include all tournament teams (they're all peers by definition - tournament players)
                peer_df = tournament_df.copy()
                
                # Filter out any rows with missing team names or GP=0 (shouldn't happen but double-check)
                try:
                    peer_df = peer_df.reset_index(drop=True)
                    if 'Team' in peer_df.columns and 'GP' in peer_df.columns and len(peer_df) > 0:
                        # Ensure Team column is string type
                        team_series = peer_df['Team'].fillna('').astype(str)
                        # Create safe filter conditions
                        team_not_empty = (team_series.str.strip() != '')
                        gp_valid = (peer_df['GP'] > 0)
                        peer_df = peer_df[team_not_empty & gp_valid].copy()
                        peer_df = peer_df.reset_index(drop=True)
                except Exception as e:
                    # If filtering fails, just use what we have
                    pass
                
                # Calculate per-game stats for tournament teams
                for idx, row in peer_df.iterrows():
                    try:
                        # Get and convert GP to float safely
                        gp_val = row.get('GP', 0)
                        gp_num = pd.to_numeric(gp_val, errors='coerce')
                        # Convert to scalar float - handle both Series and scalar
                        if hasattr(gp_num, 'iloc'):
                            gp_float = float(gp_num.iloc[0]) if len(gp_num) > 0 else 0
                        elif hasattr(gp_num, '__iter__') and not isinstance(gp_num, str):
                            gp_float = float(gp_num[0]) if len(gp_num) > 0 else 0
                        else:
                            gp_float = float(gp_num) if not pd.isna(gp_num) else 0
                        
                        # Check if valid
                        if gp_float != gp_float or gp_float <= 0:  # NaN check: gp_float != gp_float
                            continue  # Skip this row - invalid GP
                        gp = gp_float
                    except (ValueError, TypeError, AttributeError, IndexError):
                        continue  # Skip this row - couldn't parse GP
                    
                    try:
                        # Get and convert GF safely
                        gf_val_raw = row.get('GF', 0)
                        gf_num = pd.to_numeric(gf_val_raw, errors='coerce')
                        if hasattr(gf_num, 'iloc'):
                            gf_val = float(gf_num.iloc[0]) if len(gf_num) > 0 else 0
                        elif hasattr(gf_num, '__iter__') and not isinstance(gf_num, str):
                            gf_val = float(gf_num[0]) if len(gf_num) > 0 else 0
                        else:
                            gf_val = float(gf_num) if not pd.isna(gf_num) else 0
                    except (ValueError, TypeError, AttributeError, IndexError):
                        gf_val = 0
                    
                    try:
                        # Get and convert GA safely
                        ga_val_raw = row.get('GA', 0)
                        ga_num = pd.to_numeric(ga_val_raw, errors='coerce')
                        if hasattr(ga_num, 'iloc'):
                            ga_val = float(ga_num.iloc[0]) if len(ga_num) > 0 else 0
                        elif hasattr(ga_num, '__iter__') and not isinstance(ga_num, str):
                            ga_val = float(ga_num[0]) if len(ga_num) > 0 else 0
                        else:
                            ga_val = float(ga_num) if not pd.isna(ga_num) else 0
                    except (ValueError, TypeError, AttributeError, IndexError):
                        ga_val = 0
                    
                    gd_val = gf_val - ga_val
                    
                    peer_df.at[idx, 'GF_PG'] = gf_val / gp if gp > 0 else 0
                    peer_df.at[idx, 'GA_PG'] = ga_val / gp if gp > 0 else 0
                    peer_df.at[idx, 'GD_PG'] = gd_val / gp if gp > 0 else 0
                    peer_df.at[idx, 'IsDSX'] = False
                    
                    # Ensure required columns exist
                    if 'PPG' not in peer_df.columns:
                        peer_df['PPG'] = 0.0
                    
                    # Check PPG safely - convert to scalar first
                    try:
                        ppg_val = peer_df.at[idx, 'PPG']
                        # Convert to scalar float if it's a Series
                        if hasattr(ppg_val, 'iloc'):
                            ppg_float = float(ppg_val.iloc[0]) if len(ppg_val) > 0 else 0
                        elif hasattr(ppg_val, '__iter__') and not isinstance(ppg_val, (str, bytes)):
                            ppg_float = float(ppg_val[0]) if len(ppg_val) > 0 else 0
                        else:
                            ppg_float = float(ppg_val) if not (ppg_val != ppg_val) else 0  # NaN check
                        
                        if ppg_float != ppg_float or ppg_float == 0:  # NaN or zero
                            # Calculate PPG
                            w = row.get('W', 0)
                            d = row.get('D', 0)
                            w_num = pd.to_numeric(w, errors='coerce')
                            d_num = pd.to_numeric(d, errors='coerce')
                            w_float = float(w_num) if not (w_num != w_num) else 0
                            d_float = float(d_num) if not (d_num != d_num) else 0
                            pts = (w_float * 3) + d_float
                            peer_df.at[idx, 'PPG'] = pts / gp if gp > 0 else 0
                    except (ValueError, TypeError, AttributeError, IndexError):
                        # If PPG check fails, calculate it
                        try:
                            w = row.get('W', 0)
                            d = row.get('D', 0)
                            w_num = pd.to_numeric(w, errors='coerce')
                            d_num = pd.to_numeric(d, errors='coerce')
                            w_float = float(w_num) if not (w_num != w_num) else 0
                            d_float = float(d_num) if not (d_num != d_num) else 0
                            pts = (w_float * 3) + d_float
                            peer_df.at[idx, 'PPG'] = pts / gp if gp > 0 else 0
                        except:
                            peer_df.at[idx, 'PPG'] = 0
                    
                    if 'StrengthIndex' not in peer_df.columns:
                        peer_df['StrengthIndex'] = 0.0
                    
                    # Check StrengthIndex safely
                    try:
                        si_val = peer_df.at[idx, 'StrengthIndex']
                        # Convert to scalar float if it's a Series
                        if hasattr(si_val, 'iloc'):
                            si_float = float(si_val.iloc[0]) if len(si_val) > 0 else 0
                        elif hasattr(si_val, '__iter__') and not isinstance(si_val, (str, bytes)):
                            si_float = float(si_val[0]) if len(si_val) > 0 else 0
                        else:
                            si_float = float(si_val) if not (si_val != si_val) else 0  # NaN check
                        
                        if si_float != si_float or si_float == 0:  # NaN or zero
                            # Calculate Strength Index if missing
                            try:
                                ppg_raw = peer_df.at[idx, 'PPG'] if 'PPG' in peer_df.columns else 0
                                # Convert PPG to scalar
                                if hasattr(ppg_raw, 'iloc'):
                                    ppg = float(ppg_raw.iloc[0]) if len(ppg_raw) > 0 else 0
                                elif hasattr(ppg_raw, '__iter__') and not isinstance(ppg_raw, (str, bytes)):
                                    ppg = float(ppg_raw[0]) if len(ppg_raw) > 0 else 0
                                else:
                                    ppg = float(ppg_raw) if not (ppg_raw != ppg_raw) else 0
                                
                                gd_pg_raw = peer_df.at[idx, 'GD_PG']
                                # Convert GD_PG to scalar
                                if hasattr(gd_pg_raw, 'iloc'):
                                    gd_pg = float(gd_pg_raw.iloc[0]) if len(gd_pg_raw) > 0 else 0
                                elif hasattr(gd_pg_raw, '__iter__') and not isinstance(gd_pg_raw, (str, bytes)):
                                    gd_pg = float(gd_pg_raw[0]) if len(gd_pg_raw) > 0 else 0
                                else:
                                    gd_pg = float(gd_pg_raw) if not (gd_pg_raw != gd_pg_raw) else 0
                                
                                ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
                                gdpg_norm = (max(-5.0, min(5.0, gd_pg)) + 5.0) / 10.0 * 100.0
                                peer_df.at[idx, 'StrengthIndex'] = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
                            except (ValueError, TypeError, AttributeError, IndexError):
                                peer_df.at[idx, 'StrengthIndex'] = 0
                    except (ValueError, TypeError, AttributeError, IndexError):
                        # If check fails, try to calculate Strength Index
                        try:
                            ppg = 0
                            gd_pg = 0
                            if 'PPG' in peer_df.columns:
                                ppg_raw = peer_df.at[idx, 'PPG']
                                if hasattr(ppg_raw, 'iloc'):
                                    ppg = float(ppg_raw.iloc[0]) if len(ppg_raw) > 0 else 0
                                else:
                                    ppg = float(ppg_raw) if not (ppg_raw != ppg_raw) else 0
                            if 'GD_PG' in peer_df.columns:
                                gd_pg_raw = peer_df.at[idx, 'GD_PG']
                                if hasattr(gd_pg_raw, 'iloc'):
                                    gd_pg = float(gd_pg_raw.iloc[0]) if len(gd_pg_raw) > 0 else 0
                                else:
                                    gd_pg = float(gd_pg_raw) if not (gd_pg_raw != gd_pg_raw) else 0
                            ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
                            gdpg_norm = (max(-5.0, min(5.0, gd_pg)) + 5.0) / 10.0 * 100.0
                            peer_df.at[idx, 'StrengthIndex'] = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
                        except:
                            peer_df.at[idx, 'StrengthIndex'] = 0
                
                # Final cleanup: remove any rows with missing team names or invalid data
                try:
                    peer_df = peer_df.reset_index(drop=True)
                    if 'Team' in peer_df.columns and 'GP' in peer_df.columns and len(peer_df) > 0:
                        # Ensure Team column is string type
                        team_series = peer_df['Team'].fillna('').astype(str)
                        # Create safe filter conditions
                        team_not_empty = (team_series.str.strip() != '')
                        gp_valid = (peer_df['GP'] > 0)
                        peer_df = peer_df[team_not_empty & gp_valid].copy()
                        peer_df = peer_df.reset_index(drop=True)
                except Exception as e:
                    # If filtering fails, just use what we have
                    pass
                
                # Add DSX to peer group
                try:
                    # Reset indexes before concat to avoid duplicate index errors
                    peer_df = peer_df.reset_index(drop=True)
                    dsx_peer_row = dsx_row.copy().reset_index(drop=True)
                    peer_df = pd.concat([peer_df, dsx_peer_row], ignore_index=True)
                    peer_df = peer_df.reset_index(drop=True)
                except Exception as e:
                    # If concat fails, just use peer_df without DSX (shouldn't happen but safe)
                    pass
                
                # Sort by PPG then Strength Index (safely check columns exist)
                try:
                    peer_df = peer_df.reset_index(drop=True)
                    sort_cols = []
                    if 'PPG' in peer_df.columns:
                        sort_cols.append('PPG')
                    if 'StrengthIndex' in peer_df.columns:
                        sort_cols.append('StrengthIndex')
                    
                    if sort_cols:
                        peer_df = peer_df.sort_values(sort_cols, ascending=[False] * len(sort_cols)).reset_index(drop=True)
                    else:
                        peer_df = peer_df.reset_index(drop=True)
                    
                    peer_df['Rank'] = range(1, len(peer_df) + 1)
                except Exception as e:
                    # If sorting fails, just assign ranks in order
                    peer_df = peer_df.reset_index(drop=True)
                    peer_df['Rank'] = range(1, len(peer_df) + 1)
                
                # Final check: ensure no empty team names made it through
                try:
                    peer_df = peer_df.reset_index(drop=True)
                    if 'Team' in peer_df.columns and len(peer_df) > 0:
                        # Ensure Team column is string type
                        team_series = peer_df['Team'].fillna('').astype(str)
                        # Create safe filter condition
                        team_not_empty = (team_series.str.strip() != '')
                        peer_df = peer_df[team_not_empty].copy()
                        peer_df = peer_df.reset_index(drop=True)
                except Exception as e:
                    # If filtering fails, just use what we have
                    pass
                
                # Get DSX rank in peer group
                dsx_peer_rank = peer_df[peer_df['IsDSX'] == True]
                if not dsx_peer_rank.empty:
                    dsx_peer_rank_num = int(dsx_peer_rank['Rank'].values[0])
                    total_peers = len(peer_df)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("DSX Peer Rank", f"#{dsx_peer_rank_num} of {total_peers}", 
                                 f"{'Top tier' if dsx_peer_rank_num <= total_peers * 0.33 else 'Mid tier' if dsx_peer_rank_num <= total_peers * 0.67 else 'Building'}")
                    with col2:
                        st.metric("Peer Group Size", total_peers, "Tournament teams")
                    with col3:
                        st.metric("DSX Strength", f"{dsx_si:.1f}", 
                                 f"{'Strong' if dsx_si > 60 else 'Solid' if dsx_si > 40 else 'Building'}")
                    
                    # Display peer rankings table
                    st.markdown("---")
                    st.subheader("📊 Peer Rankings Table")
                    st.caption("Teams playing tournament schedules (like DSX) - ranked by PPG and Strength Index")
                    
                    # Format for display
                    display_peer_df = peer_df.copy()
                    display_peer_df['Team'] = display_peer_df.apply(
                        lambda row: f"🟢 **{row['Team']}**" if row['IsDSX'] else row['Team'],
                        axis=1
                    )
                    
                    # Round numeric columns
                    display_peer_df['PPG'] = display_peer_df['PPG'].round(2)
                    display_peer_df['StrengthIndex'] = display_peer_df['StrengthIndex'].round(1)
                    
                    # Select columns to display
                    peer_cols = ['Rank', 'Team', 'GP', 'W', 'L', 'D', 'PPG', 'StrengthIndex']
                    available_cols = [col for col in peer_cols if col in display_peer_df.columns]
                    
                    st.dataframe(
                        display_peer_df[available_cols],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                            "Team": st.column_config.TextColumn("Team"),
                            "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                            "W": st.column_config.NumberColumn("W", help="Wins"),
                            "L": st.column_config.NumberColumn("L", help="Losses"),
                            "D": st.column_config.NumberColumn("D", help="Draws"),
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
                    
                    st.success(f"✅ **DSX ranks #{dsx_peer_rank_num} of {total_peers} among tournament-playing peer teams!**")
                    
                    # Show tournament breakdown
                    st.markdown("---")
                    st.subheader("🏆 Tournament Breakdown")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Tournaments Tracked:**")
                        tournaments = []
                        if os.path.exists("Haunted_Classic_B08Orange_Division_Rankings.csv"):
                            tournaments.append("🎃 Haunted Classic")
                        if os.path.exists("Haunted_Classic_B08Black_Division_Rankings.csv"):
                            tournaments.append("🎃 Haunted Classic (Black)")
                        if os.path.exists("Club_Ohio_Fall_Classic_2025_Division_Rankings.csv"):
                            tournaments.append("🏅 Club Ohio Fall Classic")
                        if os.path.exists("CU_Fall_Finale_2025_Division_Rankings.csv"):
                            tournaments.append("🏆 CU Fall Finale")
                        
                        for tour in tournaments:
                            st.write(f"  • {tour}")
                        
                    with col2:
                        st.write("**Peer Group Insights:**")
                        peers_above = len(peer_df[peer_df['Rank'] < dsx_peer_rank_num])
                        peers_below = len(peer_df[peer_df['Rank'] > dsx_peer_rank_num])
                        st.write(f"  • {peers_above} teams above DSX")
                        st.write(f"  • {peers_below} teams below DSX")
                        
                        if dsx_peer_rank_num <= total_peers * 0.5:
                            st.success("🎯 DSX is in the **top half** of tournament teams!")
                        elif dsx_peer_rank_num <= total_peers * 0.75:
                            st.info("📈 DSX is in the **middle tier** of tournament teams")
                        else:
                            st.warning("📊 DSX is **building** - room to climb in peer rankings")
            
            else:
                st.info("💡 **No tournament division data yet.** Once you play more tournaments, this will show your rank among other tournament teams.")
        else:
            st.info("💡 **Tournament data coming soon!** As DSX plays more tournaments, this section will show your rank among other tournament-playing teams.")
    
    st.markdown("---")
    st.header("📋 Rankings vs Opponents (Played & Upcoming)")
    
    # Load division data
    df = load_division_data()
    
    # Helper function to normalize team names for matching
    def normalize_name(name):
        """Normalize team name for matching (strip, lower, remove extra spaces)"""
        if pd.isna(name):
            return ""
        return ' '.join(str(name).strip().split()).lower()
    
    # Build opponent rankings - include ALL teams DSX has played/will play
    # For teams with division data, use that. For others, use head-to-head stats only
    opponent_df = pd.DataFrame()
    matched_opponents = {}  # Map original opponent name -> matched team name
    
    # Load DSX match history to calculate head-to-head stats for unmatched teams
    try:
        actual_opponents = pd.read_csv("DSX_Actual_Opponents.csv", index_col=False)
    except:
        actual_opponents = pd.DataFrame()
    
    # First, try to match teams to division data
    if not df.empty and opponent_names:
        # Try exact match first (case-insensitive)
        for opp_name in opponent_names:
            opp_name = resolve_alias(opp_name)
            opp_normalized = normalize_name(opp_name)
            
            # Try exact match
            for idx, row in df.iterrows():
                team_normalized = normalize_name(row['Team'])
                if team_normalized == opp_normalized:
                    if opp_name not in matched_opponents:
                        matched_opponents[opp_name] = row['Team']
                        if opponent_df.empty:
                            opponent_df = df.iloc[[idx]].copy()
                        else:
                            opponent_df = pd.concat([opponent_df, df.iloc[[idx]]], ignore_index=True)
                    break
            
            # If no exact match, try partial/fuzzy matching
            if opp_name not in matched_opponents:
                # Extract key words (minimum 3 characters)
                opp_words = [w for w in opp_normalized.split() if len(w) > 3]
                
                best_match = None
                best_score = 0
                
                for idx, row in df.iterrows():
                    team_normalized = normalize_name(row['Team'])
                    team_words = [w for w in team_normalized.split() if len(w) > 3]
                    
                    # Count matching words
                    match_score = sum(1 for word in opp_words if word in team_normalized)
                    match_score += sum(1 for word in team_words if word in opp_normalized)
                    
                    if match_score >= 2 and match_score > best_score:
                        best_score = match_score
                        best_match = row['Team']
                
                if best_match:
                    matched_opponents[opp_name] = best_match
                    matched_row = df[df['Team'] == best_match]
                    if not matched_row.empty:
                        if opponent_df.empty:
                            opponent_df = matched_row.copy()
                        else:
                            opponent_df = pd.concat([opponent_df, matched_row], ignore_index=True)
    
    # Remove duplicates (same team matched from multiple opponent names)
    if not opponent_df.empty:
        opponent_df = opponent_df.drop_duplicates(subset=['Team'], keep='first')
    
    # Add ALL remaining opponents using head-to-head stats (even if not in division data)
    matched_set = set(matched_opponents.values())
    unmatched_opponents = [opp for opp in opponent_names if opp not in matched_set]
    
    if unmatched_opponents and not dsx_matches.empty:
        for opp_name in unmatched_opponents:
            # Get stats from head-to-head matches with DSX
            opp_matches = dsx_matches[dsx_matches['Opponent'] == opp_name].copy()
            
            if not opp_matches.empty:
                # Calculate opponent stats from games vs DSX (perspective: goals they scored/allowed)
                opp_gp = len(opp_matches)
                opp_gf = pd.to_numeric(opp_matches['GA'], errors='coerce').fillna(0).sum()  # Goals they scored = DSX's GA
                opp_ga = pd.to_numeric(opp_matches['GF'], errors='coerce').fillna(0).sum()  # Goals they allowed = DSX's GF
                opp_gd = opp_gf - opp_ga
                
                # Calculate W/D/L from opponent's perspective
                opp_w = len(opp_matches[opp_matches['Outcome'] == 'L'])  # Opponent wins = DSX losses
                opp_l = len(opp_matches[opp_matches['Outcome'] == 'W'])  # Opponent losses = DSX wins
                opp_d = len(opp_matches[opp_matches['Outcome'] == 'D'])  # Draws are same
                
                opp_pts = (opp_w * 3) + opp_d
                opp_ppg = opp_pts / opp_gp if opp_gp > 0 else 0
                opp_gf_pg = opp_gf / opp_gp if opp_gp > 0 else 0
                opp_ga_pg = opp_ga / opp_gp if opp_gp > 0 else 0
                opp_gd_pg = opp_gd / opp_gp if opp_gp > 0 else 0
                
                # Calculate basic Strength Index from head-to-head
                ppg_norm = max(0.0, min(3.0, opp_ppg)) / 3.0 * 100.0
                gdpg_norm = (max(-5.0, min(5.0, opp_gd_pg)) + 5.0) / 10.0 * 100.0
                opp_strength = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
                
                # Create opponent row with head-to-head stats
                opp_row = pd.DataFrame([{
                    'Team': opp_name,
                    'GP': opp_gp,
                    'W': opp_w,
                    'D': opp_d,
                    'L': opp_l,
                    'GF': round(opp_gf_pg, 2),  # Per-game average
                    'GA': round(opp_ga_pg, 2),  # Per-game average
                    'GD': round(opp_gd_pg, 2),  # Per-game average
                    'Pts': opp_pts,
                    'PPG': opp_ppg,
                    'GF_PG': opp_gf_pg,
                    'GA_PG': opp_ga_pg,
                    'GD_PG': opp_gd_pg,
                    'StrengthIndex': opp_strength,
                    'IsDSX': False,
                    'League/Division': 'Head-to-Head vs DSX Only',
                    'SourceURL': 'DSX_Matches_Fall2025.csv'
                }])
                
                if opponent_df.empty:
                    opponent_df = opp_row.copy()
                            else:
                    opponent_df = pd.concat([opponent_df, opp_row], ignore_index=True)
    
    # Show matching summary (collapsed by default)
    if not dsx_row.empty and opponent_names:
        matched_count = len(opponent_df)
        total_opponents = len(opponent_names)
        
        if matched_count > 0:
            with st.expander(f"✅ Found {matched_count} of {total_opponents} opponents in division data", expanded=False):
                st.success(f"**Matched Teams:** {matched_count}/{total_opponents}")
                
                # Show matched teams
                if matched_opponents:
                    st.write("**Matched opponents:**")
                    for orig, matched in matched_opponents.items():
                        if orig == matched:
                            st.write(f"  ✅ {orig}")
            else:
                            st.write(f"  ⚠️ {orig} → {matched} (fuzzy match)")
                
                # Show unmatched
                matched_set = set(matched_opponents.keys())
                unmatched = [opp for opp in opponent_names if opp not in matched_set]
                if unmatched:
                    st.warning(f"**Unmatched opponents ({len(unmatched)}):**")
                    for opp in unmatched:
                        st.write(f"  ❌ {opp}")
                    st.caption("These teams may not be in tracked divisions or need better name matching.")
        
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
            
            # Standardize GF, GA, GD to per-game values for consistent display
            # (Some CSVs have totals, some have per-game - make them all per-game)
            opponent_df['GF'] = opponent_df['GF_PG']  # Always use per-game
            opponent_df['GA'] = opponent_df['GA_PG']  # Always use per-game
            opponent_df['GD'] = opponent_df['GD_PG']  # Always use per-game
            
            # Combine DSX with opponents
            combined_df = pd.concat([dsx_row, opponent_df], ignore_index=True)

            # Clean up: remove invalid/empty rows and incomplete placeholders
            # 1) Drop rows without a valid team name
            combined_df = combined_df[combined_df['Team'].astype(str).str.strip() != ""]

            # 2) Prefer to show teams with real data. Keep head-to-head entries even if small sample.
            #    Drop rows where GP == 0 and not a head-to-head constructed row
            try:
                ld_col = 'League/Division' if 'League/Division' in combined_df.columns else None
                if ld_col:
                    combined_df = combined_df[~((combined_df['GP'].fillna(0) == 0) & (~combined_df[ld_col].astype(str).str.contains('Head-to-Head', case=False, na=False)) & (~combined_df['IsDSX']))]
                else:
                    combined_df = combined_df[~((combined_df['GP'].fillna(0) == 0) & (~combined_df['IsDSX']))]
            except Exception:
                pass
            
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
                
                # Tournament-specific results section
                st.subheader("🏆 Tournament Results")
                
                # Check for Haunted Classic results
                haunted_opponents = []
                if not dsx_matches.empty:
                    haunted_games = dsx_matches[dsx_matches['Tournament'] == '2025 Haunted Classic']
                    if not haunted_games.empty:
                        haunted_opponents = haunted_games['Opponent'].tolist()
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("### 🎃 2025 Haunted Classic")
                            st.write("**DSX Performance:**")
                            haunted_w = len(haunted_games[haunted_games['Outcome'] == 'W'])
                            haunted_l = len(haunted_games[haunted_games['Outcome'] == 'L'])
                            haunted_d = len(haunted_games[haunted_games['Outcome'] == 'D'])
                            st.write(f"Record: {haunted_w}-{haunted_l}-{haunted_d}")
                            
                            haunted_gf = haunted_games['GF'].sum()
                            haunted_ga = haunted_games['GA'].sum()
                            st.write(f"Goals: {haunted_gf}-{haunted_ga}")
                        
                        with col2:
                            st.markdown("### 🥇 Division Standings")
                            # Show Haunted Classic division standings
                            try:
                                haunted_orange = pd.read_csv("Haunted_Classic_B08Orange_Division_Rankings.csv")
                                dsx_in_division = haunted_orange[haunted_orange['Team'].str.contains('DSX', case=False)]
                                if not dsx_in_division.empty:
                                    dsx_rank = dsx_in_division.iloc[0]['Rank']
                                    total_teams = len(haunted_orange)
                                    st.write(f"**DSX Rank: #{int(dsx_rank)} of {total_teams}**")
                                    st.write(f"Strength Index: {dsx_in_division.iloc[0]['StrengthIndex']:.1f}")
                                else:
                                    st.write("DSX not found in division data")
                            except:
                                st.write("Division data unavailable")
                        
                        with col3:
                            st.markdown("### 🎯 Key Matchups")
                            for idx, game in haunted_games.iterrows():
                                opponent = game['Opponent']
                                gf = game['GF']
                                ga = game['GA']
                                outcome = game['Outcome']
                                date = game['Date']
                                
                                if outcome == 'W':
                                    icon = "✅"
                                    color = "success"
                                elif outcome == 'D':
                                    icon = "➖"
                                    color = "info"
                                else:
                                    icon = "❌"
                                    color = "error"
                                
                                st.write(f"{icon} **{date}**: {opponent}")
                                st.write(f"   DSX {gf}-{ga} ({outcome})")
                
                st.markdown("---")
                
                # Rankings table
                st.subheader(f"📊 Rankings - DSX vs {len(opponent_df)} Opponents (2018+ teams only)")
                st.caption("Ranked by Points Per Game (PPG), then Strength Index. All stats shown are per-game averages for fair comparison.")
                
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
                        "GF": st.column_config.NumberColumn("GF", help="Goals For (Per Game Average)", format="%.2f"),
                        "GA": st.column_config.NumberColumn("GA", help="Goals Against (Per Game Average)", format="%.2f"),
                        "GD": st.column_config.NumberColumn("GD", help="Goal Differential (Per Game Average)", format="%+.2f"),
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
                
                # Team Details Selector
                st.markdown("---")
                st.subheader("🔍 View Team Details")
                
                # Get list of teams (clean names, without bold formatting)
                team_list = combined_df['Team'].tolist()
                # Clean team names for selector (remove bold formatting)
                clean_team_names = [team.replace('🟢 **', '').replace('**', '') if '**' in str(team) else str(team) for team in team_list]
                
                selected_team_idx = st.selectbox(
                    "Select a team to view detailed information:",
                    options=range(len(clean_team_names)),
                    format_func=lambda x: f"#{combined_df.iloc[x]['Rank']} - {clean_team_names[x]}",
                    key="rankings_team_selector"
                )
                
                if selected_team_idx is not None:
                    selected_team_row = combined_df.iloc[selected_team_idx]
                    selected_team_name = clean_team_names[selected_team_idx]
                    
                    st.markdown("---")
                    st.header(f"📊 {selected_team_name} - Full Details")
                    
                    # Show basic stats
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Rank", f"#{int(selected_team_row['Rank'])}")
                        st.metric("Games Played", int(selected_team_row['GP']))
                    
                    with col2:
                        st.metric("Record", f"{int(selected_team_row['W'])}-{int(selected_team_row['L'])}-{int(selected_team_row['D'])}")
                        st.metric("Points", int(selected_team_row['Pts']))
                    
                    with col3:
                        st.metric("PPG", f"{selected_team_row['PPG']:.2f}")
                        st.metric("Strength Index", f"{selected_team_row['StrengthIndex']:.1f}")
                    
                    with col4:
                        st.metric("Goals/Game", f"{selected_team_row['GF']:.2f}")
                        st.metric("Goals Against/Game", f"{selected_team_row['GA']:.2f}")
                        st.metric("Goal Diff/Game", f"{selected_team_row['GD']:+.2f}")
                    
                    # Show three-stat snapshot (League Season + Tournament + H2H vs DSX)
                    try:
                        dsx_matches_for_team_details = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
                    except:
                        dsx_matches_for_team_details = pd.DataFrame()
                    
                    team_snapshot = get_opponent_three_stat_snapshot(selected_team_name, df, dsx_matches_for_team_details)
                    if team_snapshot:
                        display_opponent_three_stat_snapshot(team_snapshot, selected_team_name)
                    else:
                        st.info(f"📊 Scouting data not yet available for {selected_team_name}")
                    
                    # Show full season history if available in division data
                    st.markdown("---")
                    st.subheader("📈 Full Season History")
                    
                    # Try to find team in division data
                    if not df.empty:
                        opp_division_row = df[df['Team'] == selected_team_name].copy()
                        
                        # Try fuzzy matching if no exact match
                        if opp_division_row.empty:
                            selected_normalized = normalize_name(selected_team_name)
                            for idx, row in df.iterrows():
                                team_normalized = normalize_name(row['Team'])
                                if team_normalized == selected_normalized:
                                    opp_division_row = df.iloc[[idx]]
                                    break
                        
                        # Try fuzzy match
                        if opp_division_row.empty:
                            selected_normalized = normalize_name(selected_team_name)
                            opp_words = [w for w in selected_normalized.split() if len(w) > 3]
                            matches = []
                            for idx, row in df.iterrows():
                                team_normalized = normalize_name(row['Team'])
                                match_score = sum(1 for word in opp_words if word in team_normalized)
                                if match_score >= 2:
                                    matches.append((match_score, idx, row['Team']))
                            if matches:
                                matches.sort(reverse=True)
                                best_match_idx = matches[0][1]
                                opp_division_row = df.iloc[[best_match_idx]]
                        
                        if not opp_division_row.empty:
                            opp_full = opp_division_row.iloc[0]
                            
                            # Division/League info
                            division_name = opp_full.get('Division', opp_full.get('League/Division', 'Unknown'))
                            league_name = opp_full.get('League', opp_full.get('League/Division', 'Unknown'))
                            source_url = opp_full.get('SourceURL', 'N/A')
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**League:** {league_name}")
                                st.write(f"**Division:** {division_name}")
                                if source_url != 'N/A':
                                    st.write(f"**Source:** [View Division Data]({source_url})")
                            
                            with col2:
                                # Performance assessment
                                opp_ppg_full = opp_full.get('PPG', 0)
                                if opp_ppg_full >= 2.0:
                                    st.success("🔥 **Strong Season** - Top tier performance")
                                elif opp_ppg_full >= 1.5:
                                    st.info("👍 **Good Season** - Solid performance")
                                elif opp_ppg_full >= 1.0:
                                    st.warning("📊 **Average Season** - Competitive level")
                                else:
                                    st.error("⚠️ **Struggling Season** - Below average")
                            
                            # Goals analysis
                            st.markdown("---")
                            st.subheader("⚽ Goals Analysis")
                            
                            opp_gp_full = opp_full.get('GP', 1)
                            opp_gf_full = opp_full.get('GF', 0)
                            opp_ga_full = opp_full.get('GA', 0)
                            
                            # Handle totals vs per-game
                            if opp_gp_full > 0:
                                if opp_gf_full > 10:
                                    opp_gf_pg_full = opp_gf_full / opp_gp_full
                                else:
                                    opp_gf_pg_full = opp_gf_full
                                
                                if opp_ga_full > 10:
                                    opp_ga_pg_full = opp_ga_full / opp_gp_full
                                else:
                                    opp_ga_pg_full = opp_ga_full
                            else:
                                opp_gf_pg_full = 0
                                opp_ga_pg_full = 0
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Goals For:** {opp_gf_pg_full:.2f} per game")
                                if opp_gf_pg_full >= 3.0:
                                    st.success("🔥 High scoring team - strong attack")
                                elif opp_gf_pg_full >= 2.0:
                                    st.info("⚽ Moderate scoring - decent attack")
                                else:
                                    st.warning("📉 Low scoring - offensive struggles")
                            
                            with col2:
                                st.write(f"**Goals Against:** {opp_ga_pg_full:.2f} per game")
                                if opp_ga_pg_full <= 1.0:
                                    st.success("🛡️ Strong defense - tough to score on")
                                elif opp_ga_pg_full <= 2.0:
                                    st.info("⚠️ Average defense - some gaps")
                                else:
                                    st.warning("🛡️ Weak defense - scoring opportunities")
                        else:
                            st.info("💡 This team's data comes from head-to-head matches with DSX only.")
                            st.write("**Data Source:** DSX Match History")
                            st.write(f"**Games vs DSX:** {int(selected_team_row['GP'])}")
                    
                    # DSX vs This Team Head-to-Head
                    st.markdown("---")
                    st.subheader("⚔️ DSX vs This Team - Head-to-Head")
                    
                    if not dsx_matches.empty:
                        h2h_games = dsx_matches[dsx_matches['Opponent'] == selected_team_name].copy()
                        
                        if not h2h_games.empty:
                            dsx_wins = len(h2h_games[h2h_games['Outcome'] == 'W'])
                            dsx_draws = len(h2h_games[h2h_games['Outcome'] == 'D'])
                            dsx_losses = len(h2h_games[h2h_games['Outcome'] == 'L'])
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("DSX Record", f"{dsx_wins}-{dsx_draws}-{dsx_losses}")
                            
                            dsx_h2h_gf = h2h_games['GF'].sum()
                            dsx_h2h_ga = h2h_games['GA'].sum()
                            
                            with col2:
                                st.metric("Goals Scored", f"{dsx_h2h_gf:.0f}")
                            
                            with col3:
                                st.metric("Goals Against", f"{dsx_h2h_ga:.0f}")
                            
                            st.markdown("---")
                            st.subheader("📅 Game-by-Game History")
                            
                            for idx, game in h2h_games.iterrows():
                                date = game['Date']
                                tournament = game.get('Tournament', 'N/A')
                                gf = game['GF']
                                ga = game['GA']
                                outcome = game['Outcome']
                                
                                if outcome == 'W':
                                    icon = "✅"
                                    color = "success"
                                elif outcome == 'D':
                                    icon = "➖"
                                    color = "info"
                                else:
                                    icon = "❌"
                                    color = "error"
                                
                                st.write(f"{icon} **{date}** - {tournament}")
                                st.write(f"   DSX {gf} - {ga} {selected_team_name} ({outcome})")
                                st.write("")
                        else:
                            st.info("No head-to-head history yet.")
                    
                    else:
                        st.info("No match history available.")
                
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
        
        # Add all opponents DSX has played (even if not in divisions)
        try:
            matches = pd.read_csv("DSX_Matches_Fall2025.csv")
            for opp in matches['Opponent'].dropna().unique():
                # Try to match opponent to division data first (with aliases and fuzzy matching)
                opp_resolved = resolve_alias(opp)
                opp_normalized = normalize_name(opp_resolved)
                
                matched_to_division = False
                # Check if already in teams_with_data (exact match or alias)
                for team in teams_with_data:
                    if team == opp or team == opp_resolved:
                        matched_to_division = True
                        break
                    if normalize_name(team) == opp_normalized:
                        matched_to_division = True
                        break
                
                # If not matched to division data, try fuzzy matching in df
                if not matched_to_division and not df.empty:
                    opp_normalized = normalize_name(opp_resolved)
                    opp_words = [w for w in opp_normalized.split() if len(w) > 3]
                    
                    for idx, row in df.iterrows():
                        team_normalized = normalize_name(str(row.get('Team', '')))
                        team_words = [w for w in team_normalized.split() if len(w) > 3]
                        
                        match_score = sum(1 for word in opp_words if word in team_normalized)
                        match_score += sum(1 for word in team_words if word in opp_normalized)
                        
                        if match_score >= 2:
                            matched_to_division = True
                            break
                
                # Only create basic opponent entry if NOT matched to division data
                if not matched_to_division and opp not in teams_with_data:
                    # Create a basic opponent entry with limited data
                    opp_matches = matches[matches['Opponent'] == opp]
                    opp_w = len(opp_matches[opp_matches['Outcome'] == 'W'])
                    opp_d = len(opp_matches[opp_matches['Outcome'] == 'D'])
                    opp_l = len(opp_matches[opp_matches['Outcome'] == 'L'])
                    opp_gf = opp_matches['GF'].sum()
                    opp_ga = opp_matches['GA'].sum()
                    opp_gd = opp_gf - opp_ga
                    opp_pts = (opp_w * 3) + opp_d
                    opp_gp = len(opp_matches)
                    opp_ppg = opp_pts / opp_gp if opp_gp > 0 else 0
                    opp_gf_pg = opp_gf / opp_gp if opp_gp > 0 else 0
                    opp_ga_pg = opp_ga / opp_gp if opp_gp > 0 else 0
                    opp_gd_pg = opp_gd / opp_gp if opp_gp > 0 else 0
                    
                    # Calculate basic strength index
                    ppg_norm = max(0.0, min(3.0, opp_ppg)) / 3.0 * 100.0
                    gdpg_norm = (max(-5.0, min(5.0, opp_gd_pg)) + 5.0) / 10.0 * 100.0
                    opp_strength = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
                    
                    opp_row = pd.DataFrame([{
                        'Team': opp,
                        'Rank': 999,  # Not in tracked division
                        'StrengthIndex': opp_strength,
                        'W': opp_w,
                        'L': opp_l,
                        'D': opp_d,
                        'GF': opp_gf_pg,
                        'GA': opp_ga_pg,
                        'GD': opp_gd_pg,
                        'PPG': opp_ppg,
                        'GP': opp_gp,
                        'League/Division': 'DSX Opponent (Limited Data)',
                        'SourceURL': 'DSX_Matches_Fall2025.csv'
                    }])
                    
                    df = pd.concat([df, opp_row], ignore_index=True)
                    teams_with_data.append(opp)
        except:
            pass
        
        # Update teams list after adding opponents
        teams_with_data = df['Team'].tolist()
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
        
        # Show actual results for completed games
        st.header("📊 Recent Results vs Predictions")
        
        # Load match history to show actual results
        try:
            match_history = pd.read_csv("DSX_Matches_Fall2025.csv")
            
            # Show last 7 games with predictions vs actual results (covers 2 tournaments)
            # Sort by date descending (most recent first)
            match_history_sorted = match_history.sort_values('Date', ascending=False).reset_index(drop=True)
            recent_games = match_history_sorted.head(7)  # Get most recent 7
            
            if not recent_games.empty:
                st.markdown("**Last 7 Games - Prediction vs Reality:**")
                st.caption("💡 Showing last 7 games to cover 2 full tournaments (3-4 games each)")
                st.markdown("---")
                
                for idx, game in recent_games.iterrows():
                    opponent = game['Opponent']
                    actual_gf = game['GF']
                    actual_ga = game['GA']
                    actual_outcome = game['Outcome']
                    game_date = game['Date']
                    tournament = game['Tournament']
                    
                    # Get opponent stats for prediction (with fuzzy matching and aliases)
                    opp_si = None
                    opp_gf = None
                    opp_ga = None
                    
                    if not all_divisions_df.empty:
                        # Try exact match first
                        opp_data = all_divisions_df[all_divisions_df['Team'] == opponent]
                        
                        # If no exact match, try normalized matching
                        if opp_data.empty:
                            opp_normalized = normalize_name(opponent)
                            for idx, row in all_divisions_df.iterrows():
                                team_normalized = normalize_name(str(row.get('Team', '')))
                                if opp_normalized == team_normalized:
                                    opp_data = all_divisions_df.iloc[[idx]]
                                    break
                        
                        # If still no match, try alias resolution
                        if opp_data.empty:
                            opp_resolved = resolve_alias(opponent)
                            if opp_resolved != opponent:
                                opp_data = all_divisions_df[all_divisions_df['Team'] == opp_resolved]
                        
                        if not opp_data.empty:
                            opp_si = opp_data.iloc[0]['StrengthIndex']
                            opp_gp = opp_data.iloc[0].get('GP', 1)
                            opp_gp = opp_gp if opp_gp > 0 else 1
                            opp_gf = opp_data.iloc[0].get('GF', 0) / opp_gp
                            opp_ga = opp_data.iloc[0].get('GA', 0) / opp_gp
                    
                    # Calculate what the prediction would have been
                    if opp_si is not None:
                        si_diff = dsx_si - opp_si
                        si_impact = si_diff * 0.08
                        pred_dsx_goals = max(0.5, dsx_gf_avg + si_impact)
                        pred_opp_goals = max(0.5, (opp_gf if opp_gf else dsx_ga_avg) - si_impact)
                        
                        # Ensure stronger team scores more
                        if si_diff < -5 and pred_dsx_goals >= pred_opp_goals:
                            pred_dsx_goals, pred_opp_goals = pred_opp_goals, pred_dsx_goals
                        elif si_diff > 5 and pred_opp_goals >= pred_dsx_goals:
                            pred_dsx_goals, pred_opp_goals = pred_opp_goals, pred_dsx_goals
                        
                        pred_dsx = round(pred_dsx_goals)
                        pred_opp = round(pred_opp_goals)
                        
                        # Determine if prediction was accurate
                        pred_outcome = "W" if pred_dsx > pred_opp else ("D" if pred_dsx == pred_opp else "L")
                        actual_outcome_clean = actual_outcome
                        
                        # Color coding for accuracy
                        if pred_outcome == actual_outcome_clean:
                            accuracy_color = "✅"
                            accuracy_text = "CORRECT"
                        else:
                            accuracy_color = "❌"
                            accuracy_text = "WRONG"
                        
                        # Display the comparison
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{game_date}** vs {opponent}")
                            st.caption(f"{tournament}")
                        
                        with col2:
                            st.write("**Predicted:**")
                            st.write(f"DSX {pred_dsx}-{pred_opp}")
                            st.caption(f"({pred_outcome})")
                        
                        with col3:
                            st.write("**Actual:**")
                            st.write(f"DSX {actual_gf}-{actual_ga}")
                            st.caption(f"({actual_outcome_clean})")
                        
                        with col4:
                            st.write("**Result:**")
                            st.write(f"{accuracy_color} {accuracy_text}")
                            if accuracy_color == "✅":
                                st.success("Prediction Hit!")
                            else:
                                st.error("Prediction Miss")
                        
                        st.markdown("---")
            else:
                st.info("No recent games found to compare predictions.")
                
        except Exception as e:
            st.warning(f"Could not load match history: {str(e)}")
        
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
                # Try exact match first
                opp_data = all_divisions_df[all_divisions_df['Team'] == selected_opponent]
                
                # If no exact match, try normalized matching
                if opp_data.empty:
                    opp_normalized = normalize_name(selected_opponent)
                    for idx, row in all_divisions_df.iterrows():
                        team_normalized = normalize_name(str(row.get('Team', '')))
                        if opp_normalized == team_normalized:
                            opp_data = all_divisions_df.iloc[[idx]]
                            break
                
                # If still no match, try alias resolution
                if opp_data.empty:
                    opp_resolved = resolve_alias(selected_opponent)
                    if opp_resolved != selected_opponent:
                        opp_data = all_divisions_df[all_divisions_df['Team'] == opp_resolved]
                
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
                # Enhanced Strength Index display
                st.markdown("---")
                st.subheader("⚡ Strength Index Analysis")
                
                # Create a more prominent SI display
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown("### 🏆 DSX Orange")
                    st.markdown(f"**Strength Index: {dsx_si:.1f}**")
                    st.caption(f"Goals/Game: {dsx_gf_avg:.1f}")
                    st.caption(f"Goals Against: {dsx_ga_avg:.1f}")
                
                with col_b:
                    st.markdown("### ⚔️ " + selected_opponent)
                    st.markdown(f"**Strength Index: {opp_si:.1f}**")
                    if opp_gf is not None:
                        st.caption(f"Goals/Game: {opp_gf:.1f}")
                    if opp_ga is not None:
                        st.caption(f"Goals Against: {opp_ga:.1f}")
                
                with col_c:
                    si_diff = dsx_si - opp_si
                    if si_diff > 0:
                        st.markdown("### 🎯 DSX Advantage")
                        st.markdown(f"**+{si_diff:.1f} Points**")
                        st.success("✅ We're Stronger")
                    elif si_diff < 0:
                        st.markdown("### ⚠️ Opponent Advantage")
                        st.markdown(f"**{si_diff:.1f} Points**")
                        st.warning("⚠️ They're Stronger")
                    else:
                        st.markdown("### ⚖️ Even Match")
                        st.markdown("**0.0 Points**")
                        st.info("🤝 Dead Even")
                
                # Opponent Three-Stat Snapshot (League Season + Tournament + H2H vs DSX)
                try:
                    dsx_matches_for_pred = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
                except:
                    dsx_matches_for_pred = pd.DataFrame()
                
                opponent_snapshot = get_opponent_three_stat_snapshot(selected_opponent, all_divisions_df, dsx_matches_for_pred)
                if opponent_snapshot:
                    display_opponent_three_stat_snapshot(opponent_snapshot, selected_opponent)
                else:
                    st.info(f"📊 Scouting data not yet available for {selected_opponent}")
                
                # Calculate prediction
                st.markdown("---")
                st.subheader("🔮 Score Prediction")
                
                # Improved prediction logic that properly accounts for strength differences
                # When opponent is stronger (negative si_diff), they should score more, we should score less
                # When we're stronger (positive si_diff), we should score more, they should score less
                
                # Base predictions on each team's offensive capability
                # Use more aggressive SI impact for realistic predictions
                si_impact = si_diff * 0.08  # Even stronger impact
                
                pred_dsx_goals = max(0.5, dsx_gf_avg + si_impact)
                pred_opp_goals = max(0.5, (opp_gf if opp_gf else dsx_ga_avg) - si_impact)
                
                # Track if we swapped the predictions
                swapped = False
                
                # Ensure the stronger team actually scores more goals
                if si_diff < -5:  # Opponent is significantly stronger
                    if pred_dsx_goals >= pred_opp_goals:
                        # Swap the predictions so stronger team scores more
                        pred_dsx_goals, pred_opp_goals = pred_opp_goals, pred_dsx_goals
                        swapped = True
                    # If they're much stronger, give them at least 1 more goal
                    elif pred_dsx_goals == pred_opp_goals and si_diff < -10:
                        pred_opp_goals = pred_dsx_goals + 1
                elif si_diff > 5:  # We are significantly stronger
                    if pred_opp_goals >= pred_dsx_goals:
                        # Swap the predictions so stronger team scores more
                        pred_dsx_goals, pred_opp_goals = pred_opp_goals, pred_dsx_goals
                        swapped = True
                    # If we're much stronger, give us at least 1 more goal
                    elif pred_dsx_goals == pred_opp_goals and si_diff > 10:
                        pred_dsx_goals = pred_opp_goals + 1
                
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
                
                # Enhanced score prediction display
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏆 DSX Orange")
                    st.markdown(f"## **{dsx_prediction} Goals**")
                    st.caption(f"Range: {pred_dsx_low:.1f} - {pred_dsx_high:.1f}")
                
                with col2:
                    st.markdown("### ⚔️ " + selected_opponent)
                    st.markdown(f"## **{opp_prediction} Goals**")
                    st.caption(f"Range: {pred_opp_low:.1f} - {pred_opp_high:.1f}")
                
                # Final score prediction with confidence color - better sized
                st.markdown("---")
                if confidence_style == "success":
                    st.markdown(f"### 🎯 **Final Score: DSX {dsx_prediction}-{opp_prediction} {selected_opponent}**")
                    st.success(f"**{confidence_color} Confidence: {confidence}** (range: {avg_range:.1f} goals)")
                elif confidence_style == "warning":
                    st.markdown(f"### 🎯 **Final Score: DSX {dsx_prediction}-{opp_prediction} {selected_opponent}**")
                    st.warning(f"**{confidence_color} Confidence: {confidence}** (range: {avg_range:.1f} goals)")
                else:
                    st.markdown(f"### 🎯 **Final Score: DSX {dsx_prediction}-{opp_prediction} {selected_opponent}**")
                    st.error(f"**{confidence_color} Confidence: {confidence}** (range: {avg_range:.1f} goals)")
                
                # Win probability based on rounded final predicted score
                if dsx_prediction > opp_prediction:
                    # We're predicted to win
                    goal_diff = dsx_prediction - opp_prediction
                    if goal_diff >= 2:
                        win_prob = 75
                        draw_prob = 15
                        loss_prob = 10
                    else:
                        win_prob = 60
                        draw_prob = 25
                        loss_prob = 15
                elif dsx_prediction < opp_prediction:
                    # We're predicted to lose
                    goal_diff = opp_prediction - dsx_prediction
                    if goal_diff >= 2:
                        win_prob = 15
                        draw_prob = 20
                        loss_prob = 65
                    else:
                        win_prob = 25
                        draw_prob = 30
                        loss_prob = 45
                else:
                    # Predicted draw
                    win_prob = 35
                    draw_prob = 40
                    loss_prob = 25
                
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
    
    # 2017 Boys Benchmarking Section (for friend's son)
    st.markdown("---")
    st.markdown("---")
    st.header("📊 2017 Boys Benchmarking Data")
    st.info("💡 **Benchmarking data for 2017 boys teams** - These teams won't be included in main rankings (DSX is 2018), but available for comparison/benchmarking purposes.")
    
    try:
        # Load 2017 boys benchmarking data
        benchmarking_2017_file = "OCL_BU09_7v7_Stripes_Benchmarking_2017.csv"
        if os.path.exists(benchmarking_2017_file):
            benchmarking_2017_df = pd.read_csv(benchmarking_2017_file, index_col=False)
            
            if not benchmarking_2017_df.empty:
                st.success(f"✅ Loaded {len(benchmarking_2017_df)} teams from OCL BU09 7v7 Stripes (2017 Boys)")
                
                # Show summary stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_ppg = benchmarking_2017_df['PPG'].mean()
                    st.metric("Average PPG", f"{avg_ppg:.2f}")
                
                with col2:
                    avg_gf = benchmarking_2017_df['GF'].mean()
                    st.metric("Avg Goals/Game", f"{avg_gf:.2f}")
                
                with col3:
                    avg_ga = benchmarking_2017_df['GA'].mean()
                    st.metric("Avg Goals Against", f"{avg_ga:.2f}")
                
                with col4:
                    avg_si = benchmarking_2017_df['StrengthIndex'].mean()
                    st.metric("Avg Strength Index", f"{avg_si:.1f}")
                
                st.markdown("---")
                
                # Team selector for detailed view
                st.subheader("🔍 View Individual Team Stats")
                team_options_2017 = sorted(benchmarking_2017_df['Team'].dropna().unique().tolist())
                selected_team_2017 = st.selectbox(
                    "Select a 2017 Boys team to view detailed stats:",
                    team_options_2017,
                    key="benchmarking_2017_selector"
                )
                
                if selected_team_2017:
                    team_data = benchmarking_2017_df[benchmarking_2017_df['Team'] == selected_team_2017]
                    
                    if not team_data.empty:
                        team = team_data.iloc[0]
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Division Rank", f"#{int(team.get('Rank', 'N/A'))}")
                            st.metric("Games Played", int(team.get('GP', 0)))
                            st.metric("Record", f"{int(team.get('W', 0))}-{int(team.get('L', 0))}-{int(team.get('D', 0))}")
                        
                        with col2:
                            st.metric("PPG", f"{team.get('PPG', 0):.2f}")
                            st.metric("Points", int(team.get('Pts', 0)))
                            st.metric("Strength Index", f"{team.get('StrengthIndex', 0):.1f}")
                        
                        with col3:
                            st.metric("Goals/Game", f"{team.get('GF', 0):.2f}")
                            st.metric("Goals Against/Game", f"{team.get('GA', 0):.2f}")
                            st.metric("Goal Diff/Game", f"{team.get('GD', 0):+.2f}")
                        
                        # Show league context
                        st.markdown("---")
                        st.subheader("🏆 League Context")
                        st.write(f"**League/Division:** {team.get('League/Division', 'OCL BU09 7v7 Stripes')}")
                        if 'Region' in team:
                            st.write(f"**Region:** {team.get('Region', 'Unknown')}")
                        if 'SourceURL' in team:
                            st.write(f"**Source:** [View Division Standings]({team['SourceURL']})")
                
                st.markdown("---")
                
                # Full standings table
                st.subheader("📊 Complete Standings - OCL BU09 7v7 Stripes (2017 Boys)")
                
                display_cols = ['Rank', 'Team', 'GP', 'W', 'L', 'D', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
                display_cols = [col for col in display_cols if col in benchmarking_2017_df.columns]
                
                st.dataframe(
                    benchmarking_2017_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Team": st.column_config.TextColumn("Team"),
                        "GP": st.column_config.NumberColumn("GP", help="Games Played"),
                        "W": st.column_config.NumberColumn("W", help="Wins"),
                        "L": st.column_config.NumberColumn("L", help="Losses"),
                        "D": st.column_config.NumberColumn("D", help="Draws"),
                        "GF": st.column_config.NumberColumn("GF", help="Goals For (Per Game)", format="%.2f"),
                        "GA": st.column_config.NumberColumn("GA", help="Goals Against (Per Game)", format="%.2f"),
                        "GD": st.column_config.NumberColumn("GD", help="Goal Differential (Per Game)", format="%+.2f"),
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
                
                st.caption("💡 **Note:** These are 2017 boys teams (U9) - used for benchmarking only, not included in main DSX rankings")
            else:
                st.info("📊 No 2017 boys benchmarking data found. Run `python fetch_ocl_bu09_7v7_stripes.py` to fetch the data.")
        else:
            st.info("📊 **2017 Boys Benchmarking data not yet available.**")
            st.write("To fetch this data, run:")
            st.code("python fetch_ocl_bu09_7v7_stripes.py", language="bash")
            st.write("This will create `OCL_BU09_7v7_Stripes_Benchmarking_2017.csv` with all 2017 boys teams from the OCL BU09 7v7 Stripes division.")
    except Exception as e:
        st.error(f"Error loading 2017 boys benchmarking data: {e}")


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
            
            # Opponent Weakness Detection
            st.subheader("🎯 Opponent Weakness Analysis")
            
            # Load division data to get opponent's full stats
            all_divisions_df = load_division_data()
            opp_division_data = all_divisions_df[all_divisions_df['Team'] == selected_opp]
            
            if not opp_division_data.empty:
                opp_full_stats = opp_division_data.iloc[0]
                
                # Analyze opponent's weaknesses
                weaknesses = []
                
                # Goals against analysis
                opp_ga_pg = opp_full_stats.get('GA', 0) / max(1, opp_full_stats.get('GP', 1))
                if opp_ga_pg >= 3.0:
                    weaknesses.append(f"🛡️ **Defensive Vulnerability**: Concedes {opp_ga_pg:.1f} goals per game - high-scoring opportunities")
                elif opp_ga_pg >= 2.0:
                    weaknesses.append(f"⚠️ **Defensive Concerns**: Concedes {opp_ga_pg:.1f} goals per game - some defensive gaps")
                
                # Goals for analysis
                opp_gf_pg = opp_full_stats.get('GF', 0) / max(1, opp_full_stats.get('GP', 1))
                if opp_gf_pg <= 1.0:
                    weaknesses.append(f"⚽ **Offensive Struggles**: Only scores {opp_gf_pg:.1f} goals per game - limited attacking threat")
                elif opp_gf_pg <= 1.5:
                    weaknesses.append(f"📉 **Low Scoring**: Only {opp_gf_pg:.1f} goals per game - manageable attacking output")
                
                # Goal difference analysis
                opp_gd_pg = opp_gf_pg - opp_ga_pg
                if opp_gd_pg <= -1.0:
                    weaknesses.append(f"📊 **Negative GD**: {opp_gd_pg:+.1f} goal difference per game - struggling overall")
                elif opp_gd_pg <= 0:
                    weaknesses.append(f"⚖️ **Even GD**: {opp_gd_pg:+.1f} goal difference - not dominating games")
                
                # Loss analysis
                opp_losses = opp_full_stats.get('L', 0)
                opp_gp = opp_full_stats.get('GP', 1)
                loss_rate = opp_losses / opp_gp if opp_gp > 0 else 0
                
                if loss_rate >= 0.6:
                    weaknesses.append(f"❌ **High Loss Rate**: {loss_rate:.0%} of games lost - vulnerable team")
                elif loss_rate >= 0.4:
                    weaknesses.append(f"⚠️ **Moderate Loss Rate**: {loss_rate:.0%} of games lost - beatable team")
                
                # Recent form analysis (if we have enough data)
                if opp_gp >= 3:
                    # This would need to be calculated from their recent games
                    # For now, we'll use overall stats as proxy
                    if opp_ga_pg >= 2.5 and opp_gf_pg <= 1.5:
                        weaknesses.append(f"🔥 **Recent Struggles**: High goals against + low scoring = vulnerable form")
                
                # Display weaknesses
                if weaknesses:
                    st.info("🎯 **Key Weaknesses to Exploit:**")
                    for weakness in weaknesses:
                        st.write(f"• {weakness}")
                else:
                    st.info("⚠️ **No Major Weaknesses Detected** - This is a strong, well-balanced team")
                
                # Strategic recommendations based on weaknesses
                st.subheader("💡 Strategic Recommendations")
                
                recommendations = []
                
                if opp_ga_pg >= 2.5:
                    recommendations.append("🎯 **Attack Aggressively**: High goals against means scoring opportunities - press forward!")
                
                if opp_gf_pg <= 1.5:
                    recommendations.append("🛡️ **Defensive Focus**: Low scoring team - focus on solid defense and counter-attacks")
                
                if opp_gd_pg <= -0.5:
                    recommendations.append("⚡ **Control Tempo**: Negative goal difference suggests they struggle - dictate the pace")
                
                if loss_rate >= 0.5:
                    recommendations.append("💪 **Mental Edge**: High loss rate means they may lack confidence - stay positive!")
                
                if opp_ga_pg >= 2.0 and opp_gf_pg <= 2.0:
                    recommendations.append("🎲 **High-Scoring Game**: Both teams score/concede goals - expect an open, exciting match")
                
                if recommendations:
                    for rec in recommendations:
                        st.write(f"• {rec}")
                else:
                    st.write("• 🤝 **Even Matchup**: No clear tactical advantage - focus on execution and effort")
            
            else:
                st.warning("⚠️ **Limited Data**: No division data available for detailed weakness analysis")
                st.info("💡 **General Strategy**: Focus on your strengths and play with confidence!")
            
            st.markdown("---")
            
            # Opponent's Three-Stat Snapshot (League Season + Tournament + H2H vs DSX)
            all_divisions_df = load_division_data()
            opponent_snapshot = get_opponent_three_stat_snapshot(selected_opp, all_divisions_df, dsx_matches)
            if opponent_snapshot:
                display_opponent_three_stat_snapshot(opponent_snapshot, selected_opp)
            else:
                st.info(f"📊 Scouting data not yet available for {selected_opp}")
            
            st.markdown("---")
            
            # Match history (DSX vs this opponent)
            st.subheader("📅 DSX vs " + selected_opp + " - Head-to-Head History")
            
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
            
            # Opponent Three-Stat Snapshot (League Season + Tournament + H2H vs DSX)
            st.markdown("---")
            
            # Load division data and match history
            try:
                all_divisions_df = load_division_data()
            except Exception:
                all_divisions_df = pd.DataFrame()
            
            try:
                dsx_matches_upcoming = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
            except:
                dsx_matches_upcoming = pd.DataFrame()
            
            opponent_snapshot = get_opponent_three_stat_snapshot(selected_upcoming, all_divisions_df, dsx_matches_upcoming)
            if opponent_snapshot:
                display_opponent_three_stat_snapshot(opponent_snapshot, selected_upcoming)
            else:
                st.info(f"📊 Scouting data not yet available for {selected_upcoming}")
            
            # Check for additional specialized sources (BSA Celtic, Club Ohio West, etc.)
            # Check if it's a BSA Celtic team
            if "BSA Celtic" in selected_upcoming:
                if os.path.exists("BSA_Celtic_Schedules.csv"):
                    bsa_schedules = pd.read_csv("BSA_Celtic_Schedules.csv")
                    team_matches = bsa_schedules[bsa_schedules['OpponentTeam'] == selected_upcoming]
                    completed = team_matches[team_matches['GF'] != ''].copy()
                    if len(completed) > 0:
                        completed['GF'] = pd.to_numeric(completed['GF'])
                        completed['GA'] = pd.to_numeric(completed['GA'])
                        completed['GD'] = completed['GF'] - completed['GA']
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
                else:
                    st.warning("BSA Celtic schedule data not available")
                    st.write("Run `python fetch_bsa_celtic.py` to get their latest results")
            
            # Check if it's Club Ohio West (division team)
            elif "Club Ohio" in selected_upcoming:
                if os.path.exists("OCL_BU08_Stripes_Division_with_DSX.csv"):
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
                        st.write("💡 **To add data:**")
                        st.write("  - Check if they're in a division we should track")
                        st.write("  - Add their division to the fetch scripts")
                        st.write("  - Or enter data manually in Data Manager")
                
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
    
    # Game Settings Section (before tabs)
    st.markdown("---")
    st.header("⚙️ Game Settings")
    
    # Load current config
    game_lock_enabled = load_game_config()
    
    col_settings1, col_settings2 = st.columns(2)
    with col_settings1:
        st.subheader("🔒 Game Lock Mode")
        lock_mode = st.toggle(
            "Enable Game Lock Mode",
            value=game_lock_enabled,
            help="When enabled: Game settings and lineup are locked once game starts. Only game actions (goals, shots, passes) can be recorded. Timer controls still work."
        )
        
        if lock_mode != game_lock_enabled:
            save_game_config(lock_mode)
            st.cache_data.clear()  # Clear cache to reload config
            if lock_mode:
                st.success("✅ Game Lock Mode **ENABLED** - Games will lock automatically when started")
            else:
                st.success("✅ Game Lock Mode **DISABLED** - Testing mode (games stay editable)")
            st.rerun()
    
    with col_settings2:
        st.info("""
        **Game Lock Mode:**
        - **ON**: Locks lineup & settings when game starts
        - **OFF**: Everything stays editable (for testing)
        """)
    
    st.markdown("---")
    
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
        st.subheader("📂 Tracked Leagues/Divisions")
        tracked_files = [
            ("OCL BU08 Stripes", "OCL_BU08_Stripes_Division_Rankings.csv"),
            ("OCL BU08 White", "OCL_BU08_White_Division_Rankings.csv"),
            ("OCL BU08 Stars (5v5)", "OCL_BU08_Stars_Division_Rankings.csv"),
            ("OCL BU08 Stars (7v7)", "OCL_BU08_Stars_7v7_Division_Rankings.csv"),
            ("MVYSA B09-3", "MVYSA_B09_3_Division_Rankings.csv"),
            ("Haunted Classic B08 Orange", "Haunted_Classic_B08Orange_Division_Rankings.csv"),
            ("Haunted Classic B08 Black", "Haunted_Classic_B08Black_Division_Rankings.csv"),
            ("CU Fall Finale 2025 U8 Boys Platinum", "CU_Fall_Finale_2025_Division_Rankings.csv"),
            ("Club Ohio Fall Classic 2025 U09B Select III", "Club_Ohio_Fall_Classic_2025_Division_Rankings.csv"),
            ("CPL Fall 2025 U9 (multi-group)", "CPL_Fall_2025_Division_Rankings.csv"),
        ]
        rows = []
        for name, fname in tracked_files:
            exists = os.path.exists(fname)
            rows.append({'League/Division': name, 'File': fname, 'Status': '✅ Available' if exists else '❌ Missing'})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔌 Update Scripts & Sources")
        sources = [
            { 'Script': 'fetch_ocl_stripes_results.py', 'Purpose': 'OCL Stripes live results', 'Source': 'GotSport results group' },
            { 'Script': 'fetch_club_ohio_fall_classic.py', 'Purpose': 'Club Ohio Fall Classic U09B Select III', 'Source': 'GotSport (group=436954 & age=9&gender=m)' },
            { 'Script': 'fetch_cu_fall_finale.py', 'Purpose': 'CU Fall Finale divisions', 'Source': 'GotSport schedules' },
            { 'Script': 'fetch_bsa_celtic.py', 'Purpose': 'BSA schedules/results (special-case)', 'Source': 'Club site CSV scrape' },
            { 'Script': 'fetch_mvysa_division.py', 'Purpose': 'MVYSA division standings', 'Source': 'MVYSA site' },
            { 'Script': 'update_mvysa_real_scores.py', 'Purpose': 'Manual MVYSA scores update', 'Source': 'Manual entry from MVYSA' },
            { 'Script': 'fetch_gotsport_stars_division.py', 'Purpose': 'OCL Stars 5v5 division', 'Source': 'GotSport' },
            { 'Script': 'fetch_gotsport_stars_7v7.py', 'Purpose': 'OCL Stars 7v7 division', 'Source': 'GotSport' },
            { 'Script': 'fetch_gotsport_white_division.py', 'Purpose': 'OCL White division', 'Source': 'GotSport' },
            { 'Script': 'fetch_cpl_fall_2025.py', 'Purpose': 'CPL Fall 2025 U9 (multi-group consolidate)', 'Source': 'GotSport groups 380746..380754;406317' },
            { 'Script': 'fetch_division_schedules.py', 'Purpose': 'Generic division schedules', 'Source': 'GotSport' },
            { 'Script': 'fetch_ocl_bu09_7v7_stripes.py', 'Purpose': 'OCL BU09 7v7 Stripes - 2017 Boys Benchmarking (Not in main rankings)', 'Source': 'GotSport group=418537' },
        ]
        st.dataframe(pd.DataFrame(sources), use_container_width=True, hide_index=True)
    
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
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("Update Division", use_container_width=True):
            with st.spinner("Fetching division data..."):
                import subprocess
                result = subprocess.run([sys.executable, 'fetch_gotsport_division.py'], 
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
                result = subprocess.run([sys.executable, 'fetch_bsa_celtic.py'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("BSA Celtic data updated!")
                    refresh_data()
                else:
                    st.error("Error updating BSA Celtic")
                    st.code(result.stderr)
    
    with col3:
        if st.button("Update CU Fall Finale", use_container_width=True):
            with st.spinner("Fetching CU Fall Finale..."):
                import subprocess
                result = subprocess.run([sys.executable, 'fetch_cu_fall_finale.py'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("CU Fall Finale data updated!")
                    refresh_data()
                else:
                    st.error("Error updating CU Fall Finale")
                    st.code(result.stderr)
    
    with col4:
        if st.button("Update Club Ohio Fall Classic", use_container_width=True):
            with st.spinner("Fetching Club Ohio Fall Classic..."):
                import subprocess
                result = subprocess.run([sys.executable, 'fetch_club_ohio_fall_classic.py'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("Club Ohio Fall Classic data updated!")
                    refresh_data()
                else:
                    st.error("Error updating Club Ohio Fall Classic")
                    st.code(result.stderr)
    
    with col5:
        if st.button("Update OCL Stripes Results", use_container_width=True):
            with st.spinner("Fetching OCL Stripes results..."):
                import subprocess
                result = subprocess.run([sys.executable, 'fetch_ocl_stripes_results.py'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("OCL Stripes results updated!")
                    refresh_data()
                else:
                    st.error("Error updating OCL Stripes results")
                    st.code(result.stderr)
    
    with col6:
        if st.button("Update All", use_container_width=True):
            with st.spinner("Updating all data..."):
                import subprocess
                
                # Update division
                subprocess.run([sys.executable, 'fetch_gotsport_division.py'])
                # Update schedules
                subprocess.run([sys.executable, 'fetch_division_schedules.py'])
                # Update BSA Celtic
                subprocess.run([sys.executable, 'fetch_bsa_celtic.py'])
                # Update CU Fall Finale
                subprocess.run([sys.executable, 'fetch_cu_fall_finale.py'])
                # Update Club Ohio Fall Classic
                subprocess.run([sys.executable, 'fetch_club_ohio_fall_classic.py'])
                # Update OCL Stripes Results
                subprocess.run([sys.executable, 'fetch_ocl_stripes_results.py'])
                
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

