"""
Streamlit component for crowd-sourced player tagging
Integrates with dsx-tracker dashboard
"""

import streamlit as st
import pandas as pd
import cv2
import numpy as np
from typing import Dict, List, Optional
from tagging_database import TaggingDatabase
from consensus_engine import ConsensusEngine
from google_drive_integration import GoogleDriveAccess
import hashlib
from datetime import datetime

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

def get_players_at_frame(df: pd.DataFrame, frame_num: int) -> List[Dict]:
    """Get all players detected at a specific frame"""
    frame_data = df[df['frame'] == frame_num]
    
    players = []
    for _, row in frame_data.iterrows():
        players.append({
            'track_id': int(row.get('track_id', row.get('id', 0))),
            'x': float(row.get('x', row.get('center_x', 0))),
            'y': float(row.get('y', row.get('center_y', 0))),
            'player_name': str(row.get('player_name', '')),
            'team': str(row.get('team', ''))
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
    
    # Sidebar - Video Selection
    with st.sidebar:
        st.header("📹 Video Selection")
        
        # Google Drive URL or File ID
        drive_input = st.text_input(
            "Google Drive Video URL or File ID",
            placeholder="https://drive.google.com/file/d/... or FILE_ID"
        )
        
        # CSV Data Source
        csv_source = st.radio(
            "CSV Data Source",
            ["Upload CSV", "CSV URL", "Google Drive CSV"]
        )
        
        csv_data = None
        if csv_source == "Upload CSV":
            csv_file = st.file_uploader("Upload Tracking CSV", type=['csv'])
            if csv_file:
                csv_data = pd.read_csv(csv_file)
        elif csv_source == "CSV URL":
            csv_url = st.text_input("CSV URL", placeholder="https://...")
            if csv_url:
                csv_data = load_csv_data(csv_url)
        elif csv_source == "Google Drive CSV":
            csv_drive_id = st.text_input("Google Drive CSV File ID")
            if csv_drive_id:
                csv_path = drive.download_video(csv_drive_id)  # Reuse download function
                csv_data = load_csv_data(csv_path)
        
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
    
    # Get video URL
    video_url = drive.get_video_url(video_id)
    
    # Video player
    st.subheader("Video Player")
    st.video(video_url)
    
    # Frame selection
    max_frame = int(csv_data['frame'].max()) if 'frame' in csv_data.columns else 1000
    frame_num = st.slider("Frame Number", 0, max_frame, 0, step=10)
    
    # Load players at this frame
    players = get_players_at_frame(csv_data, frame_num)
    
    if not players:
        st.info(f"No players detected at frame {frame_num}")
        return
    
    st.subheader(f"Tag Players (Frame {frame_num})")
    st.markdown(f"Found {len(players)} players in this frame")
    
    # Tagging interface for each player
    for i, player in enumerate(players):
        track_id = player['track_id']
        
        with st.expander(f"Player Track #{track_id} - {player.get('player_name', 'Untagged')}", expanded=False):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Show consensus if available
                consensus = db.get_consensus(video_id, frame_num, track_id)
                if consensus:
                    confidence_color = "green" if consensus['confidence_score'] > 0.7 else "orange" if consensus['confidence_score'] > 0.5 else "red"
                    st.markdown(f"""
                    **Consensus:** {consensus['player_name']}  
                    **Confidence:** <span style="color:{confidence_color}">{consensus['confidence_score']*100:.0f}%</span>  
                    **Votes:** {consensus['vote_count']}
                    """, unsafe_allow_html=True)
                    
                    if consensus.get('alternatives'):
                        st.caption("Alternatives:")
                        for alt in consensus['alternatives']:
                            st.caption(f"  - {alt['name']}: {alt['rate']*100:.0f}%")
                else:
                    st.info("No consensus yet - be the first to tag!")
            
            with col2:
                # Tag input
                player_name = st.text_input(
                    f"Player Name (Track {track_id})",
                    value=consensus['player_name'] if consensus else player.get('player_name', ''),
                    key=f"name_{frame_num}_{track_id}"
                )
                
                confidence = st.slider(
                    "Your Confidence",
                    0.0, 1.0, 1.0,
                    key=f"conf_{frame_num}_{track_id}"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Submit Tag", key=f"submit_{frame_num}_{track_id}"):
                        try:
                            # Get user IP (if available)
                            ip_address = None
                            try:
                                import streamlit.web.server.websocket_headers as ws_headers
                                if hasattr(ws_headers, '_get_websocket_headers'):
                                    headers = ws_headers._get_websocket_headers()
                                    ip_address = headers.get('X-Forwarded-For', '').split(',')[0] if headers else None
                            except:
                                pass
                            
                            # Add tag
                            tag_id = db.add_tag(
                                video_id=video_id,
                                frame_num=frame_num,
                                track_id=track_id,
                                player_name=player_name,
                                user_id=user_id,
                                confidence=confidence,
                                ip_address=ip_address,
                                session_id=st.session_state.get('session_id')
                            )
                            
                            # Update consensus
                            consensus_engine.calculate_consensus(video_id, frame_num, track_id)
                            
                            st.success("✓ Tag submitted! Thank you for contributing.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error submitting tag: {e}")
                
                with col_btn2:
                    # Show user's previous tag for this player
                    user_tags = db.get_user_tags(user_id, limit=1000)
                    user_tag = next((t for t in user_tags 
                                   if t['video_id'] == video_id and 
                                   t['frame_num'] == frame_num and 
                                   t['track_id'] == track_id), None)
                    if user_tag:
                        st.caption(f"You tagged: {user_tag['player_name']}")
    
    # Frame consensus summary
    st.subheader("Frame Consensus Summary")
    frame_consensus = db.get_frame_consensus(video_id, frame_num)
    
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

