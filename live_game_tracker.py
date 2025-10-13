import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# Page config
st.set_page_config(page_title="DSX Live Game Tracker", layout="wide")

# Initialize session state
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'game_data' not in st.session_state:
    st.session_state.game_data = {}
if 'events' not in st.session_state:
    st.session_state.events = []
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'time_remaining' not in st.session_state:
    st.session_state.time_remaining = 25 * 60  # 25 minutes in seconds
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

# Load roster
@st.cache_data
def load_roster():
    try:
        roster = pd.read_csv("roster.csv")
        return roster[['PlayerNumber', 'PlayerName', 'Position']].sort_values('PlayerNumber')
    except:
        return pd.DataFrame()

roster = load_roster()

# Custom CSS for big buttons
st.markdown("""
<style>
    .big-button {
        font-size: 24px !important;
        padding: 20px !important;
        margin: 10px !important;
        border-radius: 10px !important;
    }
    .timer-display {
        font-size: 72px;
        font-weight: bold;
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin: 20px 0;
    }
    .score-display {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        margin: 20px 0;
    }
    .event-feed {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    .event-item {
        background-color: #2d2d2d;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def format_time(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def add_event(event_type, player=None, assist=None, notes=""):
    """Add an event to the game log"""
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
    st.session_state.events.insert(0, event)  # Add to beginning
    return event

def get_score():
    """Calculate current score from events"""
    dsx_goals = len([e for e in st.session_state.events if e['type'] == 'DSX_GOAL'])
    opp_goals = len([e for e in st.session_state.events if e['type'] == 'OPP_GOAL'])
    return dsx_goals, opp_goals

# Main app
st.title("⚽ DSX Live Game Tracker")

# Check if game is active
if not st.session_state.game_active:
    # PRE-GAME SETUP
    st.header("🏟️ New Game Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        game_date = st.date_input("Date", datetime.now())
        opponent = st.text_input("Opponent Team", "")
        location = st.text_input("Location", "")
        tournament = st.text_input("Tournament/League", "MVYSA Fall 2025")
    
    with col2:
        st.subheader("⚙️ Game Settings")
        half_length = st.number_input("Half Length (minutes)", min_value=10, max_value=45, value=25)
        st.info(f"Game will be 2 halves of {half_length} minutes each")
    
    st.markdown("---")
    
    # STARTING LINEUP SELECTION
    st.subheader("👥 Select Starting 7")
    
    if not roster.empty:
        # Create columns for lineup selection
        lineup_cols = st.columns(7)
        
        selected_starters = []
        for i, col in enumerate(lineup_cols):
            with col:
                st.write(f"**Position {i+1}**")
                player_options = ["Select..."] + [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                                   for _, row in roster.iterrows()]
                selected = st.selectbox(f"Player {i+1}", player_options, key=f"starter_{i}", label_visibility="collapsed")
                if selected != "Select...":
                    player_num = int(selected.split('#')[1].split(' ')[0])
                    selected_starters.append(player_num)
        
        st.markdown("---")
        
        # Show bench players
        if len(selected_starters) > 0:
            bench = roster[~roster['PlayerNumber'].isin(selected_starters)]
            if not bench.empty:
                st.subheader("🪑 Bench")
                bench_display = ", ".join([f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                           for _, row in bench.iterrows()])
                st.write(bench_display)
        
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
                st.rerun()
            else:
                st.error("Please enter opponent name and select at least 7 starting players!")
    else:
        st.error("No roster found! Please add players to roster.csv first.")

else:
    # LIVE GAME INTERFACE
    game_data = st.session_state.game_data
    dsx_score, opp_score = get_score()
    
    # Header with scores
    st.markdown(f"""
    <div class="score-display">
        DSX <span style="color: #667eea;">{dsx_score}</span> - 
        <span style="color: #f093fb;">{opp_score}</span> {game_data['opponent']}
    </div>
    """, unsafe_allow_html=True)
    
    # Timer and controls
    half_text = "FIRST HALF" if st.session_state.current_half == 1 else "SECOND HALF"
    st.markdown(f"""
    <div class="timer-display">
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
                add_event('HALF_TIME', notes="Half time break")
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
    
    # Update timer if running
    if st.session_state.timer_running:
        if st.session_state.last_update:
            elapsed = time.time() - st.session_state.last_update
            st.session_state.time_remaining = max(0, st.session_state.time_remaining - int(elapsed))
        st.session_state.last_update = time.time()
        
        if st.session_state.time_remaining > 0:
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.timer_running = False
            st.balloons()
            st.success(f"{half_text} Complete!")
    
    st.markdown("---")
    
    # BIG BUTTON DASHBOARD
    st.subheader("🎮 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚽ DSX GOAL", use_container_width=True, type="primary"):
            st.session_state.show_goal_dialog = True
            st.rerun()
    
    with col2:
        if st.button("🥅 OPP GOAL", use_container_width=True):
            add_event('OPP_GOAL')
            st.rerun()
    
    with col3:
        if st.button("🎯 SHOT (No Goal)", use_container_width=True):
            st.session_state.show_shot_dialog = True
            st.rerun()
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🧤 SAVE", use_container_width=True):
            st.session_state.show_save_dialog = True
            st.rerun()
    
    with col5:
        if st.button("⚠️ CORNER", use_container_width=True):
            add_event('CORNER')
            st.rerun()
    
    with col6:
        if st.button("🔄 SUBSTITUTION", use_container_width=True):
            st.session_state.show_sub_dialog = True
            st.rerun()
    
    # Undo button
    col7, col8, col9 = st.columns(3)
    
    with col7:
        if st.button("↩️ UNDO LAST", use_container_width=True, type="secondary"):
            if st.session_state.events:
                last_event = st.session_state.events[0]
                # If it was a substitution, reverse it
                if last_event['type'] == 'SUBSTITUTION':
                    # Note: Full reversal would be complex, just remove from log
                    st.warning("⚠️ Sub removed from log - manually adjust lineup if needed")
                st.session_state.events.pop(0)
                st.success(f"✅ Undid: {last_event['type']}")
                st.rerun()
            else:
                st.error("No events to undo!")
    
    with col8:
        if st.button("📝 ADD NOTE", use_container_width=True):
            st.session_state.show_note_dialog = True
            st.rerun()
    
    with col9:
        if st.button("🚨 INJURY/TIMEOUT", use_container_width=True):
            add_event('TIMEOUT', notes="Injury/timeout - clock stopped")
            if st.session_state.timer_running:
                st.session_state.timer_running = False
            st.rerun()
    
    # Goal dialog
    if 'show_goal_dialog' in st.session_state and st.session_state.show_goal_dialog:
        with st.form("goal_form"):
            st.subheader("⚽ DSX GOAL!")
            
            # Top scorers as quick buttons
            player_stats = pd.read_csv("player_stats.csv") if os.path.exists("player_stats.csv") else pd.DataFrame()
            
            # Get players on field
            on_field_players = roster[roster['PlayerNumber'].isin(st.session_state.on_field)]
            
            scorer = st.selectbox("Who scored?", 
                                  [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                   for _, row in on_field_players.iterrows()])
            
            assist = st.selectbox("Assisted by:", ["None"] + 
                                  [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                   for _, row in on_field_players.iterrows()])
            
            notes = st.text_input("Notes (optional)", placeholder="PK, header, solo run, etc.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ RECORD GOAL", use_container_width=True, type="primary"):
                    player_name = scorer.split(' ', 1)[1]
                    assist_name = assist.split(' ', 1)[1] if assist != "None" else None
                    add_event('DSX_GOAL', player=player_name, assist=assist_name, notes=notes)
                    st.session_state.show_goal_dialog = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_goal_dialog = False
                    st.rerun()
    
    # Shot dialog
    if 'show_shot_dialog' in st.session_state and st.session_state.show_shot_dialog:
        with st.form("shot_form"):
            st.subheader("🎯 Shot Attempt")
            
            on_field_players = roster[roster['PlayerNumber'].isin(st.session_state.on_field)]
            shooter = st.selectbox("Who took the shot?", 
                                   [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                    for _, row in on_field_players.iterrows()])
            
            shot_type = st.selectbox("Result", ["Saved by keeper", "Off target", "Hit post", "Blocked"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                    player_name = shooter.split(' ', 1)[1]
                    add_event('SHOT', player=player_name, notes=shot_type)
                    st.session_state.show_shot_dialog = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_shot_dialog = False
                    st.rerun()
    
    # Save dialog
    if 'show_save_dialog' in st.session_state and st.session_state.show_save_dialog:
        with st.form("save_form"):
            st.subheader("🧤 Goalkeeper Save")
            
            keeper_players = roster[(roster['PlayerNumber'].isin(st.session_state.on_field)) & 
                                    (roster['Position'] == 'Goalkeeper')]
            
            if keeper_players.empty:
                keeper_players = roster[roster['PlayerNumber'].isin(st.session_state.on_field)]
            
            keeper = st.selectbox("Goalkeeper", 
                                  [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                   for _, row in keeper_players.iterrows()])
            
            save_type = st.selectbox("Save type", ["Catch", "Punch", "Deflection", "Dive"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ RECORD", use_container_width=True, type="primary"):
                    player_name = keeper.split(' ', 1)[1]
                    add_event('SAVE', player=player_name, notes=save_type)
                    st.session_state.show_save_dialog = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_save_dialog = False
                    st.rerun()
    
    # Substitution dialog
    if 'show_sub_dialog' in st.session_state and st.session_state.show_sub_dialog:
        with st.form("sub_form"):
            st.subheader("🔄 Substitution")
            
            on_field_players = roster[roster['PlayerNumber'].isin(st.session_state.on_field)]
            bench_players = roster[roster['PlayerNumber'].isin(st.session_state.bench_players)]
            
            player_out = st.selectbox("Player coming OFF", 
                                      [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                       for _, row in on_field_players.iterrows()])
            
            player_in = st.selectbox("Player coming ON", 
                                     [f"#{int(row['PlayerNumber'])} {row['PlayerName']}" 
                                      for _, row in bench_players.iterrows()])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ MAKE SUB", use_container_width=True, type="primary"):
                    out_num = int(player_out.split('#')[1].split(' ')[0])
                    in_num = int(player_in.split('#')[1].split(' ')[0])
                    out_name = player_out.split(' ', 1)[1]
                    in_name = player_in.split(' ', 1)[1]
                    
                    # Update on-field tracking
                    st.session_state.on_field.remove(out_num)
                    st.session_state.on_field.append(in_num)
                    st.session_state.bench_players.remove(in_num)
                    st.session_state.bench_players.append(out_num)
                    
                    add_event('SUBSTITUTION', notes=f"{in_name} ON, {out_name} OFF")
                    st.session_state.show_sub_dialog = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_sub_dialog = False
                    st.rerun()
    
    # Note dialog
    if 'show_note_dialog' in st.session_state and st.session_state.show_note_dialog:
        with st.form("note_form"):
            st.subheader("📝 Add Note")
            
            note_text = st.text_area("Note", placeholder="Great defense, injury, weather change, coaching decision, etc.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ ADD NOTE", use_container_width=True, type="primary"):
                    if note_text:
                        add_event('NOTE', notes=note_text)
                        st.session_state.show_note_dialog = False
                        st.rerun()
                    else:
                        st.error("Please enter a note!")
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_note_dialog = False
                    st.rerun()
    
    st.markdown("---")
    
    # Live Event Feed and Current Stats
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Live Event Feed")
        
        if st.session_state.events:
            for event in st.session_state.events[:20]:  # Show last 20 events
                icon = {
                    'DSX_GOAL': '⚽',
                    'OPP_GOAL': '🥅',
                    'SHOT': '🎯',
                    'SAVE': '🧤',
                    'CORNER': '⚠️',
                    'SUBSTITUTION': '🔄',
                    'HALF_TIME': '⏰',
                    'TIMEOUT': '🚨',
                    'NOTE': '📝'
                }.get(event['type'], '📝')
                
                event_text = f"{icon} {event['timestamp']} - "
                
                if event['type'] == 'DSX_GOAL':
                    event_text += f"GOAL! {event['player']}"
                    if event['assist']:
                        event_text += f" (assist: {event['assist']})"
                elif event['type'] == 'OPP_GOAL':
                    event_text += "Opponent Goal"
                elif event['type'] == 'SHOT':
                    event_text += f"Shot by {event['player']} - {event['notes']}"
                elif event['type'] == 'SAVE':
                    event_text += f"Save by {event['player']} - {event['notes']}"
                elif event['type'] == 'CORNER':
                    event_text += "Corner kick"
                elif event['type'] == 'SUBSTITUTION':
                    event_text += f"Sub: {event['notes']}"
                elif event['type'] == 'HALF_TIME':
                    event_text += "HALF TIME"
                elif event['type'] == 'TIMEOUT':
                    event_text += f"Timeout - {event['notes']}"
                elif event['type'] == 'NOTE':
                    event_text += f"Note: {event['notes']}"
                
                st.markdown(f'<div class="event-item">{event_text}</div>', unsafe_allow_html=True)
        else:
            st.info("No events yet. Start recording with the buttons above!")
    
    with col2:
        st.subheader("📊 Current Stats")
        
        # Calculate stats
        goals = [e for e in st.session_state.events if e['type'] == 'DSX_GOAL']
        shots = [e for e in st.session_state.events if e['type'] == 'SHOT']
        saves = [e for e in st.session_state.events if e['type'] == 'SAVE']
        corners = [e for e in st.session_state.events if e['type'] == 'CORNER']
        
        st.metric("Goals", len(goals))
        st.metric("Shots", len(shots))
        st.metric("Saves", len(saves))
        st.metric("Corners", len(corners))
        
        if goals:
            st.write("**Goal Scorers:**")
            from collections import Counter
            scorer_counts = Counter([e['player'] for e in goals])
            for player, count in scorer_counts.most_common():
                st.write(f"• {player}: {count}")

# Show game summary after game ends
if 'show_summary' in st.session_state and st.session_state.show_summary:
    st.markdown("---")
    st.header("🎉 GAME COMPLETE!")
    
    dsx_score, opp_score = get_score()
    
    if dsx_score > opp_score:
        result = "WIN"
        emoji = "✅"
        result_code = "W"
    elif dsx_score < opp_score:
        result = "LOSS"
        emoji = "❌"
        result_code = "L"
    else:
        result = "DRAW"
        emoji = "➖"
        result_code = "D"
    
    st.markdown(f"""
    <div class="score-display">
        {emoji} {result}!<br>
        DSX {dsx_score} - {opp_score} {st.session_state.game_data['opponent']}
    </div>
    """, unsafe_allow_html=True)
    
    # Display stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚽ Goal Scorers")
        goals = [e for e in st.session_state.events if e['type'] == 'DSX_GOAL']
        if goals:
            from collections import Counter
            scorer_counts = Counter([e['player'] for e in goals])
            for player, count in scorer_counts.most_common():
                st.write(f"• {player}: {count} goal{'s' if count > 1 else ''}")
        else:
            st.write("No goals scored")
    
    with col2:
        st.subheader("🎯 Assists")
        assists = [e for e in goals if e['assist']]
        if assists:
            from collections import Counter
            assist_counts = Counter([e['assist'] for e in assists])
            for player, count in assist_counts.most_common():
                st.write(f"• {player}: {count} assist{'s' if count > 1 else ''}")
        else:
            st.write("No assists recorded")
    
    # Save options
    st.markdown("---")
    st.subheader("💾 Save Game Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save to CSV", use_container_width=True, type="primary"):
            # Save to DSX_Matches_Fall2025.csv
            match_data = {
                'Date': st.session_state.game_data['date'],
                'Tournament': st.session_state.game_data['tournament'],
                'Opponent': st.session_state.game_data['opponent'],
                'Location': st.session_state.game_data['location'],
                'GF': dsx_score,
                'GA': opp_score,
                'GD': dsx_score - opp_score,
                'Result': result_code,
                'Outcome': result
            }
            
            matches_df = pd.read_csv("DSX_Matches_Fall2025.csv") if os.path.exists("DSX_Matches_Fall2025.csv") else pd.DataFrame()
            matches_df = pd.concat([matches_df, pd.DataFrame([match_data])], ignore_index=True)
            matches_df.to_csv("DSX_Matches_Fall2025.csv", index=False)
            
            # Save to game_player_stats.csv
            goals = [e for e in st.session_state.events if e['type'] == 'DSX_GOAL']
            game_stats = []
            
            from collections import defaultdict
            player_stats = defaultdict(lambda: {'Goals': 0, 'Assists': 0})
            
            for goal in goals:
                player_stats[goal['player']]['Goals'] += 1
                if goal['assist']:
                    player_stats[goal['assist']]['Assists'] += 1
            
            for player, stats in player_stats.items():
                game_stats.append({
                    'Date': st.session_state.game_data['date'],
                    'Opponent': st.session_state.game_data['opponent'],
                    'PlayerName': player,
                    'Goals': stats['Goals'],
                    'Assists': stats['Assists'],
                    'Notes': ''
                })
            
            if game_stats:
                game_stats_df = pd.read_csv("game_player_stats.csv") if os.path.exists("game_player_stats.csv") else pd.DataFrame()
                game_stats_df = pd.concat([game_stats_df, pd.DataFrame(game_stats)], ignore_index=True)
                game_stats_df.to_csv("game_player_stats.csv", index=False)
            
            st.success("✅ Game data saved!")
    
    with col2:
        if st.button("📥 Download Event Log", use_container_width=True):
            events_df = pd.DataFrame(st.session_state.events)
            csv = events_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                f"game_events_{st.session_state.game_data['date']}_{st.session_state.game_data['opponent']}.csv",
                "text/csv",
                use_container_width=True
            )
    
    with col3:
        if st.button("🔄 New Game", use_container_width=True):
            # Reset all game state
            st.session_state.game_active = False
            st.session_state.show_summary = False
            st.session_state.events = []
            st.session_state.time_remaining = 25 * 60
            st.session_state.current_half = 1
            st.session_state.timer_running = False
            st.rerun()

