import streamlit as st

# League tier mapping
league_tiers = {
    "First Division": 5,
    "Second Division": 4,
    "Third Division": 3,
    "Fourth Division": 2
}

# Country prestige mapping
country_prestige = {
    "England": 3, "Spain": 3, "Germany": 3, "Italy": 3, "France": 3,
    "Netherlands": 2, "Portugal": 2, "USA": 2, "Belgium": 2,
    "Other": 1
}

def calculate_score(league, country, european):
    league_score = league_tiers.get(league, 2)  # Default to Fourth Division
    country_score = country_prestige.get(country, 1)
    european_bonus = 1.0 if european else 0.0
    return league_score + country_score + european_bonus

def calculate_minimum_offer(player_value, stature_diff, is_young):
    """Calculate the minimum offer based on stature difference and player age."""
    # Base multiplier based on stature difference
    if stature_diff <= 0:  # Team 2's stature is equal or lower
        multiplier = 1.7
    elif stature_diff <= 2.0:
        multiplier = 1.7
    elif stature_diff <= 4.0:
        multiplier = 1.6
    else:
        multiplier = 1.5
    
    # Additional markup for young players (16–21)
    if is_young:
        if stature_diff <= 0 or stature_diff <= 2.0:
            age_markup = 0.2  # +20% of player value
        elif stature_diff <= 4.0:
            age_markup = 0.15  # +15% of player value
        else:
            age_markup = 0.1  # +10% of player value
    else:
        age_markup = 0.0
    
    return player_value * multiplier + player_value * age_markup

# App title
st.title("FIFA Career Mode Club Stature Comparator")

# Club 1 inputs
st.header("Your Club (Team 1) Details")
club1_name = st.text_input("Enter Your Club Name", key="club1_name")
club1_league = st.selectbox("Select Your Club League/Division", list(league_tiers.keys()), key="club1_league")
club1_country = st.selectbox("Select Your Club Country", list(country_prestige.keys()), key="club1_country")
club1_european = st.checkbox("Your Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club1_european")

# Club 2 inputs
st.header("Offering Club (Team 2) Details")
club2_name = st.text_input("Enter Offering Club Name", key="club2_name")
club2_league = st.selectbox("Select Offering Club League/Division", list(league_tiers.keys()), key="club2_league")
club2_country = st.selectbox("Select Offering Club Country", list(country_prestige.keys()), key="club2_country")
club2_european = st.checkbox("Offering Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club2_european")

# Transfer inputs
st.header("Transfer Details")
player_value = st.number_input("Current Player Value (£)", min_value=0.0, step=1000.0, format="%.2f", key="player_value")
offered_bid = st.number_input("Team 2 Offered Bid (£)", min_value=0.0, step=1000.0, format="%.2f", key="offered_bid")
is_young = st.checkbox("Player is Aged 16–21", key="is_young")

# Calculate scores and offer
if club1_name and club2_name and player_value > 0:
    score1 = calculate_score(club1_league, club1_country, club1_european)
    score2 = calculate_score(club2_league, club2_country, club2_european)
    stature_diff = score2 - score1

    # Display club stature scores
    st.write(f"**{club1_name} Stature Score:** {score1:.1f}")
    st.write(f"**{club2_name} Stature Score:** {score2:.1f}")

    if score1 > score2:
        st.success(f"{club1_name} has a higher stature by {score1 - score2:.1f} points.")
    elif score2 > score1:
        st.warning(f"{club2_name} has a higher stature by {score2 - score1:.1f} points.")
    else:
        st.info("Both clubs have equal stature.")

    # Calculate and display minimum offer
    minimum_offer = calculate_minimum_offer(player_value, stature_diff, is_young)
    st.write(f"**Minimum Acceptable Offer**: £{minimum_offer:,.2f}")

    # Check if the offer must be accepted
    if offered_bid >= minimum_offer:
        st.success(f"The offered bid of £{offered_bid:,.2f} meets or exceeds the minimum acceptable offer of £{minimum_offer:,.2f}. You must accept this offer.")
    else:
        st.warning(f"The offered bid of £{offered_bid:,.2f} is below the minimum acceptable offer of £{minimum_offer:,.2f}. You can reject this offer.")
elif not club1_name or not club2_name:
    st.info("Please enter names for both clubs to compare.")
elif player_value <= 0:
    st.info("Please enter a valid player value greater than 0.")