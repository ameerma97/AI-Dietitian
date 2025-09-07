import streamlit as st
from db import init_db, count_msgs, save_message, load_history, save_plan, load_latest_plan
from nutrition import bmr_msj, activity_mult, calorie_target, macro_split
from chatbot import generate_plan, run_chatbot
from usada_api import usda_search_energy_kcal

st.set_page_config(page_title="AI Dietitian", page_icon="🥗")
st.title("AI Dietitian 🥗")


session_id = init_db()


name = st.text_input("Name")
sex = st.radio("Sex", ["Male", "Female"])
age = st.selectbox("Age 🎂", list(range(18, 61)))
height = st.selectbox("Height (cm) 📏", list(range(140, 201)))
weight = st.selectbox("Weight (kg) ⚖️", list(range(30, 201)))
activity = st.radio("Activity 🏃", ["Not active", "Moderately active", "Very active"])
goal = st.radio("Goal 🎯", ["lose", "maintain", "gain"])

if st.button("Generate Plan"):
    plan_text, plan_dict = generate_plan(age, sex, height, weight, activity, goal, session_id)
    save_plan(session_id, plan_dict)
    st.session_state["plan"] = plan_dict
    st.markdown(plan_text)
    st.rerun()

if st.session_state.get("plan"):
    st.subheader("Your Plan")
    st.markdown(st.session_state["plan"]["text"])
    run_chatbot(session_id)
