
import streamlit as st
import pandas as pd

# Load club data
df = pd.read_csv("club_data_sample.csv")

# League and country tier data
league_tiers = {
    "Premier League": 5, "La Liga": 5, "Bundesliga": 5,
    "Serie A": 5, "Ligue 1": 5, "Eredivisie": 4,
    "EFL Championship": 4
}

country_prestige = {
    "England": 3, "Spain": 3, "Germany": 3, "Italy": 3,
    "France": 3, "Netherlands": 2
}

def calculate_score(row):
    league_score = league_tiers.get(row["League"], 1)
    country_score = country_prestige.get(row["Country"], 1)
    return league_score + row["Reputation"] + country_score + row["European Bonus"] + row["Trophy Bonus"]

# App title
st.title("Club Stature Comparator")

# Dropdowns
club1_name = st.selectbox("Select Your Club", df["Club Name"])
club2_name = st.selectbox("Select Other Club", df["Club Name"])

# Get club rows
club1 = df[df["Club Name"] == club1_name].iloc[0]
club2 = df[df["Club Name"] == club2_name].iloc[0]

# Calculate scores
score1 = calculate_score(club1)
score2 = calculate_score(club2)

# Display results
st.write(f"**{club1_name} Score:** {score1}")
st.write(f"**{club2_name} Score:** {score2}")

if score1 > score2:
    st.success(f"{club1_name} has a higher stature by {score1 - score2:.1f} points.")
elif score2 > score1:
    st.warning(f"{club2_name} has a higher stature by {score2 - score1:.1f} points.")
else:
    st.info("Both clubs have equal stature.")
