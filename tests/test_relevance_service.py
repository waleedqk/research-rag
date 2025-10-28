from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from research_rag.adapters.llm_providers.base import BaseLLMProvider
from research_rag.core.services.relevance import PaperRelevanceService
from research_rag.models import ChatRequest, Message, PaperRelevanceResponse


class StaticLLMProvider(BaseLLMProvider):
    """LLM provider that returns a predetermined JSON payload."""

    def __init__(self, payload: str) -> None:
        self._payload = payload

    def chat(self, request: ChatRequest):  # type: ignore[override]
        assert request.messages, "Expected messages to be passed to the provider"
        return [Message(role="assistant", content=self._payload)]


def _write_sample_csv(tmp_path: Path) -> Path:
    csv_content = """title,year,summary,methods,results,notes
Trust in Autonomous Vehicles: A Survey,2023,This paper surveys trust in autonomous vehicles and human factors,We review studies
on user trust,,
Autonomous Vehicle Safety Evaluation,2024,Evaluates safety and trust frameworks for autonomous driving,Implements evaluation met
rics and experiments,Results highlight trust improvements,
Robotics Path Planning Advances,2019,Focuses on motion planning algorithms for robots,,,
"""
    csv_path = tmp_path / "papers.csv"
    csv_path.write_text(csv_content, encoding="utf-8")
    return csv_path


def test_rank_papers_returns_high_confidence_scores(tmp_path: Path) -> None:
    csv_path = _write_sample_csv(tmp_path)
    provider = StaticLLMProvider(
        """
[
  {"paper_title": "Trust in Autonomous Vehicles: A Survey", "score": 0.92},
  {"paper_title": "Autonomous Vehicle Safety Evaluation", "score": 0.88}
]
""".strip()
    )
    service = PaperRelevanceService(llm_provider=provider)

    response = service.rank_papers(
        "which papers talk about trust in autonomous vehicles",
        csv_path,
        pdf_dir=tmp_path,
    )

    assert isinstance(response, PaperRelevanceResponse)
    ranked = response.as_2d_list()

    assert ranked == [
        ["Trust in Autonomous Vehicles: A Survey", 0.92],
        ["Autonomous Vehicle Safety Evaluation", 0.88],
    ]

    output_file = response.output_path
    assert output_file is not None
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8").strip().startswith("[")
    expected_filename = (
        "which-papers-talk-about-trust-in-autonomous-vehicles.json"
    )
    assert output_file.name == expected_filename


def test_rank_papers_validates_pdf_directory(tmp_path: Path) -> None:
    csv_path = _write_sample_csv(tmp_path)
    provider = StaticLLMProvider("[]")
    service = PaperRelevanceService(llm_provider=provider)

    with pytest.raises(FileNotFoundError):
        service.rank_papers(
            "trust in autonomous vehicles",
            csv_path,
            pdf_dir=tmp_path / "missing",
        )
