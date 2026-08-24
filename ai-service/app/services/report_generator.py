"""
Report Generator Service (LLM 3)

Generates a comprehensive final interview report from all evaluations.

Key design decisions:
- Receives ALL evaluations as structured data (not raw text)
- Aggregates per-question scores into overall performance metrics (0-100 scale)
- Identifies strong/weak areas across all questions
- Generates actionable learning recommendations
- Uses with_structured_output(FinalReport) for guaranteed schema
"""
import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.schemas import FinalReport

logger = logging.getLogger(__name__)

REPORT_GENERATOR_PROMPT = """You are an expert interview performance analyst. Generate a 
comprehensive final interview report based on all the evaluation data provided.

═══════════════════════════════════════════════════════════
INTERVIEW EVALUATIONS
═══════════════════════════════════════════════════════════
{evaluations_text}

═══════════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════════

Analyze ALL the evaluations above and generate a comprehensive report:

1. SCORING (0-100 scale):
   - Calculate aggregate scores by considering all individual question scores.
   - Weight scores by question difficulty if possible.
   - The overall_score should reflect the candidate's complete performance.

2. STRONG AREAS:
   - Identify topics/categories where the candidate consistently scored well (7+ out of 10).
   - Be specific (e.g., "React component architecture" not just "React").

3. WEAK AREAS:
   - Identify topics where the candidate struggled (scored 5 or below).
   - Be specific about what aspects were weak.

4. RECOMMENDED LEARNING:
   - Based on weak areas, suggest specific topics to study.
   - Be actionable (e.g., "Database indexing and query optimization" not just "databases").

5. OVERALL FEEDBACK:
   - Write a comprehensive narrative (3-5 sentences minimum).
   - Mention specific strengths and areas for growth.
   - Be encouraging but honest.
   - Reference specific questions/answers when possible."""


def generate_report(evaluations: list[dict]) -> FinalReport:
    """
    Generate a final interview report from all evaluations.

    Args:
        evaluations: List of evaluation dicts, each containing:
            - question, answer, category
            - technical_score, communication_score, problem_solving_score, overall_score
            - strengths, weaknesses, feedback

    Returns:
        FinalReport with aggregated scores, analysis, and recommendations
    """
    # Format evaluations into readable text for the LLM
    evaluations_text = ""
    for i, eval_data in enumerate(evaluations, 1):
        evaluations_text += f"\n{'='*50}\n"
        evaluations_text += f"QUESTION {i}\n"
        evaluations_text += f"{'='*50}\n"
        evaluations_text += f"Category: {eval_data.get('category', 'N/A')}\n"
        evaluations_text += f"Question: {eval_data.get('question', 'N/A')}\n"
        evaluations_text += f"Answer: {eval_data.get('answer', 'N/A')}\n"
        evaluations_text += f"Technical Score: {eval_data.get('technical_score', 'N/A')}/10\n"
        evaluations_text += f"Communication Score: {eval_data.get('communication_score', 'N/A')}/10\n"
        evaluations_text += f"Problem Solving Score: {eval_data.get('problem_solving_score', 'N/A')}/10\n"
        evaluations_text += f"Overall Score: {eval_data.get('overall_score', 'N/A')}/10\n"
        evaluations_text += f"Strengths: {', '.join(eval_data.get('strengths', []))}\n"
        evaluations_text += f"Weaknesses: {', '.join(eval_data.get('weaknesses', []))}\n"
        evaluations_text += f"Feedback: {eval_data.get('feedback', 'N/A')}\n"

    # Build the report generation chain
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.4
    )
    structured_llm = llm.with_structured_output(FinalReport)

    prompt = ChatPromptTemplate.from_messages([
        ("system", REPORT_GENERATOR_PROMPT),
        ("human", "Generate the comprehensive final interview report.")
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "evaluations_text": evaluations_text
    })

    logger.info(
        f"Report generated - Overall: {result.overall_score}/100, "
        f"Technical: {result.technical_score}/100, "
        f"Communication: {result.communication_score}/100, "
        f"Problem Solving: {result.problem_solving_score}/100"
    )

    return result
