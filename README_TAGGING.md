# Crowd-Sourced Player Tagging System

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Run the dashboard:**
   ```bash
   streamlit run dsx_dashboard.py
   ```

3. **Navigate to "🏷️ Player Tagging"** in the sidebar

4. **Enter Google Drive video URL** and upload CSV tracking data

5. **Start tagging players!**

## Features

✅ **Crowd-Sourced Tagging** - Multiple users can tag the same players  
✅ **Consensus Engine** - Automatically calculates consensus with confidence scores  
✅ **Reputation System** - Users gain reputation based on agreement  
✅ **Google Drive Integration** - Videos hosted on Google Drive (free)  
✅ **Real-Time Updates** - Consensus updates as tags are submitted  

## Files Created

- `tagging_database.py` - SQLite database for storing tags
- `consensus_engine.py` - Consensus algorithm
- `google_drive_integration.py` - Google Drive video access
- `streamlit_tagging.py` - Tagging interface components
- `TAGGING_SETUP.md` - Detailed setup guide

## Integration

The tagging system is integrated into `dsx_dashboard.py` with three new pages:
- 🏷️ Player Tagging - Main tagging interface
- 📊 Consensus Viewer - View consensus across all frames
- 👤 My Tags - User statistics and reputation

## Database

SQLite database is created at `data/tagging.db` automatically on first use.

## Google Drive Setup

1. Upload video to Google Drive
2. Right-click → Share → "Anyone with the link"
3. Copy the shareable link
4. Use in the tagging interface

The system will extract the file ID automatically from the URL.

