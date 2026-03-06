# alte_calendar

Automated scraper for Alte Kamereren's member calendar at https://www.altekamereren.org/

## Setup

1. Create virtual environment and install dependencies:
```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
playwright install
```

2. Configure credentials:
```bash
cp .env.example .env
# Edit .env and add your username and password
```

## Usage

Fetch and parse events:
```bash
source myenv/bin/activate
python login.py          # Fetches events from /upcoming
python parse_calendar.py # Parses to events.json
```

## Output

`events.json` contains structured event data with fields:
- `date`, `name`, `location`
- `time_halan`, `time_plats`, `time_start`, `time_end`, `total_time_min`
- `registered`, `registration_type` (direkt/hålan/kan_inte_komma)
- `accepted`, `not_accepted` (attendance counts)
- `gig_type` (Stå/Gå)
- `details` (description and notes)

### Defaults

- **Rep**: Location=Hålan, Time=19:00-22:00 (180 min)
- **Balettrep**: Location=Replokal, Time=17:30-19:00 (90 min)
