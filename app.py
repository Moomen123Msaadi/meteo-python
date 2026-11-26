import json
from pathlib import Path
from urllib.parse import urlencode

from flask import Flask, render_template, request

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "tunisia_weather_2024.json"
PAGE_SIZE = 100

with DATA_FILE.open(encoding="utf-8") as f:
    WEATHER = json.load(f)


def get_summary():
    temps = [r["temperature_C"] for r in WEATHER]
    return {
        "count": len(WEATHER),
        "governorates": sorted({r["governorate"] for r in WEATHER}),
        "seasons": sorted({r["season"] for r in WEATHER}),
        "months": sorted({r["date"][:7] for r in WEATHER}),
        "avg_temp": round(sum(temps) / len(temps), 1),
        "max_temp": max(temps),
        "min_temp": min(temps),
        "hottest": max(WEATHER, key=lambda r: r["temperature_C"]),
        "coldest": min(WEATHER, key=lambda r: r["temperature_C"]),
        "date_from": min(r["date"] for r in WEATHER),
        "date_to": max(r["date"] for r in WEATHER),
    }


@app.route("/")
def home():
    return render_template("index.html", summary=get_summary())


@app.route("/weather")
def weather():
    governorate = request.args.get("governorate", "all")
    season = request.args.get("season", "all")
    month = request.args.get("month", "all")
    page = max(1, request.args.get("page", 1, type=int))

    rows = WEATHER
    if governorate != "all":
        rows = [r for r in rows if r["governorate"] == governorate]
    if season != "all":
        rows = [r for r in rows if r["season"] == season]
    if month != "all":
        rows = [r for r in rows if r["date"].startswith(month)]

    total = len(rows)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(page, total_pages)
    start = (page - 1) * PAGE_SIZE
    page_rows = rows[start:start + PAGE_SIZE]

    params = {}
    if governorate != "all":
        params["governorate"] = governorate
    if season != "all":
        params["season"] = season
    if month != "all":
        params["month"] = month

    return render_template(
        "weather.html",
        page_rows=page_rows,
        summary=get_summary(),
        selected={"governorate": governorate, "season": season, "month": month},
        filtered_count=total,
        page=page,
        total_pages=total_pages,
        query_string=urlencode(params),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)