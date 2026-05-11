from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import openai
import os

from dotenv import load_dotenv
from pypdf import PdfReader

app = FastAPI()

# -------------------------------------------------------
# CORS — add your GitHub Pages domain here once deployed
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rossssselle.github.io", 
        "https://rosselle.rocks"  # <-- replace with your domain
    ],
    allow_methods=["POST"],
    allow_headers=["*"],
)

client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# -------------------------------------------------------
# PASTE YOUR CONTEXT BELOW
# -------------------------------------------------------
# Tips:
#   - Copy/paste plain text from your LinkedIn PDF export
#   - Add your resume text
#   - Write a short personal bio in your own voice

reader = PdfReader("me/rosselle_linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

reader = PdfReader("me/RosselleMacabata-MarchResume.pdf")
resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()


name = "Rosselle Macabata"
nickname = "Zellie"


system_prompt = f"""
You are an AI assistant representing {name} or {nickname}. Your job is to help recruiters,
collaborators, and curious visitors learn about {nickname}'s background, skills,
projects, and experience. Respond in a warm, confident, and professional tone — as
if you ARE {nickname} speaking in first person.

Guidelines:
- Answer questions about experience, skills, projects, and background using the
  context below. Be specific and cite real details when possible.
- For recruiter questions (availability, salary, roles), be helpful and direct.
- If asked something not covered in the context, say honestly that you don't have
  that detail but offer to connect them via email.
- Never make up jobs, skills, or experiences not mentioned below.
- Keep responses concise — 2–4 sentences unless a longer answer is clearly needed.
- Sound human, not robotic. Use "I" naturally.

--- LINKEDIN / EXPERIENCE CONTEXT ---
{linkedin}

--- RESUME CONTEXT ---
{resume}

--- PERSONAL BIO ---
{summary}
"""

# -------------------------------------------------------
# Request / Response models
# -------------------------------------------------------
class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    reply: str

# -------------------------------------------------------
# Chat endpoint
# -------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    # Build the message list for OpenAI
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in req.messages[-10:]:   # keep last 10 turns to stay within context
        openai_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            max_tokens=400,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        return ChatResponse(reply=reply)
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
