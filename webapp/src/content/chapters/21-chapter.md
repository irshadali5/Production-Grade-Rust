---
title: "Intensive Deep Dive: HNSW Vector Graphs & The Curse of Dimensionality"
description: "Intensive deep dive for chapter 21"
order: 21
---


## 1. The Limitations of B-Tree Lexical Search



Standard relational databases use B-Tree indexing to perform Lexical Search (matching exact text strings). If a user queries for "fast automobile," a B-Tree will scan for those exact characters. It will completely ignore a document titled "rapid car," because the strings do not match. To build Retrieval-Augmented Generation (RAG) AI applications, we must search based on the **semantic meaning** of the text, not the characters.

## 2. High-Dimensional Vector Embeddings



We achieve Semantic Search by passing all text through an Embedding Model (such as OpenAI's `text-embedding-3-small`). The neural network analyzes the text and outputs a 1,536-dimensional Vector—a massive array of 1,536 floating-point numbers.


This Vector is a physical coordinate in a 1,536-dimensional mathematical space. In this space, the coordinate for "automobile" is physically located millimeters away from the coordinate for "car," but thousands of miles away from the coordinate for "apple." We store these massive floating-point arrays directly in Postgres using the `pgvector` extension.

## 3. Cosine Similarity & The Curse of Dimensionality



When a user types a search query, we embed their query into a Vector. We then calculate the **Cosine Similarity**—the geometric angle—between the query vector and every document vector in the database. An angle of 0 degrees (Cosine of 1.0) means perfect semantic equivalence.


However, this introduces a profound mathematical bottleneck: **The Curse of Dimensionality**. Calculating the exact Cosine angle against 100 million 1,536-dimensional arrays requires trillions of floating-point operations. Doing an exact K-Nearest Neighbors (KNN) search across the entire database is computationally impossible for a real-time API.

## 4. Hierarchical Navigable Small World (HNSW) Algorithms



We break the Curse of Dimensionality using an Approximate Nearest Neighbors (ANN) algorithm known as the **HNSW (Hierarchical Navigable Small World) Graph**.


Instead of scanning every vector, `pgvector` builds a multi-layered graph in memory. The top layer contains very few vectors with massive, long-distance links spanning the 1,536-dimensional space. The bottom layer contains all the vectors with microscopic links to their immediate neighbors.


When a search query arrives, the HNSW algorithm enters the top layer. It takes massive, sweeping mathematical leaps across the dimensional space to rapidly locate the general semantic "neighborhood" of the query (e.g., jumping straight to the "vehicle" neighborhood). It then descends to the lower layers, taking smaller and smaller steps to find the exact nearest neighbors.


This graph traversal trades a microscopic fraction of accuracy (perhaps 1% error rate) for an astronomical, logarithmic speedup. By utilizing HNSW, our Rust server can perform deep semantic searches across billions of documents, returning the results in less than 5 milliseconds.
