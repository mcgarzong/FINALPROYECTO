import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
import json
from gtts import gTTS

# ==============================
# CONFIGURACIÓN VISUAL
# ==============================
st.set_page_config(page_title="Asistente Vital 💊", page_icon="💖", layout="centered")

st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #e0f7fa, #fce4ec);
            font-family: 'Poppins', sans-serif;
        }
        .main {
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 25px;
            padding: 50px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            font-size: 50px;
            background: linear-gradient(90deg, #43cea2, #185a9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        h3 {
            text-align: center;
            color: #444;
            font-weight: 400;
        }
        .stButton>button {
            border: none;
            border-radius: 15px;
            font-size: 22px;
            font-weight: 600;
            padding: 15px 40px;
            color: white;
            cursor: pointer;
            background: linear-gradient(90deg, #4776E6, #8E54E9);
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .stButton>button:hover {
            transform: scale(1.05);
        }
        .footer {
            text-align: center;
            color: #555;
            margin-top: 50px;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# MQTT CONFIG
# ==============================
broker = "broker.mqttdashboard.com"
port = 1883
topic_voice = "voice_cami"

client = paho.Client("asistente_vital_voz")
client.connect(broker, port)

def on_publish(client, userdata, result):
    print("Mensaje MQTT enviado correctamente 🎯")

# ==============================
# INTERFAZ
# ==============================
st.markdown("<h1>Asistente Vital 💖</h1>", unsafe_allow_html=True)
st.markdown("<h3>Controla tus medicinas con tu voz</h3>", unsafe_allow_html=True)
st.write("🎙️ Di los comandos por voz: **“vitamina azul”**, **“vitamina amarilla”** o **“vitamina roja”**.")
st.write("También puedes decir **“estoy bien”** o **“ayuda”** para controlar el estado general.")
st.markdown("---")

# ==============================
# BOTÓN DE VOZ
# ==============================
stt_button = Button(label="🎤 Hablar ahora", width=300)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.lang = "es-ES";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ==============================
# PROCESAMIENTO DE COMANDOS
# ==============================
if result and "GET_TEXT" in result:
    user_command = result.get("GET_TEXT").strip().lower()
    st.success(f"🎧 Comando detectado: “{user_command}”")

    client.on_publish = on_publish
    message = json.dumps({"Act1": user_command})
    client.publish(topic_voice, message)

    # Respuesta de voz con gTTS
    if "vitamina azul" in user_command:
        respuesta = "Moviendo al compartimento de la vitamina azul."
    elif "vitamina amarilla" in user_command:
        respuesta = "Moviendo al compartimento de la vitamina amarilla."
    elif "vitamina roja" in user_command:
        respuesta = "Moviendo al compartimento de la vitamina roja."
    elif "ayuda" in user_command:
        respuesta = "Enviando alerta de ayuda."
    elif "estoy bien" in user_command:
        respuesta = "Me alegra que estés bien."
    else:
        respuesta = "No he reconocido el comando. Inténtalo de nuevo."

    tts = gTTS(respuesta, lang="es")
    tts.save("respuesta.mp3")
    st.audio("respuesta.mp3")

st.markdown("<p class='footer'>💗 Desarrollado por Camila Garzón · Comité Pixel</p>", unsafe_allow_html=True)
