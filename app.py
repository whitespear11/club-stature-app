import streamlit as st
import math
import json
import io

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

# Player position options
player_positions = [
    "GK", "LB", "LWB", "CB", "RB", "RWB", "CDM", "LM", "CM", "RM",
    "CAM", "CF", "LW", "ST", "RW"
]

# Default positions for starting 11
default_positions = ["GK", "LB", "CB", "CB", "RB", "LM", "CM", "CM", "RM", "ST", "ST"]

def calculate_score(league, country, european, league_tiers):
    league_score = league_tiers.get(league, 1)  # Default to Fourth Division
    # Halve league score if tier is < 3
    if league_tiers.get(league, 1) < 3:
        league_score /= 2
    country_score = country_prestige.get(country, 1)
    european_bonus = 1.0 if european else 0.0
    return league_score + country_score + european_bonus

def calculate_minimum_offer(player_value, stature_diff, is_young):
    """Calculate the minimum offer based on stature difference and player age."""
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

# Initialize session state for Starting 11
if "starting_11" not in st.session_state:
    st.session_state.starting_11 = [
        {"position": default_positions[i], "overall": 0, "wage": 0} for i in range(11)
    ]

# App title
st.title("FIFA Realistic Toolkit")

# Transfer Calculator Section
st.header("Transfer Calculator")
with st.form(key="transfer_form"):
    # Club 1 inputs
    st.subheader("Your Club (Team 1) Details")
    club1_name = st.text_input("Enter Your Club Name (Optional)", key="club1_name")
    club1_league = st.selectbox("Select Your Club League/Division", list(league_tiers.keys()), key="club1_league")
    club1_country = st.selectbox("Select Your Club Country", list(country_prestige.keys()), key="club1_country")
    club1_european = st.checkbox("Your Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club1_european")

    # Club 2 inputs
    st.subheader("Offering Club (Team 2) Details")
    club2_name = st.text_input("Enter Offering Club Name (Optional)", key="club2_name")
    club2_league = st.selectbox("Select Offering Club League/Division", list(league_tiers.keys()), key="club2_league")
    club2_country = st.selectbox("Select Offering Club Country", list(country_prestige.keys()), key="club2_country")
    club2_european = st.checkbox("Offering Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club2_european")

    # Transfer inputs
    st.subheader("Transfer Details")
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
    submit_transfer = st.form_submit_button("Calculate Offer")

# Transfer results
if submit_transfer:
    if player_value > 0:
        # Calculate stature scores
        score1 = calculate_score(club1_league, club1_country, club1_european, league_tiers)
        score2 = calculate_score(club2_league, club2_country, club2_european, league_tiers)
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

# Starting 11 Section
st.header("Starting 11 Overall Calculator")
st.info("Data persists during this browser session. Download as JSON to save or upload to restore.")

# Upload Starting 11 data
uploaded_file = st.file_uploader("Upload Starting 11 JSON", type=["json"])
if uploaded_file:
    try:
        loaded_data = json.load(uploaded_file)
        if isinstance(loaded_data, list) and len(loaded_data) == 11:
            valid = all(
                isinstance(player, dict) and
                "position" in player and
                "overall" in player and
                "wage" in player and
                player["position"] in player_positions and
                isinstance(player["overall"], int) and
                0 <= player["overall"] <= 99 and
                isinstance(player["wage"], int) and
                player["wage"] >= 0
                for player in loaded_data
            )
            if valid:
                st.session_state.starting_11 = loaded_data
                st.success("Starting 11 data loaded successfully.")
            else:
                st.error("Invalid JSON format or data.")
        else:
            st.error("JSON must contain exactly 11 players.")
    except json.JSONDecodeError:
        st.error("Invalid JSON file.")

with st.form(key="starting_11_form"):
    # Column headers
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.write("Position")
    with col2:
        st.write("Overall")
    with col3:
        st.write("Wage (p/w)")

    players = []
    for i in range(11):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            position = st.selectbox(
                "",
                player_positions,
                index=player_positions.index(st.session_state.starting_11[i]["position"]),
                key=f"player_{i}_position"
            )
        with col2:
            overall = st.number_input(
                "",
                min_value=0,
                max_value=99,
                value=st.session_state.starting_11[i]["overall"],
                step=1,
                format="%d",
                key=f"player_{i}_overall"
            )
        with col3:
            wage = st.number_input(
                "",
                min_value=0,
                value=st.session_state.starting_11[i]["wage"],
                step=1000,
                format="%d",
                key=f"player_{i}_wage"
            )
        players.append({"position": position, "overall": overall, "wage": wage})

    # Submit button
    submit_starting_11 = st.form_submit_button("Calculate Team Overall")

# Download Starting 11 data
if st.session_state.starting_11:
    json_str = json.dumps(st.session_state.starting_11, indent=2)
    st.download_button(
        label="Download Starting 11 as JSON",
        data=json_str,
        file_name="starting_11.json",
        mime="application/json"
    )

# Starting 11 results
if submit_starting_11:
    # Validate all overalls and wages are >= 0
    if all(player["overall"] >= 0 and player["wage"] >= 0 for player in players):
        # Update session state
        st.session_state.starting_11 = players

        # Calculate average overall and round down
        total_overall = sum(player["overall"] for player in players)
        average_overall = math.floor(total_overall / 11)
        max_signing_overall = average_overall + 2

        # Calculate wage cap
        max_wage = max(player["wage"] for player in players)
        wage_cap = int(max_wage * 1.2)

        # Display results
        st.write(f"Average Team Overall: {average_overall}")
        st.success(f"Sign players with overall {max_signing_overall} or below.")
        st.write(f"Wage Cap for this season: {wage_cap:,} (p/w)")
    else:
        st.error("All player overall ratings and wages must be non-negative.")