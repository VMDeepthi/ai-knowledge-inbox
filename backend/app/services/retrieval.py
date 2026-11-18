import math

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)

def retrieve(query_embedding: list[float], chunks, top_k: int):
    scored = [(cosine_similarity(query_embedding, chunk.embedding), chunk) for chunk in chunks]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [(score, chunk) for score, chunk in scored[:top_k] if score > 0]
