# TREC RAG 2026 Track Reference

Sources browsed May 31, 2026:

- Home: https://trec-rag.github.io/
- GitHub org: https://github.com/TREC-RAG
- Hugging Face org: https://huggingface.co/TREC-RAG

## Summary

TREC RAG 2026 is the returning Text REtrieval Conference track for retrieval-augmented generation systems; the 2026 track is agent-first and uses NVIDIA's ClimbMix-400b corpus/index. This overview reference summarizes public overview, participation, timeline, and organizer information, while task-level guidelines are covered by the main `trec-rag-2026-track-guidelines` skill.

## Track Goals

The goals of TREC RAG 2026 are:

1. **Automating Deep Research Question Generation**
   - Given a corpus, can we automatically generate open-ended deep research questions that have underspecified goals, surface long-tail domains, and require many intermediate retrieval and reasoning steps to answer?
2. **Developing Improved Evaluation Techniques for Agentic Search**
   - Developing accurate evaluation metrics for assessing retrieval in agentic search.
   - Developing accurate methods to evaluate agentic search answers through side-by-side answer comparisons.
3. **Aligning Deep Research Datasets with LLM Pre-Training Corpora**
   - *Fairness*: Building a testbed to fairly evaluate when LLMs are "memorizing" versus genuinely "generalizing," since we know what the LLM has seen.
   - *Disentanglement*: Building a controlled setting for isolating the contributions of retrieval from the contributions of parametric knowledge in agentic search systems.
4. **Understanding and formulating what an agent-first community evaluation would look like**
   - Conducting a refreshed evaluation of modern coding agents, such as Codex and Claude Code, as automatic system-vs.-system "assessors" compared with humans and previous-generation LLMs.
   - Exploring how agents can reduce the overhead of participating in community evaluation efforts and broaden participation.

## 2026 Status

- The site announces that TREC RAG is returning for 2026.
- The site announces that TREC RAG 2026 will be agent-first and points agents to the TREC-RAG `trec-rag-skills` repository.
- The site announces that TREC RAG 2026 will use NVIDIA's ClimbMix-400b.
- Corpus details are not final on the public site yet, but the site says agents can begin using the corpus through the available SKILLz repository.
- Public website updates for guidelines and timeline are still pending.
- The 2026 task guidelines are available in the `trec-rag-2026-track-guidelines` skill.
- Use `trec-rag-2026-track-guidelines` for task rules, baselines, output formats, ClimbMix/Pyserini defaults, and validation.
- Public submission logistics, deadlines, upload procedures, and portal-specific requirements should be verified from the official site before submission-critical work.
- Current 2026 timeline:
  - Corpus Details: Soon.
  - Test topics released: TBD.
  - Baselines released: TBD.
  - Submission deadline: TBD.
  - Results and judgments returned: TBD.
  - TREC 2026 Conference: November 2026.

## Participation Guidance

- Register for TREC through NIST/Evalbase. The home page says to use the first bullet under Schedule to register an organization in Evalbase.
- Join the Google Groups mailing list, Discord, and SIGIR Slack.
- Include "TREC RAG" in Google Groups join requests.
- Contact njedidi@uwaterloo.ca for issues joining.

## 2026 Organizers

- Nour Jedidi, University of Waterloo
- Lingwei Gu, University of Waterloo
- Daniel Campos, Zipf AI
- Nandan Thakur, University of Waterloo
- Nick Craswell, Microsoft
- Ronak Pradeep, University of Waterloo
- Shivani Upadhyay, University of Waterloo
- Jimmy Lin, University of Waterloo

## Handling Prior-Year Questions

This reference intentionally excludes 2024 and 2025 details.

- For TREC RAG 2025 questions, refer users to https://trec-rag.github.io/trec25/
- For TREC RAG 2024 questions, refer users to https://trec-rag.github.io/trec24/
- If asked about task-level 2026 differences from 2025, use `trec-rag-2026-track-guidelines` for the 2026 side and refer to the 2025 page for prior-year details.
