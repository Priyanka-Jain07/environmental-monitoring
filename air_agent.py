import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# AQI CATEGORY
# ============================================================

def get_aqi_category(aqi):

    if aqi is None:
        return "Unknown"

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"


# ============================================================
# APPLICATION RISK LEVEL
# ============================================================

def get_risk_status(aqi):

    if aqi is None:
        return "Unknown"

    if aqi <= 50:
        return "Low"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "High"

    else:
        return "Very High"


# ============================================================
# AIR QUALITY AGENT
# ============================================================

def air_quality_agent(city):

    city = str(city).strip()

    if not city:

        return {
            "agent": "Air Quality Agent",
            "status": "Unknown",
            "aqi": None,
            "aqi_category": "Unknown",
            "city": "",
            "station": None,
            "message": "City name is required."
        }


    # --------------------------------------------------------
    # GET TOKEN
    # --------------------------------------------------------

    token = os.getenv(
        "WAQI_TOKEN",
        ""
    ).strip()


    if not token:

        return {
            "agent": "Air Quality Agent",
            "status": "Unknown",
            "aqi": None,
            "aqi_category": "Unknown",
            "city": city,
            "station": None,
            "message": (
                "WAQI_TOKEN is missing. "
                "Add WAQI_TOKEN to the .env file."
            )
        }


    # --------------------------------------------------------
    # API REQUEST
    # --------------------------------------------------------

    try:

        encoded_city = quote(city)

        url = (
            f"https://api.waqi.info/"
            f"feed/{encoded_city}/"
        )


        response = requests.get(

            url,

            params={
                "token": token
            },

            timeout=15

        )


        response.raise_for_status()


        data = response.json()


        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        if data.get("status") != "ok":

            return {

                "agent": "Air Quality Agent",

                "status": "Unknown",

                "aqi": None,

                "aqi_category": "Unknown",

                "city": city,

                "station": None,

                "message": str(
                    data.get(
                        "data",
                        "Air quality data unavailable."
                    )
                )

            }


        # ----------------------------------------------------
        # GET API DATA
        # ----------------------------------------------------

        api_data = data.get(
            "data",
            {}
        )


        raw_aqi = api_data.get(
            "aqi"
        )


        if raw_aqi in (
            None,
            "-"
        ):

            return {

                "agent": "Air Quality Agent",

                "status": "Unknown",

                "aqi": None,

                "aqi_category": "Unknown",

                "city": city,

                "station": None,

                "message": "AQI value is unavailable."

            }


        # ----------------------------------------------------
        # CONVERT AQI
        # ----------------------------------------------------

        try:

            aqi = float(
                raw_aqi
            )

        except (
            ValueError,
            TypeError
        ):

            return {

                "agent": "Air Quality Agent",

                "status": "Unknown",

                "aqi": None,

                "aqi_category": "Unknown",

                "city": city,

                "station": None,

                "message": "Invalid AQI value received."

            }


        if aqi.is_integer():

            aqi = int(aqi)


        # ----------------------------------------------------
        # RISK + CATEGORY
        # ----------------------------------------------------

        risk = get_risk_status(
            aqi
        )

        category = get_aqi_category(
            aqi
        )


        # ----------------------------------------------------
        # STATION
        # ----------------------------------------------------

        station = None

        city_data = api_data.get(
            "city"
        )


        if isinstance(
            city_data,
            dict
        ):

            station = city_data.get(
                "name"
            )


        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {

            "agent": "Air Quality Agent",

            # Used by Coordinator
            "status": risk,

            # Actual AQI
            "aqi": aqi,

            # Human-readable category
            "aqi_category": category,

            "city": city,

            "station": station,

            "message": (
                f"AQI {aqi}: "
                f"{category} | "
                f"Risk level: {risk}"
            )

        }


    # --------------------------------------------------------
    # REQUEST ERROR
    # --------------------------------------------------------

    except requests.exceptions.RequestException as e:

        return {

            "agent": "Air Quality Agent",

            "status": "Unknown",

            "aqi": None,

            "aqi_category": "Unknown",

            "city": city,

            "station": None,

            "message": (
                f"API request failed: {str(e)}"
            )

        }


    # --------------------------------------------------------
    # GENERAL ERROR
    # --------------------------------------------------------

    except Exception as e:

        return {

            "agent": "Air Quality Agent",

            "status": "Unknown",

            "aqi": None,

            "aqi_category": "Unknown",

            "city": city,

            "station": None,

            "message": (
                f"Air agent error: {str(e)}"
            )

        }