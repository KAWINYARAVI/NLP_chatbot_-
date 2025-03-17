import streamlit as st
import requests
import pyperclip
import random
import time
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

# ✅ EcoCleanup Game Class
class EcoCleanupGame:
    def __init__(self):
        self.grid_size = 10
        self.player_pos = [5, 5]
        self.energy = 100
        self.score = 0
        self.day = 1
        self.pollution_count = 20
        self.trees_planted = 0
        self.game_over = False
        self.message = ""
        
        # Create the game grid
        self.grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Place player
        self.grid[self.player_pos[0]][self.player_pos[1]] = 'P'
        
        # Place pollution
        for _ in range(self.pollution_count):
            self.place_random_entity('X')
        
        # Place some trees
        for _ in range(5):
            self.place_random_entity('T')
        
        # Place energy boosts
        for _ in range(3):
            self.place_random_entity('E')

    def place_random_entity(self, entity):
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if self.grid[x][y] == ' ':
                self.grid[x][y] = entity
                break

    def move_player(self, direction):
        self.message = ""
        # Store current position
        current_x, current_y = self.player_pos
        self.grid[current_x][current_y] = ' '
        
        # Calculate new position
        new_x, new_y = current_x, current_y
        
        if direction == 'w' and current_x > 0:
            new_x -= 1
        elif direction == 's' and current_x < self.grid_size - 1:
            new_x += 1
        elif direction == 'a' and current_y > 0:
            new_y -= 1
        elif direction == 'd' and current_y < self.grid_size - 1:
            new_y += 1
        
        # Check what's at the new position
        target = self.grid[new_x][new_y]
        
        if target == 'X':
            # Clean pollution
            self.energy -= 10
            self.score += 20
            self.pollution_count -= 1
            self.message = "Cleaned up pollution! +20 points, -10 energy"
        elif target == 'E':
            # Get energy boost
            self.energy = min(100, self.energy + 30)
            self.message = "Energy boost! +30 energy"
        elif target == 'T':
            # Rest under a tree
            self.energy = min(100, self.energy + 10)
            self.message = "Rested under a tree. +10 energy"
        
        # Update player position
        self.player_pos = [new_x, new_y]
        self.grid[new_x][new_y] = 'P'
        
        # Moving costs energy
        self.energy -= 2
        
        # Check game state after move
        self.check_game_state()
        
        # Check if day should end (25% chance after each action)
        if not self.game_over and random.random() < 0.25:
            self.message += "\nThe day is ending..."
            self.end_day()

    def plant_tree(self):
        self.message = ""
        # Check adjacent cells
        x, y = self.player_pos
        can_plant = False
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.grid[nx][ny] == ' ':
                self.grid[nx][ny] = 'T'
                can_plant = True
                break
        
        if can_plant:
            self.energy -= 15
            self.score += 30
            self.trees_planted += 1
            self.message = "Tree planted! +30 points, -15 energy"
        else:
            self.message = "No space to plant a tree nearby!"
            
        # Check game state after planting
        self.check_game_state()
        
        # Check if day should end (25% chance after each action)
        if not self.game_over and random.random() < 0.25:
            self.message += "\nThe day is ending..."
            self.end_day()

    def end_day(self):
        day_message = []
        # Add some new pollution
        if random.random() < 0.7:  # 70% chance
            new_pollution = random.randint(1, 3)
            for _ in range(new_pollution):
                self.place_random_entity('X')
                self.pollution_count += 1
            day_message.append(f"{new_pollution} new pollution sources appeared!")
        
        # Add some energy boosts
        if random.random() < 0.5:  # 50% chance
            self.place_random_entity('E')
        
        # Trees help clean the environment
        pollution_cleaned = min(self.pollution_count, self.trees_planted // 3)
        if pollution_cleaned > 0:
            self.pollution_count -= pollution_cleaned
            self.score += pollution_cleaned * 5
            day_message.append(f"Your trees naturally cleaned {pollution_cleaned} pollution sources! +{pollution_cleaned * 5} points")
        
        self.day += 1
        self.energy = min(100, self.energy + 20)  # Rest overnight
        day_message.append("A new day begins. You feel refreshed! +20 energy")
        
        # Find and remove pollution from the grid
        removed = 0
        while removed < pollution_cleaned:
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.grid[i][j] == 'X':
                        self.grid[i][j] = ' '
                        removed += 1
                        if removed >= pollution_cleaned:
                            break
                if removed >= pollution_cleaned:
                    break
                    
        self.message += "\n" + "\n".join(day_message)
        
        # Check game state after day ends
        self.check_game_state()

    def check_game_state(self):
        # Check if player has run out of energy
        if self.energy <= 0:
            self.message += "\nYou've run out of energy! Game over."
            self.game_over = True
            return
        
        # Check if all pollution is cleaned
        if self.pollution_count == 0:
            self.message += "\nCongratulations! You've cleaned all pollution!"
            self.message += f"\nFinal score: {self.score}"
            self.message += f"\nTrees planted: {self.trees_planted}"
            self.message += f"\nDays taken: {self.day}"
            self.game_over = True
            return
            
        # Check if too much pollution
        if self.pollution_count >= 50:
            self.message += "\nThe environment is too polluted! Game over."
            self.game_over = True
            return

    def reset_game(self):
        self.__init__()

# ✅ Initialize game if not in session state
if 'game' not in st.session_state:
    st.session_state.game = EcoCleanupGame()

# 🏷️ Tabs for Navigation
tab1, tab2, tab3 = st.tabs(["💬 Chat", "⛅ Weather", "🌳 EcoCleanup Game"])

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

# ✅ Tab 3: EcoCleanup Game
with tab3:
    st.header("🌳 EcoCleanup Game")
    st.write("Help clean up pollution and plant trees to save the environment!")
    
    game = st.session_state.game
    
    # Game legend
    with st.expander("Game Instructions"):
        st.markdown("""
        ### How to Play:
        - **P**: Your character - move around to clean pollution and plant trees
        - **X**: Pollution - clean it up to score points
        - **T**: Trees - rest here to gain energy, plant more to help clean the environment
        - **E**: Energy boosts - collect these to replenish your energy
        
        ### Controls:
        - **W**: Move up
        - **A**: Move left
        - **S**: Move down  
        - **D**: Move right
        - **P**: Plant a tree (must be next to an empty space)
        
        ### Game Rules:
        - Moving costs 2 energy
        - Cleaning pollution costs 10 energy but gives 20 points
        - Planting trees costs 15 energy but gives 30 points
        - Trees help clean pollution over time
        - Each day has a chance of adding new pollution
        - Win by cleaning all pollution
        - Lose if you run out of energy or pollution exceeds 50
        """)
    
    # Display game stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌞 Day", game.day)
        st.metric("🌳 Trees Planted", game.trees_planted)
    with col2:
        st.metric("⚡ Energy", game.energy)
        st.metric("🎯 Score", game.score)
   
    with col3:
        st.metric("☠️ Pollution", game.pollution_count)
        if game.game_over:
            st.button("🔄 New Game", on_click=game.reset_game)
    
    # Display game message
    if game.message:
        st.text_area("Messages", value=game.message, height=100, disabled=True)
    
    # Display game grid
    st.write("### Game Board")
    
    # Create a grid of cells with CSS styling
    grid_html = """
    <style>
    .game-grid {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 2px;
        max-width: 600px;
        margin: 0 auto;
    }
    .cell {
        width: 100%;
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: bold;
    }
    .empty { background-color: #f0f0f0; }
    .player { background-color: #4CAF50; color: white; }
    .pollution { background-color: #f44336; color: white; }
    .tree { background-color: #2E7D32; color: white; }
    .energy { background-color: #FFC107; color: black; }
    </style>
    <div class="game-grid">
    """
    
    for i in range(game.grid_size):
        for j in range(game.grid_size):
            cell = game.grid[i][j]
            if cell == ' ':
                grid_html += '<div class="cell empty"></div>'
            elif cell == 'P':
                grid_html += '<div class="cell player">P</div>'
            elif cell == 'X':
                grid_html += '<div class="cell pollution">X</div>'
            elif cell == 'T':
                grid_html += '<div class="cell tree">T</div>'
            elif cell == 'E':
                grid_html += '<div class="cell energy">E</div>'
    
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)
    
    # Game controls
    if not game.game_over:
        st.write("### Controls")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col2:
            up_button = st.button("⬆️", key="up_button")
            if up_button:
                game.move_player('w')
                st.rerun()
        with col1:
            left_button = st.button("⬅️", key="left_button")
            if left_button:
                game.move_player('a')
                st.rerun()
        with col3:
            right_button = st.button("➡️", key="right_button")
            if right_button:
                game.move_player('d')
                st.rerun()
        with col2:
            down_button = st.button("⬇️", key="down_button")
            if down_button:
                game.move_player('s')
                st.rerun()
        with col5:
            plant_button = st.button("🌱 Plant Tree", key="plant_button")
            if plant_button:
                game.plant_tree()
                st.rerun()
    else:
        st.write("### Game Over")
        restart_button = st.button("🔄 Restart Game")
        if restart_button:
            st.session_state.game = EcoCleanupGame()
            st.rerun()

# ✅ Run the app using: `streamlit run frontend.py`