import streamlit as st

# Initialize session state for player value
if "player_value" not in st.session_state:
    st.session_state.player_value = 0.0

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

def calculate_score(league, country, european):
    league_score = league_tiers.get(league, 1)  # Default to Fourth Division
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
st.title("FIFA Career Mode Club Stature Comparator")

# Increment buttons for player value (outside the form)
st.subheader("Adjust Player Value")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("+1k"):
        st.session_state.player_value += 1000.0
with col2:
    if st.button("+10k"):
        st.session_state.player_value += 10000.0
with col3:
    if st.button("+100k"):
        st.session_state.player_value += 100000.0
with col4:
    if st.button("+1m"):
        st.session_state.player_value += 1000000.0
with col5:
    if st.button("+10m"):
        st.session_state.player_value += 10000000.0

# Form for inputs
with st.form(key="transfer_form"):
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
    # Player value input synced with session state
    st.session_state.player_value = st.number_input(
        "Current Player Value (£)",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        value=st.session_state.player_value,
        help="Enter value without commas, e.g., 1000000 for £1,000,000",
        key="player_value"
    )
    is_young = st.checkbox("Player is Aged 16–21", key="is_young")

    # Submit button
    submit_button = st.form_submit_button("Calculate Offer")

# Calculate and display results only if the button is clicked
if submit_button:
    if club1_name and club2_name and st.session_state.player_value > 0:
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
        minimum_offer = calculate_minimum_offer(st.session_state.player_value, stature_diff, is_young)
        st.success(f"You must accept any offer from {club2_name} of £{minimum_offer:,.2f} or higher for this player.")
    elif not club1_name or not club2_name:
        st.info("Please enter names for both clubs to compare.")
    elif st.session_state.player_value <= 0:
        st.info("Please enter a valid player value greater than 0.")