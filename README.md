# Story-teller-3000

Urdu story generation app powered by a custom BPE tokenizer and an interpolated trigram language model.

## Features

- Streaming story generation from `/generate` endpoint
- BPE + trigram LM with no heavy GPU dependencies
- Minimal chat UI

## Repository Structure

```text
backend/        FastAPI app, tokenizer/model loader, pretrained artifacts
frontend/       Next.js app and chat UI components
scraper/        Urdu stories scraping and preprocessing assets
tokenizer/      BPE tokenizer notebooks and exported vocab/merges
trigram model/  Trigram model training notebook and exported model
```

## Workflow (High Level)

1. Frontend sends a prompt to `POST /generate`.
2. Prompt is encoded with BPE tokenizer.
3. Trigram LM samples next token using interpolated probabilities.
4. Tokens are decoded and streamed back as plain text.

Model interpolation:

$$
P(w_3 \mid w_1, w_2) = \lambda_1 P(w_3) + \lambda_2 P(w_3 \mid w_2) + \lambda_3 P(w_3 \mid w_1, w_2)
$$

## Requirements

- Python 3.10+
- Node.js 20+
- npm

## Quick Start (Local)

### 1) Run Backend

From repository root:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at:
- `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### 2) Run Frontend

In a second terminal, from repository root:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

By default, frontend calls `http://localhost:8000`. To use another backend URL, set:

```bash
NEXT_PUBLIC_API_URL=http://backend-host:8000
```

## API

### `POST /generate`

Request body:

```json
{
	"prompt": "ایک خوبصورت کہانی لکھیں"
}
```

Response:
- `200 OK`: streamed plain text story output.
- `400 Bad Request`: plain text Urdu validation message when input is not primarily Urdu.

Example using `curl`:

```bash
curl -N -X POST "http://localhost:8000/generate" \
	-H "Content-Type: application/json" \
	-d '{"prompt":"ایک دفعہ کا ذکر ہے"}'
```

## Docker (Backend)

From repository root:

```bash
cd backend
docker build -t story-teller-backend .
docker run --rm -p 8000:8000 story-teller-backend
```

## Data & Training Assets

- `scraper/scraping.py`: crawls Urdu stories from UrduPoint pages and saves JSON.
- `tokenizer/`: BPE notebook + artifacts (`vocab.json`, `merges.json`, `id2char.json`).
- `trigram model/`: training notebook + serialized trigram model.
- `backend/`: production copy of tokenizer/model artifacts used at runtime.

## Limitations

- This is an n-gram based generator; coherence can degrade on long generations.
- Sampling is random (`random.choices`), so outputs vary per run.
- Frontend currently displays one active user message and one active assistant response (single-turn style).