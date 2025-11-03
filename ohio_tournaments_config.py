#!/usr/bin/env python3
"""
Ohio Tournaments Configuration File
Add new tournament URLs here as they're discovered
"""

# Configuration for Ohio tournaments with 2018 Boys teams
# Add new tournaments as they're discovered

OHIO_TOURNAMENTS_CONFIG = [
    {
        'name': 'Club Ohio Fall Classic',
        'event_id': '44565',
        'year': 2025,
        'division_urls': [
            'https://system.gotsport.com/org_event/events/44565/schedules?group=436954',  # U09B Select III
            'https://system.gotsport.com/org_event/events/44565/results?group=436954',
        ],
        'age_gender_filter': {
            'age': 9,
            'gender': 'm'
        },
        'notes': 'November 1-2, 2025 - Club Ohio Tournaments - DSX played 3 matches'
    },
    {
        'name': 'Cincinnati United Fall Finale',
        'event_id': '40635',
        'year': 2025,
        'division_urls': [
            'https://system.gotsport.com/org_event/events/40635/results?age=8&gender=m',
            'https://system.gotsport.com/org_event/events/40635/schedules?age=8&gender=m',
        ],
        'age_gender_filter': {
            'age': 8,
            'gender': 'm'
        },
        'notes': 'Cincinnati United tournament - October 25-26, 2025 - Warren County Sports Complex & Voice of America Park'
    },
    {
        'name': 'Haunted Classic',
        'event_id': '418537',
        'year': 2025,
        'division_urls': [
            'https://system.gotsport.com/org_event/events/418537/results?group=418537',
        ],
        'age_gender_filter': {
            'age': 9,
            'gender': 'm'
        },
        'notes': 'Halloween tournament - October 18-19, 2025 - DSX played 3 matches'
    },
    {
        'name': 'Dublin Charity Cup',
        'event_id': None,  # Local tournament - no GotSport event page
        'year': 2025,
        'division_urls': [],
        'age_gender_filter': {
            'age': 8,
            'gender': 'm'
        },
        'notes': 'Local tournament - August 9-16, 2025 - DSX played 2 matches - Division file: Dublin_Charity_Cup_2025_Division_Rankings.csv'
    },
    {
        'name': 'Grove City Fall Classic',
        'event_id': None,  # Local tournament - no GotSport event page
        'year': 2025,
        'division_urls': [],
        'age_gender_filter': {
            'age': 8,
            'gender': 'm'
        },
        'notes': 'Local tournament - September 27-28, 2025 - DSX played 4 matches - Division file: Grove_City_Fall_Classic_2025_Division_Rankings.csv'
    },
    {
        'name': 'Murfin Friendly Series',
        'event_id': None,  # Friendly tournament - no GotSport event page
        'year': 2025,
        'division_urls': [],
        'age_gender_filter': {
            'age': 8,
            'gender': 'm'
        },
        'notes': 'Friendly tournament - September 5-7, 2025 - DSX played 3 matches - Division file: Murfin_Friendly_Series_2025_Division_Rankings.csv'
    },
    {
        'name': 'Obetz Futbol Cup',
        'event_id': None,  # Local tournament - no GotSport event page found
        'year': 2025,
        'division_urls': [],
        'age_gender_filter': {
            'age': 8,
            'gender': 'm'
        },
        'notes': 'Local tournament - August 30-31, 2025 - DSX played 3 matches - Location: Darree Fields - No division data available'
    },
]

# Event ID ranges to scan for new tournaments
# Adjust these based on current year and expected event ID ranges
EVENT_ID_SCAN_RANGES = [
    {
        'start': 44000,
        'end': 45000,
        'step': 50,
        'description': '2025 Tournament Range'
    },
    {
        'start': 43000,
        'end': 44000,
        'step': 50,
        'description': '2024 Tournament Range'
    },
]

# Keywords that indicate Ohio tournaments
OHIO_KEYWORDS = [
    'ohio', 'columbus', 'cincinnati', 'cleveland', 'dayton',
    'club ohio', 'ossl', 'ospl', 'ocl', 'cpl', 'mvysa',
    'dublin', 'worthington', 'upper arlington', 'gahanna',
    'westerville', 'lewis center', 'delaware', 'hilliard',
    'grove city', 'reynoldsburg', 'pickerington'
]

# Age/gender patterns for 2018 Boys
AGE_PATTERNS = [
    r'2018.*[Bb]oys?',
    r'U9.*[Bb]oys?',
    r'U09.*[Bb]oys?',
    r'BU08',
    r'BU09',
    r'Male.*U9',
    r'Male.*2018',
]

