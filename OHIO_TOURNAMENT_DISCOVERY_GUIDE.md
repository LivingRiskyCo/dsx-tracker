# Ohio Tournament Discovery Guide

## Overview

The `discover_ohio_tournaments_2018_boys.py` script expands GotSport scraping to automatically find all Ohio tournaments with 2018 Boys teams. This dramatically increases the amount of opponent data available for analysis.

## How It Works

### Strategy

1. **Known Tournaments**: Checks a pre-configured list of known Ohio tournaments
2. **Event ID Scanning**: Scans GotSport event ID ranges to discover new tournaments
3. **Division Discovery**: Finds all 2018 Boys divisions within each tournament
4. **Standings Scraping**: Extracts team standings and calculates Strength Indexes

### Features

- **Automatic Discovery**: Finds tournaments by scanning event ID ranges
- **2018 Boys Filtering**: Only captures divisions with 2018 Boys teams
- **Ohio Focus**: Filters for Ohio-specific tournaments using keywords
- **Comprehensive Data**: Extracts full standings, stats, and calculates Strength Indexes
- **Rate Limiting**: Built-in delays to respect GotSport's servers

## Usage

### Basic Usage

```bash
python discover_ohio_tournaments_2018_boys.py
```

The script will:
1. Check known tournaments (Club Ohio Fall Classic, CU Fall Finale, Haunted Classic)
2. Ask if you want to scan event ID ranges for additional tournaments
3. Discover all 2018 Boys divisions in found tournaments
4. Scrape standings for all discovered divisions
5. Save results to CSV files

### Output Files

- `Ohio_Tournaments_2018_Boys_Discovered_YYYYMMDD.csv` - All team data from discovered tournaments
- `Ohio_Tournaments_Summary_YYYYMMDD.csv` - Summary of discovered tournaments

## Configuration

### Adding Known Tournaments

Edit `ohio_tournaments_config.py` to add new tournaments:

```python
{
    'name': 'Tournament Name',
    'event_id': '12345',
    'year': 2025,
    'division_urls': [
        'https://system.gotsport.com/org_event/events/12345/results?group=67890',
    ],
    'age_gender_filter': {
        'age': 9,
        'gender': 'm'
    },
    'notes': 'Tournament description'
}
```

### Adjusting Event ID Scan Ranges

Edit `ohio_tournaments_config.py` to adjust scan ranges:

```python
EVENT_ID_SCAN_RANGES = [
    {
        'start': 44000,
        'end': 45000,
        'step': 50,
        'description': '2025 Tournament Range'
    },
]
```

## Integration with Dashboard

### Adding Discovered Tournaments

1. Run the discovery script
2. Review the discovered tournaments in the CSV output
3. Add promising tournaments to `ohio_tournaments_config.py`
4. Create dedicated fetch scripts (like `fetch_club_ohio_fall_classic.py`) for important tournaments
5. Add fetch scripts to `update_all_data.py` workflow

### Loading Discovered Data

The discovered tournament data will be automatically included in the dashboard if:
- The CSV file matches the naming pattern: `*_Division_Rankings.csv`
- The file is in the root directory
- The `load_division_data()` function in `dsx_dashboard.py` is configured to load it

## Best Practices

1. **Run Discovery Weekly**: New tournaments appear regularly
2. **Review Before Adding**: Check discovered tournaments before adding to known list
3. **Rate Limiting**: Don't run too frequently - built-in delays prevent server overload
4. **Manual Verification**: Verify important tournaments manually before relying on auto-discovered data
5. **Update Config**: Keep `ohio_tournaments_config.py` updated with new discoveries

## Limitations

1. **No Public Search API**: GotSport doesn't have a public search API, so we scan event IDs
2. **Rate Limiting**: Too many requests may get blocked - script includes delays
3. **Event ID Patterns**: Event IDs may not always be sequential
4. **Division Detection**: Some divisions may not be detected if naming doesn't match patterns

## Future Enhancements

- Machine learning to better identify 2018 Boys divisions
- Automatic tournament discovery from Ohio soccer organization websites
- Integration with tournament listing sites
- Periodic automatic discovery (daily/weekly scans)
- Notification system for new tournaments discovered

## Troubleshooting

### No Tournaments Found

- Check internet connection
- Verify GotSport URLs are accessible
- Try adjusting event ID scan ranges
- Check if GotSport has changed their URL structure

### Missing Divisions

- Verify division naming matches age patterns
- Check if division uses different terminology
- Manually add division URLs to config file

### Rate Limiting Errors

- Increase delays between requests in script
- Reduce scan range size
- Run discovery during off-peak hours

