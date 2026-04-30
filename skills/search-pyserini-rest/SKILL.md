---
name: rag-skills-pyserini
description: Use when working with the Pyserini REST search API exposed at http://99.251.12.72:8081, including endpoint discovery, health checks, authenticated search requests, document fetches, query experimentation, and client usage for ClimbMix, FineWeb-Edu, and MS MARCO V2.1 Segmented Doc indexes. Captures verified request and response behavior, especially the meaning of hits and parse, available routes, error cases, dataset-to-index configuration, and how query syntax is interpreted in practice.
---

# Search Pyserini REST

Use this skill when you need to query the Pyserini REST search service or help someone build against it.

## Dataset Configuration

Use these exact dataset-to-index mappings:

- ClimbMix: `climbmix-400b`
- FineWeb-Edu: `fineweb-edu-100b-karpathy`
- MS MARCO V2.1 Segmented Doc: `msmarco-v2.1-doc-segmented`

When the user asks for a dataset by name, map it to the corresponding index above. If the user provides an explicit index, use it as given after confirming it matches the intended dataset when the context is ambiguous.

If the dataset or index is not clear from context, ask the user which index to search before making authenticated search or document-fetch requests. If the user asks which indexes are available, provide the dataset configuration above.

## Authentication

The Pyserini REST API requires a Pyserini access token. Do not attempt authenticated searches or document fetches without a token.

Token handling rules:

- Ask the user for the Pyserini API token if it is not already available locally.
- Store the token only in the repo-local `.env.local` file as `PYSERINI_API_TOKEN=...`.
- Prefer storing the curl authorization header in the repo-local `.curlrc.pyserini-rest` file.
- Never commit `.env.local`, never paste the token into chat, and never print it in command output.
- Never commit `.curlrc.pyserini-rest`, and never print its contents.
- Do not put the token in tracked files, examples, logs, shell history snippets, command lines, or skill documentation.
- If `.env.local` already exists, read only enough to determine whether `PYSERINI_API_TOKEN` is present; do not display the file contents.
- If `.curlrc.pyserini-rest` is missing but `.env.local` has `PYSERINI_API_TOKEN`, create `.curlrc.pyserini-rest` with mode `600` and a single authorization header derived from the token.
- If `.curlrc.pyserini-rest` exists but authenticated requests fail after confirming `PYSERINI_API_TOKEN` is present, regenerate `.curlrc.pyserini-rest` from `.env.local` without printing either file.
- If the API returns the `401` unauthorized response, tell the user to request an access token by emailing `get-pyserini@googlegroups.com`.
- Use `.curlrc.pyserini-rest` for requests:

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-search.json "http://99.251.12.72:8081/v1/climbmix-400b/search?query=anserini&hits=5"
jq . /tmp/pyserini-rest-search.json
```

Rationale: using `curl -sS -K .curlrc.pyserini-rest` keeps the token out of visible command lines and creates a stable command prefix that can be approved once for network access. After that approval is persisted, future Pyserini REST requests can reuse the same prefix without repeated escalation prompts.

When using `jq`, prefer saving the `curl` response to a temporary JSON file with `-o` and then running `jq` as a separate local command. Do not pipe `curl` directly into `jq`; the sandbox treats each pipeline segment as a separate command and may require repeated escalation for otherwise local JSON inspection.

If the API returns an authorization error, tell the user the local token appears missing, expired, or invalid without revealing any token value. If the response says to request an access token by email, include that step and the contact address.

## Endpoints

- `GET /`
- `GET /v1/{index}/search`
- `GET /v1/{index}/doc/{docid}`
- Docs at `/docs`, `/redoc`, `/openapi.json`, `/openapi.yaml`

Base URL:

```text
http://99.251.12.72:8081
```

## Health Check

Use this procedure when the user asks whether the Pyserini REST search server is up.

Start with the unauthenticated root endpoint. This confirms that the HTTP service is reachable without needing to touch the local token:

```bash
curl -sS -i --max-time 10 "http://99.251.12.72:8081/"
```

The server is reachable if this returns `HTTP/1.1 200 OK` and a JSON body like:

```json
{"name":"Pyserini API","version":"v1","description":"REST API aligned with Anserini (Lucene indexes via Pyserini).","openapi":"/openapi.yaml","documentation":"/docs"}
```

Then run a minimal authenticated search to verify that the search endpoint, index, token, and retrieval path are working. Use `Albert Einstein` as the standard health-check query. ClimbMix is the default health-check dataset unless the user asks to check a specific dataset. If the user asks to health-check all indexes, run the same query against every index in Dataset Configuration.

```bash
curl -sS -K .curlrc.pyserini-rest --max-time 15 -o /tmp/pyserini-rest-health-search.json -w '%{http_code}\n' "http://99.251.12.72:8081/v1/climbmix-400b/search?query=Albert%20Einstein&hits=1"
```

Expected status:

```text
200
```

Inspect the saved response with `jq` as a separate local command:

```bash
jq '{api,index,query,candidate_count:(.candidates | length),first:(.candidates[0] // null | if . == null then null else {rank,docid,score,has_doc:(.doc != null)} end)}' /tmp/pyserini-rest-health-search.json
```

A healthy search response should include `api`, `index`, `query`, `candidate_count` greater than zero, and a first candidate with `rank`, `docid`, `score`, and `has_doc: true`.

Interpretation:

- Root endpoint returns `200`, authenticated search returns `200`, and `has_doc` is `true`: the search server is up.
- Root endpoint returns `200` but authenticated search returns `401` or an authorization error: the service is up, but the local token is missing, expired, or invalid.
- Root endpoint returns `200` but search returns an index error: the service is up, but the requested index may be unavailable or misnamed.
- Root endpoint times out or cannot connect: the service is likely down or unreachable from the current network.
- Do not print `.curlrc.pyserini-rest`, `.env.local`, or any authorization header while checking health.

## Request Model

### Search

```text
GET /v1/{index}/search?query=...&hits=...
```

Parameters:

- `query`: required string
- `hits`: optional positive integer, default `10`
- `parse`: optional boolean, default `true`; omit it unless the user explicitly asks to control raw vs. parsed output

### Document Fetch

```text
GET /v1/{index}/doc/{docid}
```

Parameters:

- `docid`: required path string
- `parse`: optional boolean, default `true`; omit it unless the user explicitly asks to control raw vs. parsed output

## Response Shape

Search returns:

```json
{
  "api": "v1",
  "index": "climbmix-400b",
  "query": { "text": "anserini" },
  "candidates": [
    {
      "docid": "shard_00459_61697",
      "score": 12.483799934387207,
      "rank": 1,
      "doc": "..."
    }
  ]
}
```

The `index` field should match the index requested, for example `climbmix-400b` for ClimbMix, `fineweb-edu-100b-karpathy` for FineWeb-Edu, or `msmarco-v2.1-doc-segmented` for MS MARCO V2.1 Segmented Doc.

Document fetch returns:

```json
{
  "api": "v1",
  "index": "climbmix-400b",
  "docid": "shard_00459_61697",
  "doc": "..."
}
```

`doc` may be a parsed value or a raw stored string depending on `parse`.

## `parse` Behavior

- `parse=true` or omitted: return parsed document contents when possible.
- `parse=false`: return the raw stored document string.
- For the configured indexes, `parse=false` returns the stored JSON string. ClimbMix and FineWeb-Edu documents commonly include fields such as `id` and `text`; MS MARCO V2.1 Segmented Doc documents include segment-oriented fields such as `url`, `title`, `headings`, and `segment`.
- Client-side parsing works with `jq '... | fromjson'`.
- Unless the user explicitly asks for raw stored output, do not send the `parse` parameter at all.
- This applies to both `/search` and `/doc/{docid}` requests.

Examples:

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-search-raw.json "http://99.251.12.72:8081/v1/climbmix-400b/search?query=anserini&hits=1&parse=false"
jq '.candidates[0].doc | fromjson' /tmp/pyserini-rest-search-raw.json
```

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-doc-raw.json "http://99.251.12.72:8081/v1/climbmix-400b/doc/shard_00459_61697?parse=false"
jq '.doc | fromjson' /tmp/pyserini-rest-doc-raw.json
```

Practical guidance:

- Do not include `parse` in requests by default.
- Only specify `parse=false` when the user explicitly asks for the raw stored payload.
- Only specify `parse=true` when the user explicitly asks to see or control the parameter.
- If you are simply inspecting documents to answer a question, fetch them with the default behavior and omit `parse`.

## Query Semantics

Treat `query` as analyzed text, not as a Lucene query language surface.

Observed behavior from ClimbMix query experiments:

- Case-insensitive: `anserini` and `AnSeRiNi` behave identically.
- Quotes do not materially change ranking: `"what is anserini"` matched `what is anserini`.
- Boolean/operator-like syntax was inert for ranking in these experiments:
  - `anserini lucene`
  - `anserini AND lucene`
  - `anserini OR lucene`
  - `+anserini +lucene`
  - `anserini -lucene`
  all produced the same top results and scores.
- Fielded syntax is not exposed meaningfully: `text:anserini` returned zero hits.
- Punctuation is normalized: `anserini?` behaved like `anserini`.
- Hyphenation is normalized: `open-source` behaved like `open source`.
- Morphological normalization or stemming is likely enabled: `anserinis` behaved like `anserini`.
- No-match queries return an empty `candidates` array.

Practical guidance:

- Use normal natural-language or keyword queries.
- Do not rely on Lucene parser features such as fielded search, boolean operators, or required/prohibited term syntax.
- Treat these query semantics as verified for ClimbMix and likely but not guaranteed for the other configured indexes unless separately tested.

## Error Behavior

Verified responses:

- Unauthorized or missing token:

```json
{"error":"Unauthorized. To request an access token, email get-pyserini@googlegroups.com."}
```

Resolution: email `get-pyserini@googlegroups.com` to request a Pyserini access token, then store the received token locally as `PYSERINI_API_TOKEN` in `.env.local` and regenerate `.curlrc.pyserini-rest`.

- Missing `query`:

```json
{"error":"Parameter 'query' is required"}
```

- `hits=0`:

```json
{"error":"Parameter 'hits' must be positive"}
```

- `hits=abc`:

```json
{"error":"Parameter 'hits' must be an integer"}
```

- `parse=maybe`:

```json
{"error":"Parameter 'parse' must be 'true' or 'false'"}
```

- Invalid index:

```json
{"error":"Unable to open index: no-such-index"}
```

- Missing document:

```json
{"error":"Document not found: no-such-docid"}
```

- Non-`GET` request:

```json
{"error":"Only GET is supported"}
```

Status codes observed:

- `401` for unauthorized requests, missing tokens, expired tokens, or invalid tokens; request a token by emailing `get-pyserini@googlegroups.com`
- `400` for invalid parameters and invalid index
- `404` for missing document
- `405` for unsupported method

## Useful Commands

Basic search:

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-search.json "http://99.251.12.72:8081/v1/climbmix-400b/search?query=Albert%20Einstein&hits=5"
jq . /tmp/pyserini-rest-search.json
```

Compact result list:

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-search.json "http://99.251.12.72:8081/v1/climbmix-400b/search?query=Albert%20Einstein&hits=5"
jq '.candidates[] | {rank, score, docid}' /tmp/pyserini-rest-search.json
```

Fetch one document:

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-doc.json "http://99.251.12.72:8081/v1/climbmix-400b/doc/shard_00459_61697"
jq . /tmp/pyserini-rest-doc.json
```

FineWeb-Edu search:

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-fineweb-edu-search.json "http://99.251.12.72:8081/v1/fineweb-edu-100b-karpathy/search?query=Albert%20Einstein&hits=5"
jq '.candidates[] | {rank, score, docid}' /tmp/pyserini-rest-fineweb-edu-search.json
```

MS MARCO V2.1 Segmented Doc search:

```bash
curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-msmarco-v21-segmented-doc-search.json "http://99.251.12.72:8081/v1/msmarco-v2.1-doc-segmented/search?query=Albert%20Einstein&hits=5"
jq '.candidates[] | {rank, score, docid}' /tmp/pyserini-rest-msmarco-v21-segmented-doc-search.json
```

## Workflow

When helping with this API:

1. Confirm the dataset or index name. Map ClimbMix to `climbmix-400b`, FineWeb-Edu to `fineweb-edu-100b-karpathy`, and MS MARCO V2.1 Segmented Doc to `msmarco-v2.1-doc-segmented`.
2. If the dataset or index is unclear from context, ask the user which index to search. If the user asks what is available, answer with the mappings from Dataset Configuration.
3. Check whether `.env.local` contains `PYSERINI_API_TOKEN` without printing it.
4. If the token is missing, ask the user to provide it for local storage in `.env.local`; if they do not have a token, tell them to request one by emailing `get-pyserini@googlegroups.com`. Do not proceed with authenticated API calls until a token is available.
5. Ensure `.curlrc.pyserini-rest` exists, is ignored by git, and has mode `600`.
6. Use `curl -sS -K .curlrc.pyserini-rest -o /tmp/pyserini-rest-*.json` for all Pyserini REST requests so the token stays out of command lines and the command prefix can be approved once for network access.
7. Use `/v1/{index}/search` for retrieval and `/v1/{index}/doc/{docid}` for follow-up fetches.
8. Run `jq` only as a separate local command against the saved `/tmp/pyserini-rest-*.json` file; avoid `curl | jq` pipelines.
9. Omit `parse` by default; the API already defaults to parsed output.
10. Treat including `parse=false` in ordinary retrieval as a mistake unless the user explicitly requested raw stored payloads.
11. Use `parse=false` only when the caller explicitly wants the original stored payload, or `parse=true` only when they explicitly want to control the parameter.
12. Formulate queries as ordinary text; avoid assuming Lucene query syntax support.
13. When debugging clients, check HTTP status and the JSON `error` field first.
