import streamlit as st
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho
import json
from gtts import gTTS
import os

# ====================================
# CONFIGURACIÓN GENERAL
# ====================================
st.set_page_config(page_title="Asistente Vital 💖", page_icon="💊", layout="centered")

# ---- MQTT ----
broker = "broker.mqttdashboard.com"
topic_voice = "voice_cami"
topic_button = "cmqtt_camilag"

client = paho.Client("asistente_vital")
client.connect(broker, 1883)

# ---- ESTILOS ----
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #c2e9fb, #e8c2f9);
    color: #333333;
    font-family: 'Poppins', sans-serif;
}
h1 {
    text-align: center;
    color: #4b0082;
}
.stButton>button {
    background: linear-gradient(90deg, #00b4d8, #0077b6);
    color: white;
    border-radius: 12px;
    font-size: 22px !important;
    font-weight: bold;
    height: 60px;
    width: 300px;
    border: none;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #0077b6, #00b4d8);
}
.instrucciones {
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
    padding: 20px;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ====================================
# ENCABEZADO
# ====================================
st.title("💖 Asistente Vital para Mayores")
st.markdown("<h3 style='text-align:center;'>Tu apoyo diario para recordar y pedir ayuda</h3>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div class='instrucciones'>
<h4>🗣️ Control por voz:</h4>
<p>Presiona el botón de micrófono y di una de las siguientes frases:</p>
<ul>
<li><b>“Ayuda”</b> → Enciende la alarma (LED)</li>
<li><b>“Estoy bien”</b> → Apaga la alarma</li>
<li><b>“Vitamina azul”</b> → Servo apunta a la vitamina azul (135°)</li>
<li><b>“Vitamina amarilla”</b> → Servo apunta a la amarilla (90°)</li>
<li><b>“Vitamina roja”</b> → Servo apunta a la roja (45°)</li>
</ul>
<p>También puedes usar el botón de ayuda grande si lo prefieres.</p>
</div>
""", unsafe_allow_html=True)

# ====================================
# SECCIÓN DE CONTROL POR VOZ
# ====================================
st.markdown("### 🎙️ Control por voz")
st.write("Haz clic en el botón para hablar y decir tu comando:")

stt_button = Button(label="🎤 Presiona para hablar", width=300, button_type="success")

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
    };
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
    st.success(f"🎧 Has dicho: “{user_command}”")

    # Publicar el mensaje por MQTT
    message = json.dumps({"Act1": user_command})
    client.publish(topic_voice, message)

    # Retroalimentación hablada
    if "ayuda" in user_command:
        tts = gTTS("Alarma activada, pidiendo ayuda.", lang="es")
    elif "estoy bien" in user_command:
        tts = gTTS("Alarma apagada, me alegra que estés bien.", lang="es")
    elif "vitamina azul" in user_command:
        tts = gTTS("Seleccionando la vitamina azul.", lang="es")
    elif "vitamina amarilla" in user_command:
        tts = gTTS("Seleccionando la vitamina amarilla.", lang="es")
    elif "vitamina roja" in user_command:
        tts = gTTS("Seleccionando la vitamina roja.", lang="es")
    else:
        tts = gTTS("No entendí el comando. Por favor repite.", lang="es")

    tts.save("voz.mp3")
    st.audio("voz.mp3", format="audio/mp3")

st.markdown("---")

# ====================================
# SECCIÓN DE BOTÓN DE AYUDA
# ====================================
st.markdown("### 🆘 Botón de ayuda manual")
st.write("Si necesitas ayuda inmediata, puedes encender la alarma presionando este botón:")

if st.button("🚨 Activar alarma de ayuda"):
    message = json.dumps({"Act1": "ayuda"})
    client.publish(topic_button, message)
    st.warning("🔔 Alarma activada (LED encendido)")

if st.button("✅ Estoy bien (apagar alarma)"):
    message = json.dumps({"Act1": "estoy bien"})
    client.publish(topic_button, message)
    st.success("💤 Alarma apagada (LED apagado)")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#555;'>Desarrollado con 💜 para acompañar y cuidar</p>", unsafe_allow_html=True)
