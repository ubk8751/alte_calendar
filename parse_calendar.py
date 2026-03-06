import re
import json
from datetime import datetime, timedelta

with open("events_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

date_pattern = r'^((?:Måndag|Tisdag|Onsdag|Torsdag|Fredag|Lördag|Söndag) \d{2}/\d{2})$'
lines = text.split('\n')

events = []
current_event = None

for line in lines:
    if re.match(date_pattern, line.strip()):
        if current_event and current_event.get('name'):
            events.append(current_event)
        current_event = {'date': line.strip(), 'name': '', 'location': '', 'raw_lines': []}
    elif current_event is not None:
        stripped = line.strip()
        if stripped:
            if not current_event['name']:
                current_event['name'] = stripped
            elif not current_event['location']:
                current_event['location'] = stripped
            else:
                current_event['raw_lines'].append(stripped)

if current_event and current_event.get('name'):
    events.append(current_event)

# Parse structured fields
for ev in events:
    raw_text = '\n'.join(ev['raw_lines'])
    
    # Apply defaults for Rep and Balettrep
    if ev['name'] == 'Rep':
        ev['location'] = 'Hålan'
        ev['time_start'] = '19:00'
        ev['time_end'] = '22:00'
        ev['total_time_min'] = 180
    elif ev['name'] == 'Balettrep':
        ev['location'] = 'Replokal'
        ev['time_start'] = '17:30'
        ev['time_end'] = '19:00'
        ev['total_time_min'] = 90
    
    # Extract times (override defaults if present)
    halan_match = re.search(r'Samling i hålan: (\d{2}:\d{2})', raw_text)
    plats_match = re.search(r'Samling på plats: (\d{2}:\d{2})', raw_text)
    start_match = re.search(r'Spelning startar: (\d{2}:\d{2})', raw_text)
    replokal_match = re.search(r'Vid replokal: (\d{2}:\d{2})', ev.get('location', ''))
    
    ev['time_halan'] = halan_match.group(1) if halan_match else ev.get('time_halan')
    ev['time_plats'] = plats_match.group(1) if plats_match else ev.get('time_plats')
    if start_match:
        ev['time_start'] = start_match.group(1)
    elif replokal_match and ev['name'] != 'Balettrep':
        ev['time_start'] = replokal_match.group(1)
    
    # Set defaults if not set
    if 'time_halan' not in ev:
        ev['time_halan'] = None
    if 'time_plats' not in ev:
        ev['time_plats'] = None
    if 'time_start' not in ev:
        ev['time_start'] = None
    
    # Parse total time and calculate end time
    time_match = re.search(r'Total spelningstid: (\d+) min', raw_text)
    if time_match:
        ev['total_time_min'] = int(time_match.group(1))
        if ev['time_start']:
            start = datetime.strptime(ev['time_start'], '%H:%M')
            end = start + timedelta(minutes=ev['total_time_min'])
            ev['time_end'] = end.strftime('%H:%M')
        else:
            ev['time_end'] = None
    elif 'total_time_min' not in ev:
        ev['total_time_min'] = None
        ev['time_end'] = None
    elif 'time_end' not in ev and ev.get('total_time_min') and ev.get('time_start'):
        start = datetime.strptime(ev['time_start'], '%H:%M')
        end = start + timedelta(minutes=ev['total_time_min'])
        ev['time_end'] = end.strftime('%H:%M')
    
    # Parse registration
    if 'Anmäld (Direkt)' in raw_text:
        ev['registered'] = True
        ev['registration_type'] = 'direkt'
    elif 'Anmäld (Hålan)' in raw_text:
        ev['registered'] = True
        ev['registration_type'] = 'hålan'
    elif 'Kan inte komma' in raw_text:
        ev['registered'] = True
        ev['registration_type'] = 'kan_inte_komma'
    elif 'Anmäl' in raw_text and 'Anmäld' not in raw_text:
        ev['registered'] = False
        ev['registration_type'] = None
    else:
        ev['registered'] = None
        ev['registration_type'] = None
    
    # Parse attendance
    attendance_match = re.search(r'(\d+) Kommer - (\d+) Kommer inte', raw_text)
    if attendance_match:
        ev['accepted'] = int(attendance_match.group(1))
        ev['not_accepted'] = int(attendance_match.group(2))
    else:
        ev['accepted'] = None
        ev['not_accepted'] = None
    
    # Parse gig type
    gig_match = re.search(r'Speltyp: (.+)', raw_text)
    ev['gig_type'] = gig_match.group(1).strip() if gig_match else None
    
    # Extract description (everything after structured fields)
    description_lines = []
    skip_patterns = ['Samling', 'Spelning', 'Total spelningstid', 'Anmäld', 'Anmäl', 'Kommer', 'Speltyp']
    for line in ev['raw_lines']:
        if not any(p in line for p in skip_patterns):
            description_lines.append(line)
    ev['details'] = '\n'.join(description_lines).strip()
    
    del ev['raw_lines']

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print(f"Saved {len(events)} events to events.json")
