from fastapi import FastAPI, Depends
from pydantic import BaseModel
import joblib, os
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine
from models import Base, TicketRecord

from sqlalchemy.future import select

# Load model
clf = joblib.load(os.path.join("model", "classifier.pkl"))
vectorizer = joblib.load(os.path.join("model", "vectorizer.pkl"))

app = FastAPI(title="Ticket Classifier API")

# Create DB tables at startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class Ticket(BaseModel):
    id: int
    message: str
    topic_group: str
    status: str

    class Config:
        orm_mode = True

@app.post("/predict")
async def predict_ticket(ticket: Ticket, db: AsyncSession = Depends(get_db)):
    X = vectorizer.transform([ticket.message])
    prediction = clf.predict(X)[0]

    new_record = TicketRecord(message=ticket.message, topic_group=prediction)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return {"id": new_record.id, "topic_group": prediction}

@app.get("/tickets", response_model=List[Ticket])
async def get_all_tickets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketRecord))
    tickets = result.scalars().all()
    return tickets

@app.delete("/ticket/{ticket_id}")
async def delete_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TicketRecord).where(TicketRecord.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket:
        return {"error": "Ticket not found"}

    await db.delete(ticket)
    await db.commit()
    return {"status": "deleted", "id": ticket_id}
