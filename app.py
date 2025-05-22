import streamlit as st
import math
import json
import io

# Apply custom CSS with improved tab and custom progress bar styling
st.markdown(
    """
    <style>
    /* Button styling */
    button[kind="primary"] {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    button[kind="primary"]:hover {
        background-color: #218838;
        color: white;
    }
    /* Input field styling */
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > select {
        border-radius: 0.25rem;
        border: 1px solid #ced4da;
        padding: 0.5rem;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    /* Ensure selectbox options are readable */
    .stSelectbox > div > div > select > option {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    /* Section headers */
    .stMarkdown h2, .stMarkdown h3 {
        color: #1e3a8a;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    /* Expander styling */
    .streamlit-expander {
        border: 1px solid #e2e8f0;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        padding: 0.5rem;
        font-weight: 500;
        color: #1e3a8a !important;
    }
    .streamlit-expanderContent {
        background-color: #ffffff;
        padding: 1rem;
        color: #000000 !important;
    }
    /* Ensure form elements inside expanders are visible */
    .streamlit-expanderContent .stTextInput, 
    .streamlit-expanderContent .stNumberInput, 
    .streamlit-expanderContent .stSelectbox, 
    .streamlit-expanderContent .stCheckbox {
        color: #000000 !important;
    }
    .streamlit-expanderContent label, 
    .streamlit-expanderContent p {
        color: #000000 !important;
    }
    /* Success and error messages */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
    .stWarning {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
    /* Tab styling - Improved */
    .stTabs {
        display: flex;
        justify-content: center;
        background-color: #1a2526;
        padding: 0.5rem 0;
        border-bottom: 2px solid #28a745;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.2rem;
        font-family: 'Arial', sans-serif;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        margin: 0 0.5rem;
        color: #ffffff;
        background-color: #2c3e50;
        border-radius: 8px 8px 0 0;
        transition: all 0.3s ease;
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #34495e;
        color: #ffffff;
        cursor: pointer;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #28a745;
        color: #ffffff;
        border-bottom: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    /* Custom progress bar styling */
    .custom-progress-container {
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
        margin: 10px 0;
    }
    .custom-progress-bar {
        height: 20px;
        transition: width 0.3s ease, background-color 0.3s ease;
    }
    /* Checklist styling */
    .checklist-section {
        margin-bottom: 1rem;
    }
    .checklist-counter {
        font-weight: bold;
        color: #000000;
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

# Function definitions
def calculate_score(league, country, european, league_tiers):
    league_score = league_tiers.get(league, 1)
    if league_tiers.get(league, 1) < 3:
        league_score /= 2
    country_score = country_prestige.get(country, 1)
    european_bonus = 1.0 if european else 0.0
    return league_score + country_score + european_bonus

def calculate_minimum_offer(player_value, stature_diff, is_young):
    if stature_diff <= 0:
        markup = 65.0
    else:
        markup = 65.0 - (stature_diff / 12.0) * 50.0
        markup = max(markup, 15.0)
    multiplier = 1.0 + markup / 100.0
    if is_young:
        if stature_diff <= 0 or stature_diff <= 3.5:
            age_markup = 0.25
        elif stature_diff <= 7.0:
            age_markup = 0.18
        else:
            age_markup = 0.12
    else:
        age_markup = 0.0
    return player_value * multiplier + player_value * age_markup

def calculate_starting_bid(player_value, player_overall, player_age, average_team_overall=None):
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
        return player_value * 1.30, average_team_overall is not None

def calculate_proportional_wage(player_overall, starting_11):
    valid_players = [
        player for player in starting_11
        if player["overall"] > 0 and player["wage"] > 0
    ]
    if not valid_players:
        return None, "No valid Starting 11 data with non-zero wages and overalls."
    max_wage = max(player["wage"] for player in valid_players)
    max_wage_players = [player for player in valid_players if player["wage"] == max_wage]
    max_wage_overall = max_wage_players[0]["overall"]
    max_overall = max(player["overall"] for player in valid_players)
    wage = max_wage * (player_overall / max_wage_overall)
    if player_overall > max_overall:
        wage *= 1.2
    wage = math.ceil(wage / 100) * 100
    return wage, None

# Initialize session state for existing sections
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

# Initialize session state for Career Checklist
if "checklist" not in st.session_state:
    st.session_state.checklist = {
        "summer": {
            "starting_signings": 0,
            "bench_signings": 0,
            "reserve_signings": 0,
            "loans": 0,
            "starting_sold": 0
        },
        "winter": {
            "starting_signings": 0,
            "bench_signings": 0,
            "reserve_signings": 0,
            "loans": 0,
            "starting_sold": 0,
            "pre_contract_16_29": 0,
            "pre_contract_30_plus": 0
        }
    }

# App title
st.title("FIFA Realistic Toolkit")

# Create tabs with Career Checklist as second
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Club Details", "Career Checklist", "Starting 11", "Transfer Calculators", "Help/Info"])

# Tab 1: Club Details
with tab1:
    st.header("Your Club Details")
    st.write(
        """
        Welcome to the FIFA Realistic Toolkit! Enter your club details below to calculate team stature and guide transfers.
        Save or upload your data to continue where you left off.
        """
    )
    
    # Progress indicator for club details with clarification
    def is_field_valid(value, field_type):
        if field_type == "league" and value in league_tiers:
            return True
        elif field_type == "country" and value in country_prestige:
            return True
        elif field_type == "european" and isinstance(value, bool):
            return True
        elif field_type == "name" and value != "":
            return True
        return False

    club_progress = (
        (1 if is_field_valid(st.session_state.club_details["league"], "league") else 0) +
        (1 if is_field_valid(st.session_state.club_details["country"], "country") else 0) +
        (1 if is_field_valid(st.session_state.club_details["european"], "european") else 0) +
        (1 if is_field_valid(st.session_state.club_details["name"], "name") else 0)
    ) / 4
    club_progress_percentage = int(club_progress * 100)
    club_progress_color = "#28a745" if club_progress == 1 else "#3498db"
    st.markdown(
        f"""
        <div style="margin-bottom: 5px;">Club Details Completion: {club_progress_percentage}%</div>
        <div class="custom-progress-container">
            <div class="custom-progress-bar" style="width: {club_progress_percentage}%; background-color: {club_progress_color};"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("**Required**: League, Country, European status.")

    # File uploader
    uploaded_file = st.file_uploader("Upload Club and Starting 11 JSON", type=["json"], key="combined_upload")
    if st.session_state.get("combined_upload") is not None:
        st.warning("Clear the uploaded file before editing form fields.")
    if uploaded_file:
        try:
            loaded_data = json.load(uploaded_file)
            club_valid = (
                isinstance(loaded_data.get("club_details"), dict) and
                all(key in loaded_data["club_details"] for key in ["name", "league", "country", "european"]) and
                isinstance(loaded_data["club_details"]["name"], str) and
                loaded_data["club_details"]["league"] in league_tiers and
                loaded_data["club_details"]["country"] in country_prestige and
                isinstance(loaded_data["club_details"]["european"], bool)
            )
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
                st.session_state.club_details = loaded_data["club_details"]
                st.session_state.starting_11 = loaded_data["starting_11"]
                st.session_state.club_details_updated = True
                st.session_state.pending_club_details = None
                st.session_state["club_name"] = loaded_data["club_details"]["name"]
                st.session_state["form_league"] = loaded_data["club_details"]["league"]
                st.session_state["club_country"] = loaded_data["club_details"]["country"]
                st.session_state["club_european"] = loaded_data["club_details"]["european"]
                for i, player in enumerate(loaded_data["starting_11"]):
                    st.session_state[f"player_{i}_position"] = player["position"]
                    st.session_state[f"player_{i}_overall"] = player["overall"]
                    st.session_state[f"player_{i}_wage"] = player["wage"]
                total_overall = sum(player["overall"] for player in loaded_data["starting_11"])
                st.session_state.average_team_overall = math.floor(total_overall / 11)
                st.success(
                    f"Club data loaded: {loaded_data['club_details']['name'] or 'None'}, "
                    f"{loaded_data['club_details']['league']}, "
                    f"{loaded_data['club_details']['country']}, "
                    f"European: {loaded_data['club_details']['european']}. "
                    f"Stature: {calculate_score(loaded_data['club_details']['league'], loaded_data['club_details']['country'], loaded_data['club_details']['european'], league_tiers):.1f}"
                )
            else:
                st.error("Invalid JSON format or data.")
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")

    # Download button
    if st.session_state.club_details and st.session_state.starting_11:
        combined_data = {
            "club_details": st.session_state.club_details,
            "starting_11": st.session_state.starting_11
        }
        json_str = json.dumps(combined_data, indent=2)
        st.download_button(
            label="Save Club and Starting 11 Data",
            data=json_str,
            file_name="team_data.json",
            mime="application/json",
            key="download_club",
            use_container_width=True
        )

    # Club details form in expander
    with st.expander("Enter Club Details", expanded=True):
        with st.form(key="club_details_form"):
            club_name = st.text_input("Club Name", key="club_name")
            club_league = st.selectbox(
                "League/Division",
                list(league_tiers.keys()),
                index=list(league_tiers.keys()).index(st.session_state.form_league),
                key="form_league"
            )
            club_country = st.selectbox(
                "Country",
                list(country_prestige.keys()),
                index=list(country_prestige.keys()).index(st.session_state.club_country),
                key="club_country"
            )
            club_european = st.checkbox("Participates in European Competitions", key="club_european")
            submit_club_details = st.form_submit_button("Save Club Details")

        if submit_club_details:
            st.session_state.club_details = {
                "name": st.session_state["club_name"],
                "league": st.session_state["form_league"],
                "country": st.session_state["club_country"],
                "european": st.session_state["club_european"]
            }
            st.session_state.club_details_updated = False
            st.session_state.pending_club_details = None
            st.rerun()

# Tab 2: Career Checklist
with tab2:
    st.header("Career Checklist")
    st.write("Track your signings and sales to stay within the guidelines for each transfer window.")

    # Reset button for the checklist
    if st.button("Reset for New Season", key="reset_checklist"):
        st.session_state.checklist = {
            "summer": {
                "starting_signings": 0,
                "bench_signings": 0,
                "reserve_signings": 0,
                "loans": 0,
                "starting_sold": 0
            },
            "winter": {
                "starting_signings": 0,
                "bench_signings": 0,
                "reserve_signings": 0,
                "loans": 0,
                "starting_sold": 0,
                "pre_contract_16_29": 0,
                "pre_contract_30_plus": 0
            }
        }
        st.success("Checklist reset for the new season!")
        st.rerun()

    # Summer Window
    with st.expander("Summer Window", expanded=True):
        st.subheader("Summer Window Guidelines")

        # Starting 11 Signings
        st.markdown('<div class="checklist-section"><strong>Starting 11 Signings (Max 2)</strong></div>', unsafe_allow_html=True)
        summer_starting_max = 2
        summer_starting_extra = 1 if st.session_state.checklist["summer"]["starting_sold"] >= 2 else 0
        summer_starting_total_max = summer_starting_max + summer_starting_extra
        if summer_starting_extra:
            st.markdown("*Extra signing unlocked (2 starting players sold)!*")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Signings made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['summer']['starting_signings']}</span>/{summer_starting_total_max}", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["summer"]["starting_signings"] < summer_starting_total_max:
                if st.button("Add", key="summer_starting_add"):
                    st.session_state.checklist["summer"]["starting_signings"] += 1
                    st.rerun()
            if st.session_state.checklist["summer"]["starting_signings"] > 0:
                if st.button("Remove", key="summer_starting_remove"):
                    st.session_state.checklist["summer"]["starting_signings"] -= 1
                    st.rerun()
        if st.session_state.checklist["summer"]["starting_signings"] > summer_starting_total_max:
            st.error("Exceeded starting 11 signings limit!")

        # Bench Signings
        st.markdown('<div class="checklist-section"><strong>Bench Signings (Max 2)</strong></div>', unsafe_allow_html=True)
        summer_bench_total_max = summer_bench_max + summer_starting_extra
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Signings made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['summer']['bench_signings']}</span>/{summer_bench_total_max}", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["summer"]["bench_signings"] < summer_bench_total_max:
                if st.button("Add", key="summer_bench_add"):
                    st.session_state.checklist["summer"]["bench_signings"] += 1
                    st.rerun()
            if st.session_state.checklist["summer"]["bench_signings"] > 0:
                if st.button("Remove", key="summer_bench_remove"):
                    st.session_state.checklist["summer"]["bench_signings"] -= 1
                    st.rerun()
        if st.session_state.checklist["summer"]["bench_signings"] > summer_bench_total_max:
            st.error("Exceeded bench signings limit!")

        # Reserve Signings
        st.markdown('<div class="checklist-section"><strong>Reserve Signings (Max 3)</strong></div>', unsafe_allow_html=True)
        summer_reserve_max = 3
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Signings made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['summer']['reserve_signings']}</span>/{summer_reserve_max}", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["summer"]["reserve_signings"] < summer_reserve_max:
                if st.button("Add", key="summer_reserve_add"):
                    st.session_state.checklist["summer"]["reserve_signings"] += 1
                    st.rerun()
            if st.session_state.checklist["summer"]["reserve_signings"] > 0:
                if st.button("Remove", key="summer_reserve_remove"):
                    st.session_state.checklist["summer"]["reserve_signings"] -= 1
                    st.rerun()
        if st.session_state.checklist["summer"]["reserve_signings"] > summer_reserve_max:
            st.error("Exceeded reserve signings limit!")

        # Loans Tracking
        st.markdown('<div class="checklist-section"><strong>Loans (Max 3 Across All Signings)</strong></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Loans made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['summer']['loans']}</span>/3", unsafe_allow_html=True)
        with col3