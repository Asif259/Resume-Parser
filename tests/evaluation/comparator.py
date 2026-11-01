from dataclasses import dataclass
from typing import Any, List, Optional
from app.schemas.resume import ParsedResume

@dataclass
class FieldComparison:
    field: str
    expected: Any
    actual: Any
    match: bool
    similarity: float

def _compare_str(val1: Optional[str], val2: Optional[str]) -> tuple[bool, float]:
    if val1 is None and val2 is None:
        return True, 1.0
    if val1 is None or val2 is None:
        return False, 0.0
    s1 = str(val1).strip().lower()
    s2 = str(val2).strip().lower()
    if s1 == s2:
        return True, 1.0
    if s1 in s2 or s2 in s1:
        return False, 0.5
    return False, 0.0

def _compare_set(expected_list: list[str], actual_list: list[str]) -> tuple[bool, float]:
    if not expected_list and not actual_list:
        return True, 1.0
    if not expected_list:
        return True, 1.0
    s_exp = {str(x).strip().lower() for x in expected_list if x}
    s_act = {str(x).strip().lower() for x in actual_list if x}
    if not s_exp:
        return True, 1.0
    intersection = s_exp.intersection(s_act)
    recall = len(intersection) / len(s_exp)
    return (recall == 1.0), recall

def compare_resumes(expected: ParsedResume, actual: ParsedResume) -> List[FieldComparison]:
    comparisons: List[FieldComparison] = []

    # 1. Personal Info
    for field_name in ["name", "email", "phone", "location", "linkedin", "github"]:
        exp_val = getattr(expected.personal_info, field_name, None)
        act_val = getattr(actual.personal_info, field_name, None)
        if exp_val is not None:
            match, sim = _compare_str(exp_val, act_val)
            comparisons.append(
                FieldComparison(
                    field=f"personal_info.{field_name}",
                    expected=exp_val,
                    actual=act_val,
                    match=match,
                    similarity=sim,
                )
            )

    # 2. Professional Summary
    if expected.professional_summary is not None:
        match, sim = _compare_str(expected.professional_summary, actual.professional_summary)
        comparisons.append(
            FieldComparison(
                field="professional_summary",
                expected=expected.professional_summary,
                actual=actual.professional_summary,
                match=match,
                similarity=sim,
            )
        )

    # 3. Skills
    if expected.skills:
        match, sim = _compare_set(expected.skills, actual.skills)
        comparisons.append(
            FieldComparison(
                field="skills",
                expected=expected.skills,
                actual=actual.skills,
                match=match,
                similarity=sim,
            )
        )

    # 4. Languages
    if expected.languages:
        match, sim = _compare_set(expected.languages, actual.languages)
        comparisons.append(
            FieldComparison(
                field="languages",
                expected=expected.languages,
                actual=actual.languages,
                match=match,
                similarity=sim,
            )
        )

    # 5. Experience
    for idx, exp_item in enumerate(expected.experience):
        act_item = actual.experience[idx] if idx < len(actual.experience) else None
        for prop in ["job_title", "company", "start_date", "end_date", "is_current"]:
            exp_val = getattr(exp_item, prop, None)
            act_val = getattr(act_item, prop, None) if act_item else None
            if exp_val is not None:
                if prop == "is_current":
                    match = (exp_val == act_val)
                    sim = 1.0 if match else 0.0
                else:
                    match, sim = _compare_str(exp_val, act_val)
                comparisons.append(
                    FieldComparison(
                        field=f"experience.{idx}.{prop}",
                        expected=exp_val,
                        actual=act_val,
                        match=match,
                        similarity=sim,
                    )
                )

    # 6. Education
    for idx, edu_item in enumerate(expected.education):
        act_item = actual.education[idx] if idx < len(actual.education) else None
        for prop in ["degree", "institution", "graduation_year", "field_of_study"]:
            exp_val = getattr(edu_item, prop, None)
            act_val = getattr(act_item, prop, None) if act_item else None
            if exp_val is not None:
                if prop == "graduation_year":
                    match = (exp_val == act_val)
                    sim = 1.0 if match else 0.0
                else:
                    match, sim = _compare_str(exp_val, act_val)
                comparisons.append(
                    FieldComparison(
                        field=f"education.{idx}.{prop}",
                        expected=exp_val,
                        actual=act_val,
                        match=match,
                        similarity=sim,
                    )
                )

    return comparisons

