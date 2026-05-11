# Zellie AI - Chat Bot

A personal AI chatbot API that lets recruiters, collaborators, and visitors learn about you through natural conversation. Built with FastAPI and powered by OpenAI's GPT-4o-mini, it uses your LinkedIn profile, resume, and a personal bio as context to answer questions in your voice.

## Tech Stack

- **Python 3.10+**
- **An OpenAI API key** — you can generate one at [platform.openai.com](https://platform.openai.com)
- My personal context files in a `me/` directory:
  - `rosselle_linkedin.pdf` — LinkedIn profile export
  - `RosselleMacabata-MarchResume.pdf` — your resume
  - `summary.txt` — a short personal bio written in your own voice

## Running the Application

### Local Development

1. **Clone the repository:**

   ```bash
   git clone https://github.com/<your-username>/fast-chat.git
   cd fast-chat
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your OpenAI API key.** Create a `.env` file in the project root:

   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

4. **Add your context files.** Place your LinkedIn PDF, resume PDF, and `summary.txt` inside the `me/` directory.

5. **Start the server:**

   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`. The `--reload` flag enables auto-restart on code changes during development.

### Deploying to Render

The repository includes a `Procfile` that Render uses to start the application:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Steps:**

1. Push your repository to GitHub (make sure the `me/` directory with your PDFs and summary is included, or upload them as part of your Render service).
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your GitHub repository.
4. Set the following:
   - **Runtime:** Python
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** (auto-detected from Procfile)
5. Add an environment variable: `OPENAI_API_KEY` = your key.
6. Deploy. Render will assign a public URL like `https://your-service.onrender.com`.

## API Documentation

### POST /chat

The main endpoint. Sends a conversation to the AI assistant and receives a reply.

| Field      | Type             | Required | Description                                                      |
| ---------- | ---------------- | -------- | ---------------------------------------------------------------- |
| `messages` | Array of Message | Yes      | The conversation history. Each message has `role` and `content`. |

**Example Request:**

```bash
curl -X POST https://your-service.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "What kind of work does Zellie do?" }
    ]
  }'
```

**Example Response (200 OK):**

```json
{
  "reply": "I'm a product-minded, user-focused software engineer with experience across the stack. I love building thoughtful products and I'm especially energized by tech for good."
}
```

## Design Decisions and Trade-offs

### Model Choice: GPT-4o-mini

`GPT-4o-mini` was chosen over larger models like `GPT-4o` for a few reasons: it is significantly cheaper per token and responds faster, which is important for a chatbot that needs to feel conversational. The assistant only needs to retrieve and rephrase information from the provided context, not perform complex reasoning. The trade-off is slightly less nuanced language generation, but for concise 2–4 sentence answers about a specific person, the difference is negligible.

### Context via PDF Extraction at Startup

Rather than storing personal data in a database or calling an external service, the app reads LinkedIn and resume PDFs at startup using `pypdf` and loads a plain-text bio from `summary.txt`. This keeps the architecture simple (no database, no migrations, no extra infrastructure). The trade-off is that updating your information requires a redeploy, and very large or heavy PDFs might not extract cleanly. However, there are infrequent redeploys of context.

### Conversation Window: Last 10 Messages

The `/chat` endpoint truncates the conversation history to the last 10 messages before sending it to OpenAI. This prevents token usage from growing unboundedly in long conversations while still preserving enough context for natural dialogue. The trade-off is that very early messages in a long conversation will be forgotten, but in practice most visitors ask a few focused questions and move on.

### CORS: Explicit Origin Allowlist

The API uses an explicit allowlist of origins (`localhost:3000`, `rossssselle.github.io`, `rosselle.rocks`) rather than a wildcard `*`. This means only your known frontend domains can call the API from a browser, which reduces the risk of unauthorized usage or abuse of your OpenAI key.

### Max Tokens: 400

Responses are capped at 400 tokens to keep answers concise and costs predictable. This aligns with the prompt's guideline of 2–4 sentences. Longer, open-ended answers would cost more and risk going off topic or hallucinating beyond the provided context.

### No Authentication

The API has no authentication layer — it is open to any request from an allowed origin. For a personal portfolio chatbot this keeps things simple, and the CORS policy provides a basic layer of protection. If abuse became a concern, rate limiting or an API key could be added without changing the core architecture.
