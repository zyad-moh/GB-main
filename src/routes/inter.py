from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from controllers import NLPController
import uuid
import json
import logging
from typing import Optional

logger = logging.getLogger('uvicorn.error')

interview_router1 = APIRouter(
    prefix="/api/v1/interview",
    tags=["api_v1", "interview"],
)

# In-memory session store
sessions = {}


class StartRequest(BaseModel):
    role: str = "AI Engineer"
    difficulty: str = "Mid-Level"
    interview_type: str = "Mixed"


class AnswerRequest(BaseModel):
    answer: str
    session_id: str


class EvaluateRequest(BaseModel):
    session_id: str


@interview_router1.post("/start")
async def start(request: Request):
    """Start a new interview session — LLM generates questions based on role, difficulty, and type."""
    # Defaults
    role = "AI Engineer"
    difficulty = "Mid-Level"
    interview_type = "Mixed"

    # Try to read from body if provided
    try:
        body = await request.json()
        if body:
            role = body.get("role", role)
            difficulty = body.get("difficulty", difficulty)
            interview_type = body.get("interview_type", interview_type)
    except Exception:
        pass

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    # Build context string with role + difficulty + type
    context = f"{difficulty} {role} - {interview_type} interview"
    questions = nlp_controller.generate_interview_questions(context=context)

    if not questions or len(questions) == 0:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to generate interview questions."}
        )

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "role": role,
        "difficulty": difficulty,
        "interview_type": interview_type,
        "questions": questions,
        "answers": [],
        "evaluations": [],
        "current_index": 0,
        "score": 0,
        "finished": False,
    }

    return {
        "session_id": session_id,
        "question": questions[0],
        "total_questions": len(questions),
        "current": 1,
        "role": role,
        "difficulty": difficulty,
        "interview_type": interview_type,
    }


@interview_router1.post("/answer")
async def answer(request: Request, req: AnswerRequest):
    """Submit an answer, get AI evaluation and next question."""
    if req.session_id not in sessions:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Session not found. Please start a new interview."}
        )

    session = sessions[req.session_id]
    idx = session["current_index"]
    questions = session["questions"]

    if idx >= len(questions):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Interview already completed."}
        )

    current_question = questions[idx]

    # Use LLM to evaluate the answer
    generation_client = request.app.generation_client
    system_prompt = "You are a strict but fair technical interviewer."
    eval_prompt = f"""
You are evaluating a candidate's interview answer.

Role: {session['role']}
Difficulty: {session['difficulty']}

Question:
{current_question}

Candidate Answer:
{req.answer}

Evaluate the answer and return JSON ONLY:
{{
    "correct": true or false,
    "score": 0-10,
    "feedback": "brief constructive feedback"
}}
"""

    chat_history = [generation_client.construct_prompt(
        prompt=system_prompt,
        role=generation_client.enums.SYSTEM.value
    )]

    result_text = generation_client.generate_text(
        prompt=eval_prompt,
        chat_history=chat_history
    )

    try:
        cleaned = result_text.replace("```json", "").replace("```", "").strip()
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1:
            cleaned = cleaned[start_idx:end_idx + 1]
        result = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        result = {"correct": False, "score": 0, "feedback": "Could not evaluate answer."}

    # Update session
    session["answers"].append(req.answer)
    session["evaluations"].append(result)
    session["score"] += result.get("score", 0)
    session["current_index"] = idx + 1

    # Check if there are more questions
    has_next = (idx + 1) < len(questions)
    next_question = questions[idx + 1] if has_next else None

    if not has_next:
        session["finished"] = True

    response = {
        "correct": result.get("correct", False),
        "score": result.get("score", 0),
        "feedback": result.get("feedback", ""),
        "total_score": session["score"],
        "current": idx + 2,
        "total_questions": len(questions),
        "finished": not has_next,
    }

    if next_question:
        response["next_question"] = next_question

    return response


@interview_router1.post("/evaluate")
async def evaluate(request: Request):
    """Generate a final interview report using the LLM."""
    try:
        body = await request.json()
        session_id = body.get("session_id")
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "session_id is required."}
        )

    if not session_id or session_id not in sessions:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Session not found."}
        )

    session = sessions[session_id]

    if not session["finished"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Interview not yet completed."}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    evaluation = nlp_controller.evaluate_interview(
        questions=session["questions"],
        answers=session["answers"]
    )

    # Determine readiness level
    overall = evaluation.get("overall_score", 0)
    difficulty = session.get("difficulty", "Mid-Level")
    role = session.get("role", "Engineer")
    if overall >= 7:
        readiness = f"Ready for {difficulty} {role}"
    elif overall >= 5:
        readiness = f"Almost ready for {difficulty} {role} — needs improvement"
    else:
        readiness = f"Not yet ready for {difficulty} {role} — more preparation needed"

    return {
        "session_id": session_id,
        "role": session["role"],
        "difficulty": session["difficulty"],
        "interview_type": session["interview_type"],
        "total_questions": len(session["questions"]),
        "overall_score": evaluation.get("overall_score", 0),
        "scores": evaluation.get("scores", {}),
        "strengths": evaluation.get("strengths", []),
        "weaknesses": evaluation.get("weaknesses", []),
        "feedback": evaluation.get("feedback", ""),
        "decision": evaluation.get("decision", ""),
        "readiness": readiness,
    }


@interview_router1.get("/sessions")
async def list_sessions():
    """List all interview sessions (for upcoming/history display)."""
    result = []
    for sid, session in sessions.items():
        result.append({
            "session_id": sid,
            "role": session["role"],
            "difficulty": session["difficulty"],
            "interview_type": session["interview_type"],
            "total_questions": len(session["questions"]),
            "answered": len(session["answers"]),
            "score": session["score"],
            "finished": session["finished"],
        })
    return result
