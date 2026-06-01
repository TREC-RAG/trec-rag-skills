# Pyserini ClimbMix Baseline

Use this reference when building the default TREC RAG 2026 baseline retrieval system or when no custom retriever is provided. This file defines the track-specific baseline contract only. For Pyserini REST API access, authentication, service location, endpoint discovery, request examples, response parsing, health checks, query behavior, or error handling, use the `pyserini-rest-api` skill.

## Baseline Defaults

- Corpus/index: ClimbMix / `climbmix-400b`.
- Retrieval method: Pyserini BM25 through the Pyserini REST API.
- Default retrieval depth: top 100 ClimbMix documents per topic.
- Custom systems may choose a different retrieval depth.
- For `R`, write `r_output_trec_rag_2026.tsv` from returned document IDs, ranks, and scores.
- For default baseline `RAG`, Pyserini/ClimbMix BM25 provides the candidate evidence pool; it is not the final answer generator.
- Unless a custom non-agent generator is specified, the agent using this skill is the default `RAG` answer generator.

## API Routing

Use `pyserini-rest-api` when the request needs any API-specific implementation detail, including:

- Token setup or safe local authentication workflow.
- Current service location, OpenAPI docs, health checks, or endpoint discovery.
- Search or document-fetch command examples.
- Response parsing, `parse` behavior, query semantics, or error handling.

This guidelines skill should not duplicate Pyserini REST command examples, response schemas, token handling, or endpoint behavior. Load this baseline reference for the TREC RAG 2026 baseline policy, then load `pyserini-rest-api` only if implementation details are needed.

## Baseline RAG Generator

For the default `RAG` baseline, the top 100 Pyserini/ClimbMix BM25 results are candidate evidence. The agent acts as an evidence-grounded research reporter: it reads the retrieved source packet, identifies the documents that support an answer, and writes concise cited answer sentences from that evidence.

- Review the retrieved candidate documents.
- Reason over the evidence as a source packet, looking for corroboration, disagreement, missing context, and limits in coverage.
- Select only the ClimbMix documents that directly support final answer sentences.
- Put only cited document IDs in `references`.
- Manually write sentence-level answers grounded only in the selected documents.
- Use zero-indexed citation positions into `references`.

Default baseline answer-writing rules:

- Use only retrieved ClimbMix documents as evidence.
- Do not use intrinsic, parametric, or memory-based knowledge to add facts.
- Keep every substantive claim tightly supported by cited documents.
- Prefer careful synthesis over extractive copying, but do not introduce facts that are not supported by the retrieved evidence.
- If support is partial, write only the supported claim rather than filling the gap.
- If the retrieved evidence is insufficient, say so in the answer rather than guessing.
- Do not include diagnostic fields, search traces, rewritten queries, or raw snippets in the submitted `RAG` object unless official instructions require them.
- Write the answer as sentence-level JSON objects; do not embed bracketed citations inside `answer[].text`.

Use `metadata.type: "manual"` when an agent interactively reads evidence and composes the answer. This remains true even if a script later packages the agent-written answer into JSONL, validates citations, or copies fields into the output schema.

Use `metadata.type: "automatic"` only when a specified generator produces the answer text without manual per-topic composition by the agent. A deterministic template, heuristic extractor, or script-authored answer should not be treated as the default baseline RAG generator unless the run explicitly declares that generator as a custom system.

## Baseline Steps

1. Load `trec_rag_2026_queries.jsonl`.
2. For each topic, use `title` as the default initial ClimbMix query, and use `narrative` as the full information need for query rewriting, decomposition, evidence selection, and answer generation.
3. For the default baseline, retrieve `hits=100` from `climbmix-400b`; custom systems may use a different depth.
4. For `R`, write `r_output_trec_rag_2026.tsv` directly from returned `docid`, `rank`, and `score`.
5. For default baseline `RAG`, have the agent review the retrieved documents, select the cited evidence subset, manually compose cited sentence-level answers, and write or package `rag_output_trec_rag_2026.jsonl` with `metadata.type: "manual"`.
6. If a custom non-agent generator is used instead, document it in the run configuration or prompt, have it generate the cited sentence-level answers, and use `metadata.type: "automatic"`.
7. Validate all outputs before returning or submitting them.
