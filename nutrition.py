def bmr_msj(age, sex, height_cm, weight_kg):
    return 10*weight_kg + 6.25*height_cm - 5*age + (5 if sex.lower().startswith("m") else -161)

def activity_mult(level):
    return {"Not active":1.2, "Moderately active":1.55, "Very active":1.725}.get(level, 1.2)

def calorie_target(tdee, goal):
    return round(tdee * {"lose":0.80, "maintain":1.0, "gain":1.15}.get(goal, 1.0))

def macro_split(weight_kg, calories, goal):
    p_per_kg = {"lose":1.8, "maintain":1.6, "gain":2.0}.get(goal, 1.6)
    protein_g = round(p_per_kg * weight_kg)
    fat_g = round(0.8 * weight_kg)
    carbs_g = max(0, round((calories - protein_g*4 - fat_g*9)/4))
    return protein_g, fat_g, carbs_g
