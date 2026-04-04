import hashlib
import re
from typing import Iterable, List

import numpy as np
from tqdm import tqdm


TOKEN_RE = re.compile(r"[a-z0-9']+")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "if", "in", "is", "it", "of", "on", "or", "that", "the", "this",
    "to", "was", "we", "with", "you", "your",
}


def normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def tokenize(text: str) -> List[str]:
    tokens = TOKEN_RE.findall(normalize_text(text))
    return [token for token in tokens if token not in STOPWORDS]


def _hash_token(token: str, dim: int) -> int:
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest, 16) % dim


def encode_text(text: str, dim: int = 512) -> np.ndarray:
    vector = np.zeros(dim, dtype=float)
    tokens = tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        vector[_hash_token(token, dim)] += 1.0

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector


def encode_texts(texts: Iterable[str], dim: int = 512) -> np.ndarray:
    vectors = [encode_text(text, dim=dim) for text in texts]
    if not vectors:
        return np.zeros((0, dim), dtype=float)
    return np.vstack(vectors)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return float(np.dot(a, b) / (a_norm * b_norm))


def pairwise_mean_cosine_distance(vectors: List[np.ndarray]) -> float:
    if len(vectors) < 2:
        return 0.0

    distances = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            distances.append(1.0 - cosine_similarity(vectors[i], vectors[j]))

    return float(sum(distances) / len(distances))


def pca_2d(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros((0, 2), dtype=float)

    centered = matrix - matrix.mean(axis=0, keepdims=True)
    if centered.shape[0] == 1:
        return np.array([[0.0, 0.0]])

    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:2].T
    projected = centered @ components

    if projected.shape[1] == 1:
        projected = np.hstack([projected, np.zeros((projected.shape[0], 1))])

    return projected[:, :2]


def safe_mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def round_float(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


class SimpleEncoder:
    def __init__(self, dim: int = 512):
        self.dim = dim
        self.name = "simple"

    def encode(self, texts: List[str]) -> np.ndarray:
        return encode_texts(texts, dim=self.dim)

    def metadata(self) -> dict:
        return {
            "type": "simple",
            "dim": self.dim,
        }


class LiteLLMEncoder:
    def __init__(self, model: str, api_base: str = "", batch_size: int = 32):
        self.model = model
        self.api_base = api_base
        self.batch_size = batch_size
        self.name = "llm"

    def encode(self, texts: List[str]) -> np.ndarray:
        try:
            from litellm import embedding
        except ImportError as exc:
            raise ImportError("litellm is required for encoder.type='llm'.") from exc

        all_vectors = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size if texts else 0
        batch_starts = range(0, len(texts), self.batch_size)

        for start in tqdm(batch_starts, total=total_batches, desc=f"Encoding with {self.model}", unit="batch"):
            batch = texts[start:start + self.batch_size]
            kwargs = {"model": self.model, "input": batch}
            if self.api_base:
                kwargs["api_base"] = self.api_base

            try:
                response = embedding(**kwargs)
            except Exception as exc:
                message = str(exc)
                short_message = message.split("Traceback", 1)[0].strip()
                if len(short_message) > 500:
                    short_message = short_message[:500].rstrip() + "..."
                raise RuntimeError(
                    f"Embedding request failed for model '{self.model}' at batch starting index {start}. "
                    f"Check model, api_base, and environment API keys. Original error: {short_message}"
                ) from exc

            batch_vectors = [item["embedding"] for item in response["data"]]
            all_vectors.extend(batch_vectors)

        return np.array(all_vectors, dtype=float)

    def metadata(self) -> dict:
        return {
            "type": "llm",
            "model": self.model,
            "api_base": self.api_base,
            "batch_size": self.batch_size,
        }
