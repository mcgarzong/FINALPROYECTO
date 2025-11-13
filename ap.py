import streamlit as st
from PIL import Image
import paho.mqtt.client as mqtt
import speech_recognition as sr
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente Senior", page_icon="🧓", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
<style>
    .stApp {
        background-color: #FFF8E7; /* Fondo cálido y suave */
        color: #2B2B2B; /* Texto oscuro para contraste */
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
    .info {
        background-color: #43A047;
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
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Escuchando... hable después del sonido")
        audio = r.listen(source, timeout=5)
        try:
            comando = r.recognize_google(audio, language="es-ES")
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
st.image("a25941a5-6e55-4080-a5fb-c914aea2654c.png", use_column_width=True)

st.markdown("<h1>🧓 Asistente de Apoyo para Personas Mayores</h1>", unsafe_allow_html=True)
st.markdown("<h3>Tu compañero para recordatorios, emergencias y ayuda con la voz</h3>", unsafe_allow_html=True)

# --- BOTONES GRANDES ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 Botón SOS", key="sos_btn", use_container_width=True):
        enviar_sos()

with col2:
    if st.button("🎙️ Activar Asistente de Voz", key="voz_btn", use_container_width=True):
        escuchar_voz()

# --- SECCIÓN DE EXPLICACIÓN ---
st.markdown("---")
st.subheader("📘 ¿Cómo funciona?")
st.markdown("""
- **Botón SOS:** En caso de emergencia, presiona este botón rojo grande.  
  Enviará una señal de ayuda y alertará al sistema.  
- **Asistente de voz:** Presiona el botón azul para hablar.  
  Puedes decir frases como:  
  - “Recordar medicina” → activa un recordatorio de medicamentos 💊  
  - “Encender alarma” → activa una alarma de ayuda ⏰  
""")

st.markdown("<div class='footer'>Hecho con ❤️ para apoyar a nuestros adultos mayores.</div>", unsafe_allow_html=True)
