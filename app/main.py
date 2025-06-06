import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import handoff, question, response, user, channel, user_channel
from fastapi_mcp import FastApiMCP

app = FastAPI(title="HITL Workflow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(handoff.router, prefix="/handoff", tags=["handoff"])
app.include_router(question.router, prefix="/questions", tags=["questions"])
app.include_router(response.router, prefix="/responses", tags=["responses"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(channel.router, prefix="/channels", tags=["channels"])
app.include_router(user_channel.router, prefix="/user-channels", tags=["user-channels"])


mcp = FastApiMCP(app, include_tags=["handoff"])
mcp.mount()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8900)