import streamlit as st
import os
import sys
import io
import csv
import json
import time
from fpdf import FPDF

# -------------------------------
# Configuration de la page Streamlit
# -------------------------------
st.set_page_config(
    page_title="Analyse de Vidéo",
    layout="wide",
    page_icon="🎬"
)

# -------------------------------
# Ajout du chemin racine pour pouvoir importer le backend
# -------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -------------------------------
# Import des modules backend
# -------------------------------
from VideoManager import VideoManager
from api import generate_content


# -------------------------------
# Initialisation de l'état de session
# -------------------------------
if "description" not in st.session_state:
    st.session_state["description"] = ""
if "video_file" not in st.session_state:
    st.session_state["video_file"] = None  # Va contenir le nom de la vidéo (upload_name)
if "video_filename" not in st.session_state:
    st.session_state["video_filename"] = None
if "custom_prompt" not in st.session_state:
    st.session_state["custom_prompt"] = ""
if "custom_prompt_confirmed" not in st.session_state:
    st.session_state["custom_prompt_confirmed"] = False
if "analyze_requested" not in st.session_state:
    st.session_state["analyze_requested"] = False

# -------------------------------
# Fonction pour saisir le prompt personnalisé
# -------------------------------
def custom_prompt_dialog():
    st.markdown("### Veuillez saisir votre prompt personnalisé")
    prompt_value = st.text_area(
        "Entrez votre prompt :",
        value=st.session_state.get("custom_prompt", ""),
        height=100
    )
    if st.button("Confirmer le prompt"):
        st.session_state["custom_prompt"] = prompt_value
        st.session_state["custom_prompt_confirmed"] = True
        st.experimental_rerun()

# -------------------------------
# Fonction d'analyse de la vidéo via le backend
# -------------------------------
def analyze_video(video_upload_name, task, custom_prompt=""):
    with st.spinner("Analyse en cours..."):
        progress_bar = st.progress(0)
        steps = [
            "Étape 1 : Traitement du fichier",
            "Étape 2 : Appel à l'API Gemini",
            "Étape 3 : Récupération du résultat"
        ]
        for i, step in enumerate(steps):
            st.write(step)
            time.sleep(1)  # Simulation du temps de traitement
            progress_bar.progress(int((i + 1) / len(steps) * 100))
        # Appel du backend pour générer le contenu
        result = generate_content(video_upload_name, task, custom_prompt=custom_prompt)
        st.session_state["description"] = result
    st.success("Analyse terminée !")

# -------------------------------
# Configuration de la Sidebar
# -------------------------------
st.sidebar.image("images/Esme-sudria-logo.png", width=150)
st.sidebar.title("Options")

# Choix du modèle de vision (affichage uniquement ici)
model = st.sidebar.selectbox(
    "Choisir le modèle de vision :",
    ["LLama Vision", "gpt4 with vision"]
)

# Choix du mode de description/prompt
mode = st.sidebar.selectbox(
    "Mode de description :",
    [
        "description de la scène",
        "description des sous titres",
        "description de la scène + des sous titres",
        "prompt custom"
    ]
)

# Fonction de mapping du mode de description aux tâches backend
def map_mode_to_task(mode_choice):
    if mode_choice == "description de la scène":
        return "SUMMARIZE"
    elif mode_choice == "description des sous titres":
        return "AUDIO_SUMMARY"
    elif mode_choice == "description de la scène + des sous titres":
        return "TIMESTAMPS"  # Ou adapter selon ton besoin
    elif mode_choice == "prompt custom":
        return "CUSTOM_PROMPT"
    else:
        return "SUMMARIZE"

selected_task = map_mode_to_task(mode)

# File uploader pour ajouter une nouvelle vidéo
uploaded_file = st.sidebar.file_uploader(
    "Charger une vidéo",
    type=["mp4", "avi", "mov", "mkv"]
)

# Instanciation du VideoManager du backend
vm = VideoManager()

# Si un fichier est uploadé, on le sauvegarde dans le dossier videos/ et on l'upload via le backend
if uploaded_file is not None:
    video_save_path = os.path.join("videos", uploaded_file.name)
    with open(video_save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    vm.upload_video(video_save_path)
    st.sidebar.success("Vidéo uploadée avec succès !")
    st.experimental_rerun()

# Affichage de la liste des vidéos disponibles récupérées par le backend
st.sidebar.markdown("---")
st.sidebar.subheader("Vidéos disponibles")
for video in vm.videos:
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        st.image(video["thumbnail_filename"], width=80)
    with col2:
        st.write(f"**{video['upload_name']}**")
    # Bouton de sélection pour charger la vidéo
    if st.sidebar.button(f"Charger {video['upload_name']}"):
        st.session_state["video_file"] = video["upload_name"]
        st.session_state["video_filename"] = video["upload_name"]
        st.session_state["description"] = ""
        st.session_state["custom_prompt_confirmed"] = False
        st.experimental_rerun()

# Bouton pour lancer l'analyse
if st.sidebar.button("Analyser la vidéo"):
    st.session_state["analyze_requested"] = True

# Si le mode est "prompt custom" et que le prompt n'est pas encore confirmé, affiche la saisie du prompt
if selected_task == "CUSTOM_PROMPT" and not st.session_state["custom_prompt_confirmed"]:
    custom_prompt_dialog()
    st.stop()

# Si une analyse est demandée et qu'une vidéo est sélectionnée, lance l'analyse via le backend
if st.session_state["analyze_requested"] and st.session_state["video_file"] is not None:
    analyze_video(st.session_state["video_file"], selected_task, custom_prompt=st.session_state["custom_prompt"])
    st.session_state["analyze_requested"] = False

# -------------------------------
# Mise en page principale : affichage de la vidéo et de la description
# -------------------------------
col1, col2 = st.columns([2, 3])
with col1:
    st.header("Vidéo chargée")
    if st.session_state["video_file"] is not None:
        # On tente de charger la vidéo depuis le dossier videos/
        video_path = os.path.join("videos", st.session_state["video_file"])
        if os.path.exists(video_path):
            st.video(video_path)
        else:
            st.write("Vidéo introuvable.")
    else:
        st.write("Aucune vidéo n'est encore chargée.")
with col2:
    st.header("Description générée")
    if st.session_state["description"]:
        st.text_area("Description", st.session_state["description"], height=300)
    else:
        st.write("Aucune description disponible pour le moment.")

# -------------------------------
# Options d'export de la description
# -------------------------------
if st.session_state["description"]:
    st.subheader("Exporter la description")
    txt_data = st.session_state["description"]
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Description"])
    writer.writerow([st.session_state["description"]])
    csv_data = csv_buffer.getvalue()
    json_data = json.dumps({"description": st.session_state["description"]}, ensure_ascii=False)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, st.session_state["description"])
    pdf_data = pdf.output(dest="S").encode("latin-1")

    col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
    with col_exp1:
        st.download_button("TXT", txt_data, "description.txt", "text/plain")
    with col_exp2:
        st.download_button("CSV", csv_data, "description.csv", "text/csv")
    with col_exp3:
        st.download_button("JSON", json_data, "description.json", "application/json")
    with col_exp4:
        st.download_button("PDF", pdf_data, "description.pdf", "application/pdf")
