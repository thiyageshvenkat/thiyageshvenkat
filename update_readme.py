import requests
import base64
import os
from dotenv import load_dotenv # for local testing

load_dotenv()

API_KEY = os.getenv("WAKATIME_API_KEY")
API_URL = "https://hackatime.hackclub.com/api/hackatime/v1/users/current/stats/last_7_days"

def generate_svg_card(stats, title, items_key, filename="wakatime.svg"): # f-strings into a css format
    if not stats:
        return
    
    svg = f'''<svg width="500" height="350" xmlns="http://www.w3.org/2000/svg">
    <style>
        .header {{ font: 600 18px 'Consolas', Ubuntu, sans-serif; fill: #58A6FF; filter: drop-shadow(0 0 1px rgba(88, 166, 255, 0.8)); }}
        .stat-text {{ font: 400 14px Consolas, 'Courier New', monospace; fill: #C9D1D9; }}
        .title-text {{ font: 600 14px Consolas, 'Courier New', monospace; fill: #8B949E; }}
        .bar-bg {{ fill: #21262D; rx: 5px; }}
        .bar-fg {{ fill: #58A6FF; rx: 5px; filter: drop-shadow(0 0 8px rgba(88, 166, 255, 0.8)); }}
        /* Animation for a cool fade-in effect */
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        g {{ animation: fadeIn 1s ease-in-out; }}
    </style>
    
    <!-- Background rounded rectangle -->
    <rect width="500" height="350" fill="#0D1117" rx="10" stroke="#30363D" stroke-width="1"/>
    
    <!-- Header text -->
    <text x="25" y="35" class="header">{title}</text>
    <text x="25" y="60" class="stat-text">🕛 Total Time: {stats.get('human_readable_total', '0 hrs')}</text>
    <text x="25" y="80" class="stat-text">🔥 Daily Average: {stats.get('human_readable_daily_average', '0 hrs')}</text>
    
    <g transform="translate(25, 110)">
    '''
    y = 0
    for item in stats.get(items_key, [])[:5]: # get the top 5 items
        percent = item.get('percent', 0)
        name = item.get('name', 'Unknown')
        text = item.get('text', '0 hrs')
        
        bar_width = 450 * (percent / 100)
        # f-strings into a css format
        svg += f'''
        <text x="0" y="{y + 12}" class="title-text">{name}</text>
        <text x="450" y="{y + 12}" text-anchor="end" class="stat-text">{text} ({percent}%)</text>
        
        <!-- The background of the progress bar -->
        <rect x="0" y="{y + 20}" width="450" height="10" class="bar-bg"/>
        <!-- The filled part of the progress bar -->
        <rect x="0" y="{y + 20}" width="{bar_width}" height="10" class="bar-fg"/>
        '''
        y += 45
        
    svg += '''
    </g>
</svg>'''

    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"-> Successfully generated {filename}!")

if not API_KEY:
    print("-> Error: WAKATIME_API_KEY is missing from environment variables or .env file")
    exit(1)

auth_header = base64.b64encode(API_KEY.encode()).decode()

print(f"Connecting to Hackatime...")

try:
    response = requests.get(API_URL, headers={"Authorization": f"Basic {auth_header}"})
    
    if response.status_code != 200:
        print(f"-> Failed! Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)

    result = response.json()
    
    if "data" in result:
        print("-> Connection Successful!")
        stats_data = result['data']
        generate_svg_card(stats_data, "📊 This Week's Languages", "languages", "wakatime.svg")
        generate_svg_card(stats_data, "📁 This Week's Projects", "projects", "wakatime_projects.svg")
    else:
        print("-> Connected, but 'data' key missing. Full response:")
        print(result)
except Exception as e:
    print(f"-> An error occurred: {e}")