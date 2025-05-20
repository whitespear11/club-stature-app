import streamlit as st

# League tier mapping
league_tiers = {
    "First Division (e.g., Premier League, La Liga, Bundesliga, Serie A, Ligue 1)": 5,
    "Second Division (e.g., Eredivisie, Liga Portugal, EFL Championship, MLS)": 4,
    "Third Division (e.g., Belgian Pro League, Swiss Super League, 2. Bundesliga)": 3,
    "Lower Second Tiers (e.g., Serie B, Ligue 2)": 2,
    "Lesser-Known Leagues (e.g., Polish, Irish)": 1
}

# Country prestige mapping
country_prestige = {
    "England": 3, "Spain": 3, "Germany": 3, "Italy": 3, "France": 3,
    "Netherlands": 2, "Portugal": 2, "USA": 2, "Belgium": 2,
    "Other": 1
}

def calculate_score(league, country, european):
    league_score = league_tiers.get(league, 1)
    country_score = country_prestige.get(country, 1)
    european_bonus = 1.0 if european else 0.0
    return league_score + country_score + european_bonus

# App title
st.title("Club Stature Comparator")

# Club 1 inputs
st.header("Club 1 Details")
club1_name = st.text_input("Enter Club 1 Name", key="club1_name")
club1_league = st.selectbox("Select Club 1 League/Division", list(league_tiers.keys()), key="club1_league")
club1_country = st.selectbox("Select Club 1 Country", list(country_prestige.keys()), key="club1_country")
club1_european = st.checkbox("Club 1 Participates in European Competitions (e.g., Champions League, Europa League)", key="club1_european")

# Club 2 inputs
st.header("Club 2 Details")
club2_name = st.text_input("Enter Club 2 Name", key="club2_name")
club2_league = st.selectbox("Select Club 2 League/Division", list(league_tiers.keys()), key="club2_league")
club2_country = st.selectbox("Select Club 2 Country", list(country_prestige.keys()), key="club2_country")
club2_european = st.checkbox("Club 2 Participates in European Competitions (e.g., Champions League, Europa League)", key="club2_european")

# Calculate scores
if club1_name and club2_name:
    score1 = calculate_score(club1_league, club1_country, club1_european)
    score2 = calculate_score(club2_league, club2_country, club2_european)

    # Display results
    st.write(f"**{club1_name} Score:** {score1:.1f}")
    st.write(f"**{club2_name} Score:** {score2:.1f}")

    if score1 > score2:
        st.success(f"{club1_name} has a higher stature by {score1 - score2:.1f} points.")
    elif score2 > score1:
        st.warning(f"{club2_name} has a higher stature by {score2 - score1:.1f} points.")
    else:
        st.info("Both clubs have equal stature.")
else:
    st.info("Please enter names for both clubs to compare.")