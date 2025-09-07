import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from usada_api import usda_search_energy_kcal
from db import save_message, load_history, load_latest_plan
from nutrition import bmr_msj, activity_mult, calorie_target, macro_split


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PLAN = (
    "You are a nutrition coach. Using the given facts, produce a concise daily plan. "
    "Output exactly 5 bullet points: (1) calorie target, (2) macro targets, "
    "(3) three meal ideas with grams, (4) one snack, (5) two quick tips."
)

def generate_plan(age, sex, height, weight, activity, goal, session_id):
    bmr = bmr_msj(int(age), sex, int(height), float(weight))
    tdee = bmr * activity_mult(activity)
    cals = calorie_target(tdee, goal)
    P, F, C = macro_split(float(weight), cals, goal)

    user_facts = (
        f"Facts:\n"
        f"- Age: {age}, Sex: {sex}, Height: {height} cm, Weight: {weight} kg\n"
        f"- Activity: {activity}, Goal: {goal}\n"
        f"- Targets: {cals} kcal/day; Protein {P} g; Fat {F} g; Carbs {C} g"
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PLAN},
            {"role": "user", "content": user_facts},
        ],
    )
    plan_text = resp.choices[0].message.content

    plan_dict = {
        "targets": {
            "cal": cals, "p": P, "f": F, "c": C,
            "age": age, "sex": sex, "h": height, "w": weight,
            "level": activity, "goal": goal
        },
        "text": plan_text
    }
    return plan_text, plan_dict

def build_context(session_id):
    msgs = [
        {
            "role": "system",
            "content": (
                "You are a helpful nutrition coach. "
                "Use the user's saved plan, their chat history, "
                "and any food nutrition lookups to answer precisely."
            ),
        }
    ]

  
    row = load_latest_plan(session_id)
    if row:
        msgs.append({"role": "system", "content": f"User plan:\n{row[0]}"})

    
    for role, content in load_history(session_id, limit=8):
        msgs.append({"role": role, "content": content})

   
    if msgs and msgs[-1]["role"] == "user":
        last_user = msgs[-1]["content"]
        



        if any(k in last_user.lower() for k in ["calorie", "protein", "fat", "carb", "kcal"]):
            words = last_user.split()
            food = words[-1]  # take last word as candidate
            res = usda_search_energy_kcal(food)
            if res:
                desc, kcal = res
                msgs.append(
                    {
                        "role": "system",
                        "content": f"USDA lookup for '{food}': {desc}, {kcal} kcal per 100g.",
                    }
                )

    return msgs

def run_chatbot(session_id):
   
    for m in st.session_state.get("messages", []):
        if m["role"] != "system":
            st.chat_message("user" if m["role"] == "user" else "assistant").write(m["content"])

   
    user_text = st.chat_input("Ask anything.")
    if user_text:
        st.session_state.setdefault("messages", []).append({"role": "user", "content": user_text})
        save_message(session_id, "user", user_text)

        context = build_context(session_id)
       
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=context,
            stream=True
        )
        assistant_text = st.write_stream(stream)

        st.session_state["messages"].append({"role": "assistant", "content": assistant_text})
        save_message(session_id, "assistant", assistant_text)

        st.rerun()
