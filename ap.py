import streamlit as st
import paho.mqtt.client as paho
import json
import speech_recognition as sr
from gtts import gTTS
import os
from io import BytesIO

# ----------------------------------------
# 🔹 CONFIGURACIÓN INICIAL
# ----------------------------------------
st.set_page_config(
    page_title="Asistente de Apoyo para Personas Mayores",
    page_icon="👵",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ----------------------------------------
# 🌈 ESTILOS PERSONALIZADOS
# ----------------------------------------
st.markdown("""
    <style>
    body {
        background-color: #FFF8EE;
        font-family: 'Segoe UI', sans-serif;
    }
    .main {
        padding: 2rem;
        border-radius: 15px;
    }
    .title {
        color: #4E342E;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: #6D4C41;
        font-size: 20px;
        margin-bottom: 2em;
    }
    .button {
        width: 100%;
        height: 70px;
        border: none;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 15px;
        cursor: pointer;
        margin-bottom: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    .sos {
        background: linear-gradient(45deg, #FF4E50, #F9D423);
    }
    .voz {
        background: linear-gradient(45deg, #2196F3, #21CBF3);
    }
    .alarma {
        background: linear-gradient(45deg, #66BB6A, #43A047);
    }
    .footer {
        text-align: center;
        color: #8D6E63;
        margin-top: 3em;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# 🌐 MQTT CONFIG
# ----------------------------------------
broker = "broker.mqttdashboard.com"
topic_button = "cmqtt_cami"
topic_voice = "voice_cami"

client = paho.Client()

try:
    client.connect(broker, 1883, 60)
except Exception as e:
    st.warning(f"⚠️ No se pudo conectar al broker MQTT: {e}")

# ----------------------------------------
# 🔊 FUNCIÓN DE VOZ
# ----------------------------------------
def escuchar_voz():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Escuchando... habla ahora.")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='es-ES')
            st.success(f"Has dicho: {text}")
            procesar_comando(text)
        except sr.UnknownValueError:
            st.error("❌ No pude entenderte, intenta de nuevo.")
        except sr.RequestError:
            st.error("❌ Error al conectar con el servicio de reconocimiento.")

# ----------------------------------------
# 🤖 PROCESAR COMANDO DE VOZ
# ----------------------------------------
def procesar_comando(text):
    text_lower = text.lower()
    if "ayuda" in text_lower:
        mensaje = {"Act1": "ayuda"}
        client.publish(topic_voice, json.dumps(mensaje))
        st.warning("🚨 Señal de ayuda enviada.")
    elif "estoy bien" in text_lower:
        mensaje = {"Act1": "estoy bien"}
        client.publish(topic_voice, json.dumps(mensaje))
        st.success("✅ Señal de tranquilidad enviada.")
    elif any(med in text_lower for med in ["vitamina", "analgésico", "lírica"]):
        mensaje = {"Act1": text_lower}
        client.publish(topic_voice, json.dumps(mensaje))
        st.info(f"💊 Medicamento '{text_lower}' solicitado.")
    else:
        st.info("🤔 No reconocí el comando, intenta de nuevo.")

# ----------------------------------------
# 🧭 NAVEGACIÓN ENTRE PÁGINAS
# ----------------------------------------
pagina = st.sidebar.radio("🧭 Navegación", ["🏠 Inicio", "🎙️ Asistente de Voz", "🚨 Emergencia"])

# ----------------------------------------
# 🏠 PÁGINA DE INICIO
# ----------------------------------------
if pagina == "🏠 Inicio":
    st.markdown('<h1 class="title">👵 Asistente de Apoyo para Personas Mayores</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Tu compañero para recordatorios, emergencias y ayuda con la voz 💬</p>', unsafe_allow_html=True)

    st.image("https://cdn-icons-png.flaticon.com/512/4472/4472580.png", width=180)
    st.markdown("""
    Bienvenido/a al Asistente de Apoyo.  
    Aquí podrás **pedir ayuda con tu voz**, **recordar tus medicamentos**  
    o **enviar una alerta de emergencia** si la necesitas.
    """)

# ----------------------------------------
# 🎙️ PÁGINA ASISTENTE DE VOZ
# ----------------------------------------
elif pagina == "🎙️ Asistente de Voz":
    st.markdown('<h1 class="title">🎙️ Control por Voz</h1>', unsafe_allow_html=True)
    st.write("Presiona el botón para grabar tu voz y dar una instrucción. Ejemplo: *'Ayuda', 'Estoy bien', 'Tomar analgésico'*.")

    if st.button("🎤 Iniciar grabación", key="voz", help="Presiona para hablar"):
        escuchar_voz()

# ----------------------------------------
# 🚨 PÁGINA EMERGENCIA
# ----------------------------------------
elif pagina == "🚨 Emergencia":
    st.markdown('<h1 class="title">🚨 Botón de Emergencia</h1>', unsafe_allow_html=True)
    st.write("En caso de emergencia, presiona el botón para enviar una señal de ayuda inmediata.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🆘 Enviar SOS", key="sos", use_container_width=True):
            mensaje = {"Act1": "ON"}
            client.publish(topic_button, json.dumps(mensaje))
            st.warning("🚨 Señal SOS enviada al sistema.")
    with col2:
        if st.button("✅ Cancelar SOS", key="off", use_container_width=True):
            mensaje = {"Act1": "OFF"}
            client.publish(topic_button, json.dumps(mensaje))
            st.success("✅ Señal de calma enviada.")

# ----------------------------------------
# 📜 PIE DE PÁGINA
# ----------------------------------------
st.markdown('<div class="footer">© 2025 Asistente de Apoyo | Desarrollado con 💛 por Camila Garzón</div>', unsafe_allow_html=True)
