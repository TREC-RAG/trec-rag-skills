# TREC RAG Track Reference

Sources browsed April 25, 2026:

- Home: https://trec-rag.github.io/
- TREC RAG 2025: https://trec-rag.github.io/trec25/
- TREC RAG 2024: https://trec-rag.github.io/trec24/
- 2025 corpus: https://trec-rag.github.io/annoucements/2025-rag25-corpus/
- 2025 timeline: https://trec-rag.github.io/annoucements/2025-timeline/
- 2025 guidelines: https://trec-rag.github.io/annoucements/2025-track-guidelines/
- 2025 topics: https://trec-rag.github.io/annoucements/2025-topics-released/
- 2025 baselines and validator: https://trec-rag.github.io/annoucements/2025-baselines/
- GitHub org: https://github.com/TREC-RAG
- Hugging Face org: https://huggingface.co/TREC-RAG

## One-Sentence Summary

TREC RAG is a Text REtrieval Conference track for evaluating retrieval-augmented generation systems over MS MARCO v2.1, separating retrieval quality, generation quality with fixed retrieved evidence, and full end-to-end RAG behavior.

## Track Goals

- Foster research on retrieval-augmented generation systems.
- Evaluate systems that combine retrieval over large corpora with LLM-based answer generation.
- Provide a unified benchmark for end-to-end RAG, while preserving task boundaries that allow component-level analysis.
- Emphasize relevant, accurate, up-to-date, contextually appropriate generated content grounded in retrieved evidence.

## Year Status

### 2026

- The site announces that TREC RAG is returning for 2026.
- Concrete 2026 guidelines and timeline are not yet posted on the browsed home page.
- Current 2026 timeline placeholders:
  - Corpus released: Soon.
  - Test topics released: TBD.
  - Baselines released: TBD.
  - Submission deadline: TBD.
  - Results and judgments returned: TBD.
  - TREC 2026 Conference: November 2026.
- Participation guidance on the home page:
  - Register for TREC through NIST/Evalbase.
  - Join the Google Groups mailing list and Discord.
  - Include "TREC RAG" in Google Groups join requests.
  - Contact njedidi@uwaterloo.ca for Google Groups issues.
- 2026 organizers listed on the site:
  - Nour Jedidi, University of Waterloo
  - Lingwei Gu, University of Waterloo
  - Daniel Campos, Zipf AI
  - Nandan Thakur, University of Waterloo
  - Nick Craswell, Microsoft
  - Ronak Pradeep, University of Waterloo
  - Shivani Upadhyay, University of Waterloo
  - Jimmy Lin, University of Waterloo

### 2025

- 2025 continues the three-task format used in 2024.
- Test topics: 105 RAG test narratives, released July 11, 2025.
- Baselines released: July 23, 2025.
- Submission deadline: August 17, 2025 AoE.
- Results and judgments returned: October 2025.
- TREC 2025 Conference: November 2025.
- 2025 organizers:
  - Shivani Upadhyay, University of Waterloo
  - Ronak Pradeep, University of Waterloo
  - Nandan Thakur, University of Waterloo
  - Jimmy Lin, University of Waterloo
  - Nick Craswell, Microsoft

### 2024

- First listed iteration on the site.
- Topics: 301 RAG 2024 topics.
- Final topics released: August 4, 2024.
- Submission deadline extended to August 25, 2024 AoE.
- Results and judgments returned: October 2024.
- TREC 2024 Conference: November 2024.
- 2024 organizers:
  - Ronak Pradeep, University of Waterloo
  - Nandan Thakur, University of Waterloo
  - Jimmy Lin, University of Waterloo
  - Nick Craswell, Microsoft

## Shared Data

TREC RAG 2024 and 2025 use MS MARCO Segment v2.1. The 2025 corpus announcement says the track uses both the MS MARCO v2.1 document corpus and its segmented counterpart.

Document corpus:

- Total documents: 10,960,555.
- Format: 70 gzipped JSONL files in a TAR archive.
- Download named `msmarco_v2.1_doc.tar`, size 28.1 GB.
- MD5: `a5950665d6448d3dbaf7135645f1e074`.
- Fields: `docid`, `url`, `title`, `headings`, `body`.
- A document `docid`, for example `msmarco_v2.1_doc_29_677149`, encodes file number and byte offset.

Segmented corpus:

- Total segments: 113,520,750.
- Format: 70 gzipped JSONL files in a TAR archive.
- Download named `msmarco_v2.1_doc_segmented.tar`, size 25.1 GB.
- MD5: `3799e7611efffd8daeb257e9ccca4d60`.
- Segmentation: sliding window of 10 sentences with stride 5.
- Segment size: roughly 500-1000 characters.
- Fields: `docid`, `url`, `title`, `headings`, `segment`, `start_char`, `end_char`.
- Segment IDs look like `msmarco_v2.1_doc_52_1274794243#7_2564847343`; the portion before `#` maps back to the document ID.

Associated qrels and topics mentioned for 2025 include TREC RAG 2024, TREC DL 2021/2022/2023, MS MARCO Dev, and MS MARCO Dev2.

## Tasks

### R: Retrieval Task

Purpose:

- Evaluate ad-hoc retrieval of relevant MS MARCO v2.1 segments for long-form, non-factoid topic narratives.
- Similar in spirit to TREC Deep Learning Track retrieval, but using MS MARCO v2.1 document chunks/segments.

Inputs:

- Topics as JSONL, e.g. `trec_rag_2025_queries.jsonl`, with `id` and `title`.
- MS MARCO v2.1 segmented collection.

Output:

- Standard TREC TSV run file such as `r_output_trec_rag_2025.tsv`.
- Top-k is 100; more than 100 results are truncated.
- Each line has six whitespace-separated fields:
  - topic ID
  - fixed string `Q0`
  - segment ID
  - rank
  - non-increasing score
  - run ID

Experimental 2025 relevance judgment subtask:

- Participants may submit QREL-style relevance judgments.
- Assessment pool should use the top-20 scored documents from baseline runs.
- Judgment scale in tentative guidelines:
  - 0: not relevant
  - 1: related to the narrative but does not answer any part
  - 2: answers 1 part
  - 3: answers 2-3 parts
  - 4: answers 4+ parts

### AG: Augmented Generation Task

Purpose:

- Evaluate generated answer quality when retrieval is fixed.
- Participants generate grounded answers using provided top-k segments from a baseline retrieval system.
- Framed as an NLP/generation task because retrieval input is supplied.

Inputs:

- Topic narratives.
- MS MARCO v2.1 segments.
- Provided ranked top-k relevant segments for each topic.

Output:

- JSONL generated-answer submission.
- Each answer is broken into sentences.
- Total response length must be less than 400 words.
- Each sentence has citations to supporting segments.
- Citations refer either to zero-indexed positions in a `references` list or directly to segment IDs, depending on the accepted format.

### RAG: Retrieval-Augmented Generation Task

Purpose:

- Evaluate end-to-end RAG systems.
- Participants may use their own retrieval system and chunking technique.
- Output must map evidence chunks back to MS MARCO Segment v2.1 for reproducibility and evaluation.

Inputs:

- Topic narratives.
- MS MARCO v2.1 corpus or segments.

Output:

- Generated answer with sentence-level citations.
- Retrieved references are participant-produced, up to 100 segment IDs.
- Answer is under 400 words and grounded in cited segment IDs.

## Generated-Answer Submission Shape

The 2025 guidelines describe two similar formats. Preserve the specific current format from the latest guidelines if preparing an actual run.

Common fields:

- `team_id`: team tag.
- `run_id`: run tag.
- `type`: `manual` or `automatic`.
- `narrative_id`: topic ID from `trec_rag_2025_queries.jsonl`.
- `narrative`: topic narrative text.
- `prompt`: optional detailed generation prompt.
- `references`: ranked list of top-k segment IDs from retrieval, maximum 100.
- `answer`: array of sentence objects.
- Sentence object:
  - `text`: one answer sentence.
  - `citations`: supporting evidence, sorted from strongest to weakest support.

Important practical constraints:

- The total answer must be under 400 words.
- Citations must refer to evidence in the MS MARCO v2.1 segment collection.
- For Format 1, citations are zero-indexed references into the `references` array.
- For Format 2, citations are segment IDs.

## Baselines and Validation

- The 2025 baselines announcement says baseline models are available for retrieval -> rerank and retrieval -> rerank -> generate.
- AG retrieval baselines and instructions are hosted on GitHub.
- The Ragnarök repository contains validator scripts for AG and RAG generated-answer submissions.
- Participants should review validator warnings and errors for common pitfalls including sentence drops and duplicate citations.

## Evaluation Notes

The 2024 page proposed this high-level generation evaluation flow:

- Gather participant answers.
- Evaluate how well citations support answer sentences.
- Pool retrieved sentences and create nuggets.
- Assign nuggets to answer sentences, allowing multiple nuggets per sentence.
- Aggregate scores along with linguistic features such as fluency and coherence.

Use this as historical context unless the user asks specifically about 2024 or no newer evaluation guidance is available.

## Common Explanations

"What are the three tasks?"

- R is retrieval only: return ranked MS MARCO v2.1 segment IDs.
- AG is generation with fixed retrieval: write a cited answer from provided segments.
- RAG is full end-to-end: retrieve evidence yourself, generate a cited answer, and map evidence to MS MARCO v2.1 segment IDs.

"What makes this different from ordinary QA?"

- Topics are long, non-factoid narratives requiring long-form answers.
- Evaluation cares about both answer quality and evidence grounding.
- The benchmark separates retrieval and generation so teams can study component interactions.

"What should I verify before submitting?"

- Correct task format.
- Correct topic IDs.
- Run ID and team ID included.
- R retrieval output has no more than 100 ranked results per topic.
- Generated answers are under 400 words.
- Sentence-level citations are valid, non-duplicative, and point to the intended segments.
- Validator scripts pass or warnings are understood.
