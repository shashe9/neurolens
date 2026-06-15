import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Observation
from app.services.ai_service import ai_engine

def get_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def cluster_observations(observations: List[Observation], threshold: float = 0.6) -> List[Dict[str, Any]]:
    """
    Groups observations using single-linkage cosine similarity clustering.
    Returns list of clusters where each cluster contains 3+ observations.
    """
    valid_obs = []
    vectors = []
    
    for obs in observations:
        if obs.deleted_at is not None:
            continue
        vec = obs.embedding_vector
        if not vec:
            try:
                # Compute on the fly if missing
                vec = ai_engine.model.encode(obs.structured_body or obs.body).tolist()
            except Exception:
                continue
        valid_obs.append(obs)
        vectors.append(vec)

    n = len(valid_obs)
    if n < 3:
        return []

    # Build adjacency list of connected components
    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            sim = get_cosine_similarity(vectors[i], vectors[j])
            if sim >= threshold:
                adj[i].append(j)
                adj[j].append(i)

    # Find connected components using Breadth-First Search
    visited = [False] * n
    components = []

    for i in range(n):
        if not visited[i]:
            comp = []
            queue = [i]
            visited[i] = True
            while queue:
                curr = queue.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append(neighbor)
            components.append(comp)

    # Format clusters (only keep components with size >= 3)
    clusters = []
    for comp in components:
        if len(comp) >= 3:
            cluster_obs = [valid_obs[idx] for idx in comp]
            first_obs = cluster_obs[0]
            domain_name = first_obs.domain.name if first_obs.domain else "General"
            
            # Simple label summarizer
            label = f"Pattern: recurring {domain_name.lower()} behaviors"
            
            clusters.append({
                "cluster_id": str(first_obs.id),
                "domain_name": domain_name,
                "label": label,
                "observation_ids": [str(o.id) for o in cluster_obs],
                "observations": [
                    {
                        "id": str(o.id),
                        "body": o.body,
                        "structured_body": o.structured_body,
                        "observed_at": o.observed_at.isoformat()
                    }
                    for o in cluster_obs
                ]
            })

    return clusters
