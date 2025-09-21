# Industry Trends Explorer (Hackathon)

A lightweight analytics UI and forecasting toolkit for industry time series.
- **Streamlit UI**: pick industries from a dropdown and plot values across years.
- **Forecasting**: Holt Exponential Smoothing to project the next 5 years per industry.
- **Formats**: works with a wide Excel file (`Industry, 2012, 2013, ..., 2023, ...`).

## Repo Structure
```
.
├── app.py                         # Streamlit UI
├── sector_forecast_holt.py        # Forecast next 5 years per industry
├── format_forecasts_wide.py       # Convert forecast output back to wide format
├── requirements.txt               # Python deps
├── README.md
├── .gitignore
└── data/
    └── plain_format_extended.xlsx # (optional) sample data; add your own or keep ignored
```

> If you don't see `format_forecasts_wide.py` yet, add your conversion script here (or ask the team to drop it in).

## Quickstart (macOS / Terminal)

### 1) Clone and set up environment
```bash
# Use Python 3.10–3.12 recommended
git clone <your-repo-url>.git industry-trends-explorer
cd industry-trends-explorer

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Add your data
Place your Excel file (wide format) at:
```
data/plain_format_extended.xlsx
```
- The app also supports upload via the UI if you prefer not to commit data.
- Wide format means columns like: `Industry, 2012, 2013, ..., 2023, ...`.

### 3) Run the Streamlit UI
```bash
streamlit run app.py
```
Then open the local URL Streamlit prints (usually http://localhost:8501).

### 4) Run forecasts (optional)
```bash
python sector_forecast_holt.py
```
This will generate:
```
sector_forecasts.csv
sector_forecasts.xlsx
```
These contain per-industry 5‑year forecasts with smoothing params (`alpha`, `beta`) and `rmse_in_sample`.

### 5) Convert forecasts back to wide format (optional)
If you have a conversion script (e.g., `format_forecasts_wide.py`) that pivots the forecast output into
`Industry | 2023 | 2024 | ...`, run:
```bash
python format_forecasts_wide.py
```

## Data Expectations
- **Wide Excel** with an `Industry` column and **year columns** (strings or ints are OK).
- The UI automatically detects available years and lets you adjust the range.
- The forecaster requires **≥ 3 years** of data for each industry to fit Holt’s model.

## Git Commands (for Hackathon)

### Initial repo
```bash
git init
git add .
git commit -m "Initial commit: Streamlit UI + forecasting"
git branch -M main
git remote add origin <your-repo-url>.git
git push -u origin main
```

### Typical workflow
```bash
git checkout -b feature/improve-ui
# ...edit files...
git add -A
git commit -m "feat(ui): add robust year handling + multiselect"
git push -u origin feature/improve-ui
# open a PR on GitHub
```

## Notes
- Keep large proprietary datasets out of the repo. Use the **Upload** control in the app or `.gitignore` rules.
- If you need to demo publicly from a notebook environment, consider tunneling tools (ngrok/Cloudflare). For local macOS use, it’s not required.

## License
Choose a license for your repo (MIT/Apache-2.0/etc.) and add a `LICENSE` file if needed.
