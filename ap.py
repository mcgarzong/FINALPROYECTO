import streamlit as st
import paho.mqtt.publish as publish
import speech_recognition as sr
import json

# ----------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------
MQTT_SERVER = "broker.mqttdashboard.com"
TOPIC_LED = "migue/demo/led"
TOPIC_SERVO = "migue/demo/servo"

st.set_page_config(page_title="Proyecto Final IoT Cami 💡", page_icon="💡", layout="wide")

st.title("💡 Proyecto IoT Multimodal — ESP32 + Streamlit")
st.caption("Control del LED y servo por voz o botones usando MQTT")

# ----------------------------
# Funciones
# ----------------------------
def send_mqtt_message(topic, message):
    publish.single(topic, message, hostname=MQTT_SERVER)
    st.success(f"📡 Mensaje enviado al topic `{topic}`: {message}")

def recognize_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Di una orden (ej: 'enciende las luces', 'apaga las luces', 'abre la puerta')")
        audio = recognizer.listen(source, timeout=5)
    try:
        text = recognizer.recognize_google(audio, language="es-ES")
        st.write(f"🗣️ Dijiste: **{text}**")
        return text.lower()
    except sr.UnknownValueError:
        st.error("❌ No se entendió lo que dijiste.")
        return None
    except sr.RequestError:
        st.error("⚠️ Error con el servicio de reconocimiento de voz.")
        return None

# ----------------------------
# NAVEGACIÓN
# ----------------------------
page = st.sidebar.radio("Selecciona un modo 👇", ["🎤 Control por Voz", "🔘 Control Manual"])

# ----------------------------
# PÁGINA 1: CONTROL POR VOZ
# ----------------------------
if page == "🎤 Control por Voz":
    st.header("🎤 Control por voz")

    if st.button("🎙️ Iniciar reconocimiento"):
        comando = recognize_voice()
        if comando:
            if "enciende" in comando or "ayuda" in comando:
                message = json.dumps({"Act1": "enciende las luces"})
                send_mqtt_message(TOPIC_LED, message)
            elif "apaga" in comando:
                message = json.dumps({"Act1": "apaga las luces"})
                send_mqtt_message(TOPIC_LED, message)
            elif "abre" in comando:
                message = json.dumps({"Act1": "abre la puerta"})
                send_mqtt_message(TOPIC_SERVO, message)
            elif "cierra" in comando:
                message = json.dumps({"Act1": "cierra la puerta"})
                send_mqtt_message(TOPIC_SERVO, message)
            else:
                st.warning("⚠️ No se reconoció un comando válido.")

# ----------------------------
# PÁGINA 2: CONTROL MANUAL
# ----------------------------
elif page == "🔘 Control Manual":
    st.header("🔘 Control Manual")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💡 LED")
        if st.button("Encender LED"):
            message = json.dumps({"Act1": "ON"})
            send_mqtt_message(TOPIC_LED, message)
        if st.button("Apagar LED"):
            message = json.dumps({"Act1": "OFF"})
            send_mqtt_message(TOPIC_LED, message)

    with col2:
        st.subheader("🚪 Servo")
        if st.button("Abrir puerta"):
            message = json.dumps({"Act1": "abre la puerta"})
            send_mqtt_message(TOPIC_SERVO, message)
        if st.button("Cerrar puerta"):
            message = json.dumps({"Act1": "cierra la puerta"})
            send_mqtt_message(TOPIC_SERVO, message)

    angle = st.slider("🎚️ Controlar ángulo manualmente", 0, 180, 90)
    if st.button("Mover servo"):
        message = json.dumps({"Analog": angle})
        send_mqtt_message(TOPIC_SERVO, message)

