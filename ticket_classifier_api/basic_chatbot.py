import json
import requests
import re

API_URL = "http://localhost:8000"

# Load intents
with open("intents.json") as f:
    intents = json.load(f)

def recognize_intent(message):
    message = message.lower()
    for intent, data in intents.items():
        for pattern in data.get("patterns", []):
            if pattern in message:
                return intent
    return "fallback"

def chat():
    state = {"mode": None, "awaiting_input": False}

    print("🤖 Hello! How can I help you today?")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("👋 Bye!")
            break

        # Handle conversational state
        if state["mode"] == "create_ticket" and state["awaiting_input"]:
            # Send to FastAPI
            response = requests.post(f"{API_URL}/predict", json={
                "id": 0,
                "message": user_input,
                "topic_group": "",
                "status": ""
            })
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Ticket created with ID {data['id']} under topic: {data['topic_group']}")
            else:
                print("❌ Failed to create ticket.")
            state["mode"] = None
            state["awaiting_input"] = False
            continue

        if state["mode"] == "delete_ticket" and state["awaiting_input"]:
            try:
                ticket_id = int(re.findall(r'\d+', user_input)[0])
                response = requests.delete(f"{API_URL}/ticket/{ticket_id}")
                if response.status_code == 200:
                    print(f"🗑️ Ticket {ticket_id} deleted.")
                else:
                    print(f"❌ Ticket {ticket_id} could not be deleted.")
            except IndexError:
                print("🤖 Please provide a valid ticket ID.")
            state["mode"] = None
            state["awaiting_input"] = False
            continue

        if state["mode"] == "get_status" and state["awaiting_input"]:
            try:
                ticket_id = int(re.findall(r'\d+', user_input)[0])
                response = requests.get(f"{API_URL}/tickets")
                if response.status_code == 200:
                    tickets = response.json()
                    match = next((t for t in tickets if t["id"] == ticket_id), None)
                    if match:
                        print(f"📋 Ticket {ticket_id} — Topic: {match['topic_group']} — Status: {match['status']}")
                    else:
                        print(f"🤖 No ticket found with ID {ticket_id}.")
                else:
                    print("❌ Could not retrieve tickets.")
            except IndexError:
                print("🤖 Please provide a valid ticket ID.")
            state["mode"] = None
            state["awaiting_input"] = False
            continue

        # Recognize intent
        intent = recognize_intent(user_input)

        if intent == "create_ticket":
            print(intents[intent]["response"])
            state["mode"] = intent
            state["awaiting_input"] = True

        elif intent == "delete_ticket":
            print(intents[intent]["response"])
            state["mode"] = intent
            state["awaiting_input"] = True

        elif intent == "get_status":
            print(intents[intent]["response"])
            state["mode"] = intent
            state["awaiting_input"] = True

        else:
            print(intents["fallback"]["response"])


if __name__ == "__main__":
    chat()