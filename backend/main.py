import asyncio
import json
import random
import ast
from collections import Counter
from bpe_tokenizer import get_tokenizer, reconvert_special_tokens
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from model import TrigramLanguageModel

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    story: str
    
tokenizer = get_tokenizer('.')

with open("trigram_model.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

model = TrigramLanguageModel(loaded["vocab_size"])
model.unigrams = Counter(loaded["unigrams"])
model.bigrams = Counter({ast.literal_eval(k): v for k, v in loaded["bigrams"].items()})
model.trigrams = Counter({ast.literal_eval(k): v for k, v in loaded["trigrams"].items()})
model.total_tokens = loaded["total_tokens"]

l1, l2, l3 = loaded["lambdas"]
eot_id = loaded["eot_id"]


def is_urdu_text(text):
    """Check if text contains primarily Urdu characters"""
    if not text.strip():
        return False
    
    # Urdu Unicode range: 0600-06FF (Arabic/Urdu), 0750-077F (Arabic Supplement)
    urdu_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F')
    total_chars = sum(1 for c in text if c.strip() and not c.isspace())
    
    if total_chars == 0:
        return False
    
    # At least 70% should be Urdu characters
    return (urdu_chars / total_chars) >= 0.7

async def generate_stream(prompt: str):
    """Generator that yields tokens one by one"""
    prefix_tokens = tokenizer.encode(prompt)
    tokens = list(prefix_tokens)
    
    while len(tokens) < 2:
        tokens.insert(0, tokens[0] if tokens else 0)
    
    # Yield the prefix first (with reconverted tokens)
    prefix_text = tokenizer.decode(prefix_tokens)
    yield reconvert_special_tokens(prefix_text)
    await asyncio.sleep(0.05)  # Small delay to ensure streaming effect
    
    while True:
        w1, w2 = tokens[-2], tokens[-1]
        
        probs = []
        for token_id in range(model.vocab_size):
            p = model.interpolated_prob(w1, w2, token_id, l1, l2, l3)
            probs.append(p)
        
        next_token = random.choices(range(model.vocab_size), weights=probs, k=1)[0]
        tokens.append(next_token)
        
        # Decode and reconvert the new token before yielding
        token_text = tokenizer.decode([next_token])
        yield reconvert_special_tokens(token_text)
        await asyncio.sleep(0.02)  # Delay between tokens
        
        if next_token == eot_id:
            break

@app.post("/generate")
async def generate_story(request: GenerateRequest):
    # Validate that input is Urdu
    if not is_urdu_text(request.prompt):
        return JSONResponse(
            status_code=400,
            content={"error": "براہ کرم اردو میں لکھیں (Please write in Urdu)"}
        )
    
    return StreamingResponse(
        generate_stream(request.prompt),
        media_type="text/plain"
    )