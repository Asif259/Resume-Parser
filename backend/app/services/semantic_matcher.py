from typing import Any, Optional
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

from app.services.skill_taxonomy import SKILL_TAXONOMY

_MATCHER_INSTANCE: Optional["SemanticSkillMatcher"] = None

class SemanticSkillMatcher:
    """Matches skill candidates to canonical taxonomy using sentence embeddings."""

    def __init__(
        self,
        taxonomy: Optional[dict[str, dict[str, Any]]] = None,
        model_name: str = "all-MiniLM-L6-v2",
        threshold: float = 0.75,
    ):
        self.taxonomy = taxonomy or SKILL_TAXONOMY
        self.threshold = threshold
        self.model = SentenceTransformer(model_name)

        self.canonical_names: list[str] = list(self.taxonomy.keys())

        # Construct semantic representation texts for each skill
        taxonomy_texts = []
        for name in self.canonical_names:
            info = self.taxonomy[name]
            aliases = ", ".join(info.get("aliases", []))
            desc = info.get("description", "")
            taxonomy_texts.append(f"{name}: {desc} ({aliases})")

        # Precompute and normalize taxonomy embeddings
        with torch.no_grad():
            embeddings = self.model.encode(
                taxonomy_texts,
                convert_to_tensor=True,
                show_progress_bar=False,
            )
            self.taxonomy_embeddings = F.normalize(embeddings, p=2, dim=1)

    def match(self, candidate: str) -> Optional[tuple[str, float]]:
        """Matches a single candidate skill string to the closest canonical skill.

        Returns:
            (canonical_name, similarity_score) if score >= threshold, else None.
        """
        if not candidate or len(candidate.strip()) < 2:
            return None

        results = self.match_batch([candidate])
        if results:
            _, canonical_name, score = results[0]
            return (canonical_name, score)
        return None

    def match_batch(self, candidates: list[str]) -> list[tuple[str, str, float]]:
        """Matches a batch of candidate skill strings.

        Returns:
            List of (candidate, canonical_name, similarity_score) for matches >= threshold.
        """
        valid_candidates = [c.strip() for c in candidates if c and len(c.strip()) >= 2]
        if not valid_candidates:
            return []

        with torch.no_grad():
            cand_embeddings = self.model.encode(
                valid_candidates,
                convert_to_tensor=True,
                show_progress_bar=False,
            )
            cand_norm = F.normalize(cand_embeddings, p=2, dim=1)

            # Cosine similarity matrix: (num_candidates, num_skills)
            sim_matrix = torch.mm(cand_norm, self.taxonomy_embeddings.t())
            max_scores, best_indices = torch.max(sim_matrix, dim=1)

        results: list[tuple[str, str, float]] = []
        for cand, score, idx in zip(valid_candidates, max_scores.tolist(), best_indices.tolist()):
            if score >= self.threshold:
                canonical = self.canonical_names[idx]
                results.append((cand, canonical, round(score, 4)))

        return results

def get_semantic_matcher(threshold: float = 0.75) -> SemanticSkillMatcher:
    """Returns singleton SemanticSkillMatcher instance."""
    global _MATCHER_INSTANCE
    if _MATCHER_INSTANCE is None:
        _MATCHER_INSTANCE = SemanticSkillMatcher(threshold=threshold)
    return _MATCHER_INSTANCE

