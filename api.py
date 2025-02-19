from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
import asyncio

app = FastAPI()

class CopilotRequest(BaseModel):
    messages: List[dict]

# Trying to get the github copilot chat completion to directly stream out but it wasn't chunking properly...
# async def event_stream(messages, x_github_token):
#     with requests.post(url="https://api.githubcopilot.com/chat/completions",
#                     json={"messages":messages},
#                     headers={"authorization": f"Bearer {x_github_token}"},
#                     stream=True) as response:
#         for line in response.iter_lines():
#             if line:
#                 yield f"data: {line.decode('utf-8')}\n\n"

# This is a backup approach of artificially chunking a copilot response to create a streaming look
async def chunked_event_stream(messages, x_github_token):
    res = requests.post(url="https://api.githubcopilot.com/chat/completions",
                    json={"messages":messages},
                    headers={"authorization": f"Bearer {x_github_token}"})
    data = res.json()
    
    # Extract the assistant message content
    content = data["choices"][0]["message"]["content"]
    message_id = data["id"]
    timestamp = data["created"]
    model_name = data["model"]
    system_fingerprint = data["system_fingerprint"]

    # Send an initial empty message chunk
    initial_chunk = {
        "id": message_id,
        "object": "chat.completion.chunk",
        "created": timestamp,
        "model": model_name,
        "system_fingerprint": system_fingerprint,
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "logprobs": None,
                "finish_reason": None,
            }
        ]
    }
    yield f"data: {json.dumps(initial_chunk)}\n\n"

    # Stream response in chunks
    for word in content.split():  # Stream word by word
        chunk = {
            "id": message_id,
            "object": "chat.completion.chunk",
            "created": timestamp,
            "model": model_name,
            "system_fingerprint": system_fingerprint,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": word + " "},  # Preserve spaces
                    "logprobs": None,
                    "finish_reason": None,
                }
            ]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05)  # Simulate streaming delay

    # Send the final finish_reason chunk
    final_chunk = {
        "id": message_id,
        "object": "chat.completion.chunk",
        "created": timestamp,
        "model": model_name,
        "system_fingerprint": system_fingerprint,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "logprobs": None,
                "finish_reason": "stop",
            }
        ]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"


@app.get("/")
def read_root():
    return {"Hello": "This is a GitHub Extension Agent demo app."}

@app.post("/")
def copilot_agent(
    request: CopilotRequest,
    x_github_token: Optional[str] = Header(None)
):
    """
    Receives a GitHub Copilot request, extracts token, and processes the query.
    """

    # GitHub Copilot sends a token like this to let you validate that the request is from GitHub
    # This is not a full verification process... only checking that something called "x-github-token" exists...
    if not x_github_token:
        raise HTTPException(status_code=401, detail="Missing GitHub token")
    else:
        print(x_github_token)

    messages = [{"role":"system","content":"Answer all user messages as if you are Michael Scott from the show The Office."}] + request.messages

    return StreamingResponse(chunked_event_stream(messages, x_github_token), media_type="text/event-stream")
