import streamlit as st
import math
import json
import io
import uuid

# Cache calculations for performance
@st.cache_data
def calculate_score(league, country, european, league_tiers):
    league_score = league_tiers.get(league, 1)
    if league_tiers.get(league, 1) < 3:
        league_score /= 2
    country_score = country_prestige.get(country, 1)
    european_bonus = 1.0 if european else 0.0
    return league_score + country_score + european_bonus

@st.cache_data
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

@st.cache_data
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

@st.cache_data
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

# Add viewport meta tag and custom CSS
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <style>
    :root {
        color-scheme: dark !important;
        --background-color: #1a2526 !important;
        --secondary-background-color: #2c3e50 !important;
        --text-color: #ffffff !important;
        --primary-color: #28a745 !important;
    }
    @media (prefers-color-scheme: light), (prefers-color-scheme: dark) {
        :root {
            color-scheme: dark !important;
            forced-colors: none !important;
        }
    }
    body {
        font-family: 'Inter', 'Roboto', sans-serif;
        background-color: #1a2526 !important;
        color: #ffffff !important;
        margin: 0;
        padding: 0;
    }
    .app-wrapper {
        width: 100vw !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
        padding-top: env(safe-area-inset-top, 0) !important;
        padding-left: env(safe-area-inset-left, 0) !important;
        background-color: #1a2526 !important;
        color: #ffffff !important;
    }
    * {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    p, h1, h2, h3, h4, h5, h6, label, span, div, a {
        color: #ffffff !important;
    }
    [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        background-color: #1a2526 !important;
    }
    button[kind="primary"] {
        background-color: #28a745 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1rem;
        min-height: 44px;
        cursor: pointer;
        transition: all 0.3s ease;
        aria-label: "Primary action button";
    }
    button[kind="primary"]:hover {
        background-color: #218838 !important;
        transform: scale(1.05);
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea,
    .stFileUploader > div > div > input {
        border-radius: 0.5rem;
        border: 1px solid #ced4da !important;
        padding: 0.75rem;
        color: #000000 !important;
        background-color: #ffffff !important;
        font-size: 1rem;
        min-height: 44px;
    }
    .stSelectbox > div > div > select > option {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stCheckbox > label,
    .stTextArea > label,
    .stFileUploader > label {
        color: #ffffff !important;
        font-weight: 500;
    }
    .stCodeBlock, .stCodeBlock pre, .stCodeBlock code {
        background-color: #2c3e50 !important;
        color: #ffffff !important;
        border: 1px solid #ced4da !important;
        border-radius: 0.5rem;
        padding: 0.75rem;
        font-size: 0.9rem;
    }
    .stMarkdown h2, .stMarkdown h3 {
        color: #2563eb !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        font-weight: 600;
        margin: 1rem 0 0.5rem;
    }
    .streamlit-expander {
        border: 1px solid #e2e8f0 !important;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        background-color: transparent !important;
    }
    .streamlit-expanderHeader {
        background-color: #f8fafc !important;
        padding: 0.75rem;
        font-weight: 500;
        color: #2563eb !important;
        font-size: 1.1rem;
    }
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        padding: 1rem;
        color: #000000 !important;
    }
    .streamlit-expanderContent p,
    .streamlit-expanderContent label,
    .streamlit-expanderContent span,
    .streamlit-expanderContent div {
        color: #000000 !important;
    }
    .streamlit-expanderContent .stTextInput > label,
    .streamlit-expanderContent .stNumberInput > label,
    .streamlit-expanderContent .stSelectbox > label,
    .streamlit-expanderContent .stCheckbox > label,
    .streamlit-expanderContent .stTextArea > label,
    .stFileUploader > label {
        color: #000000 !important;
    }
    .streamlit-expanderContent .stTextInput > div > div > input,
    .streamlit-expanderContent .stNumberInput > div > div > input,
    .streamlit-expanderContent .stSelectbox > div > div > select,
    .streamlit-expanderContent .stTextArea > div > div > textarea,
    .streamlit-expanderContent .stFileUploader > div > div > input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    .stSuccess {
        background-color: #d4edda !important;
        color: #155724 !important;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stSuccess p, .stSuccess span {
        color: #155724 !important;
    }
    .stError {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stError p, .stError span {
        color: #721c24 !important;
    }
    .stWarning {
        background-color: #fff3cd !important;
        color: #856404 !important;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stWarning p, .stWarning span {
        color: #856404 !important;
    }
    .stTabs {
        flex-direction: column;
        padding: 0.25rem 0;
        width: 100% !important;
        margin: 0 !important;
        background-color: #1a2526 !important;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        padding: 0.75rem;
        margin: 0 0 0.25rem 0 !important;
        width: 100% !important;
        text-align: center;
        background-color: #2c3e50 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.25rem;
        min-height: 44px;
        transition: background-color 0.3s ease;
        aria-label: "Tab navigation";
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #34495e !important;
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2c3e50 !important;
        color: #ffffff !important;
        box-shadow: none;
    }
    .stTabs, .stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-color: transparent !important;
    }
    .custom-progress-container {
        width: 100%;
        background-color: #e0e0e0 !important;
        border-radius: 5px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .custom-progress-bar {
        height: 20px;
        background: linear-gradient(to right, #28a745, #34c759);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff !important;
        font-size: 0.9rem;
        font-weight: bold;
        transition: width 0.3s ease, background-color 0.3s ease;
    }
    .checklist-section {
        margin-bottom: 1rem;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
        background-color: #34495e !important;
    }
    th, td {
        padding: 0.75rem;
        text-align: left;
        color: #ffffff !important;
    }
    th {
        background-color: #2c3e50 !important;
    }
    .load-message {
        background-color: #34495e !important;
        color: #ffffff !important;
        padding: 0.5rem 0.75rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
        text-align: center;
    }
    div[data-testid="stVerticalBlock"] > div {
        background-color: #1a2526 !important;
    }
    div[data-testid="stVerticalBlock"] > div .stMarkdown,
    div[data-testid="stVerticalBlock"] > div .stMarkdown p,
    div[data-testid="stVerticalBlock"] > div .stMarkdown h2,
    div[data-testid="stVerticalBlock"] > div .stMarkdown h3 {
        color: #ffffff !important;
    }
    @media (min-width: 401px) {
        .stTabs {
            flex-direction: row;
            justify-content: center;
            padding: 0.5rem 0;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 1.2rem;
            padding: 0.75rem 1rem;
            margin: 0 0.25rem !important;
            width: auto !important;
            border-radius: 8px 8px 0 0;
        }
        button[kind="primary"] {
            font-size: 1rem;
            padding: 0.6rem 1.2rem;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea,
        .stFileUploader > div > div > input {
            font-size: 1rem;
            padding: 0.6rem;
        }
        .stMarkdown h2 {
            font-size: 1.5rem;
        }
        .stMarkdown h3 {
            font-size: 1.3rem;
        }
        .streamlit-expanderHeader {
            font-size: 1.1rem;
        }
        table {
            font-size: 0.9rem;
        }
        .load-message {
            font-size: 1rem;
        }
    }
    @media (max-width: 400px) {
        .stTabs {
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: #1a2526 !important;
            padding-top: env(safe-area-inset-top, 0);
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem;
            padding: 0.5rem;
            margin: 0 0 0.2rem 0 !important;
            min-height: 40px;
        }
        button[kind="primary"] {
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
            min-height: 40px;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea,
        .stFileUploader > div > div > input {
            font-size: 0.85rem;
            padding: 0.4rem;
            min-height: 36px;
        }
        .stMarkdown h2, .stMarkdown h3 {
            font-size: 1.2rem;
        }
        .streamlit-expanderHeader {
            font-size: 1rem;
        }
        table {
            font-size: 0.8rem;
        }
        th, td {
            padding: 0.5rem;
        }
        .load-message {
            font-size: 0.8rem;
            padding: 0.4rem 0.6rem;
        }
        .stColumns > div {
            flex: 100% !important;
            max-width: 100% !important;
            margin-bottom: 0.5rem;
        }
    }
    @supports (-webkit-overflow-scrolling: touch) {
        .app-wrapper {
            padding-top: env(safe-area-inset-top, 0) !important;
            padding-left: env(safe-area-inset-left, 0) !important;
        }
    }
    #welcome-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: #2c3e50;
        padding: 1.5rem;
        border-radius: 0.5rem;
        z-index: 1000;
        max-width: 90%;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    #welcome-modal button {
        background-color: #28a745 !important;
        color: #ffffff !important;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    #welcome-modal button:hover {
        background-color: #218838 !important;
    }
    </style>
    <div class="app-wrapper">
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
if "scout_rating_display" not in st.session_state:
    st.session_state.scout_rating_display = None
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
            "starting_sold": 0
        },
        "youth_promotions": 0
    }
if "checklist_history" not in st.session_state:
    st.session_state.checklist_history = []
if "analytics" not in st.session_state:
    st.session_state.analytics = {
        "club_details_submit": 0,
        "checklist_add": 0,
        "starting_11_submit": 0,
        "transfer_calc_submit": 0,
        "save_load": 0
    }
if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False

# Welcome modal
if not st.session_state.welcome_shown:
    st.markdown(
        """
        <div id="welcome-modal">
            <h3>Welcome to FIFA Realistic Toolkit!</h3>
            <p>Start by entering your club details in the first tab. Use the checklist to track transfers and the calculators to make realistic bids.</p>
            <button onclick="document.getElementById('welcome-modal').style.display='none';">Got it!</button>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.session_state.welcome_shown = True

# App title
st.title("FIFA Realistic Toolkit")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Club Details", "Career Checklist", "Starting 11", "Transfer Calculators", "Help/Info", "Save/Load"])

# Tab 1: Club Details
with tab1:
    st.header("Your Club Details")
    with st.expander("How to Use This Tool"):
        st.write(
            """
            Enter your club details below to calculate team stature and guide transfers.
            Use the Save/Load tab to save or upload your data.
            """
        )
    
    # Progress indicator
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
            <div class="custom-progress-bar" style="width: {club_progress_percentage}%;">{club_progress_percentage}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("**Required**: League, Country, European status.")

    if st.session_state.scout_rating_display:
        st.success(st.session_state.scout_rating_display)

    with st.expander("Enter Club Details", expanded=True):
        with st.form(key="club_details_form"):
            club_name = st.text_input(
                "Club Name",
                value=st.session_state.club_details["name"],
                key="club_name",
                help="Enter your club's name (e.g., Manchester United)."
            )
            club_league = st.selectbox(
                "League/Division",
                list(league_tiers.keys()),
                index=list(league_tiers.keys()).index(st.session_state.club_details["league"]),
                key="form_league",
                help="Select the league your club plays in."
            )
            club_country = st.selectbox(
                "Country",
                list(country_prestige.keys()),
                index=list(country_prestige.keys()).index(st.session_state.club_details["country"]),
                key="club_country",
                help="Select your club's country."
            )
            club_european = st.checkbox(
                "Participates in European Competitions (e.g., Champions League)",
                value=st.session_state.club_details["european"],
                key="club_european",
                help="Check if your club is in UEFA competitions."
            )
            submit_club_details = st.form_submit_button("Save Club Details", help="Save your club details.")
        
        if submit_club_details:
            st.session_state.club_details = {
                "name": club_name,
                "league": club_league,
                "country": club_country,
                "european": club_european
            }
            score = calculate_score(club_league, club_country, club_european, league_tiers)
            if club_league == "First Division" and club_european:
                scout_rating = 10
                message = f"Scout Star Rating: {scout_rating} stars (Stature: {score:.1f}). Can assign worldwide."
            elif club_league == "First Division" and not club_european:
                scout_rating = 8
                message = f"Scout Star Rating: {scout_rating} stars (Stature: {score:.1f}). Can assign to local continent and neighbouring continents."
            elif club_league == "Second Division":
                scout_rating = 6
                message = f"Scout Star Rating: {scout_rating} stars (Stature: {score:.1f}). Can assign to local continent."
            elif club_league == "Third Division":
                scout_rating = 4
                message = f"Scout Star Rating: {scout_rating} stars (Stature: {score:.1f}). Can assign to local country and neighbouring countries."
            else:
                scout_rating = 2
                message = f"Scout Star Rating: {scout_rating} stars (Stature: {score:.1f}). Can assign to local country."
            st.session_state.scout_rating_display = message
            st.session_state.analytics["club_details_submit"] += 1

# Tab 2: Career Checklist
with tab2:
    st.header("Career Checklist")
    with st.expander("Checklist Guidelines"):
        st.write("Track your signings, sales, and youth promotions to stay within FIFA career mode guidelines.")

    if st.button("Reset for New Season", key="reset_checklist", help="Reset all checklist data for a new season."):
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
                "starting_sold": 0
            },
            "youth_promotions": 0
        }
        st.session_state.checklist_history = []
        st.session_state.pop("summer_signing_category", None)
        st.session_state.pop("winter_signing_category", None)
        st.session_state.pop("summer_loan_mode", None)
        st.session_state.pop("winter_loan_mode", None)
        st.success("Checklist reset for the new season!")
        st.session_state.analytics["checklist_add"] += 1

    if st.button("Undo Last Action", key="undo_checklist", help="Revert the last checklist action."):
        if st.session_state.checklist_history:
            st.session_state.checklist = st.session_state.checklist_history.pop()
            st.success("Last checklist action undone!")
            st.session_state.analytics["checklist_add"] += 1

    # Summer Window
    with st.expander("Summer Window", expanded=True):
        st.subheader("Summer Window Guidelines")
        summer_starting_max = 2
        summer_bench_max = 2
        summer_reserve_max = 3
        summer_loan_max = 3
        summer_starting_extra = 1 if st.session_state.checklist["summer"]["starting_sold"] >= 2 else 0
        summer_starting_total_max = summer_starting_max + summer_starting_extra
        summer_bench_total_max = summer_bench_max + summer_starting_extra
        summer_data = st.session_state.checklist["summer"]
        st.markdown(
            """
            <table style="width:100%; border-collapse: collapse; margin-bottom: 1rem;">
                <tr style="background-color: #2c3e50; color: white;">
                    <th>Category</th>
                    <th>Current Count</th>
                    <th>Max Limit</th>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>First Team Signings</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Bench Signings</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Reserve Signings</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Loans</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Starting Players Sold</td>
                    <td>{}</td>
                    <td>-</td>
                </tr>
            </table>
            """.format(
                summer_data["starting_signings"],
                summer_starting_total_max,
                summer_data["bench_signings"],
                summer_bench_total_max,
                summer_data["reserve_signings"],
                summer_reserve_max,
                summer_data["loans"],
                summer_loan_max,
                summer_data["starting_sold"]
            ),
            unsafe_allow_html=True
        )
        if summer_starting_extra:
            st.markdown("*Extra signing unlocked (2 starting players sold)!*")

        # Chart for Summer Window
        chart_data = {
            "labels": ["Starting Signings", "Bench Signings", "Reserve Signings", "Loans"],
            "values": [
                summer_data["starting_signings"],
                summer_data["bench_signings"],
                summer_data["reserve_signings"],
                summer_data["loans"]
            ],
            "limits": [summer_starting_total_max, summer_bench_total_max, summer_reserve_max, summer_loan_max]
        }
        st.markdown(
            f"""
            ```chartjs
            {{
                "type": "bar",
                "data": {{
                    "labels": {json.dumps(chart_data["labels"])},
                    "datasets": [
                        {{
                            "label": "Current",
                            "data": {json.dumps(chart_data["values"])},
                            "backgroundColor": "#28a745",
                            "borderColor": "#ffffff",
                            "borderWidth": 1
                        }},
                        {{
                            "label": "Limit",
                            "data": {json.dumps(chart_data["limits"])},
                            "backgroundColor": "#3498db",
                            "borderColor": "#ffffff",
                            "borderWidth": 1
                        }}
                    ]
                }},
                "options": {{
                    "indexAxis": "y",
                    "scales": {{
                        "x": {{
                            "beginAtZero": true,
                            "title": {{ "display": true, "text": "Count", "color": "#ffffff" }},
                            "ticks": {{ "color": "#ffffff" }}
                        }},
                        "y": {{
                            "title": {{ "display": true, "text": "Category", "color": "#ffffff" }},
                            "ticks": {{ "color": "#ffffff" }}
                        }}
                    }},
                    "plugins": {{
                        "legend": {{ "labels": {{ "color": "#ffffff" }} }}
                    }}
                }}
            }}
            ```
            """,
            unsafe_allow_html=True
        )

        if st.button("Did you make a signing?", key="summer_signing_question", help="Record a new signing for the summer window."):
            st.session_state["summer_signing_mode"] = True
            st.session_state.analytics["checklist_add"] += 1
        if st.session_state.get("summer_signing_mode", False):
            with st.container():
                if st.button("First Team Player", key="summer_starting_add", help="Add a first team signing."):
                    st.session_state["summer_signing_category"] = "starting"
                    st.session_state["summer_loan_mode"] = True
                    st.session_state["summer_signing_mode"] = False
                    st.session_state.analytics["checklist_add"] += 1
                if st.button("Bench Player", key="summer_bench_add", help="Add a bench signing."):
                    st.session_state["summer_signing_category"] = "bench"
                    st.session_state["summer_loan_mode"] = True
                    st.session_state["summer_signing_mode"] = False
                    st.session_state.analytics["checklist_add"] += 1
                if st.button("Reserve Player", key="summer_reserve_add", help="Add a reserve signing."):
                    st.session_state["summer_signing_category"] = "reserve"
                    st.session_state["summer_loan_mode"] = True
                    st.session_state["summer_signing_mode"] = False
                    st.session_state.analytics["checklist_add"] += 1
        if st.session_state.get("summer_loan_mode", False):
            st.write("Is this a loan?")
            with st.container():
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Yes", key="summer_loan_yes", help="Record the signing as a loan."):
                        st.session_state.checklist_history.append(st.session_state.checklist.copy())
                        if st.session_state.checklist["summer"]["loans"] < summer_loan_max:
                            if st.session_state["summer_signing_category"] == "starting" and st.session_state.checklist["summer"]["starting_signings"] < summer_starting_total_max:
                                st.session_state.checklist["summer"]["starting_signings"] += 1
                                st.session_state.checklist["summer"]["loans"] += 1
                                st.success("First team loan signing added!")
                            elif st.session_state["summer_signing_category"] == "bench" and st.session_state.checklist["summer"]["bench_signings"] < summer_bench_total_max:
                                st.session_state.checklist["summer"]["bench_signings"] += 1
                                st.session_state.checklist["summer"]["loans"] += 1
                                st.success("Bench loan signing added!")
                            elif st.session_state["summer_signing_category"] == "reserve" and st.session_state.checklist["summer"]["reserve_signings"] < summer_reserve_max:
                                st.session_state.checklist["summer"]["reserve_signings"] += 1
                                st.session_state.checklist["summer"]["loans"] += 1
                                st.success("Reserve loan signing added!")
                            else:
                                st.error(f"Exceeded {st.session_state['summer_signing_category']} signings limit!")
                        else:
                            st.error("Exceeded loan limit!")
                        st.session_state.pop("summer_signing_category", None)
                        st.session_state.pop("summer_loan_mode", None)
                        st.session_state.analytics["checklist_add"] += 1
                with col2:
                    if st.button("No", key="summer_loan_no", help="Record the signing as permanent."):
                        st.session_state.checklist_history.append(st.session_state.checklist.copy())
                        if st.session_state["summer_signing_category"] == "starting" and st.session_state.checklist["summer"]["starting_signings"] < summer_starting_total_max:
                            st.session_state.checklist["summer"]["starting_signings"] += 1
                            st.success("First team signing added!")
                        elif st.session_state["summer_signing_category"] == "bench" and st.session_state.checklist["summer"]["bench_signings"] < summer_bench_total_max:
                            st.session_state.checklist["summer"]["bench_signings"] += 1
                            st.success("Bench signing added!")
                        elif st.session_state["summer_signing_category"] == "reserve" and st.session_state.checklist["summer"]["reserve_signings"] < summer_reserve_max:
                            st.session_state.checklist["summer"]["reserve_signings"] += 1
                            st.success("Reserve signing added!")
                        else:
                            st.error(f"Exceeded {st.session_state['summer_signing_category']} signings limit!")
                        st.session_state.pop("summer_signing_category", None)
                        st.session_state.pop("summer_loan_mode", None)
                        st.session_state.analytics["checklist_add"] += 1

        st.markdown('<div class="checklist-section"><strong>Starting Players Sold (Unlocks Extra Signing at 2)</strong></div>', unsafe_allow_html=True)
        if st.button("Add Sold Player", key="summer_sale_add", help="Record a starting player sold."):
            st.session_state.checklist_history.append(st.session_state.checklist.copy())
            st.session_state.checklist["summer"]["starting_sold"] += 1
            st.success("Starting player sold added!")
            st.session_state.analytics["checklist_add"] += 1
        if st.session_state.checklist["summer"]["starting_sold"] > 0:
            if st.button("Remove Sold Player", key="summer_sale_remove", help="Remove a starting player sold."):
                st.session_state.checklist_history.append(st.session_state.checklist.copy())
                st.session_state.checklist["summer"]["starting_sold"] -= 1
                st.success("Starting player sold removed!")
                st.session_state.analytics["checklist_add"] += 1

    # Winter Window
    with st.expander("Winter Window", expanded=False):
        st.subheader("Winter Window Guidelines")
        winter_starting_max = 1
        winter_bench_max = 1
        winter_reserve_max = 2
        winter_loan_max = 1
        winter_starting_extra = 1 if st.session_state.checklist["winter"]["starting_sold"] >= 2 else 0
        winter_starting_total_max = winter_starting_max + winter_starting_extra
        winter_bench_total_max = winter_bench_max + winter_starting_extra
        winter_data = st.session_state.checklist["winter"]
        st.markdown(
            """
            <table style="width:100%; border-collapse: collapse; margin-bottom: 1rem;">
                <tr style="background-color: #2c3e50; color: white;">
                    <th>Category</th>
                    <th>Current Count</th>
                    <th>Max Limit</th>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>First Team Signings</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Bench Signings</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Reserve Signings</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Loans</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Starting Players Sold</td>
                    <td>{}</td>
                    <td>-</td>
                </tr>
            </table>
            """.format(
                winter_data["starting_signings"],
                winter_starting_total_max,
                winter_data["bench_signings"],
                winter_bench_total_max,
                winter_data["reserve_signings"],
                winter_reserve_max,
                winter_data["loans"],
                winter_loan_max,
                winter_data["starting_sold"]
            ),
            unsafe_allow_html=True
        )
        if winter_starting_extra:
            st.markdown("*Extra signing unlocked (2 starting players sold)!*")

        # Chart for Winter Window
        chart_data = {
            "labels": ["Starting Signings", "Bench Signings", "Reserve Signings", "Loans"],
            "values": [
                winter_data["starting_signings"],
                winter_data["bench_signings"],
                winter_data["reserve_signings"],
                winter_data["loans"]
            ],
            "limits": [winter_starting_total_max, winter_bench_total_max, winter_reserve_max, winter_loan_max]
        }
        st.markdown(
            f"""
            ```chartjs
            {{
                "type": "bar",
                "data": {{
                    "labels": {json.dumps(chart_data["labels"])},
                    "datasets": [
                        {{
                            "label": "Current",
                            "data": {json.dumps(chart_data["values"])},
                            "backgroundColor": "#28a745",
                            "borderColor": "#ffffff",
                            "borderWidth": 1
                        }},
                        {{
                            "label": "Limit",
                            "data": {json.dumps(chart_data["limits"])},
                            "backgroundColor": "#3498db",
                            "borderColor": "#ffffff",
                            "borderWidth": 1
                        }}
                    ]
                }},
                "options": {{
                    "indexAxis": "y",
                    "scales": {{
                        "x": {{
                            "beginAtZero": true,
                            "title": {{ "display": true, "text": "Count", "color": "#ffffff" }},
                            "ticks": {{ "color": "#ffffff" }}
                        }},
                        "y": {{
                            "title": {{ "display": true, "text": "Category", "color": "#ffffff" }},
                            "ticks": {{ "color": "#ffffff" }}
                        }}
                    }},
                    "plugins": {{
                        "legend": {{ "labels": {{ "color": "#ffffff" }} }}
                    }}
                }}
            }}
            ```
            """,
            unsafe_allow_html=True
        )

        if st.button("Did you make a signing?", key="winter_signing_question", help="Record a new signing for the winter window."):
            st.session_state["winter_signing_mode"] = True
            st.session_state.analytics["checklist_add"] += 1
        if st.session_state.get("winter_signing_mode", False):
            with st.container():
                if st.button("First Team Player", key="winter_starting_add", help="Add a first team signing."):
                    st.session_state["winter_signing_category"] = "starting"
                    st.session_state["winter_loan_mode"] = True
                    st.session_state["winter_signing_mode"] = False
                    st.session_state.analytics["checklist_add"] += 1
                if st.button("Bench Player", key="winter_bench_add", help="Add a bench signing."):
                    st.session_state["winter_signing_category"] = "bench"
                    st.session_state["winter_loan_mode"] = True
                    st.session_state["winter_signing_mode"] = False
                    st.session_state.analytics["checklist_add"] += 1
                if st.button("Reserve Player", key="winter_reserve_add", help="Add a reserve signing."):
                    st.session_state["winter_signing_category"] = "reserve"
                    st.session_state["winter_loan_mode"] = True
                    st.session_state["winter_signing_mode"] = False
                    st.session_state.analytics["checklist_add"] += 1
        if st.session_state.get("winter_loan_mode", False):
            st.write("Is this a loan?")
            with st.container():
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Yes", key="winter_loan_yes", help="Record the signing as a loan."):
                        st.session_state.checklist_history.append(st.session_state.checklist.copy())
                        if st.session_state.checklist["winter"]["loans"] < winter_loan_max:
                            if st.session_state["winter_signing_category"] == "starting" and st.session_state.checklist["winter"]["starting_signings"] < winter_starting_total_max:
                                st.session_state.checklist["winter"]["starting_signings"] += 1
                                st.session_state.checklist["winter"]["loans"] += 1
                                st.success("First team loan signing added!")
                            elif st.session_state["winter_signing_category"] == "bench" and st.session_state.checklist["winter"]["bench_signings"] < winter_bench_total_max:
                                st.session_state.checklist["winter"]["bench_signings"] += 1
                                st.session_state.checklist["winter"]["loans"] += 1
                                st.success("Bench loan signing added!")
                            elif st.session_state["winter_signing_category"] == "reserve" and st.session_state.checklist["winter"]["reserve_signings"] < winter_reserve_max:
                                st.session_state.checklist["winter"]["reserve_signings"] += 1
                                st.session_state.checklist["winter"]["loans"] += 1
                                st.success("Reserve loan signing added!")
                            else:
                                st.error(f"Exceeded {st.session_state['winter_signing_category']} signings limit!")
                        else:
                            st.error("Exceeded loan limit!")
                        st.session_state.pop("winter_signing_category", None)
                        st.session_state.pop("winter_loan_mode", None)
                        st.session_state.analytics["checklist_add"] += 1
                with col2:
                    if st.button("No", key="winter_loan_no", help="Record the signing as permanent."):
                        st.session_state.checklist_history.append(st.session_state.checklist.copy())
                        if st.session_state["winter_signing_category"] == "starting" and st.session_state.checklist["winter"]["starting_signings"] < winter_starting_total_max:
                            st.session_state.checklist["winter"]["starting_signings"] += 1
                            st.success("First team signing added!")
                        elif st.session_state["winter_signing_category"] == "bench" and st.session_state.checklist["winter"]["bench_signings"] < winter_bench_total_max:
                            st.session_state.checklist["winter"]["bench_signings"] += 1
                            st.success("Bench signing added!")
                        elif st.session_state["winter_signing_category"] == "reserve" and st.session_state.checklist["winter"]["reserve_signings"] < winter_reserve_max:
                            st.session_state.checklist["winter"]["reserve_signings"] += 1
                            st.success("Reserve signing added!")
                        else:
                            st.error(f"Exceeded {st.session_state['winter_signing_category']} signings limit!")
                        st.session_state.pop("winter_signing_category", None)
                        st.session_state.pop("winter_loan_mode", None)
                        st.session_state.analytics["checklist_add"] += 1

        st.markdown('<div class="checklist-section"><strong>Starting Players Sold (Unlocks Extra Signing at 2)</strong></div>', unsafe_allow_html=True)
        if st.button("Add Sold Player", key="winter_sale_add", help="Record a starting player sold."):
            st.session_state.checklist_history.append(st.session_state.checklist.copy())
            st.session_state.checklist["winter"]["starting_sold"] += 1
            st.success("Starting player sold added!")
            st.session_state.analytics["checklist_add"] += 1
        if st.session_state.checklist["winter"]["starting_sold"] > 0:
            if st.button("Remove Sold Player", key="winter_sale_remove", help="Remove a starting player sold."):
                st.session_state.checklist_history.append(st.session_state.checklist.copy())
                st.session_state.checklist["winter"]["starting_sold"] -= 1
                st.success("Starting player sold removed!")
                st.session_state.analytics["checklist_add"] += 1

    # Youth Academy
    with st.expander("Youth Academy", expanded=False):
        st.subheader("Youth Academy Guidelines")
        st.write("A total of 3 players can be promoted to the senior team.")
        youth_promotion_max = 3
        st.markdown(
            """
            <table style="width:100%; border-collapse: collapse; margin-bottom: 1rem;">
                <tr style="background-color: #2c3e50; color: white;">
                    <th>Category</th>
                    <th>Current Count</th>
                    <th>Max Limit</th>
                </tr>
                <tr style="background-color: #34495e; color: white;">
                    <td>Youth Promotions</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            </table>
            """.format(
                st.session_state.checklist["youth_promotions"],
                youth_promotion_max
            ),
            unsafe_allow_html=True
        )
        if st.button("I promoted a youth player", key="youth_promotion_add", help="Record a youth player promotion."):
            st.session_state.checklist_history.append(st.session_state.checklist.copy())
            if st.session_state.checklist["youth_promotions"] < youth_promotion_max:
                st.session_state.checklist["youth_promotions"] += 1
                st.success("Youth player promoted!")
                st.session_state.analytics["checklist_add"] += 1
            else:
                st.error("Exceeded youth promotion limit of 3!")
        if st.session_state.checklist["youth_promotions"] > 0:
            if st.button("Remove Youth Promotion", key="youth_promotion_remove", help="Remove a youth player promotion."):
                st.session_state.checklist_history.append(st.session_state.checklist.copy())
                st.session_state.checklist["youth_promotions"] -= 1
                st.success("Youth promotion removed!")
                st.session_state.analytics["checklist_add"] += 1

# Tab 3: Starting 11
with tab3:
    st.header("Starting 11 Calculator")
    with st.expander("How to Use This Tool"):
        st.write("Enter your starting 11 to calculate team average overall and wage cap. Use the Save/Load tab to save your data.")
    
    valid_players = sum(1 for player in st.session_state.starting_11 if player["overall"] > 0) / 11
    starting_11_progress_percentage = int(valid_players * 100)
    starting_11_progress_color = "#28a745" if valid_players == 1 else "#3498db"
    st.markdown(
        f"""
        <div style="margin-bottom: 5px;">Starting 11 Completion: {starting_11_progress_percentage}%</div>
        <div class="custom-progress-container">
            <div class="custom-progress-bar" style="width: {starting_11_progress_percentage}%;">{starting_11_progress_percentage}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Real-time feedback
    if st.session_state.starting_11 and len(st.session_state.starting_11) == 11:
        total_overall = sum(player["overall"] for player in st.session_state.starting_11)
        avg_overall = math.floor(total_overall / 11) if total_overall > 0 else 0
        valid_wages = [player["wage"] for player in st.session_state.starting_11 if player.get("wage", 0) > 0]
        max_wage = max(valid_wages) if valid_wages else 0
        wage_cap = int(max_wage * 1.2)
        st.info(f"Current Average Overall: {avg_overall} | Wage Cap: {wage_cap:,} p/w")
    else:
        st.warning("Starting 11 data is incomplete. Please enter all player details.")
        avg_overall = 0
        wage_cap = 0

    with st.expander("Enter Starting 11 Details", expanded=True):
        edited_starting_11 = st.data_editor(
            st.session_state.starting_11,
            column_config={
                "position": st.column_config.SelectboxColumn(
                    label="Position",
                    options=player_positions,
                    required=True,
                    help="Select the player's position."
                ),
                "overall": st.column_config.NumberColumn(
                    label="Overall",
                    min_value=0,
                    max_value=99,
                    step=1,
                    required=True,
                    help="Enter the player's overall rating (0-99)."
                ),
                "wage": st.column_config.NumberColumn(
                    label="Wage (p/w)",
                    min_value=0,
                    step=1000,
                    required=True,
                    help="Enter the player's weekly wage in pounds."
                )
            },
            num_rows="fixed",
            key="starting_11_editor"
        )
        if st.button("Save Starting 11", key="save_starting_11", help="Save and calculate team overall."):
            if all(player["overall"] >= 0 and player["wage"] >= 0 for player in edited_starting_11):
                st.session_state.starting_11 = edited_starting_11
                st.session_state.average_team_overall = avg_overall
                max_signing_overall = avg_overall + 2
                st.success(f"Average Team Overall: {avg_overall}")
                st.success(f"Sign players with overall {max_signing_overall} or below.")
                st.success(f"Wage Cap: {wage_cap:,} p/w")
                st.session_state.analytics["starting_11_submit"] += 1
            else:
                st.error("All player overalls and wages must be non-negative.")

    # Position distribution chart
    position_counts = {}
    for player in st.session_state.starting_11:
        pos = player["position"]
        position_counts[pos] = position_counts.get(pos, 0) + 1
    st.markdown(
        f"""
        ```chartjs
        {{
            "type": "pie",
            "data": {{
                "labels": {json.dumps(list(position_counts.keys()))},
                "datasets": [{{
                    "data": {json.dumps(list(position_counts.values()))},
                    "backgroundColor": ["#28a745", "#3498db", "#e74c3c", "#f1c40f", "#9b59b6"],
                    "borderColor": "#ffffff",
                    "borderWidth": 1
                }}]
            }},
            "options": {{
                "plugins": {{
                    "legend": {{
                        "position": "right",
                        "labels": {{ "color": "#ffffff" }}
                    }}
                }}
            }}
        }}
        ```
        """,
        unsafe_allow_html=True
    )

# Tab 4: Transfer Calculators
with tab4:
    st.header("Transfer Calculators")
    
    with st.expander("Selling Transfer Calculator", expanded=False):
        with st.form(key="selling_transfer_form"):
            st.subheader("Offering Club Details")
            club2_name_sell = st.text_input(
                "Offering Club Name (Optional)",
                key="club2_name_sell",
                help="Enter the name of the club making the offer (optional)."
            )
            club2_league_sell = st.selectbox(
                "Offering Club League",
                list(league_tiers.keys()),
                key="club2_league_sell",
                help="Select the league of the offering club."
            )
            club2_country_sell = st.selectbox(
                "Offering Club Country",
                list(country_prestige.keys()),
                key="club2_country_sell",
                help="Select the country of the offering club."
            )
            club2_european_sell = st.checkbox(
                "Offering Club in European Competitions",
                key="club2_european_sell",
                help="Check if the offering club is in UEFA competitions."
            )
            st.subheader("Transfer Details")
            player_value_sell = st.number_input(
                "Player Value",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key="player_value_sell",
                help="Enter the player's market value in FIFA (e.g., 1000000 for €1M)."
            )
            is_young_sell = st.checkbox(
                "Player Aged 16-21",
                key="is_young_sell",
                help="Check if the player is aged 16-21 for age-based transfer calculations."
            )
            submit_selling_transfer = st.form_submit_button("Calculate Selling Offer", help="Calculate the minimum offer to accept.")
        
        if submit_selling_transfer:
            if player_value_sell > 0:
                club_details = st.session_state.club_details
                score1 = calculate_score(club_details["league"], club_details["country"], club_details["european"], league_tiers)
                score2 = calculate_score(club2_league_sell, club2_country_sell, club2_european_sell, league_tiers)
                stature_diff = score2 - score1
                display_name1 = club_details["name"] if club_details["name"] else "Your Club"
                display_name2 = club2_name_sell if club2_name_sell else "Offering Club"
                st.write(f"**{display_name1}**: {club_details['league']}, {club_details['country']}, European: {club_details['european']}")
                st.write(f"**Stature Score**: {score1:.1f} (How prestigious your club is)")
                st.write(f"**{display_name2}**: {club2_league_sell}, {club2_country_sell}, European: {club2_european_sell}")
                st.write(f"**Stature Score**: {score2:.1f} (How prestigious the offering club is)")
                if score1 > score2:
                    st.success(f"{display_name1} has higher stature by {score1 - score2:.1f}.")
                elif score2 > score1:
                    st.warning(f"{display_name2} has higher stature by {score2 - score1:.1f}.")
                else:
                    st.info("Clubs have equal stature.")
                minimum_offer = calculate_minimum_offer(player_value_sell, stature_diff, is_young_sell)
                minimum_offer = math.ceil(minimum_offer / 1000) * 1000
                st.success(f"Accept offers from {display_name2} of {minimum_offer:,.0f} or higher.")
                st.session_state.analytics["transfer_calc_submit"] += 1
            else:
                st.error("Player value must be greater than 0.")

    with st.expander("Buying Transfer Calculator", expanded=False):
        with st.form(key="buying_transfer_form"):
            st.subheader("Player Details")
            player_value_buy = st.number_input(
                "Player Value",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key="player_value_buy",
                help="Enter the player's market value in FIFA (e.g., 1000000 for €1M)."
            )
            player_overall_buy = st.number_input(
                "Player Overall",
                min_value=0,
                max_value=99,
                step=1,
                format="%d",
                key="player_overall_buy",
                help="Enter the player's overall rating (0-99)."
            )
            player_age_buy = st.number_input(
                "Player Age",
                min_value=16,
                max_value=40,
                step=1,
                format="%d",
                key="player_age_buy",
                help="Enter the player's age (16-40)."
            )
            submit_buying_transfer = st.form_submit_button("Calculate Bid and Wage", help="Calculate the starting bid and minimum wage.")
        
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
                st.session_state.analytics["transfer_calc_submit"] += 1
            else:
                st.error("Player value and overall must be greater than 0.")

# Tab 5: Help/Info
with tab5:
    st.header("Help & Info")
    st.write(
        """
        **FIFA Realistic Toolkit** helps you manage your FIFA career mode with realistic transfer and wage guidelines.
        
        - **Club Details**: Enter your club's league, country, and European status to calculate stature and determine maximum scout ratings.
        - **Career Checklist**: Track your signings, sales, and youth promotions to ensure compliance with transfer window rules.
        - **Starting 11**: Input your starting lineup to determine average overall and wage caps.
        - **Transfer Calculators**: Compute minimum selling offers and starting bids for buying players.
        - **Save/Load**: Save your progress as JSON or load previous data to continue your session.
        
        If you enjoy this tool, consider [buying me a coffee](https://buymeacoffee.com/whitespear11).
        """
    )

# Tab 6: Save/Load
with tab6:
    st.header("Save/Load Data")
    with st.expander("How to Save/Load"):
        st.write(
            """
            Save your progress by copying the JSON text or downloading it as team_data.json.
            Load a previous session by pasting JSON text or uploading a JSON file, then clicking 'Load Data'.
            Data includes club details, starting 11, and career checklist.
            """
        )

    st.subheader("Save Your Data")
    if st.session_state.club_details and st.session_state.starting_11 and st.session_state.checklist:
        combined_data = {
            "club_details": st.session_state.club_details,
            "starting_11": st.session_state.starting_11,
            "checklist": st.session_state.checklist
        }
        json_str = json.dumps(combined_data, indent=2)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_area(
                "Copy this JSON text or use the button to save as a file:",
                value=json_str,
                height=300,
                key="save_json",
                help="Copy this text to your clipboard or save it to a file (e.g., team_data.json)."
            )
        with col2:
            st.download_button(
                label="Save to JSON File",
                data=json_str,
                file_name="team_data.json",
                mime="application/json",
                key="download_json",
                use_container_width=True,
                help="Download your data as a JSON file."
            )
        if st.checkbox("Enable Auto-Save", key="auto_save", help="Automatically save data after changes."):
            st.download_button(
                label="Auto-Saving...",
                data=json_str,
                file_name="team_data_autosave.json",
                mime="application/json",
                key="auto_save_json",
                disabled=True
            )
    else:
        st.warning("No data to save. Please fill out Club Details, Starting 11, or Career Checklist first.")

    st.subheader("Load Your Data")
    col1, col2 = st.columns([3, 1])
    with col1:
        json_input = st.text_area(
            "Paste your JSON text here:",
            value="",
            height=300,
            key="load_json",
            help="Paste JSON text or upload a file to load data."
        )
    with col2:
        uploaded_file = st.file_uploader(
            "Upload JSON File",
            type=["json"],
            key="upload_json",
            help="Upload a team_data.json file to load its content."
        )
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
                checklist_valid = (
                    isinstance(loaded_data.get("checklist"), dict) and
                    "summer" in loaded_data["checklist"] and
                    "winter" in loaded_data["checklist"] and
                    "youth_promotions" in loaded_data["checklist"] and
                    isinstance(loaded_data["checklist"]["summer"], dict) and
                    isinstance(loaded_data["checklist"]["winter"], dict) and
                    isinstance(loaded_data["checklist"]["youth_promotions"], int) and
                    loaded_data["checklist"]["youth_promotions"] >= 0 and
                    all(
                        key in loaded_data["checklist"]["summer"]
                        for key in ["starting_signings", "bench_signings", "reserve_signings", "loans", "starting_sold"]
                    ) and
                    all(
                        key in loaded_data["checklist"]["winter"]
                        for key in ["starting_signings", "bench_signings", "reserve_signings", "loans", "starting_sold"]
                    ) and
                    all(
                        isinstance(loaded_data["checklist"]["summer"][key], int) and
                        loaded_data["checklist"]["summer"][key] >= 0
                        for key in loaded_data["checklist"]["summer"]
                    ) and
                    all(
                        isinstance(loaded_data["checklist"]["winter"][key], int) and
                        loaded_data["checklist"]["winter"][key] >= 0
                        for key in loaded_data["checklist"]["winter"]
                    )
                )
                if club_valid and starting_11_valid:
                    st.session_state.club_details = loaded_data["club_details"]
                    st.session_state.starting_11 = loaded_data["starting_11"]
                    st.session_state.checklist = loaded_data.get("checklist", st.session_state.checklist)
                    total_overall = sum(player["overall"] for player in loaded_data["starting_11"])
                    st.session_state.average_team_overall = math.floor(total_overall / 11)
                    score = calculate_score(
                        loaded_data["club_details"]["league"],
                        loaded_data["club_details"]["country"],
                        loaded_data["club_details"]["european"],
                        league_tiers
                    )
                    st.success(
                        f"Club data loaded: {loaded_data['club_details']['name'] or 'None'}, "
                        f"{loaded_data['club_details']['league']}, "
                        f"{loaded_data['club_details']['country']}, "
                        f"European: {loaded_data['club_details']['european']}. "
                        f"Stature: {score:.1f}"
                    )
                    st.session_state.analytics["save_load"] += 1
                    st.rerun()
                else:
                    st.error("Invalid JSON format or data. Ensure 'club_details' and 'starting_11' are correctly formatted.")
            except json.JSONDecodeError:
                st.error("Invalid JSON file uploaded.")
        if st.button("Load Data", key="load_data_button", help="Load data from pasted JSON text."):
            if json_input:
                try:
                    loaded_data = json.loads(json_input)
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
                    checklist_valid = (
                        isinstance(loaded_data.get("checklist"), dict) and
                        "summer" in loaded_data["check