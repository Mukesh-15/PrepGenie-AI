"""
Interview Session Store

Provides thread-safe in-memory storage for active interview sessions,
questions, evaluations, and reports.
"""
import uuid
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime


class InterviewStore:
    """In-memory data store for interview sessions."""

    def __init__(self):
        self._lock = threading.Lock()
        self._interviews: Dict[str, Dict[str, Any]] = {}

    def create_interview(self, session_id: str, resume_file_name: str) -> Dict[str, Any]:
        """Create a new interview record."""
        interview_id = uuid.uuid4().hex
        interview = {
            "interviewId": interview_id,
            "sessionId": session_id,
            "resumeFileName": resume_file_name,
            "status": "in_progress",
            "totalQuestions": 0,
            "createdAt": datetime.utcnow().isoformat(),
            "questions": [],
            "report": None
        }

        with self._lock:
            self._interviews[interview_id] = interview

        return interview

    def get_interview(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve interview state by ID."""
        with self._lock:
            interview = self._interviews.get(interview_id)
            if not interview:
                return None
            return dict(interview)

    def add_question(
        self,
        interview_id: str,
        question_text: str,
        category: str,
        difficulty: str,
        context_used: str
    ) -> Optional[Dict[str, Any]]:
        """Add a generated question to the interview."""
        with self._lock:
            interview = self._interviews.get(interview_id)
            if not interview:
                return None

            question_id = uuid.uuid4().hex
            order = interview["totalQuestions"] + 1

            question_item = {
                "questionId": question_id,
                "question": question_text,
                "category": category,
                "difficulty": difficulty,
                "contextUsed": context_used,
                "order": order,
                "answer": "",
                "evaluation": None
            }

            interview["questions"].append(question_item)
            interview["totalQuestions"] = order

            return {
                "questionId": question_id,
                "question": question_text,
                "category": category,
                "difficulty": difficulty,
                "questionNumber": order,
                "contextUsed": context_used
            }

    def save_answer_and_evaluation(
        self,
        interview_id: str,
        question_id: str,
        answer: str,
        evaluation_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Store user answer and evaluation for a specific question."""
        with self._lock:
            interview = self._interviews.get(interview_id)
            if not interview:
                return None

            target_q = None
            for q in interview["questions"]:
                if q["questionId"] == question_id:
                    target_q = q
                    break

            if not target_q:
                return None

            evaluation_id = uuid.uuid4().hex
            eval_record = {
                "evaluationId": evaluation_id,
                "technicalScore": evaluation_data.get("technical_score", 0),
                "communicationScore": evaluation_data.get("communication_score", 0),
                "problemSolvingScore": evaluation_data.get("problem_solving_score", 0),
                "overallScore": evaluation_data.get("overall_score", 0),
                "strengths": evaluation_data.get("strengths", []),
                "weaknesses": evaluation_data.get("weaknesses", []),
                "feedback": evaluation_data.get("feedback", ""),
                "followUpSuggestion": evaluation_data.get("follow_up_suggestion", "")
            }

            target_q["answer"] = answer
            target_q["evaluation"] = eval_record

            return eval_record

    def save_report(self, interview_id: str, report_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save final report and mark interview completed."""
        with self._lock:
            interview = self._interviews.get(interview_id)
            if not interview:
                return None

            report_id = uuid.uuid4().hex
            report_record = {
                "reportId": report_id,
                "overallScore": report_data.get("overall_score", 0),
                "technicalScore": report_data.get("technical_score", 0),
                "communicationScore": report_data.get("communication_score", 0),
                "problemSolvingScore": report_data.get("problem_solving_score", 0),
                "strongAreas": report_data.get("strong_areas", []),
                "weakAreas": report_data.get("weak_areas", []),
                "recommendedLearning": report_data.get("recommended_learning", []),
                "overallFeedback": report_data.get("overall_feedback", "")
            }

            interview["report"] = report_record
            interview["status"] = "completed"

            return report_record

    def get_interview_history(self, interview_id: str) -> List[Dict[str, Any]]:
        """Build interview history for LLM question generation."""
        with self._lock:
            interview = self._interviews.get(interview_id)
            if not interview:
                return []

            history = []
            for q in interview["questions"]:
                if q.get("answer"):
                    eval_data = q.get("evaluation") or {}
                    history.append({
                        "question": q["question"],
                        "answer": q["answer"],
                        "category": q["category"],
                        "evaluation": {
                            "overall_score": eval_data.get("overallScore", 0),
                            "technical_score": eval_data.get("technicalScore", 0),
                            "communication_score": eval_data.get("communicationScore", 0),
                            "problem_solving_score": eval_data.get("problemSolvingScore", 0),
                            "feedback": eval_data.get("feedback", ""),
                            "strengths": eval_data.get("strengths", []),
                            "weaknesses": eval_data.get("weaknesses", [])
                        } if eval_data else {}
                    })
            return history


# Global singleton instance
store = InterviewStore()
