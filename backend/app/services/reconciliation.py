from typing import Any, Optional
from app.schemas.evidence import FieldEvidence
from app.services.entity_extractor import ExtractedEntities

class ReconciliationStrategy:
    """Reconciles entity extractions from rule-based/spaCy and ML/DistilBERT models."""

    def merge(
        self,
        rules: ExtractedEntities,
        ml_entities: list[dict[str, Any]],
    ) -> ExtractedEntities:
        """Merges rules and ML predictions with confidence-weighted decision rules."""
        evidence = dict(rules.evidence)

        # Tag existing rules evidence with method
        for k, ev in evidence.items():
            if not ev.extraction_method:
                ev.extraction_method = "rules"

        # Separate ML entities by label
        ml_by_label: dict[str, list[dict[str, Any]]] = {}
        for ent in ml_entities:
            label = ent.get("label", "")
            ml_by_label.setdefault(label, []).append(ent)

        # 1. Deterministic fields: email, phone, linkedin, github stay rules-only
        final_email = rules.email
        final_phone = rules.phone
        final_linkedin = rules.linkedin
        final_github = rules.github

        # 2. Name reconciliation
        final_name = rules.name
        ml_names = ml_by_label.get("PERSON_NAME", [])
        if ml_names:
            best_ml_name = max(ml_names, key=lambda x: x["confidence"])
            ml_val = best_ml_name["entity"].strip()
            ml_conf = best_ml_name["confidence"]

            if not final_name and ml_conf >= 0.70 and len(ml_val) >= 3:
                final_name = ml_val
                evidence["personal_info.name"] = FieldEvidence(
                    value=ml_val,
                    normalized_value=ml_val,
                    source_section="header",
                    source_text=ml_val,
                    confidence=ml_conf,
                    extraction_method="ml",
                )
            elif final_name:
                rules_ev = evidence.get("personal_info.name")
                rules_conf = rules_ev.confidence if rules_ev else 0.8
                if final_name.lower() == ml_val.lower():
                    # Both agree
                    agreed_conf = min(1.0, max(rules_conf, ml_conf) + 0.05)
                    evidence["personal_info.name"] = FieldEvidence(
                        value=final_name,
                        normalized_value=final_name,
                        source_section=rules_ev.source_section if rules_ev else "header",
                        source_text=rules_ev.source_text if rules_ev else final_name,
                        confidence=agreed_conf,
                        extraction_method="hybrid",
                    )
                elif ml_conf >= 0.88 and rules_conf < 0.80:
                    final_name = ml_val
                    evidence["personal_info.name"] = FieldEvidence(
                        value=ml_val,
                        normalized_value=ml_val,
                        source_section="header",
                        source_text=ml_val,
                        confidence=ml_conf,
                        extraction_method="ml",
                    )

        # 3. Location reconciliation
        final_location = rules.location
        ml_locs = ml_by_label.get("LOCATION", [])
        if ml_locs:
            best_ml_loc = max(ml_locs, key=lambda x: x["confidence"])
            ml_loc_val = best_ml_loc["entity"].strip()
            ml_loc_conf = best_ml_loc["confidence"]

            if not final_location and ml_loc_conf >= 0.70 and len(ml_loc_val) >= 3:
                final_location = ml_loc_val
                evidence["personal_info.location"] = FieldEvidence(
                    value=ml_loc_val,
                    normalized_value=ml_loc_val,
                    source_section="header",
                    source_text=ml_loc_val,
                    confidence=ml_loc_conf,
                    extraction_method="ml",
                )
            elif final_location:
                rules_ev = evidence.get("personal_info.location")
                rules_conf = rules_ev.confidence if rules_ev else 0.8
                if final_location.lower() == ml_loc_val.lower():
                    agreed_conf = min(1.0, max(rules_conf, ml_loc_conf) + 0.05)
                    evidence["personal_info.location"] = FieldEvidence(
                        value=final_location,
                        normalized_value=final_location,
                        source_section=rules_ev.source_section if rules_ev else "header",
                        source_text=rules_ev.source_text if rules_ev else final_location,
                        confidence=agreed_conf,
                        extraction_method="hybrid",
                    )

        # 4. Collection entities: Job titles, Companies, Degrees, Institutions
        def merge_list(rules_items: list[str], ml_items: list[dict[str, Any]], min_conf: float = 0.6) -> list[str]:
            seen: set[str] = set()
            merged: list[str] = []
            for item in rules_items:
                norm = item.strip().lower()
                if norm and norm not in seen:
                    seen.add(norm)
                    merged.append(item.strip())
            for ent in ml_items:
                if ent["confidence"] >= min_conf:
                    val = ent["entity"].strip()
                    norm = val.lower()
                    if norm and norm not in seen and len(val) >= 2:
                        seen.add(norm)
                        merged.append(val)
            return merged

        final_job_titles = merge_list(rules.job_titles, ml_by_label.get("JOB_TITLE", []), min_conf=0.65)
        final_companies = merge_list(rules.companies, ml_by_label.get("COMPANY", []), min_conf=0.65)
        final_degrees = merge_list(rules.degrees, ml_by_label.get("DEGREE", []), min_conf=0.65)
        final_institutions = merge_list(rules.institutions, ml_by_label.get("INSTITUTION", []), min_conf=0.65)
        final_dates = merge_list(rules.dates, ml_by_label.get("DATE", []), min_conf=0.65)

        return ExtractedEntities(
            name=final_name,
            email=final_email,
            phone=final_phone,
            location=final_location,
            linkedin=final_linkedin,
            github=final_github,
            job_titles=final_job_titles,
            companies=final_companies,
            dates=final_dates,
            degrees=final_degrees,
            institutions=final_institutions,
            evidence=evidence,
        )

