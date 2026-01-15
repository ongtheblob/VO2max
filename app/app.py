import streamlit as st
import pandas as pd

st.set_page_config(page_title="VO₂max Calculator", layout="centered")

st.title("VO₂max Calculator (Gas Analysis)")
st.write("Enter VO₂ values (ml/kg/min) from each stage of the treadmill VO₂max test.")

# Participant info
with st.form("info_form"):
    col1, col2 = st.columns(2)
    participant = col1.text_input("Participant Number")
    researcher = col2.text_input("Researcher Name")
    date = st.date_input("Date")

    stages = st.number_input(
        "Number of minutes/stages completed",
        min_value=1,
        max_value=20,
        value=8,
        step=1
    )

    submitted = st.form_submit_button("Continue")

if submitted:
    st.session_state["stages"] = stages
    st.session_state["participant"] = participant
    st.session_state["researcher"] = researcher
    st.session_state["date"] = date


# Enter VO2 values
if "stages" in st.session_state:
    st.subheader("Enter VO₂ values (ml/kg/min)")

    vo2_inputs = []
    for i in range(st.session_state["stages"]):
        vo2 = st.number_input(
            f"Minute {i+1}",
            min_value=0.0,
            step=0.1,
            key=f"vo2_{i}"
        )
        vo2_inputs.append(vo2)

    if st.button("Calculate VO₂max"):
        df = pd.DataFrame({
            "Minute": list(range(1, st.session_state["stages"] + 1)),
            "VO2 (ml/kg/min)": vo2_inputs
        })

        vo2max = df["VO2 (ml/kg/min)"].max()
        vo2mean = df["VO2 (ml/kg/min)"].mean()

        st.success(f"**VO₂max: {vo2max:.2f} ml/kg/min**")
        st.write(f"Average VO₂: **{vo2mean:.2f} ml/kg/min**")
        st.dataframe(df)

        # Download CSV
        csv = df.to_csv(index=False).encode()
        st.download_button(
            "Download VO₂ Data (CSV)",
            csv,
            file_name=f"VO2_{st.session_state['participant']}.csv",
            mime="text/csv"
        )

