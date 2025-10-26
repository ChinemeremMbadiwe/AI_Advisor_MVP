from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .deps import get_db
from .schemas import AnalyzeRequest, AnalyzeResponse, RecommendRequest, RecommendResponse
from .ai_wrapper import analyze_user, recommend_products
from .crud import save_recommendation
from .security import basic_auth
from .models import User

app = FastAPI(title="AI Advisor API")

app = FastAPI(title="AI Advisor API")

@app.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(basic_auth)])
def analyze(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from .advisor_engine import UserProfile
    profile = UserProfile(
        user_id=user.user_id,
        name=user.name,
        user_type=user.occupation or "salary_earner",
        monthly_income=user.monthly_income or 0,
        monthly_spending=user.monthly_spending or 0,
        savings_balance=user.savings or 0,
        credit_score=user.credit_score or 650,
        active_loans=0,
        financial_goals="Improve savings"
    )

    result = analyze_user(profile)
    save_recommendation(db, user.user_id, result["prompt"], result["response"], "analyze")

    return AnalyzeResponse(summary=result["summary"], recommendations=[result["response"][:500]])

@app.post("/recommend", response_model=RecommendResponse, dependencies=[Depends(basic_auth)])
def recommend(payload: RecommendRequest, db: Session = Depends(get_db)):
    # build profile similar to above
    if payload.user_id:
        user = db.query(User).filter(User.user_id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        from .advisor_engine import UserProfile
        profile = UserProfile(
            user_id=user.user_id, name=user.name, user_type=user.occupation or "salary_earner",
            monthly_income=user.monthly_income or 0, monthly_spending=user.monthly_spending or 0,
            savings_balance=user.savings or 0, credit_score=user.credit_score or 650,
            active_loans=len(user.loans) if hasattr(user,'loans') else 0, financial_goals=""
        )
    else:
        raise HTTPException(status_code=400, detail="Provide user_id")

    result = recommend_products(profile)
    save_recommendation(db, user_id=profile.user_id, prompt=result["prompt"], response=result["response"], request_type="recommend", model="gemini")
    # parse free text into product suggestions is optional; return raw for MVP
    return RecommendResponse(products=[{"name": "AI suggestion", "rationale": result["response"][:800]}])