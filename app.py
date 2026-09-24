import html

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import pandas as pd

from air_agent import air_quality_agent
from water_agent import water_quality_agent
from waste_agent import waste_detection_agent
from coordinator import coordinator_agent


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Environmental Monitoring System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .sidebar-agent-item {
        padding: 9px 4px;
        margin: 2px 0;
        font-size: 0.92rem;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .agent-card {
        padding: 1.2rem;
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
        min-height: 150px;
    }

    .agent-card h3 {
        margin-top: 0;
    }

    .status-low {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-weight: 700;
        background-color: rgba(0, 180, 80, 0.12);
    }

    .status-moderate {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-weight: 700;
        background-color: rgba(255, 180, 0, 0.15);
    }

    .status-high {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-weight: 700;
        background-color: rgba(255, 100, 0, 0.15);
    }

    .status-very-high {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-weight: 700;
        background-color: rgba(220, 0, 0, 0.15);
    }

    .status-very-unhealthy {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-weight: 700;
        background-color: rgba(180, 0, 180, 0.15);
    }

    .status-unknown {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-weight: 700;
        background-color: rgba(128, 128, 128, 0.15);
    }

    .info-box {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin: 0.5rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "air_result": None,
    "water_result": None,
    "waste_result": None,
    "final_result": None,
    "analysis_done": False,
    "selected_page": "Dashboard",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_html(value, default="N/A"):
    """
    Safely convert values before inserting them into HTML.
    """
    if value is None:
        value = default

    return html.escape(str(value))


def safe_result(result, fallback=None):
    """
    Make sure an agent response is a dictionary.
    """
    if isinstance(result, dict):
        return result

    if fallback is not None:
        return fallback

    return {}


def get_status_class(status):
    """
    Return CSS class based on status.
    """

    if status is None:
        return "status-unknown"

    status = str(status).lower()

    if status in ["low", "good"]:
        return "status-low"

    if status in ["moderate", "medium"]:
        return "status-moderate"

    if status in ["high", "unhealthy for sensitive groups"]:
        return "status-high"

    if status in [
        "very high",
        "very unhealthy",
        "hazardous",
    ]:
        return "status-very-unhealthy"

    return "status-unknown"


def get_status_icon(status):
    """
    Return an icon for a status.
    """

    if status is None:
        return "⚪"

    status = str(status).lower()

    if status in ["low", "good"]:
        return "🟢"

    if status in ["moderate", "medium"]:
        return "🟡"

    if status in ["high", "unhealthy for sensitive groups"]:
        return "🟠"

    if status in [
        "very high",
        "very unhealthy",
    ]:
        return "🔴"

    if status == "hazardous":
        return "🟣"

    return "⚪"


# ============================================================
# AIR QUALITY AGENT
# ============================================================

def run_air(city):
    """
    Run Air Quality Agent.
    """

    if not city or not city.strip():
        st.warning("Please enter a city.")
        return

    with st.spinner("🌫️ Analyzing air quality..."):

        try:

            result = air_quality_agent(city.strip())

            result = safe_result(
                result,
                {
                    "agent": "Air Quality Agent",
                    "status": "Unknown",
                    "aqi": None,
                    "message": "No valid response received.",
                },
            )

            result.setdefault(
                "agent",
                "Air Quality Agent",
            )

            result.setdefault(
                "status",
                "Unknown",
            )

            result.setdefault(
                "aqi",
                None,
            )

            result.setdefault(
                "message",
                "",
            )

            result.setdefault(
                "city",
                city.strip(),
            )

            # Important:
            # Do NOT convert "Very Unhealthy" to "Very High".
            # Keep the exact status returned by the Air Agent.

            st.session_state.air_result = result

            # Previous coordinator result may now be outdated.
            st.session_state.final_result = None

            st.session_state.analysis_done = True

            st.success("Air quality analysis completed.")

        except Exception as e:

            st.session_state.air_result = {
                "agent": "Air Quality Agent",
                "status": "Unknown",
                "aqi": None,
                "city": city.strip(),
                "message": f"Air quality analysis failed: {str(e)}",
            }

            st.session_state.final_result = None

            st.error(
                f"Air Quality Agent Error: {str(e)}"
            )


# ============================================================
# WATER QUALITY AGENT
# ============================================================

def run_water(ph, turbidity, tds, dissolved_oxygen):
    """
    Run Water Quality Agent.
    """

    with st.spinner("💧 Analyzing water quality..."):

        try:

            result = water_quality_agent(
                ph,
                turbidity,
                tds,
                dissolved_oxygen,
            )

            result = safe_result(
                result,
                {
                    "agent": "Water Quality Agent",
                    "status": "Unknown",
                    "message": "No valid response received.",
                },
            )

            result.setdefault(
                "agent",
                "Water Quality Agent",
            )

            result.setdefault(
                "status",
                "Unknown",
            )

            result.setdefault(
                "message",
                "",
            )

            # Keep one consistent water pH field.
            result["ph"] = result.get("ph", result.get("pH", ph))
            result.pop("pH", None)

            result.setdefault(
                "turbidity",
                turbidity,
            )

            result.setdefault(
                "tds",
                tds,
            )

            result.setdefault(
                "dissolved_oxygen",
                dissolved_oxygen,
            )

            st.session_state.water_result = result

            st.session_state.final_result = None
            st.session_state.analysis_done = True

            st.success(
                "Water quality analysis completed."
            )

        except Exception as e:

            st.session_state.water_result = {
                "agent": "Water Quality Agent",
                "status": "Unknown",
                "ph": ph,
                "turbidity": turbidity,
                "tds": tds,
                "dissolved_oxygen": dissolved_oxygen,
                "message": (
                    f"Water quality analysis failed: {str(e)}"
                ),
            }

            st.session_state.final_result = None

            st.error(
                f"Water Quality Agent Error: {str(e)}"
            )


# ============================================================
# WASTE DETECTION AGENT
# ============================================================

def run_waste(uploaded_file):
    """
    Run Waste Detection Agent.
    """

    if uploaded_file is None:
        st.warning(
            "Please upload a waste image first."
        )
        return False

    with st.spinner("♻️ Detecting waste..."):

        try:

            result = waste_detection_agent(
                uploaded_file
            )

            result = safe_result(
                result,
                {
                    "agent": "Waste Detection Agent",
                    "status": "Unknown",
                    "detections": [],
                    "message": "No valid response received.",
                },
            )

            result.setdefault(
                "agent",
                "Waste Detection Agent",
            )

            result.setdefault(
                "status",
                "Unknown",
            )

            result.setdefault(
                "detections",
                [],
            )

            result.setdefault(
                "message",
                "",
            )

            if not isinstance(
                result["detections"],
                list,
            ):
                result["detections"] = []

            st.session_state.waste_result = result

            st.session_state.final_result = None
            st.session_state.analysis_done = True

            st.success(
                "Waste detection completed."
            )

            return True

        except Exception as e:

            st.session_state.waste_result = {
                "agent": "Waste Detection Agent",
                "status": "Unknown",
                "detections": [],
                "message": (
                    f"Waste detection failed: {str(e)}"
                ),
            }

            st.session_state.final_result = None

            st.error(
                f"Waste Detection Agent Error: {str(e)}"
            )

            return False


# ============================================================
# COORDINATOR AGENT
# ============================================================

def run_coordinator():
    """
    Run the Coordinator Agent.

    If Air or Water has not been analyzed yet, analyze them
    automatically. Waste remains Unknown until an image is
    actually uploaded and analyzed.
    """

    with st.spinner(
        "🤖 Coordinator Agent is evaluating the environment..."
    ):

        try:

            # ------------------------------------------------
            # CITY
            # ------------------------------------------------

            city = st.session_state.get(
                "dashboard_city",
                "Pune",
            )

            city = str(city).strip() or "Pune"


            # ------------------------------------------------
            # AIR AGENT
            # ------------------------------------------------

            if st.session_state.air_result is None:

                air_result = air_quality_agent(city)

                st.session_state.air_result = safe_result(
                    air_result,
                    {
                        "agent": "Air Quality Agent",
                        "status": "Unknown",
                        "aqi": None,
                        "city": city,
                        "message": (
                            "Air Quality Agent did not "
                            "return a valid response."
                        ),
                    },
                )

                st.session_state.air_result.setdefault(
                    "agent",
                    "Air Quality Agent",
                )
                st.session_state.air_result.setdefault(
                    "status",
                    "Unknown",
                )
                st.session_state.air_result.setdefault(
                    "aqi",
                    None,
                )
                st.session_state.air_result.setdefault(
                    "city",
                    city,
                )
                st.session_state.air_result.setdefault(
                    "message",
                    "",
                )


            # ------------------------------------------------
            # WATER AGENT
            # ------------------------------------------------
            # These are the same default values used by the
            # Dashboard Complete Analysis button.

            if st.session_state.water_result is None:

                water_result = water_quality_agent(
                    7.2,
                    2.0,
                    350.0,
                    7.0,
                )

                water_result = safe_result(
                    water_result,
                    {
                        "agent": "Water Quality Agent",
                        "status": "Unknown",
                        "ph": 7.2,
                        "turbidity": 2.0,
                        "tds": 350.0,
                        "dissolved_oxygen": 7.0,
                        "message": (
                            "Water Quality Agent did not "
                            "return a valid response."
                        ),
                    },
                )

                water_result.setdefault(
                    "agent",
                    "Water Quality Agent",
                )
                water_result.setdefault(
                    "status",
                    "Unknown",
                )
                water_result["ph"] = water_result.get(
                    "ph",
                    water_result.get("pH", 7.2),
                )
                water_result.pop("pH", None)
                water_result.setdefault(
                    "turbidity",
                    2.0,
                )
                water_result.setdefault(
                    "tds",
                    350.0,
                )
                water_result.setdefault(
                    "dissolved_oxygen",
                    7.0,
                )
                water_result.setdefault(
                    "message",
                    "",
                )

                st.session_state.water_result = water_result


            # ------------------------------------------------
            # WASTE AGENT
            # ------------------------------------------------
            # Missing waste analysis must never be treated as
            # Low risk.

            if st.session_state.waste_result is None:

                st.session_state.waste_result = {
                    "agent": "Waste Detection Agent",
                    "status": "Unknown",
                    "detections": [],
                    "message": (
                        "No waste image uploaded. "
                        "Waste analysis was not performed."
                    ),
                }


            # ------------------------------------------------
            # RUN COORDINATOR
            # ------------------------------------------------

            final_result = coordinator_agent(
                st.session_state.air_result,
                st.session_state.water_result,
                st.session_state.waste_result,
            )

            final_result = safe_result(
                final_result,
                {
                    "agent": "Coordinator Agent",
                    "status": "Unknown",
                    "overall_risk": "Unknown",
                    "message": (
                        "No valid coordinator response received."
                    ),
                    "reason": (
                        "No valid coordinator response received."
                    ),
                },
            )

            final_result.setdefault(
                "agent",
                "Coordinator Agent",
            )

            # Support both old and new coordinator field names.
            status = final_result.get("status")

            if not status or status == "Unknown":
                status = final_result.get(
                    "overall_risk",
                    "Unknown",
                )

            final_result["status"] = status
            final_result.setdefault(
                "overall_risk",
                status,
            )

            if not final_result.get("message"):
                final_result["message"] = final_result.get(
                    "reason",
                    "No summary available.",
                )

            final_result.setdefault(
                "reason",
                final_result.get("message", ""),
            )

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            st.session_state.final_result = final_result
            st.session_state.analysis_done = True

            st.success(
                "Environmental coordination completed."
            )

        except Exception as e:

            error_message = (
                f"Coordinator analysis failed: {str(e)}"
            )

            st.session_state.final_result = {
                "agent": "Coordinator Agent",
                "status": "Unknown",
                "overall_risk": "Unknown",
                "message": error_message,
                "reason": error_message,
                "agents_analyzed": 0,
                "average_risk": None,
            }

            st.error(
                f"Coordinator Agent Error: {str(e)}"
            )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🌍 Environmental Monitoring"
    )

    # --------------------------------------------------------
    # NAVIGATION BOX
    # --------------------------------------------------------
    with st.container(border=True):

        st.markdown(
            "### 🧭 Navigation"
        )

        page = st.radio(
            "Select Agent",
            [
                "Dashboard",
                "Air Detection",
                "Water Detection",
                "Waste Detection",
                "Coordinator Agent",
                "Live Location",
            ],
            index=[
                "Dashboard",
                "Air Detection",
                "Water Detection",
                "Waste Detection",
                "Coordinator Agent",
                "Live Location",
            ].index(
                st.session_state.selected_page
            ),
            label_visibility="collapsed",
        )

    st.session_state.selected_page = page

    # --------------------------------------------------------
    # AI AGENTS BOX
    # --------------------------------------------------------
    with st.container(border=True):

        st.markdown(
            "### 🤖 AI Agents"
        )

        st.markdown(
            """
            <div class="sidebar-agent-item">🌫️ <b>Air Quality Agent</b></div>
            <div class="sidebar-agent-item">💧 <b>Water Quality Agent</b></div>
            <div class="sidebar-agent-item">♻️ <b>Waste Detection Agent</b></div>
            <div class="sidebar-agent-item">🤖 <b>Coordinator Agent</b></div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if st.button(
        "🗑️ Clear All Results",
        use_container_width=True,
    ):

        st.session_state.air_result = None
        st.session_state.water_result = None
        st.session_state.waste_result = None
        st.session_state.final_result = None
        st.session_state.analysis_done = False

        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🌍 Environmental Monitoring System</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered monitoring of air, water and waste"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">📊 Environmental Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Run a complete environmental analysis using "
        "the available AI agents."
    )

    col1, col2 = st.columns([3, 1])

    with col1:

        dashboard_city = st.text_input(
            "📍 City",
            value="Pune",
            key="dashboard_city",
        )

    with col2:

        st.write("")

        complete_analysis = st.button(
            "🚀 Complete Analysis",
            use_container_width=True,
        )

    if complete_analysis:

        if not dashboard_city.strip():

            st.warning(
                "Please enter a city."
            )

        else:

            run_air(dashboard_city)

            run_water(
                7.2,
                2.0,
                350.0,
                7.0,
            )

            # No waste image is available on Dashboard.
            st.session_state.waste_result = {
                "agent": "Waste Detection Agent",
                "status": "Unknown",
                "detections": [],
                "message": (
                    "No waste image uploaded on the Dashboard."
                ),
            }

            run_coordinator()

    # --------------------------------------------------------
    # Agent cards
    # --------------------------------------------------------

    st.markdown("### 🤖 Agent Results")

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # AIR CARD
    # --------------------------------------------------------

    with col1:

        air = st.session_state.air_result

        if air:

            status = air.get(
                "status",
                "Unknown",
            )

            aqi = air.get(
                "aqi",
                "N/A",
            )

            city = air.get(
                "city",
                dashboard_city,
            )

            st.markdown(
                f"""
                <div class="agent-card">
                    <h3>🌫️ Air Quality</h3>
                    <p><b>Location:</b> {safe_html(city)}</p>
                    <p><b>AQI:</b> {safe_html(aqi)}</p>
                    <p class="{get_status_class(status)}">
                        {get_status_icon(status)}
                        {safe_html(status)}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "Air Quality Agent: Not analyzed"
            )

    # --------------------------------------------------------
    # WATER CARD
    # --------------------------------------------------------

    with col2:

        water = st.session_state.water_result

        if water:

            status = water.get(
                "status",
                "Unknown",
            )

            st.markdown(
                f"""
                <div class="agent-card">
                    <h3>💧 Water Quality</h3>
                    <p><b>pH:</b> {safe_html(water.get("ph"))}</p>
                    <p><b>Turbidity:</b> {safe_html(water.get("turbidity"))}</p>
                    <p><b>TDS:</b> {safe_html(water.get("tds"))}</p>
                    <p class="{get_status_class(status)}">
                        {get_status_icon(status)}
                        {safe_html(status)}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "Water Quality Agent: Not analyzed"
            )

    # --------------------------------------------------------
    # WASTE CARD
    # --------------------------------------------------------

    with col3:

        waste = st.session_state.waste_result

        if waste:

            status = waste.get(
                "status",
                "Unknown",
            )

            detections = waste.get(
                "detections",
                [],
            )

            if not isinstance(
                detections,
                list,
            ):
                detections = []

            st.markdown(
                f"""
                <div class="agent-card">
                    <h3>♻️ Waste Detection</h3>
                    <p><b>Detections:</b> {len(detections)}</p>
                    <p class="{get_status_class(status)}">
                        {get_status_icon(status)}
                        {safe_html(status)}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "Waste Detection Agent: Not analyzed"
            )

    # --------------------------------------------------------
    # COORDINATOR RESULT
    # --------------------------------------------------------

    if st.session_state.final_result:

        st.markdown(
            "### 🤖 Coordinator Summary"
        )

        final_result = st.session_state.final_result

        final_status = final_result.get(
            "status",
            "Unknown",
        )

        st.markdown(
            f"""
            <div class="info-box">
                <h3>
                    {get_status_icon(final_status)}
                    Environmental Status:
                    {safe_html(final_status)}
                </h3>
                <p>
                    {safe_html(
                        final_result.get(
                            "message",
                            "No summary available.",
                        )
                    )}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# AIR DETECTION
# ============================================================

elif page == "Air Detection":

    st.markdown(
        '<div class="section-title">🌫️ Air Quality Detection</div>',
        unsafe_allow_html=True,
    )

    city = st.text_input(
        "📍 Enter City",
        value="Pune",
        key="air_detection_city",
    )

    if st.button(
        "🔍 Analyze Air Quality",
        use_container_width=True,
    ):

        run_air(city)

    if st.session_state.air_result:

        air = st.session_state.air_result

        st.markdown(
            "### Air Agent Response"
        )

        col1, col2, col3 = st.columns(3)

        # AQI
        with col1:

            st.metric(
                "AQI",
                air.get(
                    "aqi",
                    "N/A",
                ),
            )

        # STATUS
        with col2:

            st.metric(
                "Status",
                air.get(
                    "status",
                    "Unknown",
                ),
            )

        # CITY
        with col3:

            st.metric(
                "Location",
                air.get(
                    "city",
                    city,
                ),
            )

        # Message

        if air.get("message"):

            st.info(
                air["message"]
            )

        # Optional AQI category

        if air.get("aqi_category"):

            st.caption(
                f"AQI Category: "
                f"{air['aqi_category']}"
            )

        # Raw response

        with st.expander(
            "View Full Air Agent Response"
        ):

            st.json(air)


# ============================================================
# WATER DETECTION
# ============================================================

elif page == "Water Detection":

    st.markdown(
        '<div class="section-title">💧 Water Quality Detection</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Enter the measured water-quality parameters."
    )

    col1, col2 = st.columns(2)

    with col1:

        ph = st.number_input(
            "pH",
            min_value=0.0,
            max_value=14.0,
            value=7.2,
            step=0.1,
        )

        turbidity = st.number_input(
            "Turbidity (NTU)",
            min_value=0.0,
            value=2.0,
            step=0.1,
        )

    with col2:

        tds = st.number_input(
            "TDS (mg/L)",
            min_value=0.0,
            value=350.0,
            step=10.0,
        )

        dissolved_oxygen = st.number_input(
            "Dissolved Oxygen (mg/L)",
            min_value=0.0,
            value=7.0,
            step=0.1,
        )

    if st.button(
        "🔍 Analyze Water Quality",
        use_container_width=True,
    ):

        run_water(
            ph,
            turbidity,
            tds,
            dissolved_oxygen,
        )

    if st.session_state.water_result:

        water = st.session_state.water_result

        st.markdown(
            "### Water Agent Response"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "pH",
                water.get(
                    "ph",
                    ph,
                ),
            )

        with col2:
            st.metric(
                "Turbidity",
                water.get(
                    "turbidity",
                    turbidity,
                ),
            )

        with col3:
            st.metric(
                "TDS",
                water.get(
                    "tds",
                    tds,
                ),
            )

        with col4:
            st.metric(
                "Dissolved Oxygen",
                water.get(
                    "dissolved_oxygen",
                    dissolved_oxygen,
                ),
            )

        status = water.get(
            "status",
            "Unknown",
        )

        st.markdown(
            f"""
            <div class="{get_status_class(status)}">
                {get_status_icon(status)}
                Water Quality Status:
                {safe_html(status)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if water.get("message"):

            st.info(
                water["message"]
            )

        # Water parameter chart

        try:

            chart_data = pd.DataFrame(
                {
                    "Parameter": [
                        "pH",
                        "Turbidity",
                        "TDS",
                        "Dissolved Oxygen",
                    ],
                    "Value": [
                        float(
                            water.get(
                                "ph",
                                ph,
                            )
                        ),
                        float(
                            water.get(
                                "turbidity",
                                turbidity,
                            )
                        ),
                        float(
                            water.get(
                                "tds",
                                tds,
                            )
                        ),
                        float(
                            water.get(
                                "dissolved_oxygen",
                                dissolved_oxygen,
                            )
                        ),
                    ],
                }
            )

            st.markdown(
                "### 📈 Water Parameters"
            )

            st.bar_chart(
                chart_data.set_index(
                    "Parameter"
                )
            )

        except Exception:
            pass

        with st.expander(
            "View Full Water Agent Response"
        ):

            st.json(water)


# ============================================================
# WASTE DETECTION
# ============================================================

elif page == "Waste Detection":

    st.markdown(
        '<div class="section-title">♻️ Waste Detection</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Upload an image containing waste for analysis."
    )

    uploaded_file = st.file_uploader(
        "📷 Upload Waste Image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
        key="waste_uploader",
    )

    if uploaded_file:

        st.image(
            uploaded_file,
            caption="Uploaded Waste Image",
            use_container_width=True,
        )

        if st.button(
            "🔍 Detect Waste",
            use_container_width=True,
        ):

            run_waste(
                uploaded_file
            )

    if st.session_state.waste_result:

        waste = st.session_state.waste_result

        st.markdown(
            "### Waste Agent Response"
        )

        status = waste.get(
            "status",
            "Unknown",
        )

        detections = waste.get(
            "detections",
            [],
        )

        if not isinstance(
            detections,
            list,
        ):
            detections = []

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Detected Objects",
                len(detections),
            )

        with col2:

            st.metric(
                "Status",
                status,
            )

        # Message

        if waste.get("message"):

            if (
                status == "Unknown"
                and len(detections) == 0
            ):
                st.warning(
                    waste["message"]
                )
            else:
                st.info(
                    waste["message"]
                )

        # Detections

        if detections:

            st.markdown(
                "### Detected Waste"
            )

            rows = []

            for detection in detections:

                if isinstance(
                    detection,
                    dict,
                ):

                    rows.append(
                        {
                            "Object": detection.get(
                                "object",
                                detection.get(
                                    "class",
                                    detection.get(
                                        "name",
                                        "Unknown",
                                    ),
                                ),
                            ),
                            "Confidence": detection.get(
                                "confidence",
                                detection.get(
                                    "score",
                                    "N/A",
                                ),
                            ),
                        }
                    )

                else:

                    rows.append(
                        {
                            "Object": str(
                                detection
                            ),
                            "Confidence": "N/A",
                        }
                    )

            if rows:

                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                )

        elif status != "Unknown":

            st.info(
                "No waste objects were detected."
            )

        with st.expander(
            "View Full Waste Agent Response"
        ):

            st.json(waste)


# ============================================================
# COORDINATOR AGENT
# ============================================================

elif page == "Coordinator Agent":

    st.markdown(
        '<div class="section-title">🤖 Coordinator Agent</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "The Coordinator Agent combines the outputs "
        "from the Air, Water and Waste agents."
    )

    if st.button(
        "🚀 Run Coordinator Analysis",
        use_container_width=True,
    ):

        run_coordinator()

    # --------------------------------------------------------
    # Agent Status - clean boxed layout
    # --------------------------------------------------------

    st.markdown("### 📊 Agent Status")

    air = st.session_state.air_result or {}
    water = st.session_state.water_result or {}
    waste = st.session_state.waste_result or {}

    air_status = air.get("status", "Unknown")
    water_status = water.get("status", "Unknown")
    waste_status = waste.get("status", "Unknown")

    air_aqi = air.get("aqi")
    air_city = air.get("city", "Not available")

    water_ph = water.get("ph", water.get("pH", "N/A"))
    water_tds = water.get("tds", "N/A")
    water_turbidity = water.get("turbidity", "N/A")

    waste_detections = waste.get("detections", [])
    if not isinstance(waste_detections, list):
        waste_detections = []

    col1, col2, col3 = st.columns(3)

    # AIR QUALITY BOX
    with col1:
        with st.container(border=True):
            st.markdown("### 🌫️ Air Quality")

            st.metric(
                "Air Quality Index",
                air_aqi if air_aqi is not None else "N/A",
            )

            st.markdown(
                f"**Status:** {get_status_icon(air_status)} "
                f"{safe_html(air_status)}"
            )

            st.caption(
                f"📍 Location: {safe_html(air_city)}"
            )

    # WATER QUALITY BOX
    with col2:
        with st.container(border=True):
            st.markdown("### 💧 Water Quality")

            st.metric("pH", water_ph)

            st.markdown(
                f"**Status:** {get_status_icon(water_status)} "
                f"{safe_html(water_status)}"
            )

            st.caption(
                f"TDS: {safe_html(water_tds)} mg/L"
            )

            st.caption(
                f"Turbidity: {safe_html(water_turbidity)} NTU"
            )

    # WASTE DETECTION BOX
    with col3:
        with st.container(border=True):
            st.markdown("### ♻️ Waste Detection")

            st.metric(
                "Detected Objects",
                len(waste_detections),
            )

            st.markdown(
                f"**Status:** {get_status_icon(waste_status)} "
                f"{safe_html(waste_status)}"
            )

            if waste_status == "Unknown":
                st.caption("Waste analysis has not been performed.")
            else:
                st.caption("Waste image analysis completed.")

    # --------------------------------------------------------
    # Coordinator result
    # --------------------------------------------------------

    if st.session_state.final_result:

        st.markdown(
            "### 🎯 Final Environmental Assessment"
        )

        final_result = st.session_state.final_result

        status = final_result.get(
            "status",
            "Unknown",
        )

        agents_analyzed = final_result.get(
            "agents_analyzed",
            0,
        )

        average_risk = final_result.get(
            "average_risk",
            None,
        )

        message = final_result.get(
            "message",
            final_result.get(
                "reason",
                "No summary available.",
            ),
        )

        # --------------------------------------------
        # Overall status
        # --------------------------------------------

        if status == "Low":

            st.success(
                f"🟢 Environmental Status: **{status}**"
            )

        elif status == "Moderate":

            st.warning(
                f"🟡 Environmental Status: **{status}**"
            )

        elif status in ("High", "Very High"):

            st.error(
                f"🔴 Environmental Status: **{status}**"
            )

        else:

            st.info(
                f"⚪ Environmental Status: **{status}**"
            )

        # --------------------------------------------
        # Summary metrics
        # --------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Agents Analyzed",
                f"{agents_analyzed}/3",
            )

        with col2:

            if average_risk is not None:

                st.metric(
                    "Average Risk Score",
                    f"{float(average_risk):.2f}",
                )

            else:

                st.metric(
                    "Average Risk Score",
                    "N/A",
                )

        with col3:

            st.metric(
                "Overall Status",
                status,
            )

        # --------------------------------------------
        # Explanation
        # --------------------------------------------

        if message:

            st.info(
                f"📋 {message}"
            )


# ============================================================
# LIVE LOCATION
# ============================================================
elif page == "Live Location":

    st.markdown(
        '<div class="section-title">📍 Live Location</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Get your current device location using your browser's "
        "GPS/location permission."
    )

    st.info(
        "📌 On the first click, Chrome should ask for location permission. "
        "Choose **Allow**. This works on localhost when location permission "
        "is enabled for the site."
    )

    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: transparent;
                }

                .location-card {
                    padding: 22px;
                    border-radius: 14px;
                    border: 1px solid #d9d9d9;
                    background: white;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
                }

                .location-title {
                    font-size: 22px;
                    font-weight: 700;
                    margin-bottom: 14px;
                }

                button {
                    padding: 11px 20px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 15px;
                    font-weight: 600;
                    background: #ff4b4b;
                    color: white;
                    margin-right: 8px;
                    margin-bottom: 12px;
                }

                button:hover {
                    opacity: 0.9;
                }

                .secondary {
                    background: #666;
                }

                #location {
                    line-height: 1.8;
                    margin-top: 10px;
                }

                .success {
                    padding: 12px;
                    border-radius: 8px;
                    background: #eaf8ee;
                    border: 1px solid #b7e4c7;
                }

                .error {
                    padding: 12px;
                    border-radius: 8px;
                    background: #fff1f0;
                    border: 1px solid #ffccc7;
                }

                .small {
                    font-size: 13px;
                    color: #666;
                }

                a {
                    color: #1565c0;
                    text-decoration: none;
                    font-weight: 600;
                }
            </style>
        </head>

        <body>
            <div class="location-card">
                <div class="location-title">📍 Current Location</div>

                <button onclick="getLocation()">
                    📍 Get My Current Location
                </button>

                <button class="secondary" onclick="checkPermission()">
                    🔐 Check Permission
                </button>

                <div id="location">
                    Click <b>Get My Current Location</b> to request your
                    browser's current location.
                </div>
            </div>

            <script>
                const output = document.getElementById("location");

                function showError(message, extra = "") {
                    output.className = "error";
                    output.innerHTML =
                        "<b>❌ Location access failed</b><br>" +
                        message +
                        (extra ? "<br><br>" + extra : "");
                }

                function checkPermission() {
                    if (!navigator.permissions) {
                        output.innerHTML =
                            "Browser permission status cannot be checked automatically. " +
                            "Click <b>Get My Current Location</b> instead.";
                        return;
                    }

                    navigator.permissions.query({name: "geolocation"})
                        .then(function(permission) {
                            let state = permission.state;

                            if (state === "granted") {
                                output.className = "success";
                                output.innerHTML =
                                    "✅ Location permission is already <b>Allowed</b>.";
                            }
                            else if (state === "prompt") {
                                output.className = "";
                                output.innerHTML =
                                    "🟡 Location permission has not been decided yet. " +
                                    "Click <b>Get My Current Location</b> and choose <b>Allow</b>.";
                            }
                            else {
                                showError(
                                    "Location permission is currently <b>Blocked</b>.",
                                    "In Chrome, open the 🔒 icon beside the address " +
                                    "bar → Site settings → Location → Allow, then reload the page."
                                );
                            }

                            permission.onchange = function() {
                                checkPermission();
                            };
                        })
                        .catch(function() {
                            output.innerHTML =
                                "Click <b>Get My Current Location</b> to request location.";
                        });
                }

                function getLocation() {
                    output.className = "";
                    output.innerHTML =
                        "⏳ Requesting your current location... " +
                        "Please allow the browser permission if it appears.";

                    if (!window.isSecureContext) {
                        showError(
                            "This page is not running in a secure context.",
                            "Use http://localhost:8501 for local testing or deploy the app with HTTPS."
                        );
                        return;
                    }

                    if (!navigator.geolocation) {
                        showError(
                            "Geolocation is not supported by this browser.",
                            "Please use a modern version of Chrome, Edge, or Firefox."
                        );
                        return;
                    }

                    navigator.geolocation.getCurrentPosition(
                        function(position) {
                            const latitude =
                                position.coords.latitude.toFixed(6);

                            const longitude =
                                position.coords.longitude.toFixed(6);

                            const accuracy =
                                Math.round(position.coords.accuracy);

                            const timestamp =
                                new Date(position.timestamp).toLocaleString();

                            const mapUrl =
                                "https://www.google.com/maps?q=" +
                                latitude + "," + longitude;

                            output.className = "success";

                            output.innerHTML =
                                "<b>✅ Current location detected!</b><br><br>" +
                                "📍 <b>Latitude:</b> " + latitude + "<br>" +
                                "📍 <b>Longitude:</b> " + longitude + "<br>" +
                                "🎯 <b>Accuracy:</b> approximately " +
                                accuracy + " meters<br>" +
                                "🕒 <b>Updated:</b> " + timestamp + "<br><br>" +
                                "<a href='" + mapUrl +
                                "' target='_blank'>🗺️ Open Location in Google Maps</a>";
                        },

                        function(error) {
                            if (error.code === 1) {
                                showError(
                                    "Browser permission was denied.",
                                    "Chrome: click the 🔒 icon beside localhost:8501 → " +
                                    "Site settings → Location → Allow → reload the page."
                                );
                            }
                            else if (error.code === 2) {
                                showError(
                                    "Your device could not determine the location.",
                                    "Turn on Windows Location Services and make sure Wi-Fi/GPS/location services are available."
                                );
                            }
                            else if (error.code === 3) {
                                showError(
                                    "The location request timed out.",
                                    "Try again with Wi-Fi/location services enabled."
                                );
                            }
                            else {
                                showError(
                                    "Unable to access location: " + error.message
                                );
                            }
                        },

                        {
                            enableHighAccuracy: true,
                            timeout: 20000,
                            maximumAge: 0
                        }
                    );
                }

                // Show the current permission state when the page opens.
                checkPermission();
            </script>
        </body>
        </html>
        """,
        height=390,
        scrolling=False,
    )



# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🌍 Environmental Monitoring System • "
    "Air + Water + Waste + Coordinator AI"
)