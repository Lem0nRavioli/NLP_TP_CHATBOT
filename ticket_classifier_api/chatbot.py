# chatbot.py
import joblib
import json
import requests
import re
from utils import clean_text

# load model and encoder
model = joblib.load("model/chatbot_model.pkl")
encoder = joblib.load("model/label_encoder.pkl")

# load intents
with open("intents.json") as f:
    intent_data = json.load(f)["intents"]
intent_dict = {intent["tag"]: intent for intent in intent_data}

API_URL = "http://localhost:8000"
state = {"mode": None, "awaiting_input": False}

def get_response(tag):
    return intent_dict.get(tag, intent_dict["fallback"])["response"]

def chat():
    print("Hello! How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Bye!")
            break

        if state["mode"] == "create_ticket" and state["awaiting_input"]:
            response = requests.post(f"{API_URL}/predict", json={
                "id": 0, "message": user_input, "topic_group": "", "status": ""
            })
            if response.status_code == 200:
                data = response.json()
                print(f"Ticket created with ID {data['id']} — Topic: {data['topic_group']}")
            else:
                print("Could not create ticket.")
            state.update({"mode": None, "awaiting_input": False})
            continue

        if state["mode"] == "delete_ticket" and state["awaiting_input"]:
            try:
                ticket_id = int(re.findall(r"\d+", user_input)[0])
                response = requests.delete(f"{API_URL}/ticket/{ticket_id}")
                print("Deleted." if response.status_code == 200 else "❌ Not deleted.")
            except:
                print("Invalid ID.")
            state.update({"mode": None, "awaiting_input": False})
            continue

        if state["mode"] == "get_status" and state["awaiting_input"]:
            try:
                ticket_id = int(re.findall(r"\d+", user_input)[0])
                response = requests.get(f"{API_URL}/tickets")
                if response.status_code == 200:
                    tickets = response.json()
                    match = next((t for t in tickets if t["id"] == ticket_id), None)
                    if match:
                        print(f"Ticket {ticket_id} — Topic: {match['topic_group']} — Status: {match['status']}")
                    else:
                        print("Ticket not found.")
                else:
                    print("API failure.")
            except:
                print("Invalid ID.")
            state.update({"mode": None, "awaiting_input": False})
            continue
        
        # predict intent
        cleaned = clean_text(user_input)
        proba = model.predict_proba([cleaned])[0]
        max_conf = max(proba)
        tag_index = proba.argmax()

        # if certain threshold not met, fallback to default intent
        if max_conf < 0.3:
            intent_tag = "fallback"
        else:
            intent_tag = encoder.inverse_transform([tag_index])[0]

        print(f"[DEBUG] confidence: {max_conf:.2f}, intent: {intent_tag}")
        print(f"{get_response(intent_tag)}")

        if intent_tag in ["create_ticket", "delete_ticket", "get_status"]:
            state.update({"mode": intent_tag, "awaiting_input": True})

if __name__ == "__main__":
    chat()