# NLP_TP_CHATBOT

A simple chatbot and ticket classification API using FastAPI and Python.

## Getting Started

### 1. Setup

Open a terminal and navigate to the project folder:

```bash
cd ticket_classifier_api
```

### 2. Install Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the API

In one terminal, start the FastAPI server:

```bash
uvicorn main:app --reload
```

### 4. Run the Chatbot

In another terminal, run the chatbot interface:

```bash
python chatbot.py
```

---

## Usage

- **Create a ticket:** Type a message describing your issue.
- **Delete a ticket:** Ask to delete a ticket and provide the ticket ID.
- **Check ticket status:** Ask for the status and provide the ticket ID.
- **Exit:** Type `exit` to quit the chatbot.

---

## Notes

- The API runs at `http://localhost:8000`
- Make sure the API is running before starting the chatbot.
- All data is stored in a local SQLite database (`tickets.db`).

---


