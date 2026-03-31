# ChineseStrVisualizer

ChineseStrVisualizer is a lightweight Streamlit app for visualizing Chinese sentence structure with interactive OrgChart cards.

## What It Does

- Displays sentence structure as a hierarchical card graph
- Supports multiple sample sentences (`1a.html` to `4b.html`)
- Provides an interactive search control in the chart area
- Lets you adjust card/frame size in the sidebar

## Tech Stack

- Streamlit
- OrgChart.js
- HTML5 demo data

## Run Locally

1. Create or use a Python virtual environment
2. Install dependencies
3. Run the Streamlit app

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

- `app.py`: Streamlit entrypoint
- `orgchart.js`: OrgChart library source used by demos
- `1a.html` to `4b.html`: sample sentence chart pages
- `requirements.txt`: Python dependencies

## Deployment

This repository is ready for Streamlit Community Cloud deployment using:

- Branch: `main`
- App file: `app.py`
