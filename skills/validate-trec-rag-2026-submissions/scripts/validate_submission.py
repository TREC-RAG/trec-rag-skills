#!/usr/bin/env python3
"""Validate TREC RAG 2026 submission artifacts."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


CLIMBMIX_DOCUMENT_ID = re.compile(r"shard_\d+_\d+\Z")


@dataclass(frozen=True)
class Topic:
    topic_id: str
    narrative: str


@dataclass(frozen=True)
class Finding:
    message: str
    line_number: int | None = None
    topic_id: str | None = None


@dataclass(frozen=True)
class ArtifactResult:
    task: Literal["retrieval", "rag"]
    path: Path
    status: Literal["pass", "pass-with-warnings", "fail"]
    row_count: int | None
    topic_count: int | None
    depth_min: int | None
    depth_max: int | None
    findings: tuple[Finding, ...]
    detail: str = ""


def load_topics(path: Path) -> tuple[Topic, ...]:
    """Load organizer topics from TSV or AutoJudge Request JSONL."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ValueError(f"topics file is not valid UTF-8: {path}") from error

    topics: list[Topic] = []
    seen: set[str] = set()
    is_jsonl = path.suffix.lower() == ".jsonl"

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        if is_jsonl:
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"invalid topics JSON on line {line_number}: {error.msg}"
                ) from error
            if not isinstance(record, dict):
                raise ValueError(
                    f"topics JSON line {line_number} must be an object"
                )
            topic_id = record.get("request_id")
            narrative = record.get("title")
            if not isinstance(topic_id, str) or not isinstance(narrative, str):
                raise ValueError(
                    f"topics JSON line {line_number} requires string request_id and title"
                )
        else:
            fields = line.split("\t")
            if len(fields) != 2:
                raise ValueError(
                    f"topics TSV line {line_number} must contain exactly two columns"
                )
            topic_id, narrative = fields

        topic_id = topic_id.strip()
        narrative = narrative.strip()
        if not topic_id or not narrative:
            raise ValueError(
                f"topics line {line_number} has an empty topic ID or narrative"
            )
        if topic_id in seen:
            raise ValueError(f"duplicate topic ID: {topic_id}")
        seen.add(topic_id)
        topics.append(Topic(topic_id, narrative))

    if not topics:
        raise ValueError(f"topics file contains no topics: {path}")
    return tuple(topics)


def validate_retrieval(path: Path, topics: tuple[Topic, ...]) -> ArtifactResult:
    """Validate one organizer-facing TREC Retrieval run."""
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        finding = Finding("retrieval run is not valid UTF-8")
        return ArtifactResult(
            "retrieval", path, "fail", None, None, None, None, (finding,)
        )

    expected_topics = {topic.topic_id for topic in topics}
    actual_topics: set[str] = set()
    row_count = 0
    depths: dict[str, int] = {}
    documents: dict[str, set[str]] = {}
    previous_scores: dict[str, float] = {}
    run_id: str | None = None
    findings: list[Finding] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        row_count += 1
        fields = line.split()
        if len(fields) != 6:
            findings.append(
                Finding("expected six columns", line_number=line_number)
            )
            continue

        topic_id, q0, document_id, rank_text, score_text, current_run_id = fields
        actual_topics.add(topic_id)
        depth = depths.get(topic_id, 0) + 1
        depths[topic_id] = depth

        if q0 != "Q0":
            findings.append(
                Finding(
                    "column 2 must be Q0",
                    line_number=line_number,
                    topic_id=topic_id,
                )
            )

        try:
            rank = int(rank_text)
        except ValueError:
            rank = None
        if rank is None or rank <= 0 or rank != depth:
            findings.append(
                Finding(
                    "ranks must start at 1 and be dense in file order",
                    line_number=line_number,
                    topic_id=topic_id,
                )
            )

        try:
            score = float(score_text)
        except ValueError:
            score = None
            findings.append(
                Finding(
                    "score must be numeric",
                    line_number=line_number,
                    topic_id=topic_id,
                )
            )
        if score is not None:
            if not math.isfinite(score):
                findings.append(
                    Finding(
                        "score must be finite",
                        line_number=line_number,
                        topic_id=topic_id,
                    )
                )
            else:
                previous_score = previous_scores.get(topic_id)
                if previous_score is not None and score > previous_score:
                    findings.append(
                        Finding(
                            "scores must be non-increasing in file order",
                            line_number=line_number,
                            topic_id=topic_id,
                        )
                    )
                previous_scores[topic_id] = score

        if CLIMBMIX_DOCUMENT_ID.fullmatch(document_id) is None:
            findings.append(
                Finding(
                    "invalid ClimbMix document ID",
                    line_number=line_number,
                    topic_id=topic_id,
                )
            )

        topic_documents = documents.setdefault(topic_id, set())
        if document_id in topic_documents:
            findings.append(
                Finding(
                    "duplicate document ID within topic",
                    line_number=line_number,
                    topic_id=topic_id,
                )
            )
        topic_documents.add(document_id)

        if run_id is None:
            run_id = current_run_id
        elif current_run_id != run_id:
            findings.append(
                Finding(
                    f"conflicting run IDs: {run_id!r} and {current_run_id!r}",
                    line_number=line_number,
                    topic_id=topic_id,
                )
            )

    if row_count == 0:
        findings.append(Finding("run contains no rows"))

    missing_topics = sorted(expected_topics - actual_topics)
    if missing_topics:
        findings.append(
            Finding("missing expected topics: " + ", ".join(missing_topics))
        )
    extra_topics = sorted(actual_topics - expected_topics)
    if extra_topics:
        findings.append(
            Finding(
                "topics outside expected population: " + ", ".join(extra_topics)
            )
        )

    topic_depths = tuple(depths.values())
    return ArtifactResult(
        task="retrieval",
        path=path,
        status="fail" if findings else "pass",
        row_count=row_count,
        topic_count=len(actual_topics),
        depth_min=min(topic_depths) if topic_depths else None,
        depth_max=max(topic_depths) if topic_depths else None,
        findings=tuple(findings),
    )
