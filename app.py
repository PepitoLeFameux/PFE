import time
import streamlit as st
import io
import csv
import json
import os

from fpdf import FPDF
from moviepy import VideoFileClip
from VideoManager import VideoManager

SUMMARIZE = "Résumé de la vidéo"
TIMESTAMPS = "Liste des évènements avec timestamps"
AUDIO_SUMMARY = "Résumé audio"
AUDIO_TRANSCRIPTION = "Transcription audio"
CUSTOM_PROMPT = "Prompt customisé"

mode_to_task = {SUMMARIZE: 'SUMMARIZE',
                TIMESTAMPS: 'TIMESTAMPS',
                AUDIO_SUMMARY: 'AUDIO_SUMMARY',
                AUDIO_TRANSCRIPTION: 'AUDIO_TRANSCRIPTION',
                CUSTOM_PROMPT: 'CUSTOM_PROMPT'}

# Configuration de la page
st.set_page_config(
    page_title="Analyse de Vidéo (Simulation)",
    layout="wide",
    page_icon="🎬"
)

# Titre principal
st.title("Analyse de Vidéo (Simulation)")

manager = VideoManager()


if "description" not in st.session_state:
    st.session_state["description"] = ""
if "video_file" not in st.session_state:
    st.session_state["video_file"] = None
if "video_filename" not in st.session_state:
    st.session_state["video_filename"] = None
if "custom_prompt" not in st.session_state:
    st.session_state["custom_prompt"] = ""
if "custom_prompt_confirmed" not in st.session_state:
    st.session_state["custom_prompt_confirmed"] = False
if "analyze_requested" not in st.session_state:
    st.session_state["analyze_requested"] = False


# --- Fonction d'analyse de la vidéo ---
def analyze_video():
    with st.spinner("Analyse en cours..."):
        progress_bar = st.progress(0)
        steps = [
            "Étape 1 : Redimensionnement de la vidéo",
            "Étape 2 : Upload de la vidéo",
            "Étape 3 : Génération de la réponse",
            "Étape 4 : Suppression de la vidéo du cloud",
            "Étape 5 : Suppression de la vidéo redimensionnée temporaire"
        ]

        filename = 'videos/' + st.session_state["video_filename"]
        task = mode_to_task[mode]

        # Step 1
        st.write(steps[0])
        resized_filename = manager.resize_video(filename)
        progress_bar.progress(int(1 / len(steps) * 100))

        # Step 2
        st.write(steps[1])
        upload_name = manager.upload_video(resized_filename)
        progress_bar.progress(int(2 / len(steps) * 100))

        # Step 3
        st.write(steps[2])
        content = manager.generate_content(upload_name, task, st.session_state["custom_prompt"])
        progress_bar.progress(int(3 / len(steps) * 100))

        # Step 4
        st.write(steps[3])
        manager.remove_uploaded_video(upload_name)
        progress_bar.progress(int(4 / len(steps) * 100))

        # Step 5
        st.write(steps[4])
        manager.remove_resized_video(resized_filename)
        progress_bar.progress(int(5 / len(steps) * 100))

        description = (
            f"Modèle utilisé : {model}\n"
            f"Mode de description : {mode}\n\n"
            f"La vidéo a été analysée avec succès.\n"
            f"Contenu généré :\n"
            f"\n"
            f"{content}"
        )
        if mode == CUSTOM_PROMPT:
            description += f"\n\nPrompt custom utilisé : {st.session_state['custom_prompt']}"
        st.session_state["description"] = description
    st.success("Analyse terminée !")


# --- Fonction de dialog pour le prompt personnalisé ---
@st.dialog("Prompt personnalisé requis")
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
        st.rerun()  # Ferme la modale et relance l'app


# ------------------------
# Barre latérale (sidebar)
# ------------------------

st.sidebar.image("images/Esme-sudria-logo.png", width=150)
st.sidebar.title("Options")

# 1. Choix du modèle de vision
model = st.sidebar.selectbox(
    "Choisir le modèle de vision :",
    ["Gemini 1.5 Pro"]
)

# 2. Choix du mode de description (ajout du mode "prompt custom")
mode = st.sidebar.selectbox(
    "Type de prompt :",
    [
        SUMMARIZE,
        TIMESTAMPS,
        AUDIO_SUMMARY,
        AUDIO_TRANSCRIPTION,
        CUSTOM_PROMPT
    ]
)

# 3. Chargement de la vidéo via file_uploader
uploaded_file = st.sidebar.file_uploader(
    "Charger une vidéo",
    type=["mp4"]
)

# Bouton pour lancer le traitement
if st.sidebar.button("Analyser la vidéo"):
    st.session_state["analyze_requested"] = True

# Si l'analyse est demandée, on lance le traitement
if st.session_state["analyze_requested"]:
    # Pour le mode "prompt custom", si le prompt n'est pas confirmé, afficher la modale
    if mode == CUSTOM_PROMPT and not st.session_state["custom_prompt_confirmed"]:
        custom_prompt_dialog()
        st.stop()  # Attendre la confirmation du prompt
    # Détermine la vidéo à analyser (priorité au file uploader)
    if uploaded_file is not None:
        st.session_state["video_file"] = uploaded_file
        st.session_state["video_filename"] = uploaded_file.name
    elif st.session_state["video_file"] is None:
        st.warning("Veuillez d'abord sélectionner une vidéo ou en choisir une ci-dessous.")
    if st.session_state["video_file"] is not None:
        analyze_video()
        st.session_state["analyze_requested"] = False

# -----------------------
# Liste des vidéos locales
# -----------------------

st.sidebar.markdown("---")
st.sidebar.subheader("Vidéos disponibles")

video_folder = "videos"
local_videos = []
if not os.path.isdir(video_folder):
    os.makedirs(video_folder)

local_videos = [f for f in os.listdir(video_folder) if f.lower().endswith('mp4')]

for video_name in local_videos:
    path = os.path.join(video_folder, video_name)
    try:
        clip = VideoFileClip(path)
        duration = clip.duration  # en secondes
        fps = clip.fps
        frame = clip.get_frame(int(duration/2*fps))  # première frame pour miniature
        clip.close()
        c1, c2 = st.sidebar.columns([2, 3])
        with c1:
            st.image(frame, width=80)
        with c2:
            st.write(f"**{video_name}**\nDurée: {duration:.2f} sec")
            if st.button(f"Charger_{video_name}"):
                with open(path, "rb") as f:
                    st.session_state["video_file"] = f.read()
                st.session_state["video_filename"] = video_name
                # Réinitialiser la confirmation du prompt lors du changement de vidéo
                st.session_state["custom_prompt_confirmed"] = False
                st.rerun()
    except Exception as e:
        st.sidebar.write(f"Impossible de lire la vidéo {video_name}: {e}")

# ----------------------------------
# Espace principal : vidéo + export
# ----------------------------------

col1, col2 = st.columns([2, 3])

with col1:
    st.header("Vidéo Chargée")
    if st.session_state["video_file"] is not None:
        st.video(st.session_state["video_file"])
        if st.session_state["description"]:
            st.subheader("Exporter la description")
            txt_data = st.session_state["description"]

            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(["Description"])
            writer.writerow([st.session_state["description"]])
            csv_data = csv_buffer.getvalue()

            json_data = json.dumps({"description": st.session_state["description"]}, ensure_ascii=False)

            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                st.download_button(
                    label="TXT",
                    data=txt_data,
                    file_name="description.txt",
                    mime="text/plain"
                )
            with bc2:
                st.download_button(
                    label="CSV",
                    data=csv_data,
                    file_name="description.csv",
                    mime="text/csv"
                )
            with bc3:
                st.download_button(
                    label="JSON",
                    data=json_data,
                    file_name="description.json",
                    mime="application/json"
                )
    else:
        st.write("Aucune vidéo n'est encore chargée.")

with col2:
    st.header("Description Générée")
    # Si le mode est "prompt custom", afficher le prompt saisi
    if mode == "prompt custom" and st.session_state["custom_prompt"]:
        st.markdown(f"**Prompt personnalisé :** {st.session_state['custom_prompt']}")
        st.write("---")
    if st.session_state["description"]:
        st.text_area(
            label="Description",
            label_visibility="collapsed",
            value=st.session_state["description"],
            height=400
        )
    else:
        st.write("Aucune description disponible pour le moment.")
