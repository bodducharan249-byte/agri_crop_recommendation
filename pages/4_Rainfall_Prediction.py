import requests
import pandas as pd
import streamlit as st


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class RainfallApiError(Exception):
    pass


@st.cache_data(ttl=60 * 30)
def search_location(city_name: str) -> dict:
    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=12,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RainfallApiError("No internet connection. Please check your network and try again.") from exc
    except requests.exceptions.Timeout as exc:
        raise RainfallApiError("The location service took too long to respond. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise RainfallApiError("Location service is unavailable right now. Please try again later.") from exc

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
                "forecast_days": 7,
                "timezone": "auto",
            },
            timeout=12,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RainfallApiError("No internet connection. Please check your network and try again.") from exc
    except requests.exceptions.Timeout as exc:
        raise RainfallApiError("The weather service took too long to respond. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise RainfallApiError("Weather forecast service is unavailable right now. Please try again later.") from exc

    daily = response.json().get("daily", {})
    dates = daily.get("time", [])
    rainfall = daily.get("precipitation_sum", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])

    if not dates or not rainfall:
        raise RainfallApiError("Rainfall forecast data is not available for this location.")

    table = pd.DataFrame(
        {
            "Date": dates,
            "Rainfall (mm)": rainfall,
            "Max Temp (C)": temp_max if temp_max else [None] * len(dates),
            "Min Temp (C)": temp_min if temp_min else [None] * len(dates),
        }
    )
    table["Date"] = pd.to_datetime(table["Date"]).dt.date
    return table


def rainfall_message(total_rainfall: float) -> tuple[str, str]:
    if total_rainfall < 10:
        return (
            "Low rainfall expected",
            "Irrigation may be needed, especially for young crops and dry soil.",
        )
    if total_rainfall > 50:
        return (
            "High rainfall expected",
            "Avoid overwatering and check field drainage before heavy rain.",
        )
    return (
        "Moderate rainfall expected",
        "Rainfall looks useful, but keep checking soil moisture before irrigation.",
    )


st.title("🌧️ Rainfall Prediction")
st.write("Enter a location to check the next 7 days of expected rainfall and temperature.")

with st.form("rainfall_prediction_form"):
    city_name = st.text_input("Location / city name", placeholder="Example: Hyderabad")
    submit = st.form_submit_button("Get Rainfall Forecast")

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
    except RainfallApiError as exc:
        st.error(str(exc))
        st.stop()

    total_rainfall = float(forecast["Rainfall (mm)"].sum())
    place_parts = [
        location.get("name"),
        location.get("admin1"),
        location.get("country"),
    ]
    place_name = ", ".join(part for part in place_parts if part)
    message_title, message_text = rainfall_message(total_rainfall)

    st.subheader(place_name or clean_city.title())
    st.metric("Total expected rainfall for next 7 days", f"{total_rainfall:.1f} mm")

    if total_rainfall < 10:
        st.warning(f"{message_title}: {message_text}")
    elif total_rainfall > 50:
        st.info(f"{message_title}: {message_text}")
    else:
        st.success(f"{message_title}: {message_text}")

    st.subheader("Daily Rainfall Forecast")
    st.dataframe(forecast, use_container_width=True, hide_index=True)

    st.subheader("Rainfall Trend")
    chart_data = forecast.set_index("Date")["Rainfall (mm)"]
    st.line_chart(chart_data)
