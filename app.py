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
        background-color: # dépasse la limite de caractères, je vais donc fournir la section pertinente corrigée et m'assurer que l'artefact complet est disponible si nécessaire.

### Section Corrigée (Tab 6: Save/Load)
Voici la section corrigée pour l'onglet "Save/Load", en remplaçant la partie tronquée à la ligne 1543. Cette section complète le bloc `checklist_valid` et ferme correctement toutes les parenthèses et accolades.

```python
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
                if club_valid and starting_11_valid and checklist_valid:
                    st.session_state.club_details = loaded_data["club_details"]
                    st.session_state.starting_11 = loaded_data["starting_11"]
                    st.session_state.checklist = loaded_data["checklist"]
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
                    st.error("Invalid JSON format or data. Ensure 'club_details', 'starting_11', and 'checklist' are correctly formatted.")
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
                    if club_valid and starting_11_valid and checklist_valid:
                        st.session_state.club_details = loaded_data["club_details"]
                        st.session_state.starting_11 = loaded_data["starting_11"]
                        st.session_state.checklist = loaded_data["checklist"]
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
                        st.error("Invalid JSON format or data. Ensure 'club_details', 'starting_11', and 'checklist' are correctly formatted.")
                except json.JSONDecodeError:
                    st.error("Invalid JSON text pasted.")
```

### Modifications Effectuées
1. **Correction de l'Erreur de Syntaxe** : La condition `checklist_valid` a été complétée pour inclure toutes les vérifications nécessaires, en s'assurant que l'expression `"summer" in loaded_data["checklist"]` est correctement fermée et suivie des autres conditions.
2. **Validation Complète** : La logique vérifie que `checklist` est un dictionnaire avec les clés `"summer"`, `"winter"`, et `"youth_promotions"`, et que les sous-dictionnaires contiennent les clés requises avec des valeurs entières non négatives.
3. **Préservation de la Fonctionnalité** : Le reste du code dans l'onglet "Save/Load" (et les autres onglets) reste inchangé, sauf pour la correction de l'erreur de syntaxe.
4. **ID d'Artefact Conservé** : L'`artifact_id` reste `224fd0d7-c5b2-43ce-b176-744fcf8d0d3c`, car il s'agit d'une mise à jour de l'artefact existant.

### Étapes Suivantes
1. Remplacez le contenu de votre `app.py` par le code de l'artefact ci-dessus.
2. Exécutez l'application pour vérifier que l'erreur de syntaxe est résolue.
3. Testez la fonctionnalité "Load Data" en téléchargeant un fichier JSON ou en collant du texte JSON pour vous assurer que la validation fonctionne correctement.
4. Si d'autres erreurs surviennent (par exemple, liées à des données JSON invalides), fournissez un exemple de JSON que vous essayez de charger pour un dépannage supplémentaire.

Si vous avez besoin du fichier `app.py` complet (y compris les onglets précédents comme "Club Details", "Career Checklist", etc.), je peux fournir l'artefact entier dans une réponse ultérieure, bien que la section corrigée ci-dessus devrait suffire pour résoudre l'erreur de syntaxe. Faites-moi savoir si vous avez d'autres questions ou si vous rencontrez de nouvelles erreurs !