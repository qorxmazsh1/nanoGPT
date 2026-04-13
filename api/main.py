from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import torch.nn as nn
from torch.nn import functional as F
import os

app = FastAPI(title="NanoGPT Azerbaijani API")

class BigramLanguageModel(nn.Module):
    def __init__(self, vocab_size, n_embd, block_size):
        super().__init__()
        self.block_size = block_size
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_emdedding_table = nn.Embedding(block_size, n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding_table(idx)
        pos_emb = self.position_emdedding_table(torch.arange(T, device=idx.device))
        x = tok_emb + pos_emb
        logits = self.lm_head(tok_emb)
        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=-1)
        return idx

model = None
stoi = None
itos = None
block_size = None
device = 'cuda' if torch.cuda.is_available() else 'cpu'

@app.on_event("startup")
async def load_model():
    global model, stoi, itos, block_size
    ckpt_path = 'out/ckpt.pt'
    if not os.path.exists(ckpt_path):
        raise RuntimeError(f"Checkpoint not found: {ckpt_path}")

    ckpt = torch.load(ckpt_path, map_location=device)
    stoi = ckpt['stoi']
    itos = ckpt['itos']
    block_size = ckpt['block_size']

    model = BigramLanguageModel(
        vocab_size=ckpt['vocab_size'],
        n_embd=ckpt['n_embd'],
        block_size=block_size
    )
    model.load_state_dict(ckpt['model'])
    model.eval().to(device)
    print("Model uğurla yükləndi!")

class GenerateRequest(BaseModel):
    prompt: str = ""
    max_new_tokens: int = 200
    temperature: float = 0.8

class GenerateResponse(BaseModel):
    output: str

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model has not been loaded yet")

    encode = lambda s: [stoi[c] for c in s if c in stoi]
    decode = lambda l: ''.join([itos[i] for i in l])

    if req.prompt:
        tokens = encode(req.prompt)
        if not tokens:
            raise HTTPException(status_code=400, detail="Enter a valid prompt with characters in the vocabulary")
        x = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(device)
    else:
        x = torch.zeros((1, 1), dtype=torch.long, device=device)

    with torch.no_grad():
        output = model.generate(x, req.max_new_tokens)

    return {"output": decode(output[0].tolist())}