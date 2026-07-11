---
title: "Intensive Deep Dive: AST Macros & Compile-Time OpenAPI"
description: "Intensive deep dive for chapter 26"
order: 26
---


## 1. The Disconnect Between Code and Documentation



In legacy API development, engineers manually write Swagger (OpenAPI) YAML documentation. This guarantees a fatal desynchronization. A developer will change a database column from a 32-bit integer to a 64-bit integer in the Rust code, but forget to update the YAML file. The iOS and React teams, relying on the Swagger file to generate their SDKs, will compile their clients expecting a 32-bit integer. When the 64-bit payload arrives in production, the iOS app suffers a fatal deserialization panic and crashes.

## 2. AST Reflection via Procedural Macros



We eliminate this mathematically by binding the documentation directly to the Rust Abstract Syntax Tree (AST) using the `utoipa` crate.


We attach the `#[derive(ToSchema)]` procedural macro to our Rust structs. During compilation, before the binary is even generated, the macro intercepts the compiler's AST. It recursively analyzes the memory layout and types of the struct. If a field is defined as `email: Option<String>`, the macro uses Rust's type system to mathematically deduce that the OpenAPI JSON Schema field must be marked as `type: "string"` and `nullable: true`.

## 3. The Zero-Maintenance API Contract



If a developer changes the `email` field to a custom `EmailAddress` Newtype, the compiler automatically updates the generated JSON Schema to reflect the new validation rules. If the developer adds a new route to the Axum router but forgets to add the `#[utoipa::path]` macro, the compiler throws a warning.


This creates a mathematically perfect, self-updating API contract. We serve this generated JSON Schema at the `/api-docs/openapi.json` endpoint. The frontend teams use `openapi-generator` to pull this JSON and auto-generate type-safe TypeScript and Swift SDKs. By elevating API documentation to a compile-time AST artifact, we guarantee that the frontend and backend are always in perfect cryptographic synchronization.
