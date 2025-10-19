# DSX Tracker - Data Sources Reference

## 📊 **All Websites We Track**

This document lists all external data sources the DSX Tracker scrapes for opponent intelligence.

---

## 🌐 **Primary Data Sources**

### **1. GotSport (Ohio Challenge League - OCL)**

**Website:** https://system.gotsport.com

**What We Track:**

#### **A. OCL BU08 Stripes Division (7v7)**
- **URL:** https://system.gotsport.com/org_event/events/45535/results?group=418528
- **Teams:** 23 teams (Northeast, Northwest, Southeast regional groups)
- **Script:** `fetch_gotsport_division.py`
- **Output:** `OCL_BU08_Stripes_Division_Rankings.csv`

**Your Opponents in This Division:**
- Elite FC 2018 Boys Liverpool
- Elite FC 2018 Boys Tottenham
- Barcelona United Barcelona United Elite II 18B
- LFC United LFC United 2018 B Elite 2
- Grove City Kids Association GCKA 2018B
- Northwest FC Northwest FC 2018B Academy Blue
- Blast FC Soccer Academy Blast FC 2018B

---

#### **B. OCL BU08 White Division (7v7)**
- **URL:** https://system.gotsport.com/org_event/events/45535/results?group=418523
- **Teams:** 7 teams (Club Ohio West division)
- **Script:** `fetch_gotsport_white_division.py`
- **Output:** `OCL_BU08_White_Division_Rankings.csv`

**Your Opponents in This Division:**
- Club Ohio Club Ohio West 18B Academy II

---

#### **C. OCL BU08 Stars 5v5 Division**
- **URL:** https://system.gotsport.com/org_event/events/45535/results?group=418525
- **Teams:** 8 teams (5v5 format)
- **Script:** `fetch_gotsport_stars_division.py`
- **Output:** `OCL_BU08_Stars_Division_Rankings.csv`

**Note:** This division is 5v5, not 7v7 like DSX plays.

---

#### **D. OCL BU08 Stars 7v7 Division**
- **URL:** https://system.gotsport.com/org_event/events/45535/results
- **Teams:** 7 teams (7v7 format)
- **Script:** `fetch_gotsport_stars_7v7.py`
- **Output:** `OCL_BU08_Stars_7v7_Division_Rankings.csv`

**Your Opponents in This Division:**
- Elite FC Elite FC 2018 Boys Arsenal

---

### **2. MVYSA (Mid-Valley Youth Soccer Association)**

**Website:** https://www.mvysa.com

**What We Track:**

#### **A. BSA Celtic Team Schedules**
- **BSA Celtic 18B United:** https://www.mvysa.com/cgi-bin/sked.cgi?fnc=sked2&bt=4264&season=202509
- **BSA Celtic 18B City:** https://www.mvysa.com/cgi-bin/sked.cgi?fnc=sked2&bt=4263&season=202509
- **Script:** `fetch_bsa_celtic.py`
- **Output:** `BSA_Celtic_Schedules.csv`

**Your Opponents:**
- BSA Celtic 18B United (Oct 18 game)
- BSA Celtic 18B City (Oct 19 game)

---

#### **B. MVYSA B09-3 Division Standings**
- **URL:** https://www.mvysa.com/cgi-bin/standings.cgi?fnc=choosed&season=202509
- **Teams:** 6 teams (BSA Celtic's division)
- **Script:** `fetch_mvysa_division.py`
- **Output:** `MVYSA_B09_3_Division_Rankings.csv`

**Note:** This division includes the BSA Celtic teams you play against.

---

## 📋 **Complete Opponent Coverage**

### **Your 15 Opponents:**

| Opponent | Division | Data Source | Status |
|----------|----------|-------------|--------|
| Barcelona United Elite II 18B | OCL Stripes | GotSport | ✅ Tracked |
| LFC United 2018 B Elite 2 | OCL Stripes | GotSport | ✅ Tracked |
| Elite FC 2018 Boys Arsenal | OCL Stars 7v7 | GotSport | ✅ Tracked |
| Elite FC 2018 Boys Liverpool | OCL Stripes | GotSport | ✅ Tracked |
| Elite FC 2018 Boys Tottenham | OCL Stripes | GotSport | ✅ Tracked |
| Grove City Kids Association GCKA 2018B | OCL Stripes | GotSport | ✅ Tracked |
| Northwest FC 2018B Academy Blue | OCL Stripes | GotSport | ✅ Tracked |
| Blast FC Soccer Academy Blast FC 2018B | OCL Stripes | GotSport | ✅ Tracked |
| Club Ohio West 18B Academy II | OCL White | GotSport | ✅ Tracked |
| BSA Celtic 18B United | MVYSA B09-3 | MVYSA | ✅ Tracked |
| BSA Celtic 18B City | MVYSA B09-3 | MVYSA | ✅ Tracked |
| Columbus United U8B | Unknown | N/A | ❌ Not tracked |
| Ohio Premier 2017 Boys Academy Dublin White | U9 Division | N/A | ⚠️ Different age group |
| Ohio Premier 2017 Boys Premier OCL | U9 Division | N/A | ⚠️ Different age group |
| Club Ohio Fall Classic TBD | Tournament | N/A | ⚠️ Placeholder |

**Coverage:** 11 of 15 opponents (73%) - **85% when excluding U9 teams and TBD**

---

## 🔄 **How Often We Update**

### **Automatic Updates:**
Run `update_all_data.py` or `update_all_data.bat` to refresh all sources at once.

**What it does:**
1. Fetches OCL BU08 Stripes Division (GotSport)
2. Fetches OCL BU08 White Division (GotSport)
3. Fetches OCL BU08 Stars 5v5 Division (GotSport)
4. Fetches OCL BU08 Stars 7v7 Division (GotSport)
5. Fetches BSA Celtic schedules (MVYSA)
6. Fetches MVYSA B09-3 Division standings (MVYSA)

**Recommended frequency:** Once per week (Sunday after weekend games)

---

## 🎯 **What Data We Extract**

### **For Each Team:**
- **Standings:** Wins, Losses, Draws, Goals For/Against
- **Performance:** Points, PPG (Points Per Game)
- **Strength Index:** Calculated metric (0-100) based on PPG + Goal Differential
- **Schedule:** Upcoming games, results, opponents
- **Rank:** Position in their division

### **For Each Match:**
- Date, Time, Location
- Home/Away designation
- Score (if completed)
- Opponent

---

## ⚠️ **Opponents We DON'T Track (And Why)**

### **1. Columbus United Columbus United U8B**
- **Reason:** Team name doesn't match any in tracked divisions
- **Possible explanations:**
  - Different league (not OCL or MVYSA)
  - Team withdrew or name changed mid-season
  - Different age group
- **Impact:** No strength index or predictions available

### **2. Ohio Premier 2017 Boys Teams**
- **Reason:** These are U9 teams (2017 birth year), not U8
- **Why DSX plays them:** Mixed age scrimmages or tournament games
- **Impact:** We don't track U9 divisions (different competitive level)

### **3. Club Ohio Fall Classic TBD**
- **Reason:** Tournament placeholder - opponents assigned later
- **When available:** After tournament brackets are published
- **Where:** Typically on Club Ohio's website or GotSport

---

## 🆘 **Missing an Opponent?**

### **If your team plays a new opponent not listed above:**

1. **Find their team page:**
   - GotSport: https://system.gotsport.com/ (search by team name)
   - MVYSA: https://www.mvysa.com/ (search schedules/standings)

2. **Share with me:**
   - Team full name
   - Division/league name
   - URL to their schedule or division standings

3. **I can add them:**
   - Create new scraper (5-10 minutes)
   - Add to `update_all_data.py`
   - Track their stats going forward

---

## 🌐 **How to Share This with Your Team**

### **Simple Version (for parents):**

> "We track opponents from 2 websites:
> 
> **GotSport (gotsport.com):**
> - OCL divisions where most opponents play
> - 4 divisions, 45 teams tracked
> 
> **MVYSA (mvysa.com):**
> - BSA Celtic teams (upcoming opponents)
> - Division standings and schedules
> 
> This gives us Strength Index and predictions for 11 of our 15 opponents!"

### **Detailed Version (for coaches/managers):**

Send them this document or the relevant URLs above for their reference.

---

## 📱 **Quick Links**

### **OCL (GotSport):**
- **Main Event:** https://system.gotsport.com/org_event/events/45535
- **Stripes Division:** https://system.gotsport.com/org_event/events/45535/results?group=418528
- **White Division:** https://system.gotsport.com/org_event/events/45535/results?group=418523
- **Stars 7v7:** https://system.gotsport.com/org_event/events/45535/results

### **MVYSA:**
- **Main Site:** https://www.mvysa.com/
- **BSA Celtic 18B United:** https://www.mvysa.com/cgi-bin/sked.cgi?fnc=sked2&bt=4264&season=202509
- **BSA Celtic 18B City:** https://www.mvysa.com/cgi-bin/sked.cgi?fnc=sked2&bt=4263&season=202509

---

## ✅ **Summary**

**Total Data Sources:** 2 websites (GotSport + MVYSA)  
**Total Divisions Tracked:** 5 divisions  
**Total Teams Tracked:** 51 teams  
**Your Opponents Tracked:** 11 of 15 (73%)  

**Scripts:**
- `fetch_gotsport_division.py` - OCL Stripes
- `fetch_gotsport_white_division.py` - OCL White
- `fetch_gotsport_stars_division.py` - OCL Stars 5v5
- `fetch_gotsport_stars_7v7.py` - OCL Stars 7v7
- `fetch_bsa_celtic.py` - BSA Celtic schedules
- `fetch_mvysa_division.py` - MVYSA division
- `update_all_data.py` - Updates all sources at once

**All data is publicly available on these league websites - we're just automating the collection!**

---

**Last Updated:** October 14, 2025  
**Next Update Recommended:** After weekend games (Oct 18-19)


