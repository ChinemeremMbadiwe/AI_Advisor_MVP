# src/advisor_engine.py
from dataclasses import dataclass
from typing import Dict, Any
import json


# ============================================================
# DATA MODEL FOR USER CONTEXT
# ============================================================

@dataclass
class UserProfile:
    user_id: int
    name: str
    user_type: str             # "salary_earner", "student", "sme_owner"
    monthly_income: float
    monthly_spending: float
    savings_balance: float
    credit_score: int
    active_loans: int
    financial_goals: str


# ============================================================
# RULE-BASED PERSONALIZATION ENGINE
# ============================================================

class RuleEngine:
    """Determines advisory focus and selects appropriate LLM prompt type."""

    def classify_user(self, profile: UserProfile) -> str:
        """Classify user into a financial segment."""
        if profile.user_type == "student":
            return "student"
        elif profile.user_type == "sme_owner":
            return "sme_owner"
        elif profile.monthly_income < 150_000:
            return "low_income"
        elif 150_000 <= profile.monthly_income <= 500_000:
            return "mid_income"
        else:
            return "high_income"

    def generate_context(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate contextual summary for personalization."""
        ratio = profile.monthly_spending / profile.monthly_income if profile.monthly_income else 0
        category = self.classify_user(profile)

        return {
            "user_segment": category,
            "spending_ratio": round(ratio, 2),
            "income": profile.monthly_income,
            "spending": profile.monthly_spending,
            "savings": profile.savings_balance,
            "credit_score": profile.credit_score,
            "goals": profile.financial_goals,
            "active_loans": profile.active_loans,
        }


# ============================================================
# PROMPT TEMPLATE MANAGER
# ============================================================

class PromptTemplates:
    """Holds pre-defined LLM prompt templates."""

    SAVINGS_TEMPLATE = """
    You are an AI financial advisor. Analyze the user's financial data:
    - Income: {monthly_income}
    - Spending: {monthly_spending}
    - Savings: {savings_balance}
    - Goals: {financial_goals}
    - Active loans: {active_loans}

    Based on this, create a personalized savings plan.
    Include:
    1. Recommended savings per month
    2. Spending adjustment advice
    3. 3-month financial improvement tips
    """

    INVESTMENT_TEMPLATE = """
    You are a professional wealth advisor. Given this profile:
    - Income: {monthly_income}
    - Savings ratio: {savings_ratio}
    - Credit score: {credit_score}
    - Goals: {financial_goals}

    Recommend suitable investment options.
    For each option, include expected returns, risks, and timeframe.
    """

    LOAN_TEMPLATE = """
    You are a credit specialist. Evaluate this customer's loan eligibility:
    - Monthly income: {monthly_income}
    - Spending: {monthly_spending}
    - Active loans: {active_loans}
    - Credit score: {credit_score}
    - Loan purpose: {loan_purpose}

    Suggest:
    1. Safe loan amount range
    2. Ideal repayment tenure
    3. Tips to maintain a healthy credit score
    """

    SME_TEMPLATE = """
    You are a financial strategist for small business owners.
    The user's business generates about {monthly_income} monthly and spends {monthly_spending}.
    Their goals: {financial_goals}

    Provide:
    1. Cash flow improvement advice
    2. Reinvestment or expansion ideas
    3. Suitable SME loan or credit line recommendation
    """


# ============================================================
# MAIN ADVISORY ENGINE
# ============================================================

class AdvisorEngine:
    """Combines rule engine and templates to build dynamic LLM prompts."""

    def __init__(self):
        self.rules = RuleEngine()
        self.templates = PromptTemplates()

    def create_prompt(self, profile: UserProfile, request_type: str = "auto") -> str:
        """
        Dynamically generate a prompt based on user profile and context.
        request_type can be: 'savings', 'investment', 'loan', or 'auto'
        """

        context = self.rules.generate_context(profile)
        segment = context["user_segment"]

        # AUTO-SELECTION logic
        if request_type == "auto":
            if segment == "low_income":
                request_type = "savings"
            elif segment == "mid_income":
                request_type = "savings"
            elif segment == "high_income":
                request_type = "investment"
            elif segment == "student":
                request_type = "savings"
            elif segment == "sme_owner":
                request_type = "sme"

        # Select the template
        if request_type == "savings":
            template = self.templates.SAVINGS_TEMPLATE
        elif request_type == "investment":
            template = self.templates.INVESTMENT_TEMPLATE
        elif request_type == "loan":
            template = self.templates.LOAN_TEMPLATE
        elif request_type == "sme":
            template = self.templates.SME_TEMPLATE
        else:
            raise ValueError(f"Unknown request_type: {request_type}")

        # Format prompt
        prompt = template.format(
            monthly_income=profile.monthly_income,
            monthly_spending=profile.monthly_spending,
            savings_balance=profile.savings_balance,
            savings_ratio=round(profile.savings_balance / profile.monthly_income, 2)
            if profile.monthly_income else 0,
            financial_goals=profile.financial_goals,
            credit_score=profile.credit_score,
            active_loans=profile.active_loans,
            loan_purpose="personal development"
        )

        return prompt


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Example user
    user = UserProfile(
        user_id=101,
        name="Adaeze Okafor",
        user_type="salary_earner",
        monthly_income=350_000,
        monthly_spending=200_000,
        savings_balance=150_000,
        credit_score=720,
        active_loans=1,
        financial_goals="Save for a car and build emergency fund"
    )

    advisor = AdvisorEngine()

    # Generate prompt automatically
    savings_prompt = advisor.create_prompt(user)
    print("🧾 Generated Prompt:")
    print("=" * 50)
    print(savings_prompt)

    # If using an LLM (e.g., OpenAI API):
    # response = llm_api.generate(savings_prompt)
    # print(response)