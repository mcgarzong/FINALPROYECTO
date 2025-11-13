import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
from gtts import gTTS

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================
st.set_page_config(page_title="Asistente Vital 👵", page_icon="💖", layout="wide")

# Estilos visuales personalizados
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #ffe7e7, #fff9e6, #e7ffe7);
            font-family: 'Poppins', sans-serif;
        }
        .main {
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        h1.title {
            text-align: center;
            font-size: 45px;
            background: linear-gradient(90deg, #ff758c, #ff7eb3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        h3.subtitle {
            text-align: center;
            color: #555;
            margin-top: -10px;
            font-weight: 400;
            font-size: 22px;
        }
        .section {
            background-color: rgba(255,255,255,0.85);
            border-radius: 20px;
            padding: 25px;
            margin-top: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .stButton>button {
            border: none;
            border-radius: 14px;
            font-size: 22px;
            font-weight: 600;
            padding: 12px 30px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(0,0,0,0.25);
        }
        .sos-btn>button {
            background: linear-gradient(90deg, #ff1e56, #ff7e5f);
        }
        .voice-btn>button {
            background: linear-gradient(90deg, #42a5f5, #478ed1);
        }
        .reminder-btn>button {
            background: linear-gradient(90deg, #81c784, #66bb6a);
        }
        .footer {
            text-align: center;
            color: #777;
            font-size: 14px;
            margin-top: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# ======================================
# MQTT CONFIG
# ======================================
broker = "broker.mqttdashboard.com"
port = 1883
topic_sos = "cmqtt_cami"
topic_voice = "voice_cami"
client = paho.Client("asistente_cami")
client.connect(broker, port)

def on_publish(client, userdata, result):
    print("Mensaje enviado correctamente ✅")

# ======================================
# INTERFAZ PRINCIPAL
# ======================================
st.markdown("<h1 class='title'>Asistente Vital 💖</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='subtitle'>Tu compañía confiable para bienestar y apoyo diario</h3>", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)

    # ===============================
    # 🚨 BOTÓN SOS
    # ===============================
    with col1:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🚨 Emergencia")
        st.write("Si te sientes mal o necesitas ayuda, presiona este botón para pedir asistencia inmediata.")
        
        if st.button("🆘 Enviar alerta SOS", key="sos", use_container_width=True):
            data = {"Act1": "ayuda"}
            client.publish(topic_sos, json.dumps(data))
            st.error("🚨 ¡Alerta enviada! Alguien acudirá a ayudarte pronto.")
            tts = gTTS("Tu alerta ha sido enviada. Tranquilo, la ayuda está en camino.", lang="es")
            tts.save("sos_audio.mp3")
            st.audio("sos_audio.mp3")
        st.markdown("</div>", unsafe_allow_html=True)

    # ===============================
    # 🎙️ CONTROL POR VOZ
    # ===============================
    with col2:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🎙️ Control por Voz")
        st.write("Presiona el botón y di tu comando. Ejemplos: “Estoy bien”, “Tomar medicina”, “Encender luz”.")
        
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

        if result and "GET_TEXT" in result:
            user_command = result.get("GET_TEXT").strip()
            st.success(f"🎧 Comando detectado: “{user_command}”")
            client.on_publish = on_publish
            message = json.dumps({"Act1": user_command})
            client.publish(topic_voice, message)

            tts = gTTS(f"He entendido: {user_command}", lang="es")
            tts.save("respuesta.mp3")
            st.audio("respuesta.mp3")
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# 🕒 RECORDATORIOS
# ===============================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("⏰ Recordatorios diarios")
st.write("Configura tus recordatorios importantes:")

rem1 = st.text_input("💊 Medicamentos:", "Tomar vitamina D a las 9:00 AM")
rem2 = st.text_input("💧 Hidratación:", "Beber un vaso de agua cada hora")
rem3 = st.text_input("🚶 Actividad física:", "Dar un paseo de 10 minutos")

if st.button("💾 Guardar recordatorios", key="reminder", use_container_width=True):
    st.success("✅ Recordatorios guardados con éxito.")
    tts = gTTS("Tus recordatorios han sido guardados.", lang="es")
    tts.save("recordatorios.mp3")
    st.audio("recordatorios.mp3")

st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# PIE DE PÁGINA
# ===============================
st.markdown("<p class='footer'>Desarrollado con 💗 por Camila Garzón · Comité Pixel</p>", unsafe_allow_html=True)
