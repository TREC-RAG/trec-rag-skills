# Retrieval Task (`R`)

Use this reference when building, explaining, or validating the TREC RAG 2026 Retrieval task.

## Task Summary

- **Given**: a list of narratives and access to the ClimbMix collection through the Pyserini REST API or a custom retrieval system.
- **Task**: return a ranked list of ClimbMix documents for each narrative, and declare how many of the top-ranked documents the system predicts are relevant to the narrative and useful as evidence for answer generation.
- **Depth**: choose that number, `k`, separately for each narrative and report it in a companion file. There is no organizer-supplied fixed cutoff to fill.

## Input Format: Narratives

Use the official shared test-narrative file described in [test-data.md](test-data.md). Narratives are provided as TSV in `trec_rag_2026_queries.tsv`. Each line contains the narrative ID and narrative, separated by a tab.

```tsv
rag2026-37	I work for a New York City council member whose district has a lot of transit riders but also some small businesses worried about delivery costs. Can you help me understand whether congestion pricing is a credible and fair way to fund the MTA? What should we weigh about the revenue promise, who pays, who benefits, environmental tradeoffs in places like the Bronx and New Jersey, and whether the MTA and Albany can be held accountable for actually spending the money on reliable service instead of repeating past mistakes?
```

Required fields:

- First column: narrative identifier. Preserve this exactly in all outputs.
- Second column: narrative, usually a two- to three-sentence description of the information need. Use it as the default initial retrieval query unless the system intentionally performs query rewriting or decomposition internally. For `RAG` output, copy this value exactly into `metadata.narrative`.

## Input Format: Documents

For baseline systems, retrieve ClimbMix documents from the Pyserini REST API. The configured index name is:

```text
climbmix-400b
```

Search returns a response with a `candidates` array. Each candidate represents one retrieved ClimbMix document:

```json
{
  "api": "v1",
  "index": "climbmix-400b",
  "query": { "text": "congestion pricing MTA funding accountability" },
  "candidates": [
    {
      "docid": "shard_00459_61697",
      "rank": 1,
      "score": 12.483799934387207,
      "doc": "..."
    }
  ]
}
```

Document fetch by ClimbMix document ID returns one document wrapper:

```json
{
  "api": "v1",
  "index": "climbmix-400b",
  "docid": "shard_00459_61697",
  "doc": "..."
}
```

Document field rules:

- `docid`: ClimbMix document ID to use in submissions.
- `rank`: returned rank for a search candidate.
- `score`: retrieval score for a search candidate.
- `doc`: ClimbMix document contents. The Pyserini REST API schema allows this payload to be a string, object, array, number, boolean, or null depending on index contents and `parse` behavior. Current ClimbMix search responses commonly return `doc` as a string containing the document text.

Use `docid` as the external identifier in Retrieval run files and RAG `references`. Use the document text from `doc` as evidence content. Do not put full `doc` payloads, raw snippets, `rank`, or `score` in official Retrieval or RAG outputs unless official instructions explicitly require them.

When a system needs full document contents for generation, fetch by `docid` through the document endpoint. If `doc` is an object, extract its text-bearing field such as `text` or `contents`; if it is a string, use the string directly as the document text. If the API returns raw stored JSON instead of parsed content, parse it according to the `pyserini-rest-api` skill before extracting the document text.

## Variable-Depth Retrieval Rule

For each narrative, participants must predict how many of their ranked documents are actually useful. Call that narrative-specific number `k`.

The intended target for `k` is **all and only** documents that the system predicts satisfy both of these conditions:

1. The document is relevant to the narrative.
2. The document is useful evidence for producing a high-quality answer to the narrative.

Rank documents in predicted usefulness order, with the most useful document at rank 1, so that **the claimed useful set is exactly ranks 1 through `k`**. Declare `k` per narrative in the companion file described under [Output Format: Declared `k`](#output-format-declared-k). The value of `k` may differ across narratives because some information needs require more supporting evidence than others.

Submit the ranked list itself to a depth of **up to 1000 documents per narrative**. Documents ranked below `k` are submitted for pooling and depth-based measurement; they are **not** part of the system's usefulness claim and are not penalized as if they were.

There is no fixed depth that participants should pad `k` to. In particular:

- Do not inflate `k` merely to reach a conventional cutoff such as 10, 100, or 1000.
- Do not treat a larger claimed set as inherently better.

This rule applies to the submitted claim, not to internal candidate generation. A system may retrieve a large fixed-depth candidate pool, perform query decomposition, fuse multiple searches, or rerank many candidates internally, and may submit up to 1000 of those candidates in ranked order.

For example, if a system predicts that 7 documents are useful for one narrative and 23 are useful for another, it should declare `k = 7` and `k = 23` respectively. It may still submit its full ranked list for both narratives; the declared `k`, not the list length, carries the usefulness claim.

### Why `k` is reported separately from the list

Separating the two lets both be measured. `k` is the system's usefulness prediction and supports set-based scoring such as precision, recall, and F1 over ranks 1 through `k`. The ranked list supports rank-based measurement and contributes to the judgment pool.

Truncating the submitted list at `k` would discard the ranks below it irrecoverably: organizers can always truncate a deeper run at a declared `k`, but no later analysis can reconstruct what a system would have ranked below its own cutoff. It would also make pool depth a function of each participant's cutoff choice, so documents below aggressive cutoffs go unjudged, treating unjudged documents as non-relevant penalizes participants who submitted more, and the resulting collection is less reusable for future work.

Submission depth is not judging depth. Pooling depth remains an organizer choice and is independent of how deep participants submit.

## Output Format: Ranked Results

For official submissions, provide a standard TREC runfile in `r_output_trec_rag_2026.tsv`. Each line contains six whitespace-separated fields:

```text
topic_id Q0 docid rank score run_id
```

Example:

```text
rag2026-37 Q0 shard_00459_61697 1 12.4838 my-run
rag2026-37 Q0 shard_01012_88420 2 11.9721 my-run
rag2026-37 Q0 shard_00210_44018 3 10.5542 my-run
rag2026-38 Q0 shard_00044_91812 1 10.8114 my-run
```

**Note:** List lengths may differ across narratives, and a list may be longer than the narrative's declared `k`. The usefulness claim is carried by `k` in the companion file, not by the length of the list.

Field rules:

- `topic_id`: narrative identifier from `trec_rag_2026_queries.tsv`; `topic_id` is the standard TREC run-file field name.
- `Q0`: fixed string.
- `docid`: ClimbMix document ID.
- `rank`: rank of the retrieved document for that narrative, starting at 1.
- `score`: numeric score used to rank documents.
- `run_id`: stable identifier for the submitted run.

## Output Format: Declared `k`

Alongside the runfile, provide `r_k_trec_rag_2026.tsv`: one line per narrative, two whitespace-separated fields.

```text
topic_id k
```

Example, for the runfile above:

```text
rag2026-37 2
rag2026-38 1
```

Here the system submitted three documents for `rag2026-37` but predicts only the top two are useful evidence; the third is submitted for pooling and depth-based measurement.

Field rules:

- `topic_id`: narrative identifier from `trec_rag_2026_queries.tsv`, matching the runfile.
- `k`: non-negative integer, the number of top-ranked documents claimed relevant and useful. The claimed set is ranks 1 through `k` of that narrative's ranked list.

`k = 0` is valid and means the system predicts none of its retrieved documents are useful evidence for that narrative. The narrative's ranked list is still submitted and still contributes to the pool.

This file is **optional**. If it is absent, or if a narrative present in the runfile is missing from it, `k` for that narrative defaults to the number of rows submitted for it — the whole submitted list is taken as the usefulness claim.

## Validation Rules

- There is no fixed required number of rows per narrative.
- A narrative may have at most 1000 rows in the runfile.
- Sort each narrative's rows by rank ascending.
- Keep scores non-increasing within each narrative.
- `r_output_trec_rag_2026.tsv` must have exactly six whitespace-separated columns per line.
- Retrieval ranks must restart at 1 for each narrative.
- Every Retrieval `docid` must be a ClimbMix document ID returned by the retriever or custom index.
- Do not emit MS MARCO segment IDs unless official 2026 instructions explicitly require a mapping step.
- If `r_k_trec_rag_2026.tsv` is supplied, it must have exactly two whitespace-separated columns per line, `k` must be a non-negative integer, and `k` must not exceed the number of rows submitted for that narrative.
- Do not reject a run because a narrative's `k` is smaller than its number of submitted rows; that is the intended use.
- Do not reject a run because `r_k_trec_rag_2026.tsv` is absent; treat each narrative's `k` as its submitted row count.
