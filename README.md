# NanoGPT — Azerbaijani Language Model

A character-level language model trained on Azerbaijani text, built from scratch following Andrej Karpathy's nanoGPT. Features a full Transformer architecture with multi-head self-attention, trained on 260MB+ of Azerbaijani text data.

## Architecture

- **Model:** Transformer-based character-level language model
- **Layers:** 6 Transformer blocks
- **Attention heads:** 6 multi-head self-attention heads
- **Embedding size:** 384
- **Context length:** 256 characters
- **Parameters:** ~10.93M

## Project Structure

```
NanoGPT/
├── model.py              # Transformer model architecture
├── bigram.py             # Training script
├── az_data_scrapper.py   # Azerbaijani text data scraper
├── api/
│   └── main.py           # FastAPI inference server
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── out/
    └── ckpt.pt           # Model checkpoint (not tracked by git)
```

## Model Architecture Details

The model consists of the following components:

- **Token + Position Embeddings** — character and position representations
- **Head** — single scaled dot-product self-attention head with causal masking
- **MultiHeadAttention** — parallel attention heads with projection
- **FeedForward** — 2-layer MLP with 4x expansion and ReLU activation
- **Block** — Transformer block with residual connections and LayerNorm
- **BigramLanguageModel** — full model stacking N blocks with final LayerNorm

## Data

Trained on 260MB+ of Azerbaijani text collected from:
- Azerbaijani Wikipedia (specific articles + 100 random articles)
- azertag.az news
- report.az news
- oxu.az news
- Additional Azerbaijani text corpora

Text is filtered to retain only Latin-script Azerbaijani content.

## Training

```bash
python bigram.py
```

Training configuration:
- Batch size: 64
- Max iterations: 5000
- Learning rate: 3e-4
- Optimizer: AdamW

Checkpoint is saved to `out/ckpt.pt` after training completes.

## Inference API

Run locally:

```bash
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Generate text via API:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Azərbaycan", "max_new_tokens": 200, "temperature": 0.8}'
```

Check health:

```bash
curl http://localhost:8000/health
```

API documentation available at `http://localhost:8000/docs`

## Docker

```bash
docker build -t nanogpt-az .
docker run -p 8000:8000 -v $(pwd)/out:/app/out nanogpt-az
```

## Deployment

The API is deployed via Railway with GitHub Actions CI/CD. Every push to `main` triggers an automatic redeploy.


## Sample Output

Generated 500 tokens with prompt: 
'''
 Siyadov və Sar Eyni oğlu, Ədalət-qızı,Qərbi Qəbələrimlə xanət zəifləməyəcək. Yox ust edərək, Şəhər xəstənin 202-ci ilin ötən nəqli şəxsi təcrübə olanlar sözləri onları arasında - bu qeyri-ədədinlik Mərkəz bacarıqlı olacaqları adlanan imzalarıq, demək olar ki, Türklenski texnologiyan təbiətçilərimizlə və onların yeganə hesabıdır.
'''