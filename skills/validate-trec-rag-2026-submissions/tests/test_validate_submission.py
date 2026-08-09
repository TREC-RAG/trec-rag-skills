from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "validate_submission.py"
)
SPEC = importlib.util.spec_from_file_location("rag26_submission_validator", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load validator script: {SCRIPT_PATH}")
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class RetrievalValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_text(self, name: str, body: str) -> Path:
        path = self.root / name
        path.write_text(body, encoding="utf-8")
        return path

    def write_bytes(self, name: str, body: bytes) -> Path:
        path = self.root / name
        path.write_bytes(body)
        return path

    def write_topics_tsv(self, *rows: tuple[str, str]) -> Path:
        return self.write_text(
            "topics.tsv",
            "".join(f"{topic_id}\t{narrative}\n" for topic_id, narrative in rows),
        )

    def one_topic(self):
        return validator.load_topics(
            self.write_topics_tsv(("rag2026-0", "First narrative"))
        )

    def assert_retrieval_failure(
        self,
        body: str | bytes,
        expected_message: str,
        *,
        topics=None,
    ):
        run = (
            self.write_bytes("run.tsv", body)
            if isinstance(body, bytes)
            else self.write_text("run.tsv", body)
        )
        result = validator.validate_retrieval(run, topics or self.one_topic())
        self.assertEqual("fail", result.status)
        self.assertTrue(
            any(expected_message in finding.message for finding in result.findings),
            tuple(finding.message for finding in result.findings),
        )
        return result

    def test_retrieval_accepts_variable_depth_and_reports_counts(self) -> None:
        topics = self.write_topics_tsv(
            ("rag2026-0", "First narrative"),
            ("rag2026-1", "Second narrative"),
        )
        run = self.write_text(
            "run.tsv",
            "rag2026-0 Q0 shard_00001_1 1 2.0 run-a\n"
            "rag2026-0 Q0 shard_00002_2 2 1.0 run-a\n"
            "rag2026-1 Q0 shard_00003_3 1 9.0 run-a\n",
        )

        result = validator.validate_retrieval(run, validator.load_topics(topics))

        self.assertEqual("pass", result.status)
        self.assertEqual(3, result.row_count)
        self.assertEqual(2, result.topic_count)
        self.assertEqual((1, 2), (result.depth_min, result.depth_max))
        self.assertEqual((), result.findings)

    def test_retrieval_ignores_blank_lines(self) -> None:
        run = self.write_text(
            "run.tsv",
            "\nrag2026-0 Q0 shard_00001_1 1 1.0 run-a\n\n",
        )

        result = validator.validate_retrieval(run, self.one_topic())

        self.assertEqual("pass", result.status)
        self.assertEqual(1, result.row_count)

    def test_topics_request_jsonl_is_accepted(self) -> None:
        topics = self.write_text(
            "topics.jsonl",
            json.dumps({"request_id": "rag2026-0", "title": "First narrative"})
            + "\n",
        )

        loaded = validator.load_topics(topics)

        self.assertEqual(
            (("rag2026-0", "First narrative"),),
            tuple((topic.topic_id, topic.narrative) for topic in loaded),
        )

    def test_topics_reject_duplicate_ids(self) -> None:
        topics = self.write_topics_tsv(
            ("rag2026-0", "First narrative"),
            ("rag2026-0", "Repeated narrative"),
        )

        with self.assertRaisesRegex(ValueError, "duplicate topic ID"):
            validator.load_topics(topics)

    def test_retrieval_rejects_malformed_column_count(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 1 1.0\n",
            "expected six columns",
        )

    def test_retrieval_rejects_wrong_q0(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 XX shard_00001_1 1 1.0 run-a\n",
            "column 2 must be Q0",
        )

    def test_retrieval_rejects_missing_topic(self) -> None:
        topics = validator.load_topics(
            self.write_topics_tsv(
                ("rag2026-0", "First narrative"),
                ("rag2026-1", "Second narrative"),
            )
        )
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 1 1.0 run-a\n",
            "missing expected topics: rag2026-1",
            topics=topics,
        )

    def test_retrieval_rejects_extra_topic(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 1 2.0 run-a\n"
            "rag2026-1 Q0 shard_00002_2 1 1.0 run-a\n",
            "topics outside expected population: rag2026-1",
        )

    def test_retrieval_rejects_rank_not_starting_at_one(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 2 1.0 run-a\n",
            "ranks must start at 1 and be dense",
        )

    def test_retrieval_rejects_rank_gap(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 1 2.0 run-a\n"
            "rag2026-0 Q0 shard_00002_2 3 1.0 run-a\n",
            "ranks must start at 1 and be dense",
        )

    def test_retrieval_rejects_duplicate_topic_document_pair(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 1 2.0 run-a\n"
            "rag2026-0 Q0 shard_00001_1 2 1.0 run-a\n",
            "duplicate document ID",
        )

    def test_retrieval_rejects_increasing_score(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 1 1.0 run-a\n"
            "rag2026-0 Q0 shard_00002_2 2 2.0 run-a\n",
            "scores must be non-increasing",
        )

    def test_retrieval_rejects_nonfinite_scores(self) -> None:
        for score in ("nan", "inf", "-inf"):
            with self.subTest(score=score):
                self.assert_retrieval_failure(
                    f"rag2026-0 Q0 shard_00001_1 1 {score} run-a\n",
                    "score must be finite",
                )

    def test_retrieval_rejects_invalid_climbmix_id(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 doc-a 1 1.0 run-a\n",
            "invalid ClimbMix document ID",
        )

    def test_retrieval_rejects_conflicting_run_ids(self) -> None:
        self.assert_retrieval_failure(
            "rag2026-0 Q0 shard_00001_1 1 2.0 run-a\n"
            "rag2026-0 Q0 shard_00002_2 2 1.0 run-b\n",
            "conflicting run IDs",
        )

    def test_retrieval_rejects_invalid_utf8(self) -> None:
        self.assert_retrieval_failure(
            b"rag2026-0 Q0 shard_00001_1 1 1.0 run-a\xff\n",
            "not valid UTF-8",
        )

    def test_retrieval_rejects_empty_run(self) -> None:
        result = self.assert_retrieval_failure("", "run contains no rows")
        self.assertEqual(0, result.row_count)


if __name__ == "__main__":
    unittest.main()
