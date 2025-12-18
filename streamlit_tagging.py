"""
Streamlit component for crowd-sourced player tagging
Integrates with dsx-tracker dashboard
"""

import streamlit as st
import pandas as pd
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
from typing import Dict, List, Optional
from pathlib import Path
import hashlib
from datetime import datetime
import sys
import uuid

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from tagging_database import TaggingDatabase
    from consensus_engine import ConsensusEngine
    from google_drive_integration import GoogleDriveAccess
except ImportError as e:
    st.error(f"Error importing tagging modules: {e}")
    TaggingDatabase = None
    ConsensusEngine = None
    GoogleDriveAccess = None

# Initialize components
@st.cache_resource
def get_database():
    """Get database instance (cached)
    
    Uses Streamlit Cloud persistent storage if available, otherwise local storage
    """
    if TaggingDatabase is None:
        return None
    try:
        # Try Streamlit Cloud persistent storage first
        import os
        if os.path.exists("/mount/src"):
            # Streamlit Cloud - use persistent storage
            db_path = "/mount/src/data/tagging.db"
        else:
            # Local development
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "tagging.db")
        
        return TaggingDatabase(db_path)
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return None

@st.cache_resource
def get_consensus_engine():
    """Get consensus engine (cached)"""
    db = get_database()
    if db is None or ConsensusEngine is None:
        return None
    return ConsensusEngine(db)

@st.cache_resource
def get_drive_access():
    """Get Google Drive access (cached)"""
    if GoogleDriveAccess is None:
        return None
    return GoogleDriveAccess()

def get_user_id():
    """Get or create user ID from session"""
    if 'user_id' not in st.session_state:
        # Create anonymous user ID from session
        session_id = st.session_state.get('session_id', str(datetime.now()))
        user_id = hashlib.md5(session_id.encode()).hexdigest()[:16]
        st.session_state['user_id'] = user_id
    return st.session_state['user_id']

def load_csv_data(csv_path: str) -> Optional[pd.DataFrame]:
    """Load CSV tracking data"""
    try:
        if csv_path.startswith('http'):
            # Download from URL
            df = pd.read_csv(csv_path)
        else:
            df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

def get_players_at_frame(df: pd.DataFrame, frame_num: int, frame_col: str = None) -> List[Dict]:
    """Get all players detected at a specific frame"""
    # Try different column name variations if frame_col not provided
    if frame_col is None:
        for col in ['frame', 'Frame', 'FRAME', 'frame_num', 'frame_number']:
            if col in df.columns:
                frame_col = col
                break
    
    if frame_col is None or frame_col not in df.columns:
        return []
    
    # Convert frame column to numeric for comparison, handling NaN values
    try:
        df_frame_numeric = pd.to_numeric(df[frame_col], errors='coerce')
        frame_data = df[df_frame_numeric == frame_num]
    except Exception:
        # Fallback to direct comparison
        frame_data = df[df[frame_col] == frame_num]
    
    players = []
    for _, row in frame_data.iterrows():
        # Try multiple column name variations
        track_id = row.get('track_id', row.get('id', row.get('track_id', row.get('track-id', 0))))
        x = row.get('x', row.get('center_x', row.get('center-x', row.get('X', 0))))
        y = row.get('y', row.get('center_y', row.get('center-y', row.get('Y', 0))))
        player_name = str(row.get('player_name', row.get('player-name', row.get('name', ''))))
        team = str(row.get('team', row.get('Team', '')))
        
        players.append({
            'track_id': int(track_id) if pd.notna(track_id) else 0,
            'x': float(x) if pd.notna(x) else 0.0,
            'y': float(y) if pd.notna(y) else 0.0,
            'player_name': player_name if player_name != 'nan' else '',
            'team': team if team != 'nan' else ''
        })
    
    return players

def render_tagging_page():
    """Main tagging interface page"""
    st.title("⚽ Crowd-Sourced Player Tagging")
    st.markdown("Help improve player identification by tagging players in video frames")
    
    db = get_database()
    consensus_engine = get_consensus_engine()
    drive = get_drive_access()
    
    if db is None or consensus_engine is None or drive is None:
        st.error("Tagging system not available. Please ensure all dependencies are installed.")
        st.code("pip install pandas opencv-python gdown")
        return
    
    user_id = get_user_id()
    
    # Initialize file history in session state
    if 'video_history' not in st.session_state:
        st.session_state.video_history = []
    if 'csv_history' not in st.session_state:
        st.session_state.csv_history = []
    
    # Sidebar - Video Selection
    with st.sidebar:
        st.header("📹 Video Selection")
        
        # Show previous videos if available
        if st.session_state.video_history:
            st.caption("📋 Recent Videos")
            selected_video = st.selectbox(
                "Select from recent videos",
                [""] + st.session_state.video_history,
                key="video_history_select"
            )
            if selected_video:
                drive_input = st.text_input(
                    "Google Drive Video URL or File ID",
                    value=selected_video,
                    help="Enter the Google Drive shareable link for your video"
                )
            else:
                drive_input = st.text_input(
                    "Google Drive Video URL or File ID",
                    placeholder="https://drive.google.com/file/d/... or FILE_ID",
                    help="Enter the Google Drive shareable link for your video"
                )
        else:
            drive_input = st.text_input(
                "Google Drive Video URL or File ID",
                placeholder="https://drive.google.com/file/d/... or FILE_ID",
                help="Enter the Google Drive shareable link for your video"
            )
        
        st.markdown("---")
        st.header("📊 Tracking Data (CSV)")
        st.caption("Upload the CSV file from your video analysis")
        
        # CSV Data Source
        csv_source = st.radio(
            "How do you want to provide the CSV?",
            ["📤 Upload File", "🔗 CSV URL", "☁️ Google Drive CSV"],
            help="Choose how to provide your tracking CSV data"
        )
        
        csv_data = None
        csv_source_identifier = None  # To track what was used for history
        
        if csv_source == "📤 Upload File":
            # Show previous uploads if available
            if st.session_state.csv_history:
                st.caption("📋 Recent CSV Files")
                recent_csvs = [item for item in st.session_state.csv_history if item.get('type') == 'upload']
                if recent_csvs:
                    csv_names = [item.get('name', 'Unknown') for item in recent_csvs]
                    selected_csv = st.selectbox(
                        "Select from recent files",
                        [""] + csv_names,
                        key="csv_history_select"
                    )
                    if selected_csv:
                        st.info(f"📄 Selected: {selected_csv}")
                        st.info("💡 Upload a new file to use it, or select from recent files above")
            
            csv_file = st.file_uploader(
                "Upload Tracking CSV File", 
                type=['csv'],
                help="Upload the CSV file exported from your video analysis (should contain columns: frame, track_id, x, y, player_name)"
            )
            if csv_file:
                try:
                    csv_data = pd.read_csv(csv_file)
                    st.success(f"✅ Loaded {len(csv_data)} rows from CSV")
                    # Add to history
                    csv_info = {
                        'type': 'upload',
                        'name': csv_file.name,
                        'size': csv_file.size,
                        'rows': len(csv_data)
                    }
                    if csv_info not in st.session_state.csv_history:
                        st.session_state.csv_history.insert(0, csv_info)
                        # Keep only last 10
                        st.session_state.csv_history = st.session_state.csv_history[:10]
                    csv_source_identifier = f"upload:{csv_file.name}"
                except Exception as e:
                    st.error(f"Error loading CSV: {e}")
        elif csv_source == "🔗 CSV URL":
            # Show previous URLs if available
            if st.session_state.csv_history:
                st.caption("📋 Recent CSV URLs")
                recent_urls = [item for item in st.session_state.csv_history if item.get('type') == 'url']
                if recent_urls:
                    url_list = [item.get('url', '') for item in recent_urls]
                    selected_url = st.selectbox(
                        "Select from recent URLs",
                        [""] + url_list,
                        key="csv_url_history_select"
                    )
                    if selected_url:
                        csv_url = st.text_input(
                            "CSV URL", 
                            value=selected_url,
                            help="Enter a direct URL to your CSV file"
                        )
                    else:
                        csv_url = st.text_input(
                            "CSV URL", 
                            placeholder="https://...",
                            help="Enter a direct URL to your CSV file"
                        )
                else:
                    csv_url = st.text_input(
                        "CSV URL", 
                        placeholder="https://...",
                        help="Enter a direct URL to your CSV file"
                    )
            else:
                csv_url = st.text_input(
                    "CSV URL", 
                    placeholder="https://...",
                    help="Enter a direct URL to your CSV file"
                )
            
            if csv_url and csv_url.strip():
                csv_data = load_csv_data(csv_url)
                if csv_data is not None:
                    st.success(f"✅ Loaded {len(csv_data)} rows from URL")
                    # Add to history
                    csv_info = {
                        'type': 'url',
                        'url': csv_url,
                        'rows': len(csv_data)
                    }
                    if csv_info not in st.session_state.csv_history:
                        st.session_state.csv_history.insert(0, csv_info)
                        # Keep only last 10
                        st.session_state.csv_history = st.session_state.csv_history[:10]
                    csv_source_identifier = f"url:{csv_url}"
        elif csv_source == "☁️ Google Drive CSV":
            # Show previous Google Drive CSVs if available
            if st.session_state.csv_history:
                st.caption("📋 Recent Google Drive CSVs")
                recent_drive = [item for item in st.session_state.csv_history if item.get('type') == 'drive']
                if recent_drive:
                    drive_list = [item.get('file_id', '') for item in recent_drive]
                    selected_drive = st.selectbox(
                        "Select from recent Google Drive files",
                        [""] + drive_list,
                        key="csv_drive_history_select"
                    )
                    if selected_drive:
                        csv_drive_id = st.text_input(
                            "Google Drive CSV File ID", 
                            value=selected_drive,
                            help="Enter the Google Drive File ID for your CSV file"
                        )
                    else:
                        csv_drive_id = st.text_input(
                            "Google Drive CSV File ID", 
                            placeholder="Enter Google Drive File ID",
                            help="Enter the Google Drive File ID for your CSV file"
                        )
                else:
                    csv_drive_id = st.text_input(
                        "Google Drive CSV File ID", 
                        placeholder="Enter Google Drive File ID",
                        help="Enter the Google Drive File ID for your CSV file"
                    )
            else:
                csv_drive_id = st.text_input(
                    "Google Drive CSV File ID", 
                    placeholder="Enter Google Drive File ID",
                    help="Enter the Google Drive File ID for your CSV file"
                )
            
            if csv_drive_id and csv_drive_id.strip():
                try:
                    csv_path = drive.download_video(csv_drive_id)  # Reuse download function
                    csv_data = load_csv_data(csv_path)
                    if csv_data is not None:
                        st.success(f"✅ Loaded {len(csv_data)} rows from Google Drive")
                        # Add to history
                        csv_info = {
                            'type': 'drive',
                            'file_id': csv_drive_id,
                            'rows': len(csv_data)
                        }
                        if csv_info not in st.session_state.csv_history:
                            st.session_state.csv_history.insert(0, csv_info)
                            # Keep only last 10
                            st.session_state.csv_history = st.session_state.csv_history[:10]
                        csv_source_identifier = f"drive:{csv_drive_id}"
                except Exception as e:
                    st.error(f"Error loading from Google Drive: {e}")
        
        # Video ID (extracted from drive URL or manual entry)
        video_id = None
        if drive_input:
            file_id = drive.extract_file_id(drive_input)
            if file_id:
                video_id = file_id
                st.success(f"✓ Video ID: {file_id[:20]}...")
            else:
                st.error("Invalid Google Drive URL")
        
        # Statistics
        if video_id:
            stats = db.get_tagging_stats(video_id)
            st.header("📊 Statistics")
            st.metric("Total Tags", stats['total_tags'])
            st.metric("Consensus Tags", stats['consensus_count'])
            st.metric("Contributors", stats['unique_users'])
    
    # Main content
    if not video_id:
        st.info("👆 Enter a Google Drive video URL or File ID in the sidebar to get started")
        return
    
    if csv_data is None:
        st.warning("⚠️ Please provide CSV tracking data")
        return
    
    # Find frame column
    frame_col = None
    for col in ['frame', 'Frame', 'FRAME', 'frame_num', 'frame_number']:
        if col in csv_data.columns:
            frame_col = col
            break
    
    if frame_col is None:
        st.error("❌ CSV file must contain a 'frame' column. Available columns: " + ", ".join(csv_data.columns[:10]))
        with st.expander("🔍 Show all CSV columns"):
            st.write(list(csv_data.columns))
        return
    
    # Show success message
    st.success(f"✅ Ready to tag! Video loaded with {len(csv_data)} tracking data rows")
    
    # Frame selection - handle NaN and non-numeric values
    try:
        # Convert to numeric, dropping NaN values
        frame_series = pd.to_numeric(csv_data[frame_col], errors='coerce')
        frame_series = frame_series.dropna()
        
        if len(frame_series) > 0:
            max_frame = int(frame_series.max())
            min_frame = int(frame_series.min())
        else:
            max_frame = 1000
            min_frame = 0
            st.warning("⚠️ No valid frame numbers found in CSV")
    except Exception as e:
        st.error(f"Error reading frame data: {e}")
        max_frame = 1000
        min_frame = 0
    
    # Simplified interface - frame navigation first
    st.subheader("🎬 Frame Navigation")
    
    # Use session state to track current frame and force updates
    if 'current_frame' not in st.session_state:
        st.session_state.current_frame = min_frame
    
    # Frame slider - this will trigger rerun when changed
    frame_num = st.slider(
        "Frame Number", 
        min_frame, 
        max_frame, 
        st.session_state.current_frame, 
        step=1, 
        key="frame_slider_main",
        help="Move this slider to navigate to different frames. Players below will update automatically."
    )
    
    # Update session state
    st.session_state.current_frame = frame_num
    
    # Show frame info
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("📊 CSV Rows", len(csv_data))
    with col_info2:
        st.metric("🎬 Current Frame", frame_num)
    with col_info3:
        st.metric("📈 Frame Range", f"{min_frame}-{max_frame}")
    
    st.markdown("---")
    
    # Simplified video section - just a link
    st.subheader("📹 Video Reference")
    video_view_url = f"https://drive.google.com/file/d/{video_id}/view"
    st.markdown(f"""
    **💡 How to tag players:**
    1. **[Open Video in New Tab]({video_view_url})** to watch the video
    2. **Use the frame slider above** to navigate to the frame you want to tag
    3. **Players detected at that frame** will appear below
    4. **Enter player names** and submit tags
    
    The video and frame slider are **separate** - navigate the video manually and use the slider to match the frame number.
    """)
    
    st.markdown("---")
    
    # Load players at this frame - this will update when frame_num changes
    players = get_players_at_frame(csv_data, frame_num, frame_col)
    
    if not players:
        st.warning(f"⚠️ No players detected at frame {frame_num}")
        st.info(f"""
        **Troubleshooting:**
        - Check if frame {frame_num} exists in your CSV
        - Verify the CSV has columns: `frame`, `track_id`, `x`, `y`
        - Try a different frame number (use the slider above)
        - Available frames in CSV: {min_frame} to {max_frame}
        """)
        
        # Show sample of CSV data for debugging
        with st.expander("🔍 Debug: Show CSV structure"):
            st.write("**First few rows:**")
            st.dataframe(csv_data.head(10))
            st.write("**Column names:**")
            st.write(list(csv_data.columns))
            st.write("**Frames in CSV (sample):**")
            if frame_col:
                unique_frames = sorted(csv_data[frame_col].unique())[:20]
                st.write(unique_frames)
        return
    
    # Display players at current frame - this updates when frame_num changes
    st.subheader(f"👥 Players at Frame {frame_num}")
    
    st.caption(f"Found **{len(players)}** players detected at frame {frame_num}")
    
    # Get consensus for this frame
    consensus = engine.get_consensus(video_id, frame_num) if engine else {}
    
    # Show consensus summary at top
    if consensus:
        st.success(f"✅ **{len(consensus)} players** already have consensus tags")
        with st.expander("📋 View Existing Consensus Tags", expanded=False):
            consensus_list = []
            for track_id, tag_info in consensus.items():
                consensus_list.append({
                    'Track ID': track_id,
                    'Player Name': tag_info.get('player_name', 'Unknown'),
                    'Confidence': f"{tag_info.get('confidence', 0):.2%}",
                    'Votes': tag_info.get('vote_count', 0)
                })
            if consensus_list:
                consensus_df = pd.DataFrame(consensus_list)
                st.dataframe(consensus_df, use_container_width=True)
    
    st.markdown("---")
    
    # Tag each player - use frame_num in keys to force updates
    for i, player in enumerate(players):
        track_id = player.get('track_id', i)
        
        # Create unique key that includes frame_num to force updates
        unique_key = f"{video_id}_f{frame_num}_t{track_id}_i{i}"
        
        # Get existing consensus for this track at this frame
        track_consensus = consensus.get(str(track_id), {})
        suggested_name = track_consensus.get('player_name', '')
        suggested_confidence = track_consensus.get('confidence', 0.0)
        
        # Player info
        player_name = player.get('player_name', 'Untagged')
        x_pos = player.get('x', 0)
        y_pos = player.get('y', 0)
        team = player.get('team', 'Unknown')
        
        # Display player card
        with st.container():
            # Header with track ID and current name
            header_col1, header_col2 = st.columns([3, 1])
            with header_col1:
                if track_consensus:
                    st.markdown(f"### 🏷️ Track #{track_id} - **{suggested_name}** (Consensus)")
                else:
                    st.markdown(f"### 🏷️ Track #{track_id} - {player_name}")
            with header_col2:
                if track_consensus:
                    st.metric("Confidence", f"{suggested_confidence:.0%}")
            
            # Player details in columns
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            with detail_col1:
                st.caption(f"📍 Position: ({x_pos:.1f}, {y_pos:.1f})")
            with detail_col2:
                st.caption(f"👕 Team: {team}")
            with detail_col3:
                st.caption(f"🎬 Frame: {frame_num}")
            
            # Show consensus info if available
            if track_consensus:
                st.info(f"💡 **Current Consensus**: {suggested_name} with {suggested_confidence:.0%} confidence ({track_consensus.get('vote_count', 0)} votes)")
            
            # Tagging form
            st.markdown("**Tag This Player:**")
            form_col1, form_col2 = st.columns([3, 1])
            
            with form_col1:
                new_player_name = st.text_input(
                    "Player Name",
                    value=suggested_name if suggested_name else "",
                    key=f"name_{unique_key}",
                    help="Enter the player's name",
                    label_visibility="collapsed",
                    placeholder="Enter player name..."
                )
            
            with form_col2:
                confidence = st.slider(
                    "Confidence",
                    0.0, 1.0, 
                    max(0.5, suggested_confidence) if suggested_confidence > 0 else 0.5,
                    step=0.1,
                    key=f"conf_{unique_key}",
                    help="How confident are you in this tag?",
                    label_visibility="collapsed"
                )
                st.caption(f"{confidence:.0%}")
            
            # Submit button
            submit_col1, submit_col2 = st.columns([1, 4])
            with submit_col1:
                if st.button("✅ Submit Tag", key=f"submit_{unique_key}", type="primary"):
                    if new_player_name and new_player_name.strip():
                        try:
                            db.add_tag(
                                video_id=video_id,
                                frame_num=frame_num,
                                track_id=track_id,
                                player_name=new_player_name.strip(),
                                user_id=user_id,
                                confidence=confidence,
                                x=x_pos,
                                y=y_pos,
                                team=team
                            )
                            st.success(f"✅ Tagged Track {track_id} as '{new_player_name}'")
                            # Force rerun to update consensus
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error submitting tag: {e}")
                    else:
                        st.warning("Please enter a player name")
            
            st.markdown("---")
    
    if frame_consensus:
        consensus_df = pd.DataFrame([
            {
                'Track ID': c['track_id'],
                'Player Name': c['player_name'],
                'Confidence': f"{c['confidence_score']*100:.0f}%",
                'Votes': c['vote_count'],
                'Status': c['status']
            }
            for c in frame_consensus
        ])
        st.dataframe(consensus_df, use_container_width=True)
    else:
        st.info("No consensus tags yet for this frame")

def render_consensus_viewer_page():
    """View consensus tags across all frames"""
    st.title("📊 Consensus Viewer")
    
    db = get_database()
    drive = get_drive_access()
    
    # Video selection
    drive_input = st.text_input("Google Drive Video URL or File ID")
    
    if not drive_input:
        st.info("Enter a video URL or File ID")
        return
    
    video_id = drive.extract_file_id(drive_input)
    if not video_id:
        st.error("Invalid Google Drive URL")
        return
    
    # Get all consensus tags for this video
    # (This would require a new database method - for now show stats)
    stats = db.get_tagging_stats(video_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tags", stats['total_tags'])
    with col2:
        st.metric("Consensus Tags", stats['consensus_count'])
    with col3:
        st.metric("Contributors", stats['unique_users'])
    
    st.info("Full consensus viewer coming soon - showing statistics for now")

def render_user_stats_page():
    """User statistics and reputation"""
    st.title("👤 Your Tagging Statistics")
    
    db = get_database()
    user_id = get_user_id()
    
    reputation = db.get_user_reputation(user_id)
    
    if reputation:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tags", reputation['total_tags'])
        with col2:
            st.metric("Agreed Tags", reputation['agreed_tags'])
        with col3:
            rep_score = reputation['reputation_score']
            rep_color = "green" if rep_score > 0.7 else "orange" if rep_score > 0.5 else "red"
            st.markdown(f"""
            **Reputation Score:**  
            <span style="color:{rep_color}; font-size:2em">{rep_score*100:.0f}%</span>
            """, unsafe_allow_html=True)
        
        st.markdown(f"**Expertise Level:** {reputation['expertise_level'].title()}")
        
        # Recent tags
        st.subheader("Your Recent Tags")
        user_tags = db.get_user_tags(user_id, limit=50)
        if user_tags:
            tags_df = pd.DataFrame([
                {
                    'Video': t['video_id'][:20] + '...',
                    'Frame': t['frame_num'],
                    'Track': t['track_id'],
                    'Player': t['player_name'],
                    'Confidence': f"{t['confidence']*100:.0f}%",
                    'Date': t['timestamp']
                }
                for t in user_tags
            ])
            st.dataframe(tags_df, use_container_width=True)
        else:
            st.info("No tags yet - start tagging to see your contributions here!")
    else:
        st.info("No statistics yet - start tagging to build your reputation!")

