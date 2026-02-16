import json
import random
from collections import Counter
from bpe_tokenizer import get_tokenizer
from fastapi import FastAPI
from pydantic import BaseModel
from model import TrigramLanguageModel

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    story: str
    
tokenizer = get_tokenizer('.')

with open("trigram_model.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

model = TrigramLanguageModel(loaded["vocab_size"])
model.unigrams = Counter(loaded["unigrams"])
model.bigrams = Counter({eval(k): v for k, v in loaded["bigrams"].items()})
model.trigrams = Counter({eval(k): v for k, v in loaded["trigrams"].items()})
model.total_tokens = loaded["total_tokens"]

l1, l2, l3 = loaded["lambdas"]
eot_id = loaded["eot_id"]

@app.post("/generate")
def generate_story(request: GenerateRequest):

    prefix_tokens = tokenizer.encode(request.prompt)
    generated_tokens = model.generate(prefix_tokens, l1, l2, l3, eot_id)    
    story = tokenizer.decode(generated_tokens)

    return GenerateResponse(story=story)