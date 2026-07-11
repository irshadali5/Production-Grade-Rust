import re

filepath = 'src/pages/index.astro'

new_chapter = """<section class="chapter" id="caching">
    <div class="chapter-label">Chapter 17</div>
    <h1>Caching & High Availability</h1>

    <p>As traffic scales, querying the Postgres database for every request becomes a bottleneck. We introduce caching to serve reads lightning-fast.</p>

    <h2>In-Memory Caching with moka</h2>
    <p>For configuration or static newsletter templates, an in-memory cache is ideal.</p>

    <div class="code-block">
      <div class="code-header">
        <span class="code-filename">src/cache.rs</span>
        <span class="code-lang">rust</span>
      </div>
      <pre><span class="kw">use</span> <span class="type">moka</span>::<span class="type">future</span>::<span class="type">Cache</span>;

<span class="kw">let</span> cache: <span class="type">Cache</span>&lt;<span class="type">String</span>, <span class="type">String</span>&gt; = <span class="type">Cache</span>::builder()
    .max_capacity(<span class="num">10_000</span>)
    .time_to_live(<span class="type">Duration</span>::from_secs(<span class="num">60</span> * <span class="num">5</span>))
    .build();

cache.insert(<span class="str">"template_1"</span>.to_string(), <span class="str">"&lt;html&gt;...&lt;/html&gt;"</span>.to_string()).<span class="kw">await</span>;</pre>
    </div>

    <h2>Distributed Caching with Redis</h2>
    <p>When scaling horizontally across multiple Kubernetes pods, in-memory caches aren't shared. We use <strong>Redis</strong> (via the <code>redis</code> or <code>fred</code> crates) for distributed caching of user sessions and rate-limit quotas.</p>

    <div class="callout success">
      <div class="callout-title">Stale-While-Revalidate</div>
      <p>For ultimate performance, serve a slightly stale cached response while spawning an async background task to fetch the fresh data from the DB. This completely hides database latency from the end-user.</p>
    </div>

    <h2>Expert Deep Dive: Cache Stampedes & Singleflight</h2>
    <p>A <strong>Cache Stampede</strong> (or Thundering Herd) is a catastrophic failure mode in hyperscale architectures. It occurs when a highly-requested cache key expires, and simultaneously, 1,000 concurrent requests realize the cache is empty. All 1,000 requests instantly query the database to rebuild the cache, immediately crushing the database under the massive spike in load.</p>
    <p>To solve this, we implement the <strong>Singleflight</strong> pattern. The goal is request deduplication: if multiple requests ask for the same expired key simultaneously, only the <em>first</em> request actually queries the database. The other 999 requests simply <code>.await</code> the result of the first request via a broadcast channel. The database sees 1 query, and all 1,000 requests are satisfied instantaneously.</p>

    <h3>Singleflight Implementation</h3>
    <p>We can build a production-grade <code>Singleflight</code> struct using a <code>DashMap</code> to track in-flight requests and <code>tokio::sync::watch</code> channels to broadcast the result to all waiting tasks.</p>

    <div class="code-block">
      <div class="code-header">
        <span class="code-filename">src/core/singleflight.rs</span>
        <span class="code-lang">rust</span>
      </div>
      <pre><span class="kw">use</span> <span class="type">dashmap</span>::<span class="type">DashMap</span>;
<span class="kw">use</span> <span class="type">std</span>::<span class="type">sync</span>::<span class="type">Arc</span>;
<span class="kw">use</span> <span class="type">tokio</span>::<span class="type">sync</span>::<span class="type">watch</span>;
<span class="kw">use</span> <span class="type">std</span>::<span class="type">future</span>::<span class="type">Future</span>;

<span class="cmt">/// A request deduplicator for eliminating cache stampedes.</span>
<span class="kw">pub struct</span> <span class="type">Singleflight</span>&lt;T&gt; {
    <span class="cmt">// Maps a cache key to a broadcast channel receiver for the running future.</span>
    in_flight: <span class="type">DashMap</span>&lt;<span class="type">String</span>, <span class="type">watch</span>::<span class="type">Receiver</span>&lt;<span class="type">Option</span>&lt;T&gt;&gt;&gt;,
}

<span class="kw">impl</span>&lt;T: <span class="type">Clone</span> + <span class="type">Send</span> + <span class="type">Sync</span> + <span class="life">'static</span>&gt; <span class="type">Singleflight</span>&lt;T&gt; {
    <span class="kw">pub fn</span> <span class="fn">new</span>() -&gt; <span class="kw">Self</span> {
        <span class="kw">Self</span> {
            in_flight: <span class="type">DashMap</span>::<span class="fn">new</span>(),
        }
    }

    <span class="cmt">/// Executes the given future if no other request is currently processing this key.</span>
    <span class="cmt">/// Otherwise, awaits the result of the existing request.</span>
    <span class="kw">pub async fn</span> <span class="fn">work</span>&lt;F&gt;(&amp;<span class="kw">self</span>, key: <span class="type">String</span>, fut: F) -&gt; T
    <span class="kw">where</span>
        F: <span class="type">Future</span>&lt;Output = T&gt; + <span class="type">Send</span> + <span class="life">'static</span>,
    {
        <span class="cmt">// Check if someone is already fetching this key</span>
        <span class="kw">let</span> rx = {
            <span class="kw">if let</span> <span class="type">Some</span>(rx) = <span class="kw">self</span>.in_flight.<span class="fn">get</span>(&amp;key) {
                <span class="type">Some</span>(rx.<span class="fn">clone</span>())
            } <span class="kw">else</span> {
                <span class="type">None</span>
            }
        };

        <span class="cmt">// If an existing request is in flight, just await its broadcast channel</span>
        <span class="kw">if let</span> <span class="type">Some</span>(<span class="kw">mut</span> rx) = rx {
            <span class="kw">while</span> rx.<span class="fn">changed</span>().<span class="kw">await</span>.<span class="fn">is_ok</span>() {
                <span class="kw">if let</span> <span class="type">Some</span>(<span class="kw">ref</span> val) = *rx.<span class="fn">borrow</span>() {
                    <span class="kw">return</span> val.<span class="fn">clone</span>();
                }
            }
            <span class="mac">panic!</span>(<span class="str">"Leader task dropped without broadcasting"</span>);
        }

        <span class="cmt">// We are the first! Become the leader.</span>
        <span class="kw">let</span> (tx, <span class="kw">mut</span> rx) = <span class="type">watch</span>::<span class="fn">channel</span>(<span class="type">None</span>);
        <span class="kw">self</span>.in_flight.<span class="fn">insert</span>(key.<span class="fn">clone</span>(), rx.<span class="fn">clone</span>());

        <span class="cmt">// Do the actual expensive work (e.g., query the database)</span>
        <span class="kw">let</span> result = fut.<span class="kw">await</span>;

        <span class="cmt">// Broadcast the result to all waiting requests</span>
        <span class="kw">let</span> _ = tx.<span class="fn">send</span>(<span class="type">Some</span>(result.<span class="fn">clone</span>()));

        <span class="cmt">// Cleanup the dashmap so future requests will query the DB again if cache expires</span>
        <span class="kw">self</span>.in_flight.<span class="fn">remove</span>(&amp;key);

        result
    }
}</pre>
    </div>
    
    <p>With this architecture, if you wrap your database queries in <code>singleflight.work()</code>, you are structurally immune to cache stampedes. You can survive a massive DDoS of cache misses while keeping your database CPU utilization practically flat.</p>
</section>"""

with open(filepath, 'r') as f:
    content = f.read()

# Replace the section block for caching
pattern = r'<section class="chapter" id="caching">.*?</section>'
content = re.sub(pattern, new_chapter, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Chapter 17 (Caching) expanded successfully.")
