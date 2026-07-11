# Retrieval Plan

## Overview

This document outlines the strategy for implementing text retrieval in the knowledge base application. The goal is to enable grounded question answering over imported documents without requiring an external LLM API.

## Chunking Approach

Documents are split into chunks using a paragraph-aware algorithm:
- Split on double newlines (paragraph boundaries)
- Merge short paragraphs until chunk reaches ~500 characters
- Each chunk gets a unique ID, document reference, and metadata

## Keyword Matching

The retrieval system uses keyword-based matching:
1. Tokenize the question into individual words
2. Filter out stop words (words shorter than 3 characters)
3. For each chunk, count how many question keywords appear in the content
4. Rank chunks by keyword overlap score
5. Return top 2 most relevant chunks as citations

## Citation Format

Each citation includes:
- Document ID and title
- Chunk index within the document
- Text excerpt (first 200 characters of the chunk)

## Mock Q&A Patterns

The mock Q&A service includes predefined answer patterns for common topics:
- Architecture and design questions
- Document import and management
- Indexing and search
- Meeting notes and summaries
- Logging and observability
- Feedback and quality

For questions that don't match a pattern, the system returns a generic response based on the most relevant citation, or indicates that no indexed documents are available.

## Confidence Scoring

Responses include a confidence score:
- 0.85 when citations are found
- 0.30 when no citations are available

This scoring system allows the UI to visually distinguish between well-grounded and speculative answers.

## Benchmarking

The retrieval pipeline should be benchmarked with:
- Document import throughput (files/second)
- Indexing speed (chunks/second)
- Query latency (milliseconds per question)
- Citation accuracy (relevance of returned chunks)
