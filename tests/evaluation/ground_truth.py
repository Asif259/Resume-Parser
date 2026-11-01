import json
from pathlib import Path
from typing import List, Union
from pydantic import BaseModel
from app.schemas.resume import ParsedResume

class GroundTruth(BaseModel):
    resume_id: str
    source_file: str
    expected: ParsedResume

def load_ground_truth(path: Union[str, Path]) -> GroundTruth:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return GroundTruth.model_validate(data)

def load_ground_truth_dir(dir_path: Union[str, Path]) -> List[GroundTruth]:
    dir_path = Path(dir_path)
    results: List[GroundTruth] = []
    for file_path in sorted(dir_path.glob("*.json")):
        results.append(load_ground_truth(file_path))
    return results

