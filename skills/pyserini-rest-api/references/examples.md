# Examples

Use these examples when running common Pyserini REST API requests manually. Replace `<base-url>` with the current service location from `SKILL.md`.

## Basic Search

```bash
curl -sS -K .curlrc.pyserini-rest -o tmp/pyserini-rest-search.json "<base-url>/v1/climbmix-400b/search?query=Albert%20Einstein&hits=5"
jq . tmp/pyserini-rest-search.json
```

## Agent Search with Academic Trace

Use this pattern by default when an agent knows the source question. These optional fields are
collected solely for academic research on agent retrieval behavior.

```bash
curl -sS -G -K .curlrc.pyserini-rest \
  -o tmp/pyserini-rest-search.json \
  --data-urlencode 'query=Albert Einstein birthplace' \
  --data-urlencode 'hits=5' \
  --data-urlencode 'qid=example-001' \
  --data-urlencode 'question=Where was Albert Einstein born?' \
  --data-urlencode 'run_id=example-001-attempt-1' \
  --data-urlencode 'agent=codex/pyserini-rest-v1' \
  --data-urlencode 'step=0' \
  '<base-url>/v1/climbmix-400b/search'
jq . tmp/pyserini-rest-search.json
```

Propagate the same `qid`, `question`, `run_id`, and `agent` to document fetches and increment `step`:

```bash
curl -sS -G -K .curlrc.pyserini-rest \
  -o tmp/pyserini-rest-doc.json \
  --data-urlencode 'qid=example-001' \
  --data-urlencode 'question=Where was Albert Einstein born?' \
  --data-urlencode 'run_id=example-001-attempt-1' \
  --data-urlencode 'agent=codex/pyserini-rest-v1' \
  --data-urlencode 'step=1' \
  '<base-url>/v1/climbmix-400b/doc/shard_00459_61697'
jq . tmp/pyserini-rest-doc.json
```

## Compact Result List

```bash
curl -sS -K .curlrc.pyserini-rest -o tmp/pyserini-rest-search.json "<base-url>/v1/climbmix-400b/search?query=Albert%20Einstein&hits=5"
jq '.candidates[] | {rank, score, docid}' tmp/pyserini-rest-search.json
```

## Fetch One Document

```bash
curl -sS -K .curlrc.pyserini-rest -o tmp/pyserini-rest-doc.json "<base-url>/v1/climbmix-400b/doc/shard_00459_61697"
jq . tmp/pyserini-rest-doc.json
```

## FineWeb-Edu Search

```bash
curl -sS -K .curlrc.pyserini-rest -o tmp/pyserini-rest-fineweb-edu-search.json "<base-url>/v1/fineweb-edu-100b-karpathy/search?query=Albert%20Einstein&hits=5"
jq '.candidates[] | {rank, score, docid}' tmp/pyserini-rest-fineweb-edu-search.json
```

## MS MARCO V2.1 Segmented Doc Search

```bash
curl -sS -K .curlrc.pyserini-rest -o tmp/pyserini-rest-msmarco-v21-segmented-doc-search.json "<base-url>/v1/msmarco-v2.1-doc-segmented/search?query=Albert%20Einstein&hits=5"
jq '.candidates[] | {rank, score, docid}' tmp/pyserini-rest-msmarco-v21-segmented-doc-search.json
```
