import requests
import pandas as pd
import streamlit as st


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CROP_RULES = {
    "rice": {"temp_min": 22, "temp_max": 35, "rain_min": 2, "rain_max": 25, "advice": "Rice needs warm weather and some water support. Prepare puddled soil and confirm irrigation availability."},
    "wheat": {"temp_min": 15, "temp_max": 28, "rain_min": 0, "rain_max": 12, "advice": "Wheat prefers cooler conditions. Avoid sowing just before heavy rain or waterlogging."},
    "maize": {"temp_min": 18, "temp_max": 34, "rain_min": 0, "rain_max": 18, "advice": "Maize needs warm soil and good drainage. Plant when the field is moist but not waterlogged."},
    "cotton": {"temp_min": 20, "temp_max": 34, "rain_min": 0, "rain_max": 15, "advice": "Cotton needs warm weather and drainage. Avoid sowing before heavy rain."},
    "tomato": {"temp_min": 18, "temp_max": 32, "rain_min": 0, "rain_max": 10, "advice": "Tomato seedlings do best in mild weather. Avoid transplanting during heavy rain or extreme heat."},
    "chilli": {"temp_min": 20, "temp_max": 32, "rain_min": 0, "rain_max": 10, "advice": "Chilli prefers warm, moderate weather. Keep nursery plants protected from heavy rain."},
    "soybean": {"temp_min": 20, "temp_max": 32, "rain_min": 1, "rain_max": 18, "advice": "Soybean needs moist soil at sowing. Avoid waterlogging and sow after initial useful rainfall."},
    "groundnut": {"temp_min": 22, "temp_max": 34, "rain_min": 0, "rain_max": 15, "advice": "Groundnut needs warm soil and loose seedbed. Avoid very wet fields at planting."},
}


class WeatherApiError(Exception):
    pass


@st.cache_data(ttl=60 * 30)
def search_location(city_name: str) -> dict:
    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            timeout=12,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise WeatherApiError("No internet connection. Please check your network and try again.") from exc
    except requests.exceptions.Timeout as exc:
        raise WeatherApiError("The location service took too long to respond. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise WeatherApiError("Location service is unavailable right now. Please try again later.") from exc

    results = response.json().get("results", [])
    if not results:
        raise ValueError("Invalid city name. Please enter a nearby town or district name.")
    return results[0]


@st.cache_data(ttl=60 * 30)
def fetch_forecast(latitude: float, longitude: float) -> pd.DataFrame:
    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                "forecast_days": 14,
                "timezone": "auto",
            },
            timeout=12,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise WeatherApiError("No internet connection. Please check your network and try again.") from exc
    except requests.exceptions.Timeout as exc:
        raise WeatherApiError("The weather service took too long to respond. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise WeatherApiError("Weather forecast service is unavailable right now. Please try again later.") from exc

    daily = response.json().get("daily", {})
    dates = daily.get("time", [])
    rainfall = daily.get("precipitation_sum", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    if not dates or not rainfall or not temp_max or not temp_min:
        raise WeatherApiError("Planting weather forecast data is not available for this location.")

    forecast = pd.DataFrame(
        {
            "Date": pd.to_datetime(dates).date,
            "Rainfall (mm)": rainfall,
            "Max Temp (C)": temp_max,
            "Min Temp (C)": temp_min,
        }
    )
    forecast["Avg Temp (C)"] = (
        forecast["Max Temp (C)"].astype(float) + forecast["Min Temp (C)"].astype(float)
    ) / 2
    return forecast


def score_day(row: pd.Series, rules: dict) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    avg_temp = float(row["Avg Temp (C)"])
    max_temp = float(row["Max Temp (C)"])
    rainfall = float(row["Rainfall (mm)"])

    if rules["temp_min"] <= avg_temp <= rules["temp_max"]:
        score += 2
        reasons.append("average temperature is suitable")
    else:
        reasons.append("average temperature is outside the preferred range")

    if max_temp < 38:
        score += 1
        reasons.append("extreme heat is not expected")
    else:
        reasons.append("extreme heat risk is high")

    if rules["rain_min"] <= rainfall <= rules["rain_max"]:
        score += 2
        reasons.append("rainfall is in a useful range")
    elif rainfall > rules["rain_max"]:
        reasons.append("rainfall may be too high")
    else:
        reasons.append("rainfall may be too low")

    return score, reasons


def find_best_date(forecast: pd.DataFrame, crop: str) -> tuple[pd.Series | None, str]:
    rules = CROP_RULES[crop]
    for _, row in forecast.iterrows():
        score, reasons = score_day(row, rules)
        if score >= 5:
            reason = (
                f"For {crop}, this day looks suitable because "
                f"{', '.join(reasons)}."
            )
            return row, reason
    return None, ""


st.title("📅 Best Planting Date Predictor")
st.write("Use crop needs and the next weather forecast to choose a better planting window.")

with st.form("best_planting_date_form"):
    crop = st.selectbox("Crop", list(CROP_RULES.keys()))
    city_name = st.text_input("Location / city name", placeholder="Example: Hyderabad")
    submit = st.form_submit_button("Find Best Date")

if submit:
    clean_city = city_name.strip()
    if not clean_city:
        st.error("Please enter a location or city name.")
        st.stop()

    try:
        location = search_location(clean_city)
        forecast = fetch_forecast(location["latitude"], location["longitude"])
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    except WeatherApiError as exc:
        st.error(str(exc))
        st.stop()

    best_row, reason = find_best_date(forecast, crop)
    place_parts = [location.get("name"), location.get("admin1"), location.get("country")]
    place_name = ", ".join(part for part in place_parts if part)

    st.subheader(place_name or clean_city.title())
    if best_row is None:
        st.warning("No ideal planting date found in the next forecast window. Wait and monitor weather.")
    else:
        st.subheader("Best Planting Date")
        st.success(str(best_row["Date"]))
        st.write(reason)

        col1, col2, col3 = st.columns(3)
        col1.metric("Rainfall", f"{float(best_row['Rainfall (mm)']):.1f} mm")
        col2.metric("Avg temp", f"{float(best_row['Avg Temp (C)']):.1f} C")
        col3.metric("Max temp", f"{float(best_row['Max Temp (C)']):.1f} C")

        st.subheader("Farmer Advice")
        st.info(CROP_RULES[crop]["advice"])

    st.subheader("Weather Summary")
    summary = forecast.copy()
    summary["Avg Temp (C)"] = summary["Avg Temp (C)"].round(1)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.line_chart(summary.set_index("Date")[["Rainfall (mm)", "Avg Temp (C)"]])

st.warning(
    "Final planting decision should also consider soil preparation, seed availability, irrigation, and local agriculture advice."
)
