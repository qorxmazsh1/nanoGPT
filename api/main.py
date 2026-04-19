from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import os
from model import BigramLanguageModel

app = FastAPI(title="NanoGPT Azerbaijani API")
model      = None
stoi       = None
itos       = None
block_size = None
device     = 'cuda' if torch.cuda.is_available() else 'cpu'

@app.on_event("startup")
async def load_model():
    global model, stoi, itos, block_size

    ckpt_path = 'out/ckpt.pt'
    if not os.path.exists(ckpt_path):
        raise RuntimeError(f"Checkpoint is not found: {ckpt_path}")

    ckpt = torch.load(ckpt_path, map_location=device)

    stoi       = ckpt['stoi']
    itos       = ckpt['itos']
    block_size = ckpt['block_size']

    model = BigramLanguageModel(
        vocab_size = ckpt['vocab_size'],
        n_embd     = ckpt['n_embd'],
        block_size = ckpt['block_size'],
        n_heads    = ckpt['n_heads'],
        n_layers   = ckpt['n_layers'],
    )
    model.load_state_dict(ckpt['model'])
    model.eval().to(device)

class GenerateRequest(BaseModel):
    prompt:         str   = ""
    max_new_tokens: int   = 200
    temperature:    float = 0.8

class GenerateResponse(BaseModel):
    output: str

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model does not exist or is not loaded yet")

    encode = lambda s: [stoi[c] for c in s if c in stoi]
    decode = lambda l: ''.join([itos[i] for i in l])

    if req.prompt:
        tokens = encode(req.prompt)
        if not tokens:
            raise HTTPException(status_code=400, detail="Prompt contains no valid characters")
        x = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(device)
    else:
        x = torch.zeros((1, 1), dtype=torch.long, device=device)

    with torch.no_grad():
        output = model.generate(x, req.max_new_tokens, temperature=req.temperature)

    return {"output": decode(output[0].tolist())}