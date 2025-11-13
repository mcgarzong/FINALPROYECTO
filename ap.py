import streamlit as st
import paho.mqtt.client as mqtt
import json
import speech_recognition as sr
from PIL import Image
import time

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Asistente Cami", page_icon="🩺", layout="centered")

# --- ESTILOS ---
st.markdown("""
    <style>
    body {
        background-color: #FFF8E7;
    }
    .stApp {
        background-color: #FFF8E7;
    }
    h1, h2, h3, p {
        font-family: "Arial Rounded MT Bold", sans-serif;
        color: #333333;
    }
    .boton-sos button {
        background-color: #FF4B4B !important;
        color: white !important;
        font-size: 22px !important;
        border-radius: 12px !important;
        padding: 15px 40px !important;
    }
    .boton-ok button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-size: 22px !important;
        border-radius: 12px !important;
        padding: 15px 40px !important;
    }
    .voz button {
        background-color: #2196F3 !important;
        color: white !important;
        font-size: 20px !important;
        border-radius: 12px !important;
        padding: 15px 40px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN MQTT ---
MQTT_SERVER = "broker.mqttdashboard.com"
MQTT_TOPIC_BOTONES_1 = "cmqtt_camilag"
MQTT_TOPIC_BOTONES_2 = "cmqtt_cami"
MQTT_TOPIC_VOZ = "voice_cami"

client = mqtt.Client(client_id="streamlitCami")
client.connect(MQTT_SERVER, 1883, 60)

# --- FUNCIÓN PARA ENVIAR MQTT ---
def send_mqtt_message(topic, data):
    msg = json.dumps(data)
    client.publish(topic, msg)

# --- ENCABEZADO ---
st.image("https://cdn-icons-png.flaticon.com/512/991/991952.png", width=120)
st.title("👵 Asistente de Ayuda")
st.subheader("Tu asistente amigable para emergencias y recordatorios 💗")
st.markdown("---")

# --- SECCIÓN DE BOTONES ---
st.header("🚨 Botón de Ayuda")

col1, col2 = st.columns(2)

with col1:
    if st.button("🆘 Enviar SOS", key="sos", help="Presiona si necesitas ayuda urgente", use_container_width=True):
        send_mqtt_message(MQTT_TOPIC_BOTONES_1, {"Act1": "ON"})
        st.success("🔴 Alarma activada (LED encendido).")
        time.sleep(2)

with col2:
    if st.button("✅ Estoy bien", key="ok", help="Presiona si ya estás bien", use_container_width=True):
        send_mqtt_message(MQTT_TOPIC_BOTONES_2, {"Act1": "OFF"})
        st.info("🟢 Alarma desactivada (LED apagado).")
        time.sleep(2)

st.markdown("---")

# --- SECCIÓN DE CONTROL POR VOZ ---
st.header("🎙️ Control por Voz")
st.write("Puedes hablar para que el asistente reconozca tus palabras:")
st.write("- Di **'ayuda'** para encender la alarma.")
st.write("- Di **'estoy bien'** para apagarla.")
st.write("- Di el nombre del **medicamento** que deseas (acetaminophen, desloratadina o lyrica).")

if st.button("🎤 Activar Reconocimiento de Voz", key="voz", help="Haz clic y habla claro", use_container_width=True):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎧 Escuchando...")
        audio = recognizer.listen(source, phrase_time_limit=4)
    try:
        text = recognizer.recognize_google(audio, language="es-ES").lower()
        st.write(f"🗣️ Dijiste: **{text}**")

        # --- DECISIONES POR VOZ ---
        if "ayuda" in text:
            send_mqtt_message(MQTT_TOPIC_VOZ, {"Act1": "ayuda"})
            st.success("LED encendido por voz (ayuda detectada).")

        elif "estoy bien" in text:
            send_mqtt_message(MQTT_TOPIC_VOZ, {"Act1": "estoy bien"})
            st.info("LED apagado por voz (estoy bien detectado).")

        elif "acetaminofen" in text or "acetaminophen" in text:
            send_mqtt_message(MQTT_TOPIC_VOZ, {"Act1": "acetaminophen"})
            st.success("💊 Indicando medicamento: Acetaminophen (135°).")

        elif "desloratadina" in text:
            send_mqtt_message(MQTT_TOPIC_VOZ, {"Act1": "desloratadina"})
            st.success("💊 Indicando medicamento: Desloratadina (90°).")

        elif "lírica" in text or "lyrica" in text:
            send_mqtt_message(MQTT_TOPIC_VOZ, {"Act1": "lyrica"})
            st.success("💊 Indicando medicamento: Lyrica (45°).")

        else:
            st.warning("No se reconoció un comando válido.")
    except sr.UnknownValueError:
        st.error("No pude entenderte. Por favor, inténtalo de nuevo.")
    except sr.RequestError:
        st.error("Error con el servicio de reconocimiento de voz.")
