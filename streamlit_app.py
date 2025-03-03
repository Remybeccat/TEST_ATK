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
    test = []
    a = 0

    # Extract time spent for phases
    for phase in phases:
        a = a + 1
        phase_name = phase.find('a', class_='discreet').text.strip()
        print(phase_name)
        duration_text = phase.find('div', class_='duration-and-load-infos resource-info-box').text.strip()
        print(duration_text)
        duration_match = re.search(r'(\d+,\d+|\d+)\s+jours?', duration_text)
        print(duration_match)
        duration = float(duration_match.group(1).replace(',', '.')) if duration_match else 0
        print(duration)
        phase_time_spent[phase_name] = duration
        print(phase_time_spent)
        test.append([phase_name, duration_text, duration_match, duration, a])
    # Extract time spent for actions
    for action in actions:
        action_name = action.find('a', class_='discreet').text.strip()
        duration_text = action.find('div', class_='duration-and-load-infos').text.strip()
        duration_match = re.search(r'(\d+,\d+|\d+)\s+jours?', duration_text)
        duration = float(duration_match.group(1).replace(',', '.')) if duration_match else 0
        action_time_spent[action_name] = duration

    return phase_time_spent, action_time_spent, test, phases

# Example usage
# code_source = ...  # The HTML content of the page
# phase_time, action_time = extract_time_spent(code_source)
# print("Time spent by phases:", phase_time)
# print("Time spent by actions:", action_time)

st.title('Analyse du temps passé sur ATK')

# Demander à l'utilisateur de saisir une adresse
url = st.text_input("saisir l'URL de la page planning atikteam:")

if url is not None:
    st.write("Adresse saisie : ", url)  # Vérification de l'entrée utilisateur

    # Obtenir la latitude et la longitude à partir de l'adresse
    code_source = get_html_content(url)
    
    if code_source is not None:
        st.write("URL existante")

        # Obtenir les stations météo les plus proches
        phase_time_spent, action_time_spent, test, test_2 = extract_time_spent(code_source)
        st.write(test)
        st.write(test_2)
        if phase_time_spent is not None:
            st.write("Données trouvées :")
                        # Display phase time spent
            st.subheader("Temps passé par Phase")
            phase_df = pd.DataFrame(list(phase_time_spent.items()), columns=["Phase", "Temps passé (jours)"])
            st.table(phase_df)

            # Display action time spent
            st.subheader("Temps passé par Actions")
            action_df = pd.DataFrame(list(action_time_spent.items()), columns=["Action", "Temps passé (jours)"])
            st.table(action_df)
        else:
            st.write("Aucune donnée trouvée.")
    else:
        st.write("URL non valide ou introuvable.")
