import streamlit as st
from PIL import Image
import paho.mqtt.client as mqtt
import time
import io
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente Senior", page_icon="🧓", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
<style>
    .stApp {
        background-color: #FFF8E7; /* Fondo cálido */
        color: #2B2B2B;
        font-family: "Arial Rounded MT Bold", sans-serif;
    }
    h1, h2, h3 {
        color: #3E2723;
        text-align: center;
        font-weight: bold;
    }
    .big-button {
        display: block;
        width: 100%;
        font-size: 28px;
        font-weight: bold;
        padding: 20px;
        border-radius: 16px;
        margin: 20px 0;
        color: white;
        border: none;
    }
    .sos {
        background-color: #E53935;
    }
    .voz {
        background-color: #1E88E5;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        color: #555;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN MQTT ---
MQTT_SERVER = "broker.mqttdashboard.com"
MQTT_TOPIC_SOS = "asistente_cami_sos"
MQTT_TOPIC_VOZ = "asistente_cami_voz"

client = mqtt.Client(client_id="streamlitCami")
client.connect(MQTT_SERVER, 1883, 60)

# --- FUNCIONES ---
def enviar_sos():
    client.publish(MQTT_TOPIC_SOS, "SOS ACTIVADO 🚨")
    st.success("🚨 ¡Se ha enviado una alerta de emergencia!")
    time.sleep(1)

def escuchar_voz():
    st.info("🎙️ Presiona el botón para grabar tu voz.")
    audio = mic_recorder(
        start_prompt="🎤 Iniciar grabación",
        stop_prompt="🛑 Detener grabación",
        just_once=True,
        use_container_width=True,
        key="mic"
    )
    if audio is not None:
        st.success("🎧 Grabación lista, procesando...")
        sound = io.BytesIO(audio["bytes"])
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(sound) as source:
                audio_data = recognizer.record(source)
                comando = recognizer.recognize_google(audio_data, language="es-ES")
                st.write(f"Has dicho: **{comando}**")

                if "medicina" in comando.lower():
                    client.publish(MQTT_TOPIC_VOZ, "Recordatorio: hora del medicamento 💊")
                    st.success("💊 Se activó el recordatorio de medicamentos.")
                elif "alarma" in comando.lower():
                    client.publish(MQTT_TOPIC_VOZ, "Alarma activada ⏰")
                    st.warning("⏰ Alarma encendida.")
                else:
                    st.info("No se reconoció ninguna acción específica.")
        except sr.UnknownValueError:
            st.error("No se entendió el comando. Intente hablar más claro.")
        except sr.RequestError:
            st.error("Error con el servicio de voz. Intenta nuevamente más tarde.")

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1>🧓 Asistente de Apoyo para Personas Mayores</h1>", unsafe_allow_html=True)
st.markdown("<h3>Tu compañero para recordatorios, emergencias y ayuda con la voz</h3>", unsafe_allow_html=True)

# --- BOTONES GRANDES ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 Botón SOS", key="sos_btn", use_container_width=True):
        enviar_sos()

with col2:
    escuchar_voz()

# --- SECCIÓN DE EXPLICACIÓN ---
st.markdown("---")
st.subheader("📘 ¿Cómo funciona?")
st.markdown("""
- **Botón SOS:** En caso de emergencia, presiona este botón rojo grande.  
  Enviará una señal de ayuda y alertará al sistema.  
- **Asistente de voz:** Usa el micrófono azul.  
  Puedes decir frases como:  
  - “Recordar medicina” → activa un recordatorio de medicamentos 💊  
  - “Encender alarma” → activa una alarma de ayuda ⏰  
""")

st.markdown("<div class='footer'>Hecho con ❤️ para apoyar a nuestros adultos mayores.</div>", unsafe_allow_html=True)
