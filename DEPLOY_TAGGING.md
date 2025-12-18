# Deploy Player Tagging to Streamlit Cloud

## Quick Deployment Steps

Since you already have `dsx-tracker.streamlit.app` deployed, you just need to:

### 1. Add New Files to GitHub

```bash
cd C:\Users\nerdw\Documents\DSX

# Add the new tagging files
git add tagging_database.py
git add consensus_engine.py
git add google_drive_integration.py
git add streamlit_tagging.py
git add requirements.txt

# Commit
git commit -m "Add crowd-sourced player tagging feature"

# Push to GitHub
git push
```

### 2. Streamlit Cloud Will Auto-Deploy

- Streamlit Cloud automatically detects the push
- It will install new dependencies (`opencv-python`, `gdown`)
- The new pages will appear in your dashboard
- **Wait 2-3 minutes** for deployment

### 3. Verify Deployment

1. Go to https://dsx-tracker.streamlit.app
2. Check the sidebar navigation
3. You should see three new pages:
   - 🏷️ Player Tagging
   - 📊 Consensus Viewer
   - 👤 My Tags

## Files Added

✅ `tagging_database.py` - SQLite database for tags  
✅ `consensus_engine.py` - Consensus algorithm  
✅ `google_drive_integration.py` - Google Drive video access  
✅ `streamlit_tagging.py` - Tagging interface  
✅ Updated `dsx_dashboard.py` - Integrated tagging pages  
✅ Updated `requirements.txt` - Added dependencies  

## Database Storage

The tagging database will be created automatically:
- **Streamlit Cloud**: Uses persistent storage at `/mount/src/data/tagging.db`
- **Local Development**: Uses `data/tagging.db`

The database persists across deployments, so tags won't be lost.

## Testing After Deployment

1. **Navigate to "🏷️ Player Tagging"**
2. **Enter a Google Drive video URL** (or File ID)
3. **Upload CSV tracking data**
4. **Tag a few players** to test
5. **Check "📊 Consensus Viewer"** to see consensus
6. **Check "👤 My Tags"** to see your statistics

## Troubleshooting

### "Tagging system not available"
- Check that all files were pushed to GitHub
- Verify `requirements.txt` includes `opencv-python` and `gdown`
- Check Streamlit Cloud logs for errors

### "Database error"
- The database is created automatically on first use
- If issues persist, check Streamlit Cloud logs
- Database path should be `/mount/src/data/tagging.db` in cloud

### "Google Drive video not loading"
- Ensure video is shared publicly ("Anyone with the link")
- Verify the URL format is correct
- Try using just the File ID instead of full URL

## Next Steps

1. ✅ Push files to GitHub
2. ✅ Wait for auto-deployment
3. ✅ Test tagging feature
4. ✅ Share with team members
5. ✅ Start tagging players!

## Features Now Available

- **Crowd-Sourced Tagging** - Multiple users can tag players
- **Consensus Engine** - Automatic aggregation with confidence scores
- **Reputation System** - Users gain reputation based on agreement
- **Google Drive Integration** - Videos hosted on Google Drive
- **Real-Time Updates** - Consensus updates as tags are submitted

Your tagging system is ready to use! 🎉

