# Emotion Analysis

Small, simple scripts for:

1. encoding tasks
2. encoding emotion instructions
3. merging them for scoring and visualization
4. running everything in one command
5. choosing the encoder from one central config file

## Files

- `config.json`: central config for paths and encoder settings
- `encode_tasks.py`: turns task text into vectors
- `encode_emotions.py`: turns emotion instruction text into vectors
- `analyze_and_visualize.py`: matches tasks to instructions, computes blend stats, and builds a simple HTML plot
- `run_all.py`: runs the full pipeline in sequence
- `text_encoder.py`: shared text encoding and math helpers

## Config

Edit `emotion_analysis/config.json`.

Simple local baseline:

```json
{
  "encoder": {
    "type": "simple",
    "dim": 512
  }
}
```

LiteLLM with an OpenAI-compatible embedding endpoint:

```json
{
  "encoder": {
    "type": "llm",
    "model": "openai/text-embedding-3-small",
    "api_base": "https://your-endpoint/v1",
    "batch_size": 32
  },
  "reranker": {
    "enabled": false,
    "model": "openai/gpt-4.1-mini",
    "top_k": 5
  }
}
```

Put your key in the repo-level `.env` file:

```bash
OPENAI_API_KEY=your_key_here
```

## Run One Step At A Time

```bash
python3 emotion_analysis/encode_tasks.py --config emotion_analysis/config.json
```

```bash
python3 emotion_analysis/encode_emotions.py --config emotion_analysis/config.json
```

```bash
python3 emotion_analysis/analyze_and_visualize.py --config emotion_analysis/config.json
```

## Run Everything

```bash
python3 emotion_analysis/run_all.py --config emotion_analysis/config.json
```

For A/B comparison:

```bash
python3 emotion_analysis/run_all.py --config emotion_analysis/config_embed.json
python3 emotion_analysis/run_all.py --config emotion_analysis/config_rerank.json
```

Then compare:

- `emotion_analysis/output_embed/analysis/task_to_instruction_rankings.csv`
- `emotion_analysis/output_rerank/analysis/task_to_instruction_rankings.csv`

## Outputs

- `task_embeddings.json`
- `emotion_embeddings.json`
- `analysis/blend_stats.csv`
- `analysis/task_to_instruction_rankings.csv`
- `analysis/plot_points.json`
- `analysis/embedding_plot.html`
- `analysis/summary.json`

## Notes

- The encoder is intentionally simple: hashed bag-of-words with cosine similarity.
- You can switch to a real embedding model by setting `encoder.type` to `llm`.
- For `llm`, put the provider in the `model` string, for example `openai/text-embedding-3-small`.
- For `llm`, the scripts use LiteLLM under the hood and read the API key from `.env` using `load_dotenv()`.
- You can enable the optional reranker with `reranker.enabled=true`.
- The reranker only looks at the top `k` embedding candidates and reorders them with an LLM.
- Tasks are encoded from an emotion-focused summary, not just the raw task blob, so retrieval is more about likely user state than reservation details.
- The rankings CSV now includes the top 3 instruction matches and a confidence margin.
- The plot is a simple PCA projection written as HTML and SVG, so it does not need `matplotlib`.
- This is a good baseline for understanding your emotion space before moving to larger embedding models.
