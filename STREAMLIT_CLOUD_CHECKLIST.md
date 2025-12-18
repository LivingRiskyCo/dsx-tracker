# Streamlit Cloud Deployment Checklist

## Pre-Deployment

- [x] All tagging files created
- [x] Database path configured for Streamlit Cloud
- [x] Requirements.txt updated with dependencies
- [x] Integration added to dsx_dashboard.py

## Files to Commit

Make sure these files are in your GitHub repository:

- [ ] `tagging_database.py`
- [ ] `consensus_engine.py`
- [ ] `google_drive_integration.py`
- [ ] `streamlit_tagging.py`
- [ ] `dsx_dashboard.py` (updated)
- [ ] `requirements.txt` (updated)

## Deployment Steps

1. **Add files to Git:**
   ```bash
   git add tagging_database.py consensus_engine.py google_drive_integration.py streamlit_tagging.py
   git add dsx_dashboard.py requirements.txt
   ```

2. **Commit:**
   ```bash
   git commit -m "Add crowd-sourced player tagging feature"
   ```

3. **Push to GitHub:**
   ```bash
   git push
   ```

4. **Wait for Streamlit Cloud to deploy** (2-3 minutes)

5. **Verify at https://dsx-tracker.streamlit.app:**
   - [ ] Dashboard loads without errors
   - [ ] New pages appear in sidebar
   - [ ] "🏷️ Player Tagging" page works
   - [ ] Can enter Google Drive URL
   - [ ] Can upload CSV
   - [ ] Can tag players
   - [ ] Consensus updates correctly

## Post-Deployment Testing

### Test Tagging Flow:
1. Navigate to "🏷️ Player Tagging"
2. Enter Google Drive video URL
3. Upload CSV tracking data
4. Select a frame
5. Tag a player
6. Submit tag
7. Verify tag appears in consensus

### Test Consensus:
1. Navigate to "📊 Consensus Viewer"
2. Enter same video ID
3. Verify consensus appears

### Test User Stats:
1. Navigate to "👤 My Tags"
2. Verify your tags appear
3. Check reputation score

## Troubleshooting

### If deployment fails:
- Check Streamlit Cloud logs
- Verify all files are in GitHub
- Check requirements.txt syntax
- Ensure no syntax errors in Python files

### If tagging doesn't work:
- Check database path (should use `/mount/src/data/` in cloud)
- Verify Google Drive URL format
- Check CSV file format
- Review Streamlit Cloud logs

### If database errors:
- Database is created automatically
- Check write permissions
- Verify path exists

## Success Criteria

✅ All three new pages appear in navigation  
✅ Tagging interface loads without errors  
✅ Can submit tags successfully  
✅ Consensus updates in real-time  
✅ User statistics display correctly  
✅ Database persists across sessions  

## Next Steps After Deployment

1. Share URL with team: https://dsx-tracker.streamlit.app
2. Test with real video and CSV data
3. Invite team members to tag
4. Monitor consensus scores
5. Export consensus data for desktop app

---

**Ready to deploy!** 🚀

