import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Upload file CSV
st.title("📊 DASHBOARD")
uploaded_file = st.file_uploader("Select file:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        df["time"] = df["time"].dt.tz_convert("Asia/Ho_Chi_Minh")

        first_features = [col for col in df.columns if "First" in col]

        if not first_features:
            st.error("❌ Không tìm thấy thuộc tính nào có 'First'")
        else:
            show_full = st.checkbox("Hiển thị toàn bộ dữ liệu", value=False)
            if show_full:
                st.dataframe(df)
            else:
                st.dataframe(df.head(1000))

            st.subheader("⏰ Chọn mốc thời gian")
            option = st.radio("Chế độ chọn:", ["Tất cả", "Chọn theo mốc thời gian"])

            if option == "Chọn theo mốc thời gian":
                date_selected = st.date_input("Chọn ngày", df["time"].min().date())

                time_text = st.text_input("Nhập giờ phút giây (HH:MM:SS):", "")

                selected_time = None
                if time_text.strip():
                    try:
                        time_selected = datetime.strptime(time_text, "%H:%M:%S").time()
                        selected_time = datetime.combine(date_selected, time_selected)
                        selected_time = pd.to_datetime(selected_time).tz_localize("Asia/Ho_Chi_Minh")
                    except ValueError:
                        st.error("⚠️ Định dạng giờ phút giây không hợp lệ! Vui lòng nhập theo HH:MM:SS")

                minutes = st.number_input(
                    "Nhập số phút (-1 để lấy tất cả):",
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

            st.subheader("🔎 Chọn thông số để quan sát")
            center_feature = st.selectbox("Chọn thông số trung tâm:", first_features)
            other_features = st.multiselect(
                "Chọn các thông số khác:",
                [f for f in first_features if f != center_feature]
            )

            selected_features = [center_feature] + other_features

            if not df_filtered.empty:
                st.subheader("📈 Biểu đồ dữ liệu")

                for col in selected_features:
                    fig = px.line(df_filtered, x="time", y=col, title=f"Biểu đồ {col}")
                    fig.update_traces(
                        mode="lines+markers",
                        hovertemplate="Thời gian=%{x|%Y-%m-%d %H:%M:%S}<br>Giá trị=%{y}"
                    )
                    fig.update_layout(xaxis_title="Thời gian", yaxis_title=col)
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("⚠️ Không có dữ liệu trong khoảng thời gian này!")
    else:
        st.error("❌ File không có cột 'time'")
