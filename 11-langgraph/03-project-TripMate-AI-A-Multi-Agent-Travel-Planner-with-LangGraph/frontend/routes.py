import json
import traceback

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import iterate_in_threadpool

from backend.runner import run_travel_agent, stream_travel_agent
from frontend.schemas import TravelRequest


def create_router(templates: Jinja2Templates) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={},
        )

    @router.post("/api/travel")
    async def travel_planner(request_data: TravelRequest):
        try:
            user_message = request_data.message.strip()

            if not user_message:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": "Message cannot be empty.",
                    },
                )

            result = run_travel_agent(
                user_input=user_message,
                thread_id=request_data.thread_id,
            )

            return JSONResponse(
                content={
                    "success": True,
                    "thread_id": result["thread_id"],
                    "answer": result["answer"],
                    "flight_results": result["flight_results"],
                    "hotel_results": result["hotel_results"],
                    "itinerary": result["itinerary"],
                    "llm_calls": result["llm_calls"],
                }
            )

        except Exception as e:
            print("ERROR:", e)
            traceback.print_exc()

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": str(e),
                },
            )

    @router.post("/api/travel/stream")
    async def travel_planner_stream(request_data: TravelRequest):
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty.",
                },
            )

        def event_stream():
            try:
                for event in stream_travel_agent(
                    user_input=user_message,
                    thread_id=request_data.thread_id,
                ):
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            except Exception as e:
                print("STREAM ERROR:", e)
                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            iterate_in_threadpool(event_stream()),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "message": "AI Travel Planner API is running",
        }

    @router.get("/favicon.ico")
    async def favicon():
        return JSONResponse(content={})

    return router
