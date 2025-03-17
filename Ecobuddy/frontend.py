import streamlit as st
import requests
import pyperclip
from streamlit_extras.stylable_container import stylable_container

# ✅ Backend API URLs
BACKEND_URL = "http://127.0.0.1:5000"
WEATHER_URL = f"{BACKEND_URL}/weather"
CHAT_URL = f"{BACKEND_URL}/chat"

# ✅ Streamlit Page Configuration
st.set_page_config(page_title="EcoBuddy - Environmental Chatbot", page_icon="🌍")

# Sidebar Navigation
st.sidebar.title("🌱 EcoBuddy - Awareness Chatbot")
st.sidebar.write("Explore environmental facts, chat with EcoBuddy, and check real-time weather updates!")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("🗂 Chat History"):
        st.session_state.show_chat_history = not st.session_state.get("show_chat_history", False)

with col2:
    if st.button("📖 About"):
        st.session_state.show_about = not st.session_state.get("show_about", False)

if st.session_state.get("show_chat_history", False):
    st.sidebar.subheader("🗂 Chat History")
    if st.session_state.chat_history:
        first_topic = st.session_state.chat_history[0][1]
        st.sidebar.write(first_topic)
        if st.sidebar.button("🗑 Delete History"):
            st.session_state.chat_history = []
            st.rerun()

if st.session_state.get("show_about", False):
    st.sidebar.subheader("📖 About EcoBuddy")
    st.sidebar.write("EcoBuddy is an AI-powered chatbot designed to spread environmental awareness. Ask about pollution, climate change, and sustainability!")
    st.sidebar.write("👨‍💻 Developed by **Kawinya R**, studying **Computer Science Engineering** at **Sri Krishna College of Technology**, specializing in **Artificial Intelligence and Machine Learning**.")
    st.sidebar.write("🔗 [GitHub](https://github.com/KAWINYARAVI) | [Profile](https://linkedin.com/in/kawinya-r)")

# ✅ Session State for Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🏷️ Tabs for Navigation
tab1, tab2 = st.tabs(["💬 Chat", "⛅ Weather"])

# ✅ Tab 1: Chatbot (Chat-style UI with Input at Bottom)
with tab1:
    st.header("💬 Chat with EcoBuddy")
    st.write("Ask about environmental topics like pollution, climate change, and sustainability!")

    # Display chat messages in order (conversation-style)
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)
            
            # Copy Button (Very Small, Right Aligned)
            if role == "assistant":
                copy_button = st.button("🗐", key=f"copy_{message}", help="Copy to Clipboard", use_container_width=False)
                if copy_button:
                    pyperclip.copy(message)
                    st.success("Copied!")

    # User input field appears **AFTER** the last response
    user_query = st.chat_input("Type your question here...")

    if user_query:
        # Append user query to chat history
        st.session_state.chat_history.append(("user", user_query))

        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Thinking..."):
            try:
                response = requests.post(CHAT_URL, json={"query": user_query})
                if response.status_code == 200:
                    bot_response = response.json()["response"]

                    # Append bot response to chat history
                    st.session_state.chat_history.append(("assistant", bot_response))

                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
                else:
                    st.error("❌ Could not fetch response. Try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Unable to connect to the backend. Make sure Flask is running.")
        
        # 🔄 Refresh to keep input box at the bottom
        st.rerun()

# ✅ Tab 2: Weather Information
with tab2:
    st.header("⛅ Weather & Environmental Data")
    st.write("Get real-time weather conditions.")

    city = st.text_input("🏙 Enter City Name:", placeholder="e.g., New York, Chennai, London", key="weather_input")
    
    if st.button("🔍 Get Weather"):
        if city.strip():
            with st.spinner("Fetching data..."):
                try:
                    weather_response = requests.get(WEATHER_URL, params={"city": city})
                    
                    if weather_response.status_code == 200:
                        weather_data = weather_response.json()
                        st.success(f"✅ Weather in {weather_data['city']}")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("🌡 Temperature", f"{weather_data['temperature']}°C")
                            st.metric("💧 Humidity", f"{weather_data['humidity']}%")
                            st.metric("🎭 Condition", weather_data['weather'].capitalize())

                        with col2:
                            st.metric("💨 Wind Speed", f"{weather_data['wind_speed']} m/s")
                            st.metric("🎚 Feels Like", f"{weather_data['feels_like']}°C")
                            st.metric("🔽 Pressure", f"{weather_data['pressure']} hPa")
                    else:
                        st.error("❌ Could not retrieve weather data.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Unable to connect to the backend. Make sure Flask is running.")
        else:
            st.warning("⚠️ Please enter a valid city name.")

# ✅ Run the app using: `streamlit run frontend.py`
