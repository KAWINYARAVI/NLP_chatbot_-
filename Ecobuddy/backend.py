from flask import Flask, request, jsonify
import requests
import google.generativeai as genai  # Gemini AI SDK

try:
    from textblob import TextBlob  # Autocorrect
except ImportError:
    TextBlob = None  # Fallback if textblob is missing

app = Flask(__name__)

# ✅ API Keys
OPENWEATHER_API_KEY = "2f61f0ac081381b2b35a98b8a357a72a"
GEMINI_API_KEY = "AIzaSyC6nV5MVh7BVQdTH7t7ip-O3hDLWXUbOpc"

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Chatbot Route (Gemini 2.0 Flash) with Autocorrect
def talk_with_gemini(user_input):
    try:
        # Auto-correct user input if TextBlob is available
        corrected_input = str(TextBlob(user_input).correct()) if TextBlob else user_input

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(corrected_input)

        return response.text.strip() if response.text else "I'm not sure about that."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query is required"}), 400

    chatbot_reply = talk_with_gemini(user_query)
    return jsonify({"response": chatbot_reply})

# ✅ Weather API Route (OpenWeather)
@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "City name is required"}), 400

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(weather_url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "City not found"}), 404

        return jsonify({
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "weather": data["weather"][0]["description"],
            "feels_like": data["main"]["feels_like"],
            "pressure": data["main"]["pressure"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
