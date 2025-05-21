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

# App title
st.title("FIFA Realistic Toolkit")

# Your Club Details Section
st.header("Your Club Details")
st.info("Enter your club details to use in the selling calculator. Save and load both club details and Starting 11 in a single JSON file.")

# Display current stature score
current_stature = calculate_score(
    st.session_state.club_details["league"],
    st.session_state.club_details["country"],
    st.session_state.club_details["european"],
    league_tiers
)
st.write(f"Current Club Stature Score: {current_stature:.1f}")

# Upload Combined Club Details and Starting 11 data
uploaded_file = st.file_uploader("Upload Club and Starting 11 JSON", type=["json"], key="combined_upload")
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
            # Update session state without clearing form widget states
            st.session_state.club_details = loaded_data["club_details"]
            st.session_state.starting_11 = loaded_data["starting_11"]
            st.session_state.club_details_updated = True
            st.session_state.pending_club_details = None
            # Recalculate average team overall
            total_overall = sum(player["overall"] for player in loaded_data["starting_11"])
            st.session_state.average_team_overall = math.floor(total_overall / 11)
            st.success(
                f"Club details and Starting 11 loaded successfully. "
                f"Club: Name: {loaded_data['club_details']['name'] or 'None'}, "
                f"League: {loaded_data['club_details']['league']}, "
                f"Country: {loaded_data['club_details']['country']}, "
                f"European: {loaded_data['club_details']['european']}. "
                f"Stature score: {calculate_score(loaded_data['club_details']['league'], loaded_data['club_details']['country'], loaded_data['club_details']['european'], league_tiers):.1f}"
            )
            # Update form widget states to reflect loaded data
            st.session_state["club_name"] = loaded_data["club_details"]["name"]
            st.session_state["form_league"] = loaded_data["club_details"]["league"]
            st.session_state["club_country"] = loaded_data["club_details"]["country"]
            st.session_state["club_european"] = loaded_data["club_details"]["european"]
            for i, player in enumerate(loaded_data["starting_11"]):
                st.session_state[f"player_{i}_position"] = player["position"]
                st.session_state[f"player_{i}_overall"] = player["overall"]
                st.session_state[f"player_{i}_wage"] = player["wage"]
        else:
            st.error("Invalid JSON format or data. Ensure it contains valid club_details and starting_11 fields.")
    except json.JSONDecodeError:
        st.error("Invalid JSON file.")

# Download Combined Club Details and Starting 11 data (top button)
if st.session_state.club_details and st.session_state.starting_11:
    combined_data = {
        "club_details": st.session_state.club_details,
        "starting_11": st.session_state.starting_11
    }
    json_str = json.dumps(combined_data, indent=2)
    st.download_button(
        label="Download Club Details and Starting 11 as JSON",
        data=json_str,
        file_name="team_data.json",
        mime="application/json",
        key="download_top"
    )

with st.form(key="club_details_form"):
    club_name = st.text_input(
        "Enter Your Club Name (Optional)",
        value=st.session_state.get("club_name", st.session_state.club_details["name"]),
        key="club_name"
    )
    club_league = st.selectbox(
        "Select Your Club League/Division",
        list(league_tiers.keys()),
        index=list(league_tiers.keys()).index(st.session_state.get("form_league", st.session_state.club_details["league"])),
        key="form_league"
    )
    club_country = st.selectbox(
        "Select Your Club Country",
        list(country_prestige.keys()),
        index=list(country_prestige.keys()).index(st.session_state.get("club_country", st.session_state.club_details["country"])),
        key="club_country"
    )
    club_european = st.checkbox(
        "Your Club Participates in European Competitions (e.g., Champions League, Europa League)",
        value=st.session_state.get("club_european", st.session_state.club_details["european"]),
        key="club_european"
    )
    
    # Submit button
    submit_club_details = st.form_submit_button("Save Club Details")

# Handle form submission
if submit_club_details:
    # Update session state with form values
    st.session_state.club_details = {
        "name": st.session_state["club_name"],
        "league": st.session_state["form_league"],
        "country": st.session_state["club_country"],
        "european": st.session_state["club_european"]
    }
    st.session_state.club_details_updated = True
    st.session_state.pending_club_details = None
    # Force re-render to update UI
    st.rerun()

# Display success message if club details were updated
if st.session_state.club_details_updated:
    club_details = st.session_state.club_details
    new_stature = calculate_score(club_details["league"], club_details["country"], club_details["european"], league_tiers)
    st.success(
        f"Club details saved: Name: {club_details['name'] or 'None'}, "
        f"League: {club_details['league']}, "
        f"Country: {club_details['country']}, "
        f"European: {club_details['european']}. "
        f"New stature score: {new_stature:.1f}"
    )

# Starting 11 Section
st.header("Starting 11 Overall Calculator")
st.info("Enter your starting 11 details. Save and load both club details and Starting 11 in a single JSON file.")

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
                index=player_positions.index(st.session_state.get(f"player_{i}_position", st.session_state.starting_11[i]["position"])),
                key=f"player_{i}_position"
            )
        with col2:
            overall = st.number_input(
                "",
                min_value=0,
                max_value=99,
                value=st.session_state.get(f"player_{i}_overall", st.session_state.starting_11[i]["overall"]),
                step=1,
                format="%d",
                key=f"player_{i}_overall"
            )
        with col3:
            wage = st.number_input(
                "",
                min_value=0,
                value=st.session_state.get(f"player_{i}_wage", st.session_state.starting_11[i]["wage"]),
                step=1000,
                format="%d",
                key=f"player_{i}_wage"
            )
        players.append({"position": position, "overall": overall, "wage": wage})

    # Submit button
    submit_starting_11 = st.form_submit_button("Calculate Team Overall")

# Download Combined Club Details and Starting 11 data (bottom button)
if st.session_state.club_details and st.session_state.starting_11:
    combined_data = {
        "club_details": st.session_state.club_details,
        "starting_11": st.session_state.starting_11
    }
    json_str = json.dumps(combined_data, indent=2)
    st.download_button(
        label="Download Club Details and Starting 11 as JSON",
        data=json_str,
        file_name="team_data.json",
        mime="application/json",
        key="download_bottom"
    )

# Starting 11 results
if submit_starting_11:
    # Validate all overalls and wages are >= 0
    if all(player["overall"] >= 0 and player["wage"] >= 0 for player in players):
        # Update session state
        st.session_state.starting_11 = players
        # Clear widget states to ensure form reflects new values
        for i in range(11):
            for key in [f"player_{i}_position", f"player_{i}_overall", f"player_{i}_wage"]:
                st.session_state.pop(key, None)
        # Set widget values to new data
        for i, player in enumerate(players):
            st.session_state[f"player_{i}_position"] = player["position"]
            st.session_state[f"player_{i}_overall"] = player["overall"]
            st.session_state[f"player_{i}_wage"] = player["wage"]

        # Calculate average overall and round down
        total_overall = sum(player["overall"] for player in players)
        average_overall = math.floor(total_overall / 11)
        st.session_state.average_team_overall = average_overall
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

# Selling Transfer Calculator Section
st.header("Transfer Calculator (Selling)")
with st.form(key="selling_transfer_form"):
    # Club 2 inputs (Offering Club)
    st.subheader("Offering Club Details")
    club2_name_sell = st.text_input("Enter Offering Club Name (Optional)", key="club2_name_sell")
    club2_league_sell = st.selectbox("Select Offering Club League/Division", list(league_tiers.keys()), key="club2_league_sell")
    club2_country_sell = st.selectbox("Select Offering Club Country", list(country_prestige.keys()), key="club2_country_sell")
    club2_european_sell = st.checkbox("Offering Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club2_european_sell")

    # Transfer inputs
    st.subheader("Transfer Details")
    player_value_sell = st.number_input(
        "Current Player Value",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="player_value_sell",
        help="Enter value without commas, e.g., 1000000 for 1,000,000"
    )
    is_young_sell = st.checkbox("Player is Aged 16–21", key="is_young_sell")

    # Submit button
    submit_selling_transfer = st.form_submit_button("Calculate Selling Offer")

# Selling transfer results
if submit_selling_transfer:
    if player_value_sell > 0:
        # Fetch current club details from session state
        club_details = st.session_state.club_details
        # Calculate stature scores
        score1 = calculate_score(
            club_details["league"],
            club_details["country"],
            club_details["european"],
            league_tiers
        )
        score2 = calculate_score(club2_league_sell, club2_country_sell, club2_european_sell, league_tiers)
        stature_diff = score2 - score1

        # Use default names if not provided
        display_name1 = club_details["name"] if club_details["name"] else "Your Club"
        display_name2 = club2_name_sell if club2_name_sell else "Offering Club"

        # Display club details used for calculation
        st.write(f"**Your Club Details Used:** Name: {display_name1}, League: {club_details['league']}, Country: {club_details['country']}, European: {club_details['european']}")
        # Display club stature scores
        st.write(f"**{display_name1} Stature Score:** {score1:.1f}")
        st.write(f"**{display_name2} Stature Score:** {score2:.1f}")

        if score1 > score2:
            st.success(f"{display_name1} has a higher stature by {score1 - score2:.1f} points.")
        elif score2 > score1:
            st.warning(f"{display_name2} has a higher stature by {score2 - score1:.1f} points.")
        else:
            st.info("Both clubs have equal stature.")

        # Calculate and round up minimum offer to nearest 1000
        minimum_offer = calculate_minimum_offer(player_value_sell, stature_diff, is_young_sell)
        minimum_offer = math.ceil(minimum_offer / 1000) * 1000
        st.success(f"You must accept any offer from {display_name2} of {minimum_offer:,.0f} or higher for this player.")
    else:
        st.error("Please enter a valid player value greater than 0.")

# Buying Transfer Calculator Section
st.header("Transfer Calculator (Buying)")
with st.form(key="buying_transfer_form"):
    # Transfer inputs
    st.subheader("Player Details")
    player_value_buy = st.number_input(
        "Current Player Value",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="player_value_buy",
        help="Enter value without commas, e.g., 1000000 for 1,000,000"
    )
    player_overall_buy = st.number_input(
        "Player Overall Rating",
        min_value=0,
        max_value=99,
        step=1,
        format="%d",
        key="player_overall_buy"
    )
    player_age_buy = st.number_input(
        "Player Age",
        min_value=16,
        max_value=40,
        step=1,
        format="%d",
        key="player_age_buy"
    )

    # Submit button
    submit_buying_transfer = st.form_submit_button("Calculate Starting Bid and Wage")

# Buying transfer results
if submit_buying_transfer:
    if player_value_buy > 0 and player_overall_buy > 0:
        # Calculate and round up starting bid to nearest 1000
        starting_bid, is_accurate = calculate_starting_bid(
            player_value_buy,
            player_overall_buy,
            player_age_buy,
            st.session_state.average_team_overall
        )
        starting_bid = resolve the error you're encountering, I'll need to address both the new `StreamlitAPIException` and the previously reported `SyntaxError: invalid syntax` at line 17, as they seem to relate to different versions of the `app.py` file you've tried. Let's tackle both issues systematically to provide a fully corrected file that resolves the current error and prevents the previous syntax error.

### Addressing the Current Error: StreamlitAPIException
The `StreamlitAPIException` occurs at line 255 in the form submission block for the "Your Club Details" form, where the code attempts to modify `st.session_state["club_name"]` after the `st.text_input` widget with `key="club_name"` is instantiated:

```python
st.session_state["club_name"] = st.session_state.club_details["name"]
```

**Root Cause**: Streamlit does not allow direct modification of session state keys associated with active widgets (e.g., `club_name`, `form_league`, `club_country`, `club_european`) within the same script run after the widgets are created. This is because Streamlit ties these keys to the widget's state, and altering them programmatically can lead to inconsistent UI behavior. The error occurs in the form submission block when trying to sync the widget states with `st.session_state.club_details` after updating the latter.

**Solution**: Remove the direct assignments to widget-associated session state keys (`st.session_state["club_name"]`, etc.) in the form submission block. Instead, rely on Streamlit's form submission to update `st.session_state.club_details` and use `st.rerun()` to refresh the UI, allowing the widgets to pick up the updated values from `st.session_state.club_details` in the next script run. The form widgets are already initialized to reflect `st.session_state.club_details` via their `value` parameters, so explicit reassignment is unnecessary.

The corrected form submission block should be:

```python
if submit_club_details:
    # Update session state with form values
    st.session_state.club_details = {
        "name": st.session_state["club_name"],
        "league": st.session_state["form_league"],
        "country": st.session_state["club_country"],
        "european": st.session_state["club_european"]
    }
    st.session_state.club_details_updated = True
    st.session_state.pending_club_details = None
    # Force re-render to update UI
    st.rerun()
```

### Addressing the Previous Error: SyntaxError at Line 17
The `SyntaxError: invalid syntax` at line 17 was reported earlier for the `country_prestige` dictionary:

```python
country_prestige = {
    appe
    "Netherlands": 2, "Portugal": 2, "USA": 2, "Belgium": 2,
    "Other": 1
}
```

**Root Cause**: The `appe` token is invalid (likely a typo from code generation or editing) and caused the dictionary to be syntactically incorrect. Additionally, the dictionary was incomplete, missing keys like `"England": 3`, etc.

**Solution**: The corrected `country_prestige` dictionary was provided in the latest version of `app.py`, and it should be:

```python
country_prestige = {
    "England": 3, "Spain": 3, "Germany": 3, "Italy": 3, "France": 3,
    "Netherlands": 2, "Portugal": 2, "USA": 2, "Belgium": 2,
    "Other": 1
}
```

### Additional Context
- **Python 3.13**: The traceback indicates you're using Python 3.13, which is newer than the previously mentioned Python 3.12. Streamlit should be compatible with Python 3.13 if you're using a recent version (e.g., Streamlit 1.30+), but ensure your Streamlit installation is up to date:
  ```bash
  pip install --upgrade streamlit
  ```
- **Previous Fixes**: The latest `app.py` already includes fixes for:
  - Replacing `st.experimental_rerun()` with `st.rerun()`.
  - Correcting the `club_league` `st.selectbox` key (`key="form_league"`).
  - Ensuring form submissions override JSON uploads and update the stature score correctly.
  - Fixing the `country_prestige` dictionary syntax.

### Corrected Code
Below is the fully corrected `app.py` file, incorporating:
- The fix for the `StreamlitAPIException` by removing direct assignments to widget-associated session state keys in the form submission block.
- The corrected `country_prestige` dictionary to prevent the `SyntaxError`.
- All previous fixes to ensure form submissions update the stature score and override JSON uploads.

<xaiArtifact artifact_id="774a0959-7521-45cb-82c9-565b94fe4649" artifact_version_id="8d779941-a478-4390-91b4-572fc623f8bf" title="app.py" contentType="text/python">
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

# App title
st.title("FIFA Realistic Toolkit")

# Your Club Details Section
st.header("Your Club Details")
st.info("Enter your club details to use in the selling calculator. Save and load both club details and Starting 11 in a single JSON file.")

# Display current stature score
current_stature = calculate_score(
    st.session_state.club_details["league"],
    st.session_state.club_details["country"],
    st.session_state.club_details["european"],
    league_tiers
)
st.write(f"Current Club Stature Score: {current_stature:.1f}")

# Upload Combined Club Details and Starting 11 data
uploaded_file = st.file_uploader("Upload Club and Starting 11 JSON", type=["json"], key="combined_upload")
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
            # Update session state without clearing form widget states
            st.session_state.club_details = loaded_data["club_details"]
            st.session_state.starting_11 = loaded_data["starting_11"]
            st.session_state.club_details_updated = True
            st.session_state.pending_club_details = None
            # Recalculate average team overall
            total_overall = sum(player["overall"] for player in loaded_data["starting_11"])
            st.session_state.average_team_overall = math.floor(total_overall / 11)
            st.success(
                f"Club details and Starting 11 loaded successfully. "
                f"Club: Name: {loaded_data['club_details']['name'] or 'None'}, "
                f"League: {loaded_data['club_details']['league']}, "
                f"Country: {loaded_data['club_details']['country']}, "
                f"European: {loaded_data['club_details']['european']}. "
                f"Stature score: {calculate_score(loaded_data['club_details']['league'], loaded_data['club_details']['country'], loaded_data['club_details']['european'], league_tiers):.1f}"
            )
            # Update form widget states to reflect loaded data
            st.session_state["club_name"] = loaded_data["club_details"]["name"]
            st.session_state["form_league"] = loaded_data["club_details"]["league"]
            st.session_state["club_country"] = loaded_data["club_details"]["country"]
            st.session_state["club_european"] = loaded_data["club_details"]["european"]
            for i, player in enumerate(loaded_data["starting_11"]):
                st.session_state[f"player_{i}_position"] = player["position"]
                st.session_state[f"player_{i}_overall"] = player["overall"]
                st.session_state[f"player_{i}_wage"] = player["wage"]
        else:
            st.error("Invalid JSON format or data. Ensure it contains valid club_details and starting_11 fields.")
    except json.JSONDecodeError:
        st.error("Invalid JSON file.")

# Download Combined Club Details and Starting 11 data (top button)
if st.session_state.club_details and st.session_state.starting_11:
    combined_data = {
        "club_details": st.session_state.club_details,
        "starting_11": st.session_state.starting_11
    }
    json_str = json.dumps(combined_data, indent=2)
    st.download_button(
        label="Download Club Details and Starting 11 as JSON",
        data=json_str,
        file_name="team_data.json",
        mime="application/json",
        key="download_top"
    )

with st.form(key="club_details_form"):
    club_name = st.text_input(
        "Enter Your Club Name (Optional)",
        value=st.session_state.get("club_name", st.session_state.club_details["name"]),
        key="club_name"
    )
    club_league = st.selectbox(
        "Select Your Club League/Division",
        list(league_tiers.keys()),
        index=list(league_tiers.keys()).index(st.session_state.get("form_league", st.session_state.club_details["league"])),
        key="form_league"
    )
    club_country = st.selectbox(
        "Select Your Club Country",
        list(country_prestige.keys()),
        index=list(country_prestige.keys()).index(st.session_state.get("club_country", st.session_state.club_details["country"])),
        key="club_country"
    )
    club_european = st.checkbox(
        "Your Club Participates in European Competitions (e.g., Champions League, Europa League)",
        value=st.session_state.get("club_european", st.session_state.club_details["european"]),
        key="club_european"
    )
    
    # Submit button
    submit_club_details = st.form_submit_button("Save Club Details")

# Handle form submission
if submit_club_details:
    # Update session state with form values
    st.session_state.club_details = {
        "name": st.session_state["club_name"],
        "league": st.session_state["form_league"],
        "country": st.session_state["club_country"],
        "european": st.session_state["club_european"]
    }
    st.session_state.club_details_updated = True
    st.session_state.pending_club_details = None
    # Force re-render to update UI
    st.rerun()

# Display success message if club details were updated
if st.session_state.club_details_updated:
    club_details = st.session_state.club_details
    new_stature = calculate_score(club_details["league"], club_details["country"], club_details["european"], league_tiers)
    st.success(
        f"Club details saved: Name: {club_details['name'] or 'None'}, "
        f"League: {club_details['league']}, "
        f"Country: {club_details['country']}, "
        f"European: {club_details['european']}. "
        f"New stature score: {new_stature:.1f}"
    )

# Starting 11 Section
st.header("Starting 11 Overall Calculator")
st.info("Enter your starting 11 details. Save and load both club details and Starting 11 in a single JSON file.")

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
                index=player_positions.index(st.session_state.get(f"player_{i}_position", st.session_state.starting_11[i]["position"])),
                key=f"player_{i}_position"
            )
        with col2:
            overall = st.number_input(
                "",
                min_value=0,
                max_value=99,
                value=st.session_state.get(f"player_{i}_overall", st.session_state.starting_11[i]["overall"]),
                step=1,
                format="%d",
                key=f"player_{i}_overall"
            )
        with col3:
            wage = st.number_input(
                "",
                min_value=0,
                value=st.session_state.get(f"player_{i}_wage", st.session_state.starting_11[i]["wage"]),
                step=1000,
                format="%d",
                key=f"player_{i}_wage"
            )
        players.append({"position": position, "overall": overall, "wage": wage})

    # Submit button
    submit_starting_11 = st.form_submit_button("Calculate Team Overall")

# Download Combined Club Details and Starting 11 data (bottom button)
if st.session_state.club_details and st.session_state.starting_11:
    combined_data = {
        "club_details": st.session_state.club_details,
        "starting_11": st.session_state.starting_11
    }
    json_str = json.dumps(combined_data, indent=2)
    st.download_button(
        label="Download Club Details and Starting 11 as JSON",
        data=json_str,
        file_name="team_data.json",
        mime="application/json",
        key="download_bottom"
    )

# Starting 11 results
if submit_starting_11:
    # Validate all overalls and wages are >= 0
    if all(player["overall"] >= 0 and player["wage"] >= 0 for player in players):
        # Update session state
        st.session_state.starting_11 = players
        # Clear widget states to ensure form reflects new values
        for i in range(11):
            for key in [f"player_{i}_position", f"player_{i}_overall", f"player_{i}_wage"]:
                st.session_state.pop(key, None)
        # Set widget values to new data
        for i, player in enumerate(players):
            st.session_state[f"player_{i}_position"] = player["position"]
            st.session_state[f"player_{i}_overall"] = player["overall"]
            st.session_state[f"player_{i}_wage"] = player["wage"]

        # Calculate average overall and round down
        total_overall = sum(player["overall"] for player in players)
        average_overall = math.floor(total_overall / 11)
        st.session_state.average_team_overall = average_overall
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

# Selling Transfer Calculator Section
st.header("Transfer Calculator (Selling)")
with st.form(key="selling_transfer_form"):
    # Club 2 inputs (Offering Club)
    st.subheader("Offering Club Details")
    club2_name_sell = st.text_input("Enter Offering Club Name (Optional)", key="club2_name_sell")
    club2_league_sell = st.selectbox("Select Offering Club League/Division", list(league_tiers.keys()), key="club2_league_sell")
    club2_country_sell = st.selectbox("Select Offering Club Country", list(country_prestige.keys()), key="club2_country_sell")
    club2_european_sell = st.checkbox("Offering Club Participates in European Competitions (e.g., Champions League, Europa League)", key="club2_european_sell")

    # Transfer inputs
    st.subheader("Transfer Details")
    player_value_sell = st.number_input(
        "Current Player Value",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="player_value_sell",
        help="Enter value without commas, e.g., 1000000 for 1,000,000"
    )
    is_young_sell = st.checkbox("Player is Aged 16–21", key="is_young_sell")

    # Submit button
    submit_selling_transfer = st.form_submit_button("Calculate Selling Offer")

# Selling transfer results
if submit_selling_transfer:
    if player_value_sell > 0:
        # Fetch current club details from session state
        club_details = st.session_state.club_details
        # Calculate stature scores
        score1 = calculate_score(
            club_details["league"],
            club_details["country"],
            club_details["european"],
            league_tiers
        )
        score2 = calculate_score(club2_league_sell, club2_country_sell, club2_european_sell, league_tiers)
        stature_diff = score2 - score1

        # Use default names if not provided
        display_name1 = club_details["name"] if club_details["name"] else "Your Club"
        display_name2 = club2_name_sell if club2_name_sell else "Offering Club"

        # Display club details used for calculation
        st.write(f"**Your Club Details Used:** Name: {display_name1}, League: {club_details['league']}, Country: {club_details['country']}, European: {club_details['european']}")
        # Display club stature scores
        st.write(f"**{display_name1} Stature Score:** {score1:.1f}")
        st.write(f"**{display_name2} Stature Score:** {score2:.1f}")

        if score1 > score2:
            st.success(f"{display_name1} has a higher stature by {score1 - score2:.1f} points.")
        elif score2 > score1:
            st.warning(f"{display_name2} has a higher stature by {score2 - score1:.1f} points.")
        else:
            st.info("Both clubs have equal stature.")

        # Calculate and round up minimum offer to nearest 1000
        minimum_offer = calculate_minimum_offer(player_value_sell, stature_diff, is_young_sell)
        minimum_offer = math.ceil(minimum_offer / 1000) * 1000
        st.success(f"You must accept any offer from {display_name2} of {minimum_offer:,.0f} or higher for this player.")
    else:
        st.error("Please enter a valid player value greater than 0.")

# Buying Transfer Calculator Section
st.header("Transfer Calculator (Buying)")
with st.form(key="buying_transfer_form"):
    # Transfer inputs
    st.subheader("Player Details")
    player_value_buy = st.number_input(
        "Current Player Value",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="player_value_buy",
        help="Enter value without commas, e.g., 1000000 for 1,000,000"
    )
    player_overall_buy = st.number_input(
        "Player Overall Rating",
        min_value=0,
        max_value=99,
        step=1,
        format="%d",
        key="player_overall_buy"
    )
    player_age_buy = st.number_input(
        "Player Age",
        min_value=16,
        max_value=40,
        step=1,
        format="%d",
        key="player_age_buy"
    )

    # Submit button
    submit_buying_transfer = st.form_submit_button("Calculate Starting Bid and Wage")

# Buying transfer results
if submit_buying_transfer:
    if player_value_buy > 0 and player_overall_buy > 0:
        # Calculate and round up starting bid to nearest 1000
        starting_bid, is_accurate = calculate_starting_bid(
            player_value_buy,
            player_overall_buy,
            player_age_buy,
            st.session_state.average_team_overall
        )
        starting_bid = math.ceil(starting_bid / 1000) * 1000
        st.success(f"You should start your bid at {starting_bid:,.0f} for this player.")
        if not is_accurate:
            st.warning("This bid is based on a default 175% markup because the Starting 11 average overall has not been calculated. Please calculate your Starting 11 average for a more accurate bid.")

        # Calculate proportional wage
        wage, wage_error = calculate_proportional_wage(player_overall_buy, st.session_state.starting_11)
        if wage is not None:
            st.success(f"Minimum Wage for this player: {wage:,} p/w")
        else:
            st.warning(f"Cannot calculate wage: {wage_error} Please ensure your Starting 11 has valid wages and overalls.")
    else:
        st.error("Please enter a valid player value and overall greater than 0.")