import streamlit as st
import math
import json
import io

# Apply custom CSS for green download buttons and info box styling
st.markdown(
    """
    <style>
    button[kind="primary"] {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
    }
    button[kind="primary"]:hover {
        background-color: #218838;
        color: white;
    }
    .custom-info {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .custom-info p {
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
    """Calculate the minimum offer for selling based on stature difference and player age."""
    if stature_diff <= 0:  # Team 2's stature is equal or lower
        markup = 65.0
    else:
        # Linear interpolation: 65% at diff=0, 15% at diff=12
        markup = 65.0 - (stature_diff / 12.0) * 50.0
        markup = max(markup, 15.0)  # Cap at 15% for diff > 12
    multiplier = 1.0 + markup / 100.0
    
    # Additional markup for young players (16–21)
    if is_young:
        if stature_diff <= 0 or stature_diff <= 3.5:
            age_markup = 0.25  # +25% of player value
        elif stature_diff <= 7.0:
            age_markup = 0.18  # +18% of player value
        else:
            age_markup = 0.12  # +12% of player value
    else:
        age_markup = 0.0
    
    return player_value * multiplier + player_value * age_markup

def calculate_starting_bid(player_value, player_overall, player_age, average_team_overall=None):
    """Calculate the starting bid for buying based on age and overall relative to team average."""
    if player_age >= 16 and player_age <= 24:
        if average_team_overall is None:
            return player_value * 1.75, False
        elif player_overall > average_team_overall:
            return player_value * 2.00, True
        elif player_overall == average_team_overall:
            return player_value * 1.75, True
        else:
            return player_value * 1.50, True
    elif player_age >= 25 and player_age <= 29:
        if average_team_overall is None:
            return player_value * 1.75, False
        elif player_overall > average_team_overall:
            return player_value * 1.40, True
        elif player_overall == average_team_overall:
            return player_value * 1.30, True
        else:
            return player_value * 1.10, True
    else:
        # Default case for ages outside 16-29
        return player_value * 1.30, average_team_overall is not None

def calculate_proportional_wage(player_overall, starting_11):
    """Calculate a proportional wage based on the player's overall and Starting 11 wages, rounded up to nearest 100."""
    # Filter players with valid overall and wage
    valid_players = [
        player for player in starting_11
        if player["overall"] > 0 and player["wage"] > 0
    ]
    
    if not valid_players:
        return None, "No valid Starting 11 data with non-zero wages and overalls."
    
    # Calculate average wage-to-overall ratio
    ratios = [player["wage"] / player["overall"] for player in valid_players]
    avg_ratio = sum(ratios) / len(ratios)
    
    # Calculate proportional wage and round up to nearest 100
    wage = player_overall * avg_ratio
    wage = math.ceil(wage / 100) * 100
    return wage, None

# Initialize session state
if "starting_11" not in st.session_state:
    st.session_state.starting_11 = [
        {"position": default_positions[i], "overall": 0, "wage": 0} for i in range(11)
    ]
if "average_team_overall" not in st.session_state:
    st.session_state.average_team_overall = None
if "club_details" not in st.session_state:
    st.session_state.club_details = {
        "name": "",
        "league": "First Division",
        "country": "England",
        "european": False
    }
if "club_details_updated" not in st.session_state:
    st.session_state.club_details_updated = False
if "pending_club_details" not in st.session_state:
    st.session_state.pending_club_details = None
if "club_name" not in st.session_state:
    st.session_state.club_name = st.session_state.club_details["name"]
if "form_league" not in st.session_state:
    st.session_state.form_league = st.session_state.club_details["league"]
if "club_country" not in st.session_state:
    st.session_state.club_country = st.session_state.club_details["country"]
if "club_european" not in st.session_state:
    st.session_state.club_european = st.session_state.club_details["european"]

# App title
st.title("FIFA Realistic Toolkit")

# Your Club Details Section
st.header("Your Club Details")
st.markdown(
    """
    <div class="custom-info">
        <p>Hello and thank you for using FIFA Realistic Toolkit! This toolkit is designed to make FIFA career mode more realistic by adding some guidelines on transfers and wages.</p>
        <p>Please fill out your team details below and your starting 11, they can be saved and uploaded.</p>
        <p>If you enjoy this tool please consider <a href="https://buymeacoffee.com/whitespear11" target="_blank">buying me a coffee</a>.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Upload Combined Club Details and Starting 11 data
uploaded_file = st.file_uploader("Upload Club and Starting 11 JSON", type=["json"], key="combined_upload")
# Show disclaimer only if a file is uploaded
if st.session_state.get("combined_upload") is not None:
    st.warning("Note: If you have uploaded a JSON file, please remove it using the clear button (X) in the uploader before making changes to the form fields below.")
if uploaded_file:
    try:
        loaded_data = json.load(uploaded_file)
        # Validate club_details
        club_valid = (
            isinstance(loaded_data.get("club_details"), dict) and
            all(key in loaded_data["club_details"] for key in ["name", "league", "country", "european"]) and
            isinstance(loaded_data["club_details"]["name"], str) and
            loaded_data["club_details"]["league"] in league_tiers and
            loaded_data["club_details"]["country"] in country_prestige and
            isinstance(loaded_data["club_details"]["european"], bool)
        )
        # Validate starting_11
        starting_11_valid = (
            isinstance(loaded_data.get("starting_11"), list) and
            len(loaded_data["starting_11"]) == 11 and
            all(
                isinstance(player, dict) and
                all(key in player for key in ["position", "overall", "wage"]) and
                player["position"] in player_positions and
                isinstance(player["overall"], int) and
                0 <= player["overall"] <= 99 and
                isinstance(player["wage"], int) and
                player["wage"] >= 0
                for player in loaded_data["starting_11"]
            )
        )
        if club_valid and starting_11_valid:
            # Update session state
            st.session_state.club_details = loaded_data["club_details"]
            st.session_state.starting_11 = loaded_data["starting_11"]
            st.session_state.club_details_updated = True
            st.session_state.pending_club_details = None
            # Update club details form widget states
            st.session_state["club_name"] = loaded_data["club_details"]["name"]
            st.session_state["form_league"] = loaded_data["club_details"]["league"]
            st.session_state["club_country"] = loaded_data["club_details"]["country"]
            st.session_state["club_european"] = loaded_data["club_details"]["european"]
            # Update starting 11 form widget states
            for i, player in enumerate(loaded_data["starting_11"]):
                st.session_state[f"player_{i}_position"] = player["position"]
                st.session_state[f"player_{i}_overall"] = player["overall"]
                st.session_state[f"player_{i}_wage"] = player["wage"]
            # Recalculate average team overall
            total_overall = sum(player["overall"] for player in loaded_data["starting_11"])
            st.session_state.average_team_overall = math.floor(total_overall / 11)
            st.success(
                f"Club details and Starting 11 loaded successfully. "
                f/tomorrow, May 22, 2025.

Let me know if you need further refinements (e.g., adjusting the info box styling, adding more features) or assistance with upgrading Streamlit! Thanks for providing the detailed error, and I’m glad we’re making progress on the app.