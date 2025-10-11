"""
Export DSX Analysis to Shareable Formats
Creates HTML and PDF reports that can be emailed
"""

import pandas as pd
from datetime import datetime
import os


def create_html_report():
    """Create a standalone HTML report"""
    
    # Load data
    try:
        df = pd.read_csv("OCL_BU08_Stripes_Division_with_DSX.csv")
    except:
        print("Error: Division data not found. Run fetch_gotsport_division.py first.")
        return None
    
    # Get DSX row
    dsx_row = df[df['Team'].str.contains('DSX', na=False)]
    if dsx_row.empty:
        print("Error: DSX data not found")
        return None
    
    dsx_rank = int(dsx_row['Rank'].values[0])
    dsx_strength = float(dsx_row['StrengthIndex'].values[0])
    dsx_record = f"{int(dsx_row['W'].values[0])}-{int(dsx_row['D'].values[0])}-{int(dsx_row['L'].values[0])}"
    
    # Create HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSX Opponent Tracker - Division Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #ff6b35;
            border-bottom: 3px solid #ff6b35;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #667eea;
            margin-top: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .metric-box {{
            display: inline-block;
            background: #f0f2f6;
            padding: 20px;
            margin: 10px;
            border-radius: 8px;
            text-align: center;
            min-width: 150px;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #ff6b35;
            margin: 5px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .highlight {{
            background: #fff3cd;
            font-weight: bold;
        }}
        .strength-bar {{
            height: 20px;
            background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
            border-radius: 10px;
            display: inline-block;
            width: 100px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #ff6b35;
        }}
        .good {{
            color: #28a745;
            font-weight: bold;
        }}
        .warning {{
            color: #ffc107;
            font-weight: bold;
        }}
        .bad {{
            color: #dc3545;
            font-weight: bold;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dublin DSX Orange 2018 Boys - Division Analysis</h1>
            <h3>OCL BU08 Stripes Division Analysis</h3>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <div class="metric-box">
                <div class="metric-label">Division Rank</div>
                <div class="metric-value">#{dsx_rank}</div>
                <div class="metric-label">of 7 teams</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Strength Index</div>
                <div class="metric-value">{dsx_strength:.1f}</div>
                <div class="metric-label">/ 100</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Record (W-D-L)</div>
                <div class="metric-value">{dsx_record}</div>
                <div class="metric-label">Season</div>
            </div>
        </div>
        
        <h2>📊 Division Rankings</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th>GP</th>
                    <th>Record</th>
                    <th>GF/G</th>
                    <th>GA/G</th>
                    <th>GD/G</th>
                    <th>Pts</th>
                    <th>PPG</th>
                    <th>Strength</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add each team
    for _, row in df.iterrows():
        is_dsx = 'DSX' in str(row['Team'])
        row_class = 'class="highlight"' if is_dsx else ''
        team_name = row['Team'].replace('>>> ', '').replace(' <<<', '')
        record = f"{int(row['W'])}-{int(row['D'])}-{int(row['L'])}"
        
        html += f"""
                <tr {row_class}>
                    <td>{int(row['Rank'])}</td>
                    <td><strong>{team_name}</strong></td>
                    <td>{int(row['GP'])}</td>
                    <td>{record}</td>
                    <td>{row['GF']:.2f}</td>
                    <td>{row['GA']:.2f}</td>
                    <td>{row['GD']:+.2f}</td>
                    <td>{int(row['Pts'])}</td>
                    <td>{row['PPG']:.2f}</td>
                    <td><strong>{row['StrengthIndex']:.1f}</strong></td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="section">
            <h2>💡 Key Insights</h2>
            <h3 class="good">✅ Strengths</h3>
            <ul>
                <li><strong>4.17 goals/game</strong> (3rd best offense in division!)</li>
                <li><strong>Competitive</strong> - 7 of 12 games earned points</li>
                <li><strong>High ceiling</strong> - 11-0 win shows potential</li>
            </ul>
            
            <h3 class="warning">⚠️ Areas to Improve</h3>
            <ul>
                <li><strong>5.08 goals against/game</strong> (defensive struggles)</li>
                <li><strong>Inconsistent</strong> - Results range from 11-0 to 0-13</li>
                <li><strong>Negative GD</strong> - -0.92 per game</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>🎯 Strategic Recommendations</h2>
            
            <h3>For Coaches</h3>
            <ol>
                <li><strong>Defensive Focus</strong> - Biggest weakness vs division (5.08 GA/game vs 1.89-3.29 for top 4)</li>
                <li><strong>Maintain Offensive Pressure</strong> - It's working (4.17 GF/game)</li>
                <li><strong>Consistency Training</strong> - Reduce performance gap</li>
            </ol>
            
            <h3>Season Goals</h3>
            <ul>
                <li><span class="good">Very Achievable:</span> <strong>Top 4 Finish</strong> (need +7.8 SI points)</li>
                <li><span class="warning">Challenging:</span> <strong>Top 3 Finish</strong> (need +16.0 SI points)</li>
                <li><span class="good">Realistic:</span> <strong>PPG > 1.50</strong> (currently 1.00)</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📈 How to Move Up</h2>
            <p><strong>To reach 4th place:</strong></p>
            <ul>
                <li><strong>Option A:</strong> Win next 3 games (PPG: 1.00 → 1.40 = +9.3 points ✅)</li>
                <li><strong>Option B:</strong> Allow only 2 goals/game over next 4 (GD/GP: -0.92 → -0.42 with 2-1-1 record = +8.1 points ✅)</li>
            </ul>
        </div>
        
        <footer style="margin-top: 50px; text-align: center; color: #666; padding-top: 20px; border-top: 1px solid #ddd;">
            <p><strong>Dublin DSX Orange 2018 Boys - Opponent Tracker</strong></p>
            <p>For updates, run: <code>python fetch_gotsport_division.py</code></p>
        </footer>
    </div>
    
    <div class="no-print" style="text-align: center; margin-top: 20px;">
        <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer;">
            Print This Report
        </button>
    </div>
</body>
</html>
"""
    
    # Save
    filename = f"DSX_Division_Report_{datetime.now().strftime('%Y%m%d')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[OK] HTML report created: {filename}")
    print(f"   Open in browser to view")
    print(f"   Can email or print as PDF")
    
    return filename


def main():
    print("=" * 60)
    print("DSX Report Exporter")
    print("=" * 60)
    print()
    
    # Create HTML report
    html_file = create_html_report()
    
    if html_file:
        print()
        print("=" * 60)
        print("[OK] Reports Created!")
        print("=" * 60)
        print()
        print(f"HTML Report: {html_file}")
        print()
        print("How to share:")
        print("  1. Open the HTML file in your browser")
        print("  2. Click 'Print' → Save as PDF")
        print("  3. Email the PDF to coaches/parents")
        print()
        print("OR:")
        print("  1. Email the HTML file directly")
        print("  2. Recipients can open in any browser")
        print("  3. No installation needed!")
        print()


if __name__ == "__main__":
    main()

