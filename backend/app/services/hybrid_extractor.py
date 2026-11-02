from typing import Optional
from app.services.entity_extractor import extract_entities, ExtractedEntities
from app.services.reconciliation import ReconciliationStrategy

class HybridExtractor:
    """Combines rule-based/spaCy extraction with fine-tuned transformer ML predictions."""

    def __init__(self, use_ml: bool = True):
        self.use_ml = use_ml
        self.reconciler = ReconciliationStrategy()

    def extract(self, sections: dict[str, str], raw_text: str = "") -> ExtractedEntities:
        """Extracts entities by running rules and ML pipelines, reconciling their results."""
        rules_entities = extract_entities(sections)

        if not self.use_ml or not raw_text:
            return rules_entities

        try:
            from app.ml.predict import predict_entities
            ml_entities = predict_entities(raw_text)
            if not ml_entities:
                return rules_entities
            return self.reconciler.merge(rules_entities, ml_entities)
        except Exception:
            # Fallback cleanly to rules if ML inference fails
            return rules_entities

