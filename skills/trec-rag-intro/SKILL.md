---
name: trec-rag-intro
description: Introductory and practical reference for discussing the TREC Retrieval-Augmented Generation (RAG) track. Use when a user wants to understand TREC RAG goals, yearly track status, R/AG/RAG tasks, MS MARCO v2.1 corpus details, topics, timelines, organizers, submission formats, baselines, validation, or how to participate.
---

# TREC RAG Intro

## Use This Skill

Use this skill to answer conversational questions about the TREC RAG track, orient new participants, compare the 2024/2025/2026 iterations, or explain what a system must produce for the Retrieval, Augmented Generation, and Retrieval-Augmented Generation tasks.

Start with the concise answer the user asked for. Load `references/trec-rag.md` when the user asks for facts, dates, task definitions, corpus details, submission formats, organizers, or source links.

## Conversation Guidance

- Distinguish years explicitly. The public site says TREC RAG is returning for 2026, but most concrete task, corpus, topic, baseline, validator, and submission details currently come from the 2025 guidelines and announcements.
- Treat 2026 dates and guidelines as pending unless updated source material is provided or browsed. As of the browsed site, the 2026 timeline says corpus "Soon", test topics "TBD", baselines "TBD", submission deadline "TBD", judgments "TBD", and conference "November 2026".
- Explain the track as an end-to-end benchmark for RAG systems, with separate tasks to evaluate retrieval, answer generation from fixed retrieval results, and full retrieval-augmented answer generation.
- When discussing submissions, emphasize constraints that commonly matter: top-100 segment retrieval for R, max-400-word sentence-level generated answers for AG/RAG, citations tied to MS MARCO v2.1 segments, and validator scripts for generated-answer tasks.
- If the user needs operationally current participation instructions, browse `https://trec-rag.github.io/` before answering because registration, timelines, and guidelines can change.

## Reference

Read `references/trec-rag.md` for the summarized track facts, links, and submission format notes.
