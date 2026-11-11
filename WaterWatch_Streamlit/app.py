
import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ============================================================
# WATERWATCH - SMART WATER LEVEL MONITORING DASHBOARD
# SIMULATION MODE: RANDOM READINGS EVERY 2 SECONDS
# ============================================================

st.set_page_config(
    page_title="WATERWATCH | Water Monitor",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Detection configuration
MIN_CM = 2.0
MAX_CM = 20.0
WARNING_CM = 10.0
CRITICAL_CM = 5.0
HISTORY_LIMIT = 180


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 12% 0%, rgba(22,105,150,.20), transparent 28%),
        linear-gradient(145deg, #07111f 0%, #0a1728 55%, #081321 100%);
    color: #eaf3ff;
}

[data-testid="stSidebar"] {
    background: #0b192b;
    border-right: 1px solid rgba(130,170,210,.16);
}

.hero {
    padding: 1.2rem 1.4rem;
    border: 1px solid rgba(110,170,220,.20);
    border-radius: 18px;
    background: linear-gradient(120deg, rgba(18,48,76,.92), rgba(12,28,49,.88));
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: .06em;
}

.hero-title span {
    color: #42d9ef;
}

.hero-sub {
    color: #9eb3cc;
    margin-top: .25rem;
    font-size: .9rem;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #14263d, #0e1c30);
    border: 1px solid rgba(130,170,210,.17);
    padding: 15px 17px;
    border-radius: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #a8bad0;
}

div[data-testid="stMetricValue"] {
    color: #f0f7ff;
}

.stPlotlyChart {
    border: 1px solid rgba(130,170,210,.13);
    border-radius: 14px;
    padding: 5px;
    background: rgba(13,29,49,.55);
}

.note {
    color: #91a8c2;
    font-size: .82rem;
}
</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AUTOMATIC REFRESH - EVERY 2 SECONDS
# ============================================================

st_autorefresh(
    interval=2000,
    key="waterwatch_refresh"
)


# ============================================================
# WATER LEVEL LOGIC
# ============================================================

def classify(distance):

    if distance <= CRITICAL_CM:
        return "Critical"

    elif distance <= WARNING_CM:
        return "Warning"

    else:
        return "Normal"


def next_reading(previous):

    if previous is None:
        return round(random.uniform(12, 19), 1)

    if random.random() < 0.13:

        target = random.uniform(2.5, 7.0)

        value = previous + (
            target - previous
        ) * random.uniform(0.25, 0.65)

    else:

        value = previous + random.uniform(-1.5, 1.5)

    return round(
        max(MIN_CM, min(MAX_CM, value)),
        1
    )


# ============================================================
# SESSION STATE AND SIMULATED READING
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.history:

    previous = st.session_state.history[-1]["distance_cm"]

else:

    previous = None

now = datetime.now()

distance = next_reading(previous)

status = classify(distance)

led_on = distance <= CRITICAL_CM

st.session_state.history.append({
    "timestamp": now,
    "distance_cm": distance,
    "status": status
})

# Keep latest 180 readings
st.session_state.history = (
    st.session_state.history[-HISTORY_LIMIT:]
)

df = pd.DataFrame(st.session_state.history)

status_color = {
    "Normal": "#35d49a",
    "Warning": "#f6bd4b",
    "Critical": "#ff6278"
}[status]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 💧 WATERWATCH")

    st.caption("SIMULATED MONITORING CONSOLE")

    st.divider()

    st.markdown("### Detection settings")

    st.metric("Maximum range", "20 cm")

    st.metric("Warning threshold", "10 cm")

    st.metric("Critical threshold", "5 cm")

    st.divider()

    st.markdown("### Simulation controls")

    if st.button(
        "🔄 Reset simulation",
        use_container_width=True
    ):

        st.session_state.history = []

        st.rerun()

    st.caption(
        "A new random reading is generated every 2 seconds."
    )

    st.caption(
        "Demo mode only. No ESP8266 or HC-SR04 connection."
    )


# ============================================================
# HEADER - FIXED HTML RENDERING
# ============================================================

st.markdown(
    """
<div class="hero">
    <div class="hero-title">WATER<span>WATCH</span></div>
    <div class="hero-sub">
        SMART WATER LEVEL MONITORING · SIMULATION MODE
    </div>
</div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ALERT SYSTEM
# ============================================================

if led_on:

    st.error(
        "🚨 CRITICAL LEVEL — "
        "Simulated distance is 5 cm or less. "
        "Red LED state: ON."
    )

elif status == "Warning":

    st.warning(
        "⚠️ WARNING — "
        "Simulated water surface is approaching "
        "the critical threshold."
    )

else:

    st.success(
        "SYSTEM NORMAL — "
        "Simulated distance is within normal range."
    )


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Sensor distance",
    f"{distance:.1f} cm"
)

col2.metric(
    "Water condition",
    status
)

col3.metric(
    "Red LED state",
    "ON" if led_on else "OFF"
)

col4.metric(
    "Recorded readings",
    f"{len(df):,}"
)

st.caption(
    f"Last simulated update: "
    f"{now.strftime('%d %b %Y · %H:%M:%S')} "
    "| Refresh interval: 2 seconds"
)


# ============================================================
# GAUGE CHART AND LIVE LINE CHART
# ============================================================

left, right = st.columns([0.85, 1.65])


# GAUGE CHART

with left:

    st.subheader("Water Proximity · Gauge")

    gauge = go.Figure(
        go.Indicator(

            mode="gauge+number",

            value=distance,

            number={
                "suffix": " cm",
                "font": {
                    "size": 30,
                    "color": "#edf6ff"
                }
            },

            title={
                "text": "Distance from sensor",
                "font": {
                    "color": "#a9bdd3",
                    "size": 14
                }
            },

            gauge={

                "axis": {
                    "range": [0, MAX_CM],
                    "tickcolor": "#8da5bf"
                },

                "bar": {
                    "color": status_color,
                    "thickness": 0.25
                },

                "bgcolor": "#10233a",

                "borderwidth": 1,

                "bordercolor": "#2b4561",

                "steps": [

                    {
                        "range": [0, CRITICAL_CM],
                        "color": "rgba(255,98,120,.25)"
                    },

                    {
                        "range": [
                            CRITICAL_CM,
                            WARNING_CM
                        ],
                        "color": "rgba(246,189,75,.20)"
                    },

                    {
                        "range": [
                            WARNING_CM,
                            MAX_CM
                        ],
                        "color": "rgba(53,212,154,.15)"
                    }

                ],

                "threshold": {

                    "line": {
                        "color": "#ff6278",
                        "width": 4
                    },

                    "thickness": 0.8,

                    "value": CRITICAL_CM

                }

            }

        )
    )

    gauge.update_layout(

        height=300,

        margin=dict(
            l=20,
            r=20,
            t=55,
            b=15
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        font_color="#edf6ff"

    )

    st.plotly_chart(
        gauge,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# LINE CHART

with right:

    st.subheader("Live Distance Trend · Line Chart")

    line_fig = px.line(

        df,

        x="timestamp",

        y="distance_cm",

        markers=True,

        labels={
            "timestamp": "Time",
            "distance_cm": "Distance (cm)"
        }

    )

    line_fig.update_traces(

        line_color="#42d9ef",

        line_width=3,

        marker_size=5,

        fill="tozeroy",

        fillcolor="rgba(66,217,239,.10)"

    )

    line_fig.add_hline(

        y=CRITICAL_CM,

        line_dash="dash",

        line_color="#ff6278",

        annotation_text="Critical · 5 cm"

    )

    line_fig.add_hline(

        y=WARNING_CM,

        line_dash="dot",

        line_color="#f6bd4b",

        annotation_text="Warning · 10 cm"

    )

    line_fig.update_yaxes(

        range=[0, MAX_CM],

        gridcolor="rgba(150,180,210,.12)"

    )

    line_fig.update_layout(

        height=300,

        margin=dict(
            l=15,
            r=15,
            t=20,
            b=15
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color="#c6d5e7"

    )

    st.plotly_chart(
        line_fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ============================================================
# BAR CHART AND DONUT CHART
# ============================================================

st.subheader("Analytics & Reading Distribution")

chart_col1, chart_col2 = st.columns(2)


# BAR CHART

with chart_col1:

    st.markdown("**Recent Readings · Bar Chart**")

    recent = df.tail(15).copy()

    recent["sample"] = range(
        1,
        len(recent) + 1
    )

    bar_fig = px.bar(

        recent,

        x="sample",

        y="distance_cm",

        color="status",

        color_discrete_map={

            "Normal": "#35d49a",

            "Warning": "#f6bd4b",

            "Critical": "#ff6278"

        },

        labels={

            "sample": "Recent sample",

            "distance_cm": "Distance (cm)",

            "status": "Condition"

        }

    )

    bar_fig.update_layout(

        height=300,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color="#c6d5e7",

        yaxis=dict(
            range=[0, MAX_CM]
        )

    )

    st.plotly_chart(
        bar_fig,
        use_container_width=True
    )


# DONUT CHART

with chart_col2:

    st.markdown("**Condition Breakdown · Donut Chart**")

    counts = df["status"].value_counts().reindex(
        ["Normal", "Warning", "Critical"],
        fill_value=0
    )

    pie_fig = px.pie(

        names=counts.index,

        values=counts.values,

        hole=0.62,

        color=counts.index,

        color_discrete_map={

            "Normal": "#35d49a",

            "Warning": "#f6bd4b",

            "Critical": "#ff6278"

        }

    )

    pie_fig.update_traces(

        textinfo="label+percent",

        textfont_color="#edf6ff"

    )

    pie_fig.update_layout(

        height=300,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        font_color="#c6d5e7"

    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )


# ============================================================
# AREA CHART AND HISTOGRAM
# ============================================================

area_col, hist_col = st.columns(2)


# AREA CHART

with area_col:

    st.markdown("**Distance History · Area Chart**")

    area_fig = px.area(

        df,

        x="timestamp",

        y="distance_cm",

        labels={

            "timestamp": "Time",

            "distance_cm": "Distance (cm)"

        }

    )

    area_fig.update_traces(

        line_color="#9b8cff",

        fillcolor="rgba(155,140,255,.22)"

    )

    area_fig.add_hline(

        y=CRITICAL_CM,

        line_dash="dash",

        line_color="#ff6278"

    )

    area_fig.update_yaxes(
        range=[0, MAX_CM]
    )

    area_fig.update_layout(

        height=280,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color="#c6d5e7"

    )

    st.plotly_chart(
        area_fig,
        use_container_width=True
    )


# HISTOGRAM

with hist_col:

    st.markdown("**Reading Frequency · Histogram**")

    hist_fig = px.histogram(

        df,

        x="distance_cm",

        nbins=10,

        color_discrete_sequence=["#42d9ef"],

        labels={

            "distance_cm": "Distance (cm)",

            "count": "Readings"

        }

    )

    hist_fig.update_layout(

        height=280,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color="#c6d5e7"

    )

    hist_fig.update_xaxes(
        range=[0, MAX_CM]
    )

    st.plotly_chart(
        hist_fig,
        use_container_width=True
    )


# ============================================================
# RECENT MEASUREMENTS TABLE
# ============================================================

st.subheader("Recent Simulated Measurements")

view = df.tail(20).copy()

view["timestamp"] = view[
    "timestamp"
].dt.strftime("%d %b %Y %H:%M:%S")

view = view.rename(
    columns={
        "timestamp": "Timestamp",
        "distance_cm": "Distance (cm)",
        "status": "Condition"
    }
)

st.dataframe(
    view.iloc[::-1],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CSV DOWNLOAD
# ============================================================

st.download_button(

    "⬇ Download Readings as CSV",

    df.to_csv(index=False).encode("utf-8"),

    file_name="waterwatch_simulated_readings.csv",

    mime="text/csv"

)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<p class="note">
WATERWATCH · Simulation dashboard ·
Random sample every 2 seconds ·
Not connected to physical hardware ·
Demo data is not suitable for safety decisions.
</p>
    """,
    unsafe_allow_html=True
)
