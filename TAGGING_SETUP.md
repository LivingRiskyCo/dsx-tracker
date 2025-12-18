# Crowd-Sourced Player Tagging Setup Guide

## Overview

The tagging system allows multiple users to tag players in video frames, with consensus-based aggregation to improve accuracy.

## Installation

### 1. Install Dependencies

```bash
pip install streamlit pandas opencv-python gdown
```

Or update `requirements_streamlit.txt`:

```
streamlit>=1.28.0
numpy>=1.24.0
pandas>=2.0.0
opencv-python>=4.8.0
gdown>=4.7.0
```

### 2. File Structure

Ensure these files are in your DSX directory:

```
DSX/
├── dsx_dashboard.py          # Main dashboard (updated)
├── streamlit_tagging.py       # Tagging interface
├── tagging_database.py        # Database layer
├── consensus_engine.py       # Consensus algorithm
├── google_drive_integration.py # Google Drive access
└── data/
    └── tagging.db            # SQLite database (auto-created)
```

## Google Drive Setup

### Option 1: Public Videos (Simplest)

1. Upload video to Google Drive
2. Right-click → Share → "Anyone with the link"
3. Copy the shareable link
4. Use the link in the tagging interface

### Option 2: Google Drive API (Advanced)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google Drive API"
4. Create OAuth 2.0 credentials
5. Download `credentials.json`
6. Place in DSX directory

## Usage

### For Taggers:

1. Open DSX Tracker dashboard
2. Navigate to "🏷️ Player Tagging"
3. Enter Google Drive video URL or File ID
4. Upload or provide CSV tracking data
5. Select frame number
6. Tag each player with their name
7. Submit tags

### For Administrators:

1. View consensus in "📊 Consensus Viewer"
2. Check statistics and contributor reputation
3. Export consensus data for use in desktop app

## Features

- **Crowd-Sourced Tagging**: Multiple users can tag the same players
- **Consensus Engine**: Automatically aggregates tags with confidence scores
- **Reputation System**: Users gain reputation based on agreement with consensus
- **Google Drive Integration**: Videos hosted on Google Drive (free storage)
- **Real-Time Updates**: Consensus updates as tags are submitted

## Database

The system uses SQLite database (`data/tagging.db`) to store:
- User tags
- Consensus tags
- User reputation
- Tag conflicts

## Integration with Desktop App

The desktop SoccerID app can:
1. Export videos and CSV to web format
2. Import consensus tags back to improve player gallery
3. Use consensus data to enhance Re-ID accuracy

## Troubleshooting

### "Tagging system not available"
- Ensure all dependencies are installed
- Check that all Python files are in the DSX directory

### "Error loading CSV"
- Verify CSV has required columns: `frame`, `track_id`, `x`, `y`
- Check CSV file format (should be comma-separated)

### "Invalid Google Drive URL"
- Ensure video is shared publicly or use File ID
- Verify URL format matches: `https://drive.google.com/file/d/FILE_ID/view`

## Next Steps

1. Test with a sample video
2. Invite team members to tag
3. Monitor consensus scores
4. Export consensus for desktop app integration

