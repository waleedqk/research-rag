"""Service for ranking paper relevance using a single LLM pass over CSV summaries."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    from rapidfuzz import fuzz
except ModuleNotFoundError:  # pragma: no cover - fallback when rapidfuzz is unavailable
    fuzz = None

from research_rag.adapters.csv import CSVLoader
from research_rag.adapters.llm_providers.base import BaseLLMProvider
from research_rag.models import ChatRequest, Message
from research_rag.models.papers import (
    PaperRelevanceResponse,
    PaperRelevanceScore,
    PaperSummary,
)


class PaperRelevanceService:
    """Analyze a CSV of paper summaries and surface high-value matches for a query."""

    def __init__(
        self,
        *,
        llm_provider: BaseLLMProvider | None,
        csv_loader: Optional[CSVLoader] = None,
        output_directory: str | Path | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._csv_loader = csv_loader or CSVLoader()
        self._output_directory = Path(output_directory) if output_directory else None

    def rank_papers(
        self,
        query: str,
        csv_path: str | Path,
        *,
        output_dir: str | Path | None = None,
    ) -> PaperRelevanceResponse:
        """Run a one-shot relevance analysis for ``query`` using ``csv_path``."""

        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Ensure the CSV can be parsed and surfaces titles for the LLM prompt.
        records = self._csv_loader.load(csv_path)
        if not records:
            return PaperRelevanceResponse(query=query, results=[], output_path=None)

        if self._llm_provider is not None:
            scores = self._rank_papers_with_llm(query=query, records=records)
        else:
            scores = self._score_locally(query=query, records=records)

        # Sort by score to make the consumer workflow deterministic.
        scores.sort(key=lambda result: result.score, reverse=True)

        output_path = self._write_output(
            query=query,
            scores=scores,
            base_directory=output_dir or self._output_directory or csv_path.parent,
        )

        return PaperRelevanceResponse(query=query, results=scores, output_path=output_path)

    def _rank_papers_with_llm(
        self, *, query: str, records: list[PaperSummary]
    ) -> list[PaperRelevanceScore]:
        """Process each paper summary with an LLM call to determine relevance."""
        all_scores: list[PaperRelevanceScore] = []
        for record in records:
            prompt = self._build_prompt(query=query, record=record)
            response_text = self._invoke_llm(prompt)
            scores = self._parse_scores(response_text)
            all_scores.extend(scores)
        return all_scores

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_prompt(self, *, query: str, record: PaperSummary) -> ChatRequest:
        system_prompt = (
            "You are a meticulous research assistant. Evaluate SEMANTIC relevance to the query "
            "based on meaning (problem/task alignment, methods/approach, domain/data, evidence/results, recency). "
            "Do NOT rely on keyword overlap. Return STRICT JSON: a list with exactly one item having "
            "'paper_title' and 'score' (0..1). No explanations."
        )
        user_prompt = (
            f"Query:\n{query}\n\n"
            "Paper text:\n"
            f"{record.to_text()}\n\n"
            'Return JSON ONLY, e.g.:\n[{"paper_title":"Exact Title","score":0.82}]'
        )
        return ChatRequest(
            messages=[
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt),
            ]
        )

    def _invoke_llm(self, request: ChatRequest) -> str:
        if self._llm_provider is None:
            raise RuntimeError("LLM provider is not configured for this service instance")
        responses = self._llm_provider.chat(request)
        if not isinstance(responses, Iterable):
            raise TypeError("LLM provider must return an iterable of Message instances")

        contents: List[str] = []
        for message in responses:
            if not isinstance(message, Message):
                raise TypeError("LLM provider yielded an unexpected payload")
            contents.append(message.content)
        return "".join(contents)

    def _parse_scores(self, response_text: str) -> List[PaperRelevanceScore]:
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            return []

        results: List[PaperRelevanceScore] = []
        if isinstance(parsed, list):
            for entry in parsed:
                if not isinstance(entry, dict):
                    continue
                title = entry.get("paper_title") or entry.get("title")
                score = entry.get("score")
                if title is None or score is None:
                    continue
                try:
                    results.append(
                        PaperRelevanceScore(paper_title=str(title), score=float(score))
                    )
                except (ValueError, TypeError):
                    continue
        return results

    def _write_output(
        self,
        *,
        query: str,
        scores: List[PaperRelevanceScore],
        base_directory: str | Path,
    ) -> Path:
        directory = Path(base_directory)
        directory.mkdir(parents=True, exist_ok=True)

        filename = f"{self._slugify(query)}.json"
        output_path = directory / filename

        data = [[score.paper_title, score.score] for score in scores]
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return output_path

    @staticmethod
    def _slugify(text: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
        return slug or "query"

    def _score_locally(self, *, query: str, records: List[PaperSummary]) -> List[PaperRelevanceScore]:
        """Fallback scoring using fuzzy matching for environments without an LLM."""

        normalized_query = query.strip()
        if not normalized_query:
            return []

        results: List[PaperRelevanceScore] = []
        query_lower = normalized_query.lower()
        for record in records:
            searchable_fragments = [record.title]
            searchable_fragments.extend(
                value for value in record.columns.values() if value is not None
            )
            combined = " ".join(fragment for fragment in searchable_fragments if fragment).strip()
            if not combined:
                continue

            ratio: float
            if fuzz is not None:
                ratio = float(fuzz.token_set_ratio(normalized_query, combined))
            else:  # pragma: no cover - exercised when rapidfuzz is absent
                ratio = SequenceMatcher(None, query_lower, combined.lower()).ratio() * 100.0
            if ratio <= 0:
                continue

            score = min(max(ratio / 100.0, 0.0), 1.0)
            try:
                results.append(
                    PaperRelevanceScore(
                        paper_title=record.title,
                        score=round(score, 4),
                    )
                )
            except ValueError:
                continue

        return results
