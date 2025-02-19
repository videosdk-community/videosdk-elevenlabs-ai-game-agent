from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from agent.ai_agent import AIAgent

port = 8000
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_agent = None

class MeetingReqConfig(BaseModel):
    meeting_id: str
    token: str
    
async def server_operations():
    # join ai agent
    # keep server alive
    pass
    
@app.get("/test")
async def test():
    return {"message": "CORS is working!"}


# join ai agent
@app.post("/join-player")
async def join_player(req: MeetingReqConfig):
    global ai_agent
    
    ai_agent = AIAgent(req.meeting_id, req.token, "AI")
    await ai_agent.join()
    
    return {"message": "AI agent joined"}

# runnning the server on port : 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
