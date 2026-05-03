import requests
import pandas as pd
import streamlit as st

from ui_style import apply_global_styles, footer, premium_header, result_card


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherApiError(Exception):
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
def fetch_weather(latitude: float, longitude: float) -> pd.DataFrame:
    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                "forecast_days": 3,
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

    if not dates or not rainfall:
        raise WeatherApiError("Weather forecast data is not available for this location.")

    table = pd.DataFrame(
        {
            "Date": pd.to_datetime(dates).date,
            "Rainfall (mm)": rainfall,
            "Max Temp (C)": temp_max if temp_max else [None] * len(dates),
            "Min Temp (C)": temp_min if temp_min else [None] * len(dates),
        }
    )
    return table


def irrigation_decision(soil_moisture: int, rainfall_3_day: float, max_temp: float) -> tuple[str, str, str]:
    if rainfall_3_day >= 20:
        return (
            "Do not irrigate now",
            "Good rainfall is expected soon, so extra watering may waste water or cause waterlogging.",
            "Check drainage channels and avoid standing water around roots.",
        )

    if soil_moisture < 30:
        if rainfall_3_day >= 8:
            return (
                "Light irrigation recommended",
                "Soil is dry, but some rain is expected. Give only enough water to protect the crop.",
                "Recheck soil moisture after rainfall before watering again.",
            )
        return (
            "Irrigate now",
            "Soil moisture is low and little rain is expected. Watering is likely needed.",
            "Prefer drip or furrow irrigation during morning or evening to reduce evaporation.",
        )

    if soil_moisture <= 55:
        if max_temp >= 36 and rainfall_3_day < 5:
            return (
                "Short irrigation may be needed",
                "Soil moisture is moderate, but high temperature and low rain can dry the field quickly.",
                "Mulch around plants where possible to conserve moisture.",
            )
        return (
            "Wait and monitor",
            "Soil moisture is acceptable. Irrigate only if the field dries further.",
            "Check soil near the root zone again tomorrow.",
        )

    return (
        "Do not irrigate now",
        "Soil moisture is already high. Extra watering may reduce root health.",
        "Keep checking for waterlogging, especially in low-lying field areas.",
    )


apply_global_styles()
premium_header(
    "💧 Smart Irrigation System",
    "Use soil moisture and weather forecast to decide whether watering is needed.",
)

with st.form("smart_irrigation_form"):
    city_name = st.text_input("Location / city name", placeholder="Example: Hyderabad")
    soil_moisture = st.slider("Soil moisture (%)", min_value=0, max_value=100, value=35)
    submit = st.form_submit_button("Check Irrigation Need")

if submit:
    clean_city = city_name.strip()
    if not clean_city:
        st.error("Please enter a location or city name.")
        st.stop()

    with st.spinner("🤖 AI is analyzing your farm data..."):
        try:
            location = search_location(clean_city)
            forecast = fetch_weather(location["latitude"], location["longitude"])
        except ValueError as exc:
            st.error(str(exc))
            st.stop()
        except WeatherApiError as exc:
            st.error(str(exc))
            st.stop()

    total_rainfall = float(forecast["Rainfall (mm)"].sum())
    max_temp = float(forecast["Max Temp (C)"].max())
    decision, reason, action = irrigation_decision(soil_moisture, total_rainfall, max_temp)
    place_parts = [location.get("name"), location.get("admin1"), location.get("country")]
    place_name = ", ".join(part for part in place_parts if part)

    st.subheader(place_name or clean_city.title())
    col1, col2, col3 = st.columns(3)
    col1.metric("Soil moisture", f"{soil_moisture}%")
    col2.metric("3-day rainfall", f"{total_rainfall:.1f} mm")
    col3.metric("Highest temp", f"{max_temp:.1f} C")

    st.subheader("Auto Water Decision")
    if decision == "Irrigate now":
        result_card("Auto water decision", decision, "danger")
    elif "Light" in decision or "Short" in decision:
        result_card("Auto water decision", decision, "warning")
    else:
        result_card("Auto water decision", decision, "success")

    st.write(reason)
    st.info(action)

    st.subheader("Weather Forecast")
    st.dataframe(forecast, use_container_width=True, hide_index=True)
    st.line_chart(forecast.set_index("Date")["Rainfall (mm)"])

st.warning(
    "This is AI support only. Always confirm soil moisture in the field and follow local irrigation advice."
)
footer()
