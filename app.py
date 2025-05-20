import streamlit as st

# League tier mapping
league_tiers = {
    "First Division": 10,
    "Second Division": 7,
    "Third Division": 4,
    "Fourth Division": 1
}

# Country prestige mapping
country_prestige = {
    "England": 3, "Spain": 3, "Germany": 3, "Italy": 3, "France": 3,
    "Netherlands": 2, "Portugal": 2, "USA": 2, "Belgium": 2,
    "Other": 1
}

def calculate_score(league, country, european, league_tiers_adjusted):
    league_score = league_tiers_adjusted.get(league, 1)  # Default to Fourth Division
    country_score = country_prestige.get(country, 1)
    european_bonus = 1.0 if european else 0.0
    return league_score + country_score + european_bonus

def calculate_minimum_offer(player_value, stature_diff, is_young):
    """Calculate the minimum offer based on stature difference and player age."""
    # Dynamic base multiplier based on stature difference
    if stature_diff <= 0:  # Team 2's stature is equal or lower
        markup = 85.0
    else:
        # Linear interpolation: 85% at diff=0, 25% at diff=12
        markup = 85.0 - (stature_diff / 12.0) * 60.0
        markup = max(markup, 25.0)  # Cap at 25% for diff > 12
    multiplier = 1.0 + markup / 100.0
    
    # Additional markup for young players (16–21)
    if is_young:
        if stature_diff <= 0 or stature_diff <= 3.5:
            age_markup = 0.2  # +20% of player value
        elif stature_diff <= 7.0:
            age_markup = 0.15  # +15% of player value
        else:
            age_markup = 0.1  # +10% of player value
    else:
        age_markup = 0.0
    
    return player_value * multiplier + player_value * age_markup

# App title
st.title("FIFA Realistic Toolkit")

# Form for inputs
with st.form(key="transfer_form"):
    # Club 1 inputs
    st.header("Your Club (Team 1) Details")
    club1_name = st.text_input("Enter Your Club Name (Optional)", key="club1_name")
    club1_league = st.selectbox("Select Your Club League/Division", list(league_tiers.keys()), key="club1_league")
    club1_country = st.selectbox("Select Your Club Country", list(country_prestige.keys()), key="club1_country")
    club1_european = st.checkbox("Your Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club1_european")

    # Club 2 inputs
    st.header("Offering Club (Team 2) Details")
    club2_name = st.text_input("Enter Offering Club Name (Optional)", key="club2_name")
    club2_league = st.selectbox("Select Offering Club League/Division", list(league_tiers.keys()), key="club2_league")
    club2_country = st.selectbox("Select Offering Club Country", list(country_prestige.keys()), key="club2_country")
    club2_european = st.checkbox("Offering Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club2_european")

    # Transfer inputs
    st.header("Transfer Details")
    player_value = st.number_input(
        "Current Player Value",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="player_value",
        help="Enter value without commas, e.g., 1000000 for 1,000,000"
    )
    is_young = st.checkbox("Player is Aged 16–21", key="is_young")

    # Submit button
    submit_button = st.form_submit_button("Calculate Offer")

# Calculate and display results only if the button is clicked
if submit_button:
    if player_value > 0:
        # Adjust league tiers if either club's league tier is < 3
        league_tiers_adjusted = league_tiers
        if league_tiers[club1_league] < 3 or league_tiers[club2_league] < 3:
            league_tiers_adjusted = {k: v / 2 for k, v in league_tiers.items()}

        score1 = calculate_score(club1_league, club1_country, club1_european, league_tiers_adjusted)
        score2 = calculate_score(club2_league, club2_country, club2_european, league_tiers_adjusted)
        stature_diff = score2 - score1

        # Use default names if not provided
        display_name1 = club1_name if club1_name else "Team 1"
        display_name2 = club2_name if club2_name else "Team 2"

        # Display club stature scores
        st.write(f"**{display_name1} Stature Score:** {score1:.1f}")
        st.write(f"**{display_name2} Stature Score:** {score2:.1f}")

        if score1 > score2:
            st.success(f"{display_name1} has a higher stature by {score1 - score2:.1f} points.")
        elif score2 > score1:
            st.warning(f"{display_name2} has a higher stature by {score2 - score1:.1f} points.")
        else:
            st.info("Both clubs have equal stature.")

        # Calculate and display minimum offer
        minimum_offer = calculate_minimum_offer(player_value, stature_diff, is_young)
        st.success(f"You must accept any offer from {display_name2} of {minimum_offer:,.2f} or higher for this player.")
    else:
        st.info("Please enter a valid player value greater than 0.")