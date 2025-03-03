import streamlit as st
from bs4 import BeautifulSoup
import requests

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

    # Extract time spent for phases
    for phase in phases:
        phase_name = phase.find('a', class_='discreet').text.strip()
        duration_text = phase.find('div', class_='duration-and-load-infos').text.strip()
        duration_match = re.search(r'(\d+,\d+|\d+)\s+jours?', duration_text)
        duration = float(duration_match.group(1).replace(',', '.')) if duration_match else 0
        phase_time_spent[phase_name] = duration

    # Extract time spent for actions
    for action in actions:
        action_name = action.find('a', class_='discreet').text.strip()
        duration_text = action.find('div', class_='duration-and-load-infos').text.strip()
        duration_match = re.search(r'(\d+,\d+|\d+)\s+jours?', duration_text)
        duration = float(duration_match.group(1).replace(',', '.')) if duration_match else 0
        action_time_spent[action_name] = duration

    return phase_time_spent, action_time_spent

# Example usage
# code_source = ...  # The HTML content of the page
# phase_time, action_time = extract_time_spent(code_source)
# print("Time spent by phases:", phase_time)
# print("Time spent by actions:", action_time)

st.title('Analyse du temps passé sur ATK')

# Demander à l'utilisateur de saisir une adresse
url = st.text_input("saisir l'URL de la page planning atikteam:")

if address:
    st.write("Adresse saisie : ", url)  # Vérification de l'entrée utilisateur

    # Obtenir la latitude et la longitude à partir de l'adresse
    code_source = get_html_content(url)
    
    if code_source is not None:
        st.write("URL existante")

        # Obtenir les stations météo les plus proches
        phase_time_spent, action_time_spent = extract_time_spent(code_source)

        if not nearby_stations.empty:
            st.write("Données trouvées :")

        else:
            st.write("Aucune donnée tourvée.")
    else:
        st.write("UTL non valide ou introuvable.")
