# Peer Rankings vs Opponent Rankings - Explanation

## 📊 **Two Different Ranking Sections**

### **1. 🎯 Peer Rankings - Tournament Teams**
**Location:** Division Rankings page → "Peer Rankings - Tournament Teams" section

**What it shows:**
- Teams that play **tournament schedules** like DSX
- Only includes teams from **tournament division files**:
  - Haunted Classic (Orange & Black divisions)
  - Club Ohio Fall Classic
  - CU Fall Finale
- Shows **tournament-specific stats** (3-4 games per tournament)
- Filters out teams with **zero games played** (they haven't started yet)

**Current teams included:**
- Lakota FC 2018 Black (Haunted Classic Orange)
- Club Ohio West 18B Academy (Haunted Classic Orange)
- Lakota FC 2018 Red (Haunted Classic Black)
- Club Ohio United 2018 Black (Haunted Classic Black)
- Little Miami FC (Haunted Classic Black)
- BSA Celtic 18B City (Haunted Classic Orange)
- TFA B18 Elite (Haunted Classic Orange)
- BSA Celtic 18B United (Haunted Classic Orange)
- Oakwood United (Haunted Classic Black)
- DSX Orange 2018 (your team)

**Purpose:** Compare DSX against similar teams that play tournament schedules (not regular league schedules).

---

### **2. 📋 Rankings vs Opponents (Played & Upcoming)**
**Location:** Division Rankings page → "Rankings vs Opponents (Played & Upcoming)" section

**What it shows:**
- **ALL opponents** DSX has played or will play
- Includes teams from:
  - Tournament divisions
  - League divisions (OCL Stripes, White, Stars, etc.)
  - Any team DSX has matched against
- Shows **full season stats** (from division data when available)
- Uses **head-to-head stats** for teams not in division data

**Current teams:** 25 opponents (as of your current data)

**Purpose:** See how DSX ranks against all teams you've actually played or will play (regardless of whether they play tournaments or leagues).

---

## 🔍 **Key Differences**

| Feature | Peer Rankings | Opponent Rankings |
|---------|--------------|------------------|
| **Data Source** | Tournament files only | All division files + match history |
| **Teams Included** | Tournament players only | All DSX opponents |
| **Stats Shown** | Tournament stats (3-4 games) | Full season stats (when available) |
| **Filtering** | Excludes teams with GP=0 | Includes all opponents |
| **Purpose** | Compare against tournament peers | Compare against all opponents |

---

## ✅ **What Was Fixed**

### **1. Missing Teams in Peer Rankings**
**Issue:** Some tournament teams weren't showing up (like Lakota FC 2018 Black, Club Ohio West 18B Academy, etc.)

**Fix:**
- Added column name normalization to handle lowercase/capitalized variations
- Fixed data parsing to ensure all tournament teams are included
- Properly handle different column name formats (`rank` vs `Rank`, `gp` vs `GP`, etc.)

### **2. Empty Rows with "85" Values**
**Issue:** Empty rows showing only StrengthIndex value (85) but no team names or other stats

**Fix:**
- Filter out teams with **GP=0** (they haven't started tournament yet)
- This removes teams from Club Ohio Fall Classic and CU Fall Finale that haven't played yet
- Prevents empty/incomplete rows from appearing

### **3. Data Parsing Issues**
**Issue:** Tournament files have different column name formats (lowercase vs capitalized)

**Fix:**
- Added column name normalization to handle:
  - `rank` → `Rank`
  - `team` → `Team`
  - `gp` → `GP`
  - `strength_index` → `StrengthIndex`
  - etc.

---

## 📈 **How It Works Now**

### **Peer Rankings Process:**
1. Load tournament files (Haunted Classic, Club Ohio Fall Classic, CU Fall Finale)
2. Normalize column names (handle lowercase/capitalized)
3. Remove DSX from tournament data (we add our own stats)
4. **Filter out teams with GP=0** (they haven't started)
5. Calculate per-game stats for each team
6. Add DSX to the peer group
7. Sort by PPG then Strength Index
8. Display ranked table

### **Opponent Rankings Process:**
1. Load all division data (from `load_division_data()`)
2. Get list of all opponents DSX has played/will play
3. Match opponents to division data (exact or fuzzy matching)
4. For matched teams: use division stats
5. For unmatched teams: use head-to-head stats from DSX matches
6. Combine and display ranked table

---

## 🎯 **What You'll See**

### **Peer Rankings Table:**
- **~10 teams** (tournament players with games played)
- Lakota FC 2018 Black (Rank #1, PPG 9.67)
- Club Ohio West 18B Academy (Rank #2, PPG 9.67)
- Lakota FC 2018 Red (Rank #3, PPG 8.67)
- DSX Orange 2018 (Rank #8, PPG 1.2)
- etc.

### **Opponent Rankings Table:**
- **25 teams** (all opponents DSX has played/will play)
- Includes tournament teams + league teams + all opponents
- Full season stats when available
- Head-to-head stats for teams not in division data

---

## 💡 **Why Two Sections?**

1. **Peer Rankings** = "How do we stack up against other tournament teams?"
   - Useful for tournament preparation
   - Shows tournament-specific performance
   - Smaller, focused comparison group

2. **Opponent Rankings** = "How do we stack up against all our opponents?"
   - Useful for overall season assessment
   - Shows full season performance
   - Comprehensive comparison across all opponents

---

## ✅ **Status**

- ✅ Peer Rankings now includes all tournament teams (with games played)
- ✅ Empty rows removed (teams with GP=0 filtered out)
- ✅ Column name normalization working
- ✅ Both sections display correctly
- ✅ All teams included and properly ranked

