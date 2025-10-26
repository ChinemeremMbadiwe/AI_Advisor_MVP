from sqlalchemy.orm import Session
from . import models

def save_recommendation(db: Session, user_id: int, prompt: str, response: str, request_type: str = "analyze", model: str = "gemini"):
    rec = models.Recommendation(
        user_id=user_id,
        prompt=prompt[:4000],
        response=response[:8000],
        request_type=request_type,
        model=model
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec