"""Service for ranking paper relevance using a single LLM pass over CSV summaries."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, List, Optional

from research_rag.adapters.csv import CSVLoader
from research_rag.adapters.llm_providers.base import BaseLLMProvider
from research_rag.models import ChatRequest, Message
from research_rag.models.papers import PaperRelevanceResponse, PaperRelevanceScore


class PaperRelevanceService:
    """Analyze a CSV of paper summaries and surface high-value matches for a query."""

    def __init__(
        self,
        *,
        llm_provider: BaseLLMProvider,
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
        pdf_dir: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> PaperRelevanceResponse:
        """Run a one-shot relevance analysis for ``query`` using ``csv_path``."""

        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        if pdf_dir is not None:
            pdf_directory = Path(pdf_dir)
            if not pdf_directory.exists():
                raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")

        # Ensure the CSV can be parsed and surfaces titles for the LLM prompt.
        records = self._csv_loader.load(csv_path)
        if not records:
            return PaperRelevanceResponse(query=query, results=[], output_path=None)

        csv_text = csv_path.read_text(encoding="utf-8")

        prompt = self._build_prompt(query=query, csv_text=csv_text)
        response_text = self._invoke_llm(prompt)
        scores = self._parse_scores(response_text)

        # Sort by score to make the consumer workflow deterministic.
        scores.sort(key=lambda result: result.score, reverse=True)

        output_path = self._write_output(
            query=query,
            scores=scores,
            base_directory=output_dir or self._output_directory or csv_path.parent,
        )

        return PaperRelevanceResponse(query=query, results=scores, output_path=output_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_prompt(self, *, query: str, csv_text: str) -> ChatRequest:
        system_prompt = (
            "You are a meticulous research assistant. Review the provided CSV rows for research "
            "papers and determine which entries deserve focused attention for the query. "
            "Evaluate each row once using the available column headings. Consider how closely the "
            "paper matches the query, how recent it is, and whether the description references "
            "implementations, methods, evaluations, or results. Only keep papers that clearly "
            "address the query. Respond strictly with JSON: a list where each item has "
            "'paper_title' and 'score' (0 to 1). Do not include explanations or low scoring papers."
        )
        user_prompt = (
            f"Query:\n{query}\n\n"
            "CSV Content:\n"
            f"{csv_text}\n\n"
            "Return JSON only, containing the high-priority papers and their single relevance score."
        )
        return ChatRequest(
            messages=[
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt),
            ]
        )

    def _invoke_llm(self, request: ChatRequest) -> str:
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
