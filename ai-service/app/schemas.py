from pydantic import BaseModel, Field, field_validator


class InterviewQuestion(BaseModel):
    """Schema for generated interview questions."""
    question: str = Field(description="Interview question based on the resume")
    category: str = Field(description="Question topic or skill category (e.g. React, System Design, Python, Projects)")
    difficulty: str = Field(description="Question difficulty: easy, medium, or hard")
    context_used: str = Field(description="Resume context text used to formulate the question")

    @field_validator("difficulty", mode="before")
    @classmethod
    def sanitize_difficulty(cls, val: str) -> str:
        if not val or not isinstance(val, str):
            return "medium"
        v = val.lower().strip()
        if "easy" in v:
            return "easy"
        elif "hard" in v:
            return "hard"
        return "medium"


class AnswerEvaluation(BaseModel):
    """Schema for answer evaluation output."""
    technical_score: int = Field(ge=0, le=10, description="Technical accuracy score (0-10)")
    communication_score: int = Field(ge=0, le=10, description="Communication clarity score (0-10)")
    problem_solving_score: int = Field(ge=0, le=10, description="Problem solving score (0-10)")
    overall_score: int = Field(ge=0, le=10, description="Overall score for this answer (0-10)")
    strengths: list[str] = Field(default_factory=list, description="Key strengths in the answer")
    weaknesses: list[str] = Field(default_factory=list, description="Areas where the answer was weak")
    feedback: str = Field(description="Constructive feedback for improvement")
    follow_up_suggestion: str = Field(default="", description="Follow-up question if answer was weak")


class FinalReport(BaseModel):
    """Schema for the final comprehensive performance report."""
    overall_score: int = Field(ge=0, le=100, description="Aggregated overall score (0-100)")
    technical_score: int = Field(ge=0, le=100, description="Technical score (0-100)")
    communication_score: int = Field(ge=0, le=100, description="Communication score (0-100)")
    problem_solving_score: int = Field(ge=0, le=100, description="Problem solving score (0-100)")
    strong_areas: list[str] = Field(default_factory=list, description="Key competencies and strong skills")
    weak_areas: list[str] = Field(default_factory=list, description="Topics that need improvement")
    recommended_learning: list[str] = Field(default_factory=list, description="Suggested study topics or resources")
    overall_feedback: str = Field(description="Comprehensive final feedback summary")


class SubmitAnswerRequest(BaseModel):
    """Request body when candidate submits an answer."""
    questionId: str
    answer: str
