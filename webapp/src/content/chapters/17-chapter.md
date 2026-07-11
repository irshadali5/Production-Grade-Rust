---
title: "Intensive Deep Dive: Cache Stampedes, Singleflight, & Redis RESP"
description: "Intensive deep dive for chapter 17"
order: 17
---


## 1. The Cache Stampede (Thundering Herd) Vulnerability



Caching is not a performance optimization; in a hyperscale system, caching is a structural requirement for survival. However, a naive caching implementation introduces a fatal vulnerability known as a **Cache Stampede**.


Imagine your Rust API executes a heavy analytical SQL query that takes 8 seconds to run. You cache the result in Garnet (Redis) with a Time-To-Live (TTL) of 60 minutes. For 59 minutes and 59 seconds, the system is flawless, serving the cached data to 1,000 users per second in less than 1 millisecond.


At exactly the 60-minute mark, the cache key expires. Because your API processes 1,000 requests per second, the next 1,000 incoming requests all check the cache simultaneously. All 1,000 requests experience a Cache Miss. Instantly, all 1,000 requests attempt to execute the heavy 8-second SQL query against the Postgres database. The database's connection pool is exhausted, the CPU hits 100%, and the Postgres instance violently crashes under the synchronized load. The cache expiration has mathematically triggered a self-inflicted Denial of Service (DoS) attack.

## 2. The Singleflight Deduplication Algorithm



We mathematically immunize the system against Cache Stampedes using the **Singleflight** pattern. Singleflight is an asynchronous deduplication algorithm. It intercepts concurrent requests for the identical cache key before they hit the database.


When the 1,000 concurrent requests arrive during the Cache Miss, Singleflight designates the very first request as the "Leader." The Leader is allowed to proceed and execute the 8-second SQL query. The remaining 999 requests are intercepted and placed into a lock-free asynchronous waiting queue (via Tokio `oneshot` channels).


When the Leader finishes the database query, it writes the result back to the Garnet cache. Crucially, it then takes that single result in memory and broadcasts it across the `oneshot` channels to the 999 waiting requests. A single physical database query successfully satisfies 1,000 users. By collapsing synchronized traffic into a single execution, Singleflight completely shields the database from traffic spikes, ensuring flat latency regardless of load.

## 3. Redis Serialization Protocol (RESP) Parsing



When our Rust application communicates with Garnet, it uses the **Redis Serialization Protocol (RESP)**. Most developers blindly rely on libraries like `redis-rs` without understanding the underlying physics. RESP is a binary-safe, text-based protocol.


When you execute a `GET` command, Garnet returns a RESP string, for example: `$5\r\nhello\r\n`. The `$5` indicates a Bulk String of 5 bytes, followed by the Carriage Return/Line Feed (`\r\n`), followed by the exact 5 bytes of payload, followed by a final `\r\n`.


To process this at 5 million operations per second, our Rust client does not parse this into a standard `String` (which would trigger a massive heap allocation). Instead, it uses zero-copy parsing. It reads the raw TCP buffer, verifies the length, and creates a lightweight slice (`&[u8]`) pointing directly into the raw network buffer. By completely bypassing the OS memory allocator, we can deserialize massive cached payloads in nanoseconds.
