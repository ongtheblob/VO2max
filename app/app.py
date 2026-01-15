import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="VO₂max + Running Economy", layout="wide")

st.title("VO₂max & Running Economy Test Logger")

st.write("""
Enter test data from both phases:
- **Running Economy** (speed increments)
- **Maximal VO₂ / Endurance** (gradient increments)
""")

# Basic info
with st.form("info"):
    col1, col2, col3 = st.columns(3)
    participant = col1.text_input("Participant Number")
    researcher = col2.text_input("Researcher Name")
    age = col3.number_input("Participant Age", min_value=10, max_value=100, value=25)

    date = st.date_input("Date")

    submitted_info = st.form_submit_button("Continue")

if submitted_info:
    st.session_state["participant"] = participant
    st.session_state["researcher"] = researcher
    st.session_state["age"] = age
    st.session_state["date"] = date
    st.session_state["hrmax"] = 220 - age


# -------------------------------
# RUNNING ECONOMY SECTION
# -------------------------------
st.header("🏃 Running Economy Test")

with st.form("running_form"):
    stages_re = st.number_input("Number of Running Economy Stages (3–12)", min_value=1, max_value=20, value=4)
    exp_speed = st.number_input("Starting Speed (km/h)", min_value=0.0, step=0.1)
    
    re_speed, re_vo2, re_hr, re_rpe = [], [], [], []

    for i in range(stages_re):
        st.subheader(f"Stage {i+1}")
        re_speed.append(st.number_input(f"Speed (km/h), minute {i+1}", min_value=0.0, step=0.1, key=f"re_speed_{i}"))
        re_vo2.append(st.number_input(f"VO₂ (ml/kg/min)", min_value=0.0, step=0.1, key=f"re_vo2_{i}"))
        re_hr.append(st.number_input(f"Heart Rate (bpm)", min_value=0, step=1, key=f"re_hr_{i}"))
        re_rpe.append(st.number_input(f"RPE (6–20)", min_value=6, max_value=20, step=1, key=f"re_rpe_{i}"))

    save_re = st.form_submit_button("Save Running Economy Data")

if save_re:
    re_df = pd.DataFrame({
        "Stage": list(range(1, stages_re + 1)),
        "Speed (km/h)": re_speed,
        "VO2 (ml/kg/min)": re_vo2,
        "Heart Rate (bpm)": re_hr,
        "RPE": re_rpe
    })
    st.session_state["re_df"] = re_df
    st.success("Running Economy data recorded!")


# -------------------------------
# ENDURANCE / VO2 MAX SECTION
# -------------------------------
st.header("⛰️ Maximal Oxygen Uptake / Endurance Test")

with st.form("vo2_form"):
    stages_vo2 = st.number_input("Number of VO₂max Stages (5–12)", min_value=1, max_value=20, value=10)
    test_speed = st.number_input("Test Speed (km/h)", min_value=0.0, step=0.1)

    vo2_grad, vo2_vals, vo2_hr, vo2_rpe = [], [], [], []

    for i in range(stages_vo2):
        st.subheader(f"Stage {i+1}")
        vo2_grad.append(st.number_input(f"Gradient (%)", min_value=0.0, step=0.5, key=f"grad_{i}"))
        vo2_vals.append(st.number_input(f"VO₂ (ml/kg/min)", min_value=0.0, step=0.1, key=f"vo2_{i}"))
        vo2_hr.append(st.number_input(f"Heart Rate (bpm)", min_value=0, step=1, key=f"vo2_hr_{i}"))
        vo2_rpe.append(st.number_input(f"RPE (6–20)", min_value=6, max_value=20, step=1, key=f"vo2_rpe_{i}"))

    save_vo2 = st.form_submit_button("Save VO₂max Data")

if save_vo2:
    hrmax = st.session_state["hrmax"]
    vo2_df = pd.DataFrame({
        "Stage": list(range(1, stages_vo2 + 1)),
        "Gradient (%)": vo2_grad,
        "VO2 (ml/kg/min)": vo2_vals,
        "Heart Rate (bpm)": vo2_hr,
        "RPE": vo2_rpe
    })

    # Flag >90% HRmax
    vo2_df["%HRmax"] = (vo2_df["Heart Rate (bpm)"] / hrmax) * 100
    vo2_df[">90% HRmax?"] = vo2_df["%HRmax"] > 90

    st.session_state["vo2_df"] = vo2_df
    st.success("VO₂max endurance data recorded!")


# -------------------------------
# ANALYSIS + PLOTS
# -------------------------------
if "vo2_df" in st.session_state:
    df = st.session_state["vo2_df"]
    hrmax = st.session_state["hrmax"]

    st.header("📊 Summary & Graphs")

    vo2max = df["VO2 (ml/kg/min)"].max()
    st.metric("VO₂max", f"{vo2max:.2f} ml/kg/min")
    st.metric("Predicted HRmax", f"{hrmax} bpm")

    st.subheader("Flagged Endurance Table (>90% HRmax ⚠️)")
    st.dataframe(df.style.apply(
        lambda s: ['background-color: yellow' if v else '' for v in s] if s.name == ">90% HRmax?" else ['']*len(s),
        axis=0
    ))

    # VO₂ curve
    fig1, ax1 = plt.subplots()
    ax1.plot(df["Stage"], df["VO2 (ml/kg/min)"])
    ax1.set_title("VO₂ Curve")
    ax1.set_xlabel("Stage")
    ax1.set_ylabel("VO₂ (ml/kg/min)")
    st.pyplot(fig1)

    # Heart rate curve
    fig2, ax2 = plt.subplots()
    ax2.plot(df["Stage"], df["Heart Rate (bpm)"])
    ax2.set_title("Heart Rate Curve")
    ax2.set_xlabel("Stage")
    ax2.set_ylabel("HR (bpm)")
    st.pyplot(fig2)

    # RPE curve
    fig3, ax3 = plt.subplots()
    ax3.plot(df["Stage"], df["RPE"])
    ax3.set_title("RPE Curve")
    ax3.set_xlabel("Stage")
    ax3.set_ylabel("RPE (6–20)")
    st.pyplot(fig3)

    # CSV
    csv = df.to_csv(index=False).encode()
    st.download_button(
        "Download VO₂max Test CSV",
        csv,
        file_name=f"VO2max_{participant}.csv",
        mime="text/csv"
    )

if "re_df" in st.session_state:
    re_df = st.session_state["re_df"]

    st.subheader("Running Economy Speed vs VO₂")
    fig4, ax4 = plt.subplots()
    ax4.plot(re_df["Speed (km/h)"], re_df["VO2 (ml/kg/min)"])
    ax4.set_title("Running Economy VO₂ vs Speed")
    ax4.set_xlabel("Speed (km/h)")
    ax4.set_ylabel("VO₂ (ml/kg/min)")
    st.pyplot(fig4)

    # CSV
    csv = re_df.to_csv(index=False).encode()
    st.download_button(
        "Download Running Economy CSV",
        csv,
        file_name=f"RunningEconomy_{participant}.csv",
        mime="text/csv"
    )
