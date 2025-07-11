import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

st.write("L'application a démarré")  # Vérification initiale

def get_html_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        # Return the HTML content of the page
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def extract_time_spent(code_source):
    # Parse the HTML content
    soup = BeautifulSoup(code_source, 'html.parser')

    # Find all phases and actions
    phases = soup.find_all('li', class_='phase')
    actions = soup.find_all('li', class_='action')

    # Initialize dictionaries to store time spent
    phase_time_spent = {}
    action_time_spent = {}
    actions_by_phase = {}
    
    total_temps_phase = 0
        
    # Extract time spent for phases
    for phase in phases:
        phase_name = phase.find('a', class_='discreet').text.strip()
        duration_text = phase.find('div', class_='tooltip-info-button')['title']
        #st.write(duration_text)
        CP_text = re.search(r'\[(.*?)\]', duration_text)
        #st.write(CP_text)
        CP_text = CP_text.group(0).replace('[', '').replace(']', '')
        duration_match = re.search(r'(\d+,\d+|\d+)\s+j.?', duration_text)
        #st.write(duration_match)
        duration = float(duration_match.group(1).replace(',', '.')) if duration_match else 0
        total_temps_phase = total_temps_phase + duration
        #phase_time_spent[phase_name] = duration #- ANCIEN
            # Stocker les informations dans le dictionnaire
        phase_time_spent[phase_name] = {
            "Time Spent (days)": duration,
            "CP Text": CP_text
            }

        # Find actions within the current phase
        actions = phase.find_all('li', class_='action')
        actions_by_phase[phase_name] = []
        
        total_temps_action = 0
        total_temps_passe = 0
        for action in actions:
            action_name = action.find('a', class_='discreet').text.strip()
            action_duration_text = action.find('div', class_='tooltip-info-button')['title']
            action_duration_match = re.search(r'(\d+,\d+|\d+)\s+j.?', action_duration_text)
            action_duration = float(action_duration_match.group(1).replace(',', '.')) if action_duration_match else 0
            CP_name = re.search(r'\[(.*?)\]', action_duration_text)
            CP_name = CP_name.group(0).replace('[', '').replace(']', '')
            #st.write(CP_name)
            realisation_text = action.find('div', class_='progress_bar')['title']
            realisation_match = re.search(r'\:(.*?)\%', realisation_text)
            realisation = float(realisation_match.group(1).replace(',', '.')) if realisation_match else 0
            #st.write(realisation_text)
            #st.write(realisation_match)
            #st.write(realisation)
            actions_by_phase[phase_name].append((action_name, action_duration, CP_name, realisation))
            total_temps_passe = total_temps_passe + action_duration*realisation/100
            total_temps_action = total_temps_action + action_duration
        actions_by_phase[phase_name].append(("Total", total_temps_action, " " , total_temps_passe))
    return phase_time_spent, actions_by_phase

# Example usage
# code_source = ...  # The HTML content of the page
# phase_time, action_time = extract_time_spent(code_source)
# print("Time spent by phases:", phase_time)
# print("Time spent by actions:", action_time)

st.title('Analyse du temps passé sur ATK')

# Demander à l'utilisateur de saisir une adresse
url = st.text_input("saisir l'URL de la page planning atikteam:")

if url is not None:
    #st.write("Adresse saisie : ", url)  # Vérification de l'entrée utilisateur

    # Obtenir la latitude et la longitude à partir de l'adresse
    code_source = st.text_input("copier coller le code source:")
    
    if code_source is not None:
        phase_time_spent, actions_by_phase = extract_time_spent(code_source)

        if phase_time_spent is not None:
            st.write("Données trouvées :")
            # Display phase time spent
            # Display phase time spent
            st.subheader("Time Spent by Phases")
            #phase_df = pd.DataFrame(list(phase_time_spent.items()), columns=["Phase", "Time Spent (days)"]) #ANCIEN
            phase_data = [{"Phase": phase, "Time Spent (days)": details["Time Spent (days)"], "CP": details["CP Text"]} for phase, details in phase_time_spent.items()]
            phase_df = pd.DataFrame(phase_data)
            st.dataframe(phase_df)

            # Display actions by phase
            for phase_name, actions in actions_by_phase.items():
                st.subheader(f"Actions in Phase: {phase_name}")
                actions_df = pd.DataFrame(actions, columns=["Action", "Time Spent (days)", "CP", "% réalisé"])
                st.dataframe(actions_df)
        else:
            st.write("Aucune donnée trouvée.")
    else:
        st.write("URL non valide ou introuvable.")
