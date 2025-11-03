# Data Strategy Recommendations for 6,029 Extracted Matches

## Current Situation Analysis

**Total Matches:** 6,029  
**2018 vs 2018 Matches:** 316 (5.2%)  
**2017 vs 2017 Matches:** 362 (6.0%)  
**Unknown Teams:** 556 (59%)  

## Recommended Actions

### 1. **Create Age-Filtered Datasets** ⭐ Priority 1
**Problem:** Currently mixing all ages, which skews analytics  
**Solution:** Create separate filtered CSV files:
- `Extracted_Matches_2018_Only.csv` - Pure 2018 vs 2018 matches (316 matches)
- `Extracted_Matches_2018_Plus_Unknown.csv` - 2018 + Unknown that might be 2018 (~389 matches)
- `Extracted_Matches_2017_Benchmarking.csv` - For benchmarking (362 matches)
- `Extracted_Matches_Other_Ages.csv` - Archive (2015, 2016, etc.)

**Benefits:**
- Clean analytics focused on DSX's age group
- Maintains benchmarking data separately
- No contamination of rankings

### 2. **Enhance Age Detection** ⭐ Priority 2
**Problem:** 59% of teams are "Unknown" - many could be 2018  
**Solution:** Multi-source age detection:
- Parse from GotSport URLs (event names, division names)
- Extract from Division/League columns
- Check tournament context (e.g., "U8", "U09", "B08", "BU08")
- Use fuzzy matching with known 2018 team patterns

**Implementation:**
```python
def detect_team_age(team_name, source_url=None, division=None):
    # Check team name patterns
    # Check URL for age indicators
    # Check division name
    # Return: '2018', '2017', '2016', '2015', 'Unknown'
```

### 3. **Prioritize 2018 Tournament Discovery** ⭐ Priority 3
**Problem:** Limited 2018 data compared to older age groups  
**Solution:** When discovering tournaments:
- Focus GotSport event scanning on known 2018 Boys tournaments
- Filter `discover_ohio_tournaments_2018_boys.py` results by age
- Prioritize extraction from tournaments with confirmed 2018 teams

**Action Items:**
- Review `Ohio_Tournaments_2018_Boys_Discovered_20251102.csv` - verify all are truly 2018
- Update discovery script to validate age before extraction
- Add age validation step to `extract_missing_teams_schedules.py`

### 4. **Update Analytics to Use Age-Filtered Data** ⭐ Priority 4
**Current State:** Analytics use all 6,029 matches  
**Recommended:** 
- Primary: Use `Extracted_Matches_2018_Only.csv` for opponent stats
- Fallback: Use `Extracted_Matches_2018_Plus_Unknown.csv` with confidence markers
- Benchmarking: Use 2017 data separately (already implemented)

**Update These Functions:**
- `calculate_team_stats_from_extracted_matches()` - Add age filter parameter
- `get_opponent_three_stat_snapshot()` - Prefer 2018-filtered data
- Rankings generation - Exclude non-2018 teams from main rankings

### 5. **Add Confidence Scoring** ⭐ Priority 5
**Problem:** Mixing high-confidence vs low-confidence matches  
**Solution:** Add confidence score to matches:
- **High (90%+)**: 2018 vs 2018 with clear indicators
- **Medium (70-90%)**: 2018 vs Unknown (likely 2018) or from 2018 tournament
- **Low (<70%)**: Unknown vs Unknown or cross-age matches

**Use Cases:**
- High confidence only for rankings
- Medium confidence for opponent intel with indicator
- Low confidence for reference only (don't use in calculations)

### 6. **Create Usage Guidelines**
**Document When to Use Each Dataset:**

1. **Main Rankings & Opponent Intel:**
   - Use: `Extracted_Matches_2018_Only.csv` (high confidence)
   - Avoid: Other ages, unknown ages

2. **Benchmarking & Comparison:**
   - Use: `Extracted_Matches_2017_Benchmarking.csv` (already separated)
   - Purpose: Understanding where 2018 teams compare to 2017 teams

3. **Gap Filling (Fallback):**
   - Use: `Extracted_Matches_2018_Plus_Unknown.csv` with warning indicator
   - Show: "Using X matches (Y% confidence) from expanded dataset"

4. **Reference Only:**
   - Archive: Older age groups for potential future use
   - Don't use in active analytics

## Implementation Priority

**Phase 1 (Immediate):**
1. Create age-filtered CSV files
2. Update analytics to use 2018-only data by default
3. Add confidence indicators where using Unknown age matches

**Phase 2 (Short-term):**
1. Enhance age detection algorithm
2. Re-run extraction with improved age detection
3. Update discovery scripts to validate age

**Phase 3 (Ongoing):**
1. Monitor data quality (confidence scores)
2. Prioritize 2018 tournament extraction
3. Build age-validated dataset over time

## Expected Outcomes

✅ **Cleaner Analytics:** Rankings and opponent intel use age-appropriate data  
✅ **Better Confidence:** Users know data quality for each opponent  
✅ **Focused Discovery:** New tournament extraction targets 2018 Boys  
✅ **Scalable:** Framework for handling multiple age groups if needed

