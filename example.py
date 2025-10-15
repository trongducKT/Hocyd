import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ========================================
# Mapping dictionary for Modbus points
# ========================================
point_titles = {
    443: "Air Compressor Alarm Status",
    444: "Air Compressor Warning Status",
    454: "Warning Code",
    310: "Fault Type",
    318: "Water Pump Alarm",
    131: "Fault Type",
    139: "Water Pump Alarm",
    7: "Fault Type",
    15: "Water Pump Alarm",
    596: "Chiller Alarm 1",
    597: "Chiller Alarm 2",
    598: "Chiller Alarm 3"
}

# ========================================
# Streamlit dashboard
# ========================================
st.title("📊 DASHBOARD")
uploaded_file = st.file_uploader("Select CSV file:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        df["time"] = df["time"].dt.tz_convert("Asia/Ho_Chi_Minh")

        first_features = [col for col in df.columns if "First" in col]

        if not first_features:
            st.error("❌ No column contains 'First'.")
        else:
            show_full = st.checkbox("Show all data", value=False)
            if show_full:
                st.dataframe(df)
            else:
                st.dataframe(df.head(1000))

            st.subheader("⏰ Select time range")
            option = st.radio("Selection mode:", ["All", "Select by time range"])

            if option == "Select by time range":
                date_selected = st.date_input("Select date", df["time"].min().date())
                time_text = st.text_input("Enter time (HH:MM:SS):", "")

                selected_time = None
                if time_text.strip():
                    try:
                        time_selected = datetime.strptime(time_text, "%H:%M:%S").time()
                        selected_time = datetime.combine(date_selected, time_selected)
                        selected_time = pd.to_datetime(selected_time).tz_localize("Asia/Ho_Chi_Minh")
                    except ValueError:
                        st.error("⚠️ Invalid time format! Please enter in HH:MM:SS format.")

                minutes = st.number_input(
                    "Enter number of minutes (-1 for all):",
                    min_value=-1, max_value=10000, value=200, step=100
                )

                if selected_time is not None:
                    if minutes == -1:
                        df_filtered = df.copy()
                    else:
                        start_time = selected_time - timedelta(minutes=minutes)
                        df_filtered = df[(df["time"] >= start_time) & (df["time"] <= selected_time)]
                else:
                    df_filtered = pd.DataFrame()
            else:
                df_filtered = df.copy()

            st.subheader("🔎 Select parameters to visualize")
            center_feature = st.selectbox("Select center parameter:", first_features)
            other_features = st.multiselect(
                "Select additional parameters:",
                [f for f in first_features if f != center_feature]
            )

            selected_features = [center_feature] + other_features

            if not df_filtered.empty:
                st.subheader("📈 Data Visualization")

                for col in selected_features:
                    # Extract Modbus key if pattern matches (e.g., "point_key=443_First")
                    modbus_key = None
                    if "point_key=" in col:
                        try:
                            modbus_key = int(col.split("point_key=")[1].split("_")[0])
                        except (IndexError, ValueError):
                            modbus_key = None

                    # Determine title from dictionary
                    if modbus_key in point_titles:
                        title = f"{col} - {point_titles[modbus_key]}"
                    else:
                        title = col

                    # Plot line chart
                    fig = px.line(df_filtered, x="time", y=col, title=title)
                    fig.update_traces(
                        mode="lines+markers",
                        hovertemplate="Time=%{x|%Y-%m-%d %H:%M:%S}<br>Value=%{y}"
                    )
                    fig.update_layout(xaxis_title="Time", yaxis_title=title)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No data in this time range!")
    else:
        st.error("❌ The file does not contain a 'time' column.")
