import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
import json
from gtts import gTTS

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================
st.set_page_config(page_title="Asistente Vital 💊", page_icon="💖", layout="wide")

# Estilos visuales
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #fff3f0, #eaf4fc, #fdfce5);
            font-family: 'Poppins', sans-serif;
        }
        .main {
            background-color: rgba(255,255,255,0.85);
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        h1.title {
            text-align: center;
            font-size: 45px;
            background: linear-gradient(90deg, #7b4397, #dc2430);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        h3.subtitle {
            text-align: center;
            color: #444;
            font-weight: 400;
            font-size: 22px;
        }
        .section {
            background-color: rgba(255,255,255,0.9);
            border-radius: 20px;
            padding: 25px;
            margin-top: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .stButton>button {
            border: none;
            border-radius: 14px;
            font-size: 20px;
            font-weight: 600;
            padding: 12px 25px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        .stButton>button:hover {
            transform: scale(1.05);
        }
        .sos-btn>button {
            background: linear-gradient(90deg, #ff416c, #ff4b2b);
        }
        .voice-btn>button {
            background: linear-gradient(90deg, #4776E6, #8E54E9);
        }
        .med-btn-blue>button {
            background: linear-gradient(90deg, #2193b0, #6dd5ed);
        }
        .med-btn-yellow>button {
            background: linear-gradient(90deg, #f9d423, #ff4e50);
        }
        .med-btn-red>button {
            background: linear-gradient(90deg, #ff4b2b, #ff6a00);
        }
        .footer {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 40px;
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

client = paho.Client("asistente_vital_cami")
client.connect(broker, port)

def on_publish(client, userdata, result):
    print("Mensaje MQTT enviado ✅")

# ======================================
# ENCABEZADO
# ======================================
st.markdown("<h1 class='title'>Asistente Vital 💖</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='subtitle'>Tu apoyo diario para bienestar, voz y medicinas</h3>", unsafe_allow_html=True)

# ======================================
# SECCIÓN DE EMERGENCIA
# ======================================
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🚨 Emergencia")
        st.write("Si te sientes mal, presiona el botón para pedir ayuda.")

        if st.button("🆘 Enviar alerta SOS", key="sos", use_container_width=True):
            data = {"Act1": "ayuda"}
            client.publish(topic_sos, json.dumps(data))
            st.error("🚨 ¡Alerta enviada! Alguien acudirá a ayudarte pronto.")
            tts = gTTS("Tu alerta ha sido enviada. La ayuda está en camino.", lang="es")
            tts.save("sos_audio.mp3")
            st.audio("sos_audio.mp3")
        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================
    # CONTROL POR VOZ
    # ======================================
    with col2:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🎙️ Control por Voz")
        st.write("Presiona el botón y di tu comando. Ejemplos: “Estoy bien”, “Vitamina azul”, “Vitamina roja”.")

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
            user_command = result.get("GET_TEXT").strip().lower()
            st.success(f"🎧 Comando detectado: “{user_command}”")

            client.on_publish = on_publish
            message = json.dumps({"Act1": user_command})
            client.publish(topic_voice, message)

            tts = gTTS(f"He entendido: {user_command}", lang="es")
            tts.save("respuesta.mp3")
            st.audio("respuesta.mp3")

        st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# MEDICINAS
# ======================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("💊 Medicinas disponibles")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💙 Vitamina Azul", key="vit_azul", use_container_width=True):
        client.publish(topic_voice, json.dumps({"Act1": "vitamina azul"}))
        st.info("🌀 Señalando vitamina azul (135°).")
        tts = gTTS("Abriendo vitamina azul.", lang="es")
        tts.save("azul.mp3")
        st.audio("azul.mp3")

with col2:
    if st.button("💛 Vitamina Amarilla", key="vit_amarilla", use_container_width=True):
        client.publish(topic_voice, json.dumps({"Act1": "vitamina amarilla"}))
        st.info("🌞 Señalando vitamina amarilla (90°).")
        tts = gTTS("Abriendo vitamina amarilla.", lang="es")
        tts.save("amarilla.mp3")
        st.audio("amarilla.mp3")

with col3:
    if st.button("❤️ Vitamina Roja", key="vit_roja", use_container_width=True):
        client.publish(topic_voice, json.dumps({"Act1": "vitamina roja"}))
        st.info("🔥 Señalando vitamina roja (45°).")
        tts = gTTS("Abriendo vitamina roja.", lang="es")
        tts.save("roja.mp3")
        st.audio("roja.mp3")

st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# PIE DE PÁGINA
# ======================================
st.markdown("<p class='footer'>Desarrollado con 💗 por Camila Garzón y Miguel Gaviria · Comité Pixel</p>", unsafe_allow_html=True)
