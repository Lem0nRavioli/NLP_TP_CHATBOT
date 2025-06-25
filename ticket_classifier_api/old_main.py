from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os

# load model and vectorizer
clf = joblib.load(os.path.join("model", "classifier.pkl"))
vectorizer = joblib.load(os.path.join("model", "vectorizer.pkl"))

app = FastAPI(title="Ticket Classifier API")

class Ticket(BaseModel):
    message: str

@app.post("/predict")
def predict_ticket(ticket: Ticket):
    X = vectorizer.transform([ticket.message])
    prediction = clf.predict(X)[0]
    return {"topic_group": prediction}
