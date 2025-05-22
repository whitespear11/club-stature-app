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
        border-bottom: none; /* Removed the dark green border-bottom */
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
        background-color: #2c3e50; /* Match the inactive tab background for consistency */
        color: #ffffff;
        border-bottom: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    /* Override any remaining dark green backgrounds or borders in the tab area */
    .stTabs, .stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-color: transparent !important;
        background-color: #2c3e50 !important; /* Ensure no green shows through */
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
        color: #ffffff; /* Ensure counter text is white */
    }
    /* Career Checklist tab text styling */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stMarkdown,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stMarkdown p,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stMarkdown h2,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stMarkdown h3,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .streamlit-expanderHeader,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .streamlit-expanderContent,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .streamlit-expanderContent p,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .streamlit-expanderContent label,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stSuccess,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stError,
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stWarning {
        color: #ffffff !important;
    }
    /* Ensure Career Checklist tab background for better readability with white text */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .streamlit-expanderContent {
        background-color: #2c3e50 !important; /* Dark background for contrast */
    }
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .streamlit-expanderHeader {
        background-color: #34495e !important; /* Slightly lighter dark background for header */
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
        summer_bench_max = 2
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
        with col3:
            if st.session_state.checklist["summer"]["loans"] < 3:
                if st.button("Add", key="summer_loan_add"):
                    st.session_state.checklist["summer"]["loans"] += 1
                    st.rerun()
            if st.session_state.checklist["summer"]["loans"] > 0:
                if st.button("Remove", key="summer_loan_remove"):
                    st.session_state.checklist["summer"]["loans"] -= 1
                    st.rerun()
        if st.session_state.checklist["summer"]["loans"] > 3:
            st.error("Exceeded loan limit!")

        # Starting Players Sold
        st.markdown('<div class="checklist-section"><strong>Starting Players Sold (Unlocks Extra Signing at 2)</strong></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Players sold:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['summer']['starting_sold']}</span>", unsafe_allow_html=True)
        with col3:
            if st.button("Add", key="summer_sale_add"):
                st.session_state.checklist["summer"]["starting_sold"] += 1
                st.rerun()
            if st.session_state.checklist["summer"]["starting_sold"] > 0:
                if st.button("Remove", key="summer_sale_remove"):
                    st.session_state.checklist["summer"]["starting_sold"] -= 1
                    st.rerun()

    # Winter Window
    with st.expander("Winter Window", expanded=False):
        st.subheader("Winter Window Guidelines")

        # Starting 11 Signings
        st.markdown('<div class="checklist-section"><strong>Starting 11 Signings (Max 1)</strong></div>', unsafe_allow_html=True)
        winter_starting_max = 1
        winter_starting_extra = 1 if st.session_state.checklist["winter"]["starting_sold"] >= 2 else 0
        winter_starting_total_max = winter_starting_max + winter_starting_extra
        if winter_starting_extra:
            st.markdown("*Extra signing unlocked (2 starting players sold)!*")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Signings made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['winter']['starting_signings']}</span>/{winter_starting_total_max}", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["winter"]["starting_signings"] < winter_starting_total_max:
                if st.button("Add", key="winter_starting_add"):
                    st.session_state.checklist["winter"]["starting_signings"] += 1
                    st.rerun()
            if st.session_state.checklist["winter"]["starting_signings"] > 0:
                if st.button("Remove", key="winter_starting_remove"):
                    st.session_state.checklist["winter"]["starting_signings"] -= 1
                    st.rerun()
        if st.session_state.checklist["winter"]["starting_signings"] > winter_starting_total_max:
            st.error("Exceeded starting 11 signings limit!")

        # Bench Signings
        st.markdown('<div class="checklist-section"><strong>Bench Signings (Max 1)</strong></div>', unsafe_allow_html=True)
        winter_bench_max = 1
        winter_bench_total_max = winter_bench_max + winter_starting_extra
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Signings made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['winter']['bench_signings']}</span>/{winter_bench_total_max}", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["winter"]["bench_signings"] < winter_bench_total_max:
                if st.button("Add", key="winter_bench_add"):
                    st.session_state.checklist["winter"]["bench_signings"] += 1
                    st.rerun()
            if st.session_state.checklist["winter"]["bench_signings"] > 0:
                if st.button("Remove", key="winter_bench_remove"):
                    st.session_state.checklist["winter"]["bench_signings"] -= 1
                    st.rerun()
        if st.session_state.checklist["winter"]["bench_signings"] > winter_bench_total_max:
            st.error("Exceeded bench signings limit!")

        # Reserve Signings
        st.markdown('<div class="checklist-section"><strong>Reserve Signings (Max 2)</strong></div>', unsafe_allow_html=True)
        winter_reserve_max = 2
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Signings made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['winter']['reserve_signings']}</span>/{winter_reserve_max}", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["winter"]["reserve_signings"] < winter_reserve_max:
                if st.button("Add", key="winter_reserve_add"):
                    st.session_state.checklist["winter"]["reserve_signings"] += 1
                    st.rerun()
            if st.session_state.checklist["winter"]["reserve_signings"] > 0:
                if st.button("Remove", key="winter_reserve_remove"):
                    st.session_state.checklist["winter"]["reserve_signings"] -= 1
                    st.rerun()
        if st.session_state.checklist["winter"]["reserve_signings"] > winter_reserve_max:
            st.error("Exceeded reserve signings limit!")

        # Loans Tracking
        st.markdown('<div class="checklist-section"><strong>Loans (Max 1 Across All Signings)</strong></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Loans made:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['winter']['loans']}</span>/1", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["winter"]["loans"] < 1:
                if st.button("Add", key="winter_loan_add"):
                    st.session_state.checklist["winter"]["loans"] += 1
                    st.rerun()
            if st.session_state.checklist["winter"]["loans"] > 0:
                if st.button("Remove", key="winter_loan_remove"):
                    st.session_state.checklist["winter"]["loans"] -= 1
                    st.rerun()
        if st.session_state.checklist["winter"]["loans"] > 1:
            st.error("Exceeded loan limit!")

        # Pre-contract Signings (16-29)
        st.markdown('<div class="checklist-section"><strong>Pre-contract Signing (Ages 16-29, Max 1)</strong></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Pre-contracts:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['winter']['pre_contract_16_29']}</span>/1", unsafe_allow_html=True)
        with col3:
            if st.session_state.checklist["winter"]["pre_contract_16_29"] < 1:
                if st.button("Add", key="winter_pre_contract_16_29_add"):
                    st.session_state.checklist["winter"]["pre_contract_16_29"] += 1
                    st.rerun()
            if st.session_state.checklist["winter"]["pre_contract_16_29"] > 0:
                if st.button("Remove", key="winter_pre_contract_16_29_remove"):
                    st.session_state.checklist["winter"]["pre_contract_16_29"] -= 1
                    st.rerun()
        if st.session_state.checklist["winter"]["pre_contract_16_29"] > 1:
            st.error("Exceeded pre-contract (16-29) limit!")

        # Pre-contract Signings (30+)
        st.markdown('<div class="checklist-section"><strong>Pre-contract Signings (Ages 30+, No Strict Limit)</strong></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Pre-contracts:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['winter']['pre_contract_30_plus']}</span>", unsafe_allow_html=True)
        with col3:
            if st.button("Add", key="winter_pre_contract_30_plus_add"):
                st.session_state.checklist["winter"]["pre_contract_30_plus"] += 1
                st.rerun()
            if st.session_state.checklist["winter"]["pre_contract_30_plus"] > 0:
                if st.button("Remove", key="winter_pre_contract_30_plus_remove"):
                    st.session_state.checklist["winter"]["pre_contract_30_plus"] -= 1
                    st.rerun()
        if st.session_state.checklist["winter"]["pre_contract_30_plus"] > 3:
            st.warning("Be cautious with too many pre-contracts for players aged 30+!")

        # Starting Players Sold
        st.markdown('<div class="checklist-section"><strong>Starting Players Sold (Unlocks Extra Signing at 2)</strong></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("Players sold:")
        with col2:
            st.write(f"<span class='checklist-counter'>{st.session_state.checklist['winter']['starting_sold']}</span>", unsafe_allow_html=True)
        with col3:
            if st.button("Add", key="winter_sale_add"):
                st.session_state.checklist["winter"]["starting_sold"] += 1
                st.rerun()
            if st.session_state.checklist["winter"]["starting_sold"] > 0:
                if st.button("Remove", key="winter_sale_remove"):
                    st.session_state.checklist["winter"]["starting_sold"] -= 1
                    st.rerun()

# Tab 3: Starting 11
with tab3:
    st.header("Starting 11 Calculator")
    st.write("Enter your starting 11 to calculate team average overall and wage cap.")
    
    # Progress indicator for starting 11
    valid_players = sum(1 for player in st.session_state.starting_11 if player["overall"] > 0) / 11
    starting_11_progress_percentage = int(valid_players * 100)
    starting_11_progress_color = "#28a745" if valid_players == 1 else "#3498db"
    st.markdown(
        f"""
        <div style="margin-bottom: 5px;">Starting 11 Completion: {starting_11_progress_percentage}%</div>
        <div class="custom-progress-container">
            <div class="custom-progress-bar" style="width: {starting_11_progress_percentage}%; background-color: {starting_11_progress_color};"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("Enter Starting 11 Details", expanded=True):
        with st.form(key="starting_11_form"):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.write("**Position**")
            with col2:
                st.write("**Overall**")
            with col3:
                st.write("**Wage (p/w)**")
            
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
            
            submit_starting_11 = st.form_submit_button("Calculate Team Overall")
    
    if submit_starting_11:
        if all(player["overall"] >= 0 and player["wage"] >= 0 for player in players):
            st.session_state.starting_11 = players
            for i in range(11):
                for key in [f"player_{i}_position", f"player_{i}_overall", f"player_{i}_wage"]:
                    st.session_state.pop(key, None)
            for i, player in enumerate(players):
                st.session_state[f"player_{i}_position"] = player["position"]
                st.session_state[f"player_{i}_overall"] = player["overall"]
                st.session_state[f"player_{i}_wage"] = player["wage"]
            total_overall = sum(player["overall"] for player in players)
            average_overall = math.floor(total_overall / 11)
            st.session_state.average_team_overall = average_overall
            max_signing_overall = average_overall + 2
            max_wage = max(player["wage"] for player in players)
            wage_cap = int(max_wage * 1.2)
            st.success(f"Average Team Overall: {average_overall}")
            st.success(f"Sign players with overall {max_signing_overall} or below.")
            st.success(f"Wage Cap: {wage_cap:,} p/w")
        else:
            st.error("All player overalls and wages must be non-negative.")

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
            key="download_starting_11",
            use_container_width=True
        )

# Tab 4: Transfer Calculators
with tab4:
    st.header("Transfer Calculators")
    
    # Selling Transfer Calculator
    with st.expander("Selling Transfer Calculator", expanded=False):
        with st.form(key="selling_transfer_form"):
            st.subheader("Offering Club Details")
            club2_name_sell = st.text_input("Offering Club Name (Optional)", key="club2_name_sell")
            club2_league_sell = st.selectbox("Offering Club League", list(league_tiers.keys()), key="club2_league_sell")
            club2_country_sell = st.selectbox("Offering Club Country", list(country_prestige.keys()), key="club2_country_sell")
            club2_european_sell = st.checkbox("Offering Club in European Competitions", key="club2_european_sell")
            
            st.subheader("Transfer Details")
            player_value_sell = st.number_input(
                "Player Value",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key="player_value_sell",
                help="Enter value without commas, e.g., 1000000"
            )
            is_young_sell = st.checkbox("Player Aged 16–21", key="is_young_sell")
            submit_selling_transfer = st.form_submit_button("Calculate Selling Offer")
        
        if submit_selling_transfer:
            if player_value_sell > 0:
                club_details = st.session_state.club_details
                score1 = calculate_score(club_details["league"], club_details["country"], club_details["european"], league_tiers)
                score2 = calculate_score(club2_league_sell, club2_country_sell, club2_european_sell, league_tiers)
                stature_diff = score2 - score1
                display_name1 = club_details["name"] if club_details["name"] else "Your Club"
                display_name2 = club2_name_sell if club2_name_sell else "Offering Club"
                st.write(f"**{display_name1}**: {club_details['league']}, {club_details['country']}, European: {club_details['european']}")
                st.write(f"**Stature Score**: {score1:.1f}")
                st.write(f"**{display_name2}**: {club2_league_sell}, {club2_country_sell}, European: {club2_european_sell}")
                st.write(f"**Stature Score**: {score2:.1f}")
                if score1 > score2:
                    st.success(f"{display_name1} has higher stature by {score1 - score2:.1f}.")
                elif score2 > score1:
                    st.warning(f"{display_name2} has higher stature by {score2 - score1:.1f}.")
                else:
                    st.info("Clubs have equal stature.")
                minimum_offer = calculate_minimum_offer(player_value_sell, stature_diff, is_young_sell)
                minimum_offer = math.ceil(minimum_offer / 1000) * 1000
                st.success(f"Accept offers from {display_name2} of {minimum_offer:,.0f} or higher.")
            else:
                st.error("Player value must be greater than 0.")

    # Buying Transfer Calculator
    with st.expander("Buying Transfer Calculator", expanded=False):
        with st.form(key="buying_transfer_form"):
            st.subheader("Player Details")
            player_value_buy = st.number_input(
                "Player Value",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key="player_value_buy",
                help="Enter value without commas, e.g., 1000000"
            )
            player_overall_buy = st.number_input(
                "Player Overall",
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
            submit_buying_transfer = st.form_submit_button("Calculate Bid and Wage")
        
        if submit_buying_transfer:
            if player_value_buy > 0 and player_overall_buy > 0:
                if st.session_state.average_team_overall is not None and player_overall_buy > st.session_state.average_team_overall + 2:
                    st.warning("Player's overall is too high. Sign players with lower overall or update Starting 11.")
                starting_bid, is_accurate = calculate_starting_bid(
                    player_value_buy, player_overall_buy, player_age_buy, st.session_state.average_team_overall
                )
                starting_bid = math.ceil(starting_bid / 1000) * 1000
                st.success(f"Start your bid at {starting_bid:,.0f}.")
                if not is_accurate:
                    st.warning("Bid uses default markup. Calculate Starting 11 average for accuracy.")
                wage, wage_error = calculate_proportional_wage(player_overall_buy, st.session_state.starting_11)
                if wage is not None:
                    st.success(f"Minimum Wage: {wage:,} p/w")
                else:
                    st.warning(f"Wage error: {wage_error}")
            else:
                st.error("Player value and overall must be greater than 0.")

# Tab 5: Help/Info
with tab5:
    st.header("Help & Info")
    st.write(
        """
        **FIFA Realistic Toolkit** helps you manage your FIFA career mode with realistic transfer and wage guidelines.
        
        - **Club Details**: Enter your club's league, country, and European status to calculate stature.
        - **Career Checklist**: Track your signings and ensure compliance with transfer window rules.
        - **Starting 11**: Input your starting lineup to determine average overall and wage caps.
        - **Transfer Calculators**: Compute minimum selling offers and starting bids for buying players.
        - **Save/Load**: Use JSON files to save or load your club and player data.
        
        If you enjoy this tool, consider [buying me a coffee](https://buymeacoffee.com/whitespear11).
        """
    )