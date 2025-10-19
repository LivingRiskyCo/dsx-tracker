# 🎮 Game Day Quick Reference - Live Tracker

## 🚀 Pre-Game Setup (2 minutes)

1. **Double-click:** `launch_game_tracker.bat`
2. **Enter game info:**
   - Opponent name
   - Location
   - Tournament/League
3. **Select starting 7:**
   - Pick 7 players from dropdown
   - Bench players shown automatically
4. **Click:** 🚀 START GAME

---

## ⚽ During Game - Big Button Actions

### Quick Actions (1-2 taps each)

| Button | What It Does | Time to Record |
|--------|-------------|----------------|
| ⚽ **DSX GOAL** | Select scorer → Add assist → Done | 5 seconds |
| 🥅 **OPP GOAL** | Instant record | 1 second |
| 🎯 **SHOT** | Select shooter → Note result | 3 seconds |
| 🧤 **SAVE** | Select keeper → Note save type | 3 seconds |
| ⚠️ **CORNER** | Instant record | 1 second |
| 🔄 **SUB** | Player out → Player in → Done | 5 seconds |

---

## ⏱️ Timer Controls

- **▶️ Start** - Begin countdown (25:00)
- **⏸️ Pause** - Stop timer (use for injuries, etc.)
- **⏭️ Next Half** - Move to 2nd half (resets to 25:00)
- **🔄 Reset Timer** - Start current half over
- **⏹️ End Game** - Finish and see summary

### 🎯 **Real Soccer Timer**
- **Continuous Clock** - Timer runs like real soccer (no auto-pause)
- **Manual Pause** - Only for injuries or timeouts
- **Visual Indicator** - Shows "Timer running" status

---

## 📱 Parent Live View

**Share the link shown in your browser with parents:**

Example: `http://192.168.1.100:8502`

**What parents see:**
- ✅ Live score
- ✅ Goal scorers
- ✅ Game timer
- ✅ Event feed
- ❌ Can't press buttons

---

## 💾 Post-Game (30 seconds)

1. **Review summary** - Score, scorers, assists
2. **Click:** 💾 Save to CSV
3. **Done!** - Data auto-updates main dashboard

---

## 🎯 Pro Tips

### Fast Recording
- ⏱️ **Timer keeps running** - Enter details while clock continues (like real soccer)
- 🔄 **Track subs early** - Keeps "on field" list accurate
- 📝 **Add notes** - "PK", "header", "solo run" for memory
- ⏸️ **Pause only for injuries** - Use manual pause for timeouts/injuries

### Accuracy
- ✅ **Double-check scorer** - Easy to tap wrong player
- ❌ **Use "Undo"** if you make a mistake (coming soon!)
- 💾 **Save periodically** - Don't wait until end

### Sharing
- 📱 **Test parent link before kickoff** - Make sure it works
- 🔄 **Auto-refresh** - Parents see updates every few seconds
- 🔇 **Silent mode** - Mute notifications so you can focus

---

## 📊 What Gets Saved

### Auto-saved to CSVs:
1. **DSX_Matches_Fall2025.csv** - Game score, result, location
2. **game_player_stats.csv** - Individual goals/assists per player
3. **Event log** - Full timestamped event feed (download option)

### What updates on dashboard:
- Match History
- Player Stats (goals, assists)
- Game Log (per-game breakdown)
- Team Analysis

---

## 🆘 Troubleshooting

### Timer won't start
- Click ▶️ Start button again
- If stuck, click 🔄 Reset Timer

### Can't find player
- Check if they're on the bench (might need to sub them in first)
- Verify roster.csv has all players

### Parent link not working
- Make sure you're on same WiFi network
- Check firewall isn't blocking port 8502
- Try restarting the tracker

### Lost connection
- Click 🔄 Refresh
- Recent events are saved in browser memory
- Always click 💾 Save periodically!

---

## 📞 Quick Commands

```bash
# Start tracker
launch_game_tracker.bat

# Stop tracker
Ctrl + C (in terminal)

# View main dashboard
launch_dashboard.bat
```

---

## ⚽ Enjoy the Game!

**Focus on coaching - let the tracker handle the stats!** 🎯

