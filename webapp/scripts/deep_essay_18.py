import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="websockets">
    <div class="chapter-label">Chapter 18</div>
    <h1>Intensive Deep Dive: The C10k Problem & Lock-Free Actor Models</h1>

    <h2>1. The Overhead of HTTP Polling</h2>
    <p>In standard REST architectures, a client requests data, the server responds, and the TCP connection is instantly terminated. If a client requires real-time data (like a live chat or stock ticker), they must implement "Long Polling" or ping the server every second. This introduces an astronomical network overhead. For a 1-byte "No new messages" response, the client and server must execute a full TCP Handshake (SYN, SYN-ACK, ACK), a heavy TLS 1.3 cryptographic key exchange, and HTTP header parsing. At 10,000 users, this polling overhead alone will completely saturate the server's CPU.</p>

    <h2>2. WebSockets and the C10k Problem</h2>
    <p>To eliminate this, we upgrade the connection to <strong>WebSockets</strong> via the <code>Sec-WebSocket-Accept</code> header, establishing a persistent, full-duplex TCP stream. However, holding 10,000 persistent TCP connections open introduces the legendary <strong>C10k Problem</strong>.</p>
    <p>In legacy thread-per-connection servers (like early Apache or Tomcat), handling 10,000 WebSockets required the OS to spawn 10,000 physical threads. The Linux kernel spent 99% of its CPU cycles violently context-switching between threads, leading to extreme latency and memory exhaustion (since each thread reserves a default 2MB stack, 10k threads instantly consume 20GB of RAM).</p>
    <p>We solve this using asynchronous I/O multiplexing. Tokio utilizes the Linux kernel's <code>epoll</code> subsystem. Tokio runs on a single thread (or a small thread pool) that simultaneously monitors all 10,000 file descriptors. When a chat message arrives on socket #4,092, the kernel fires a hardware interrupt, and <code>epoll</code> wakes up the specific Tokio task assigned to that socket. We can effortlessly manage 10 million WebSockets on a standard server.</p>

    <h2>3. The Actor Model and MPSC Queues</h2>
    <p>Holding the connections is easy; routing messages between them is terrifyingly difficult. If User A wants to send a chat message to User B, the Rust thread handling User A must find User B's socket and write to it. If we store all 10,000 sockets in a global <code>std::sync::Mutex</code>, User A will lock the entire server just to send one message. All other 9,999 users will be physically blocked from communicating until the lock is released.</p>
    <p>We eliminate Mutex contention entirely using the <strong>Actor Model</strong>. We do not share state; we share memory by communicating. Every connected WebSocket is assigned an "Actor"—an isolated Tokio task. We create an asynchronous MPSC (Multi-Producer, Single-Consumer) channel for every user.</p>
    <p>We store the <code>Sender</code> half of the channel in a lock-free concurrent hash map (like <code>DashMap</code>). When User A messages User B, User A retrieves User B's <code>Sender</code> and drops the message into the channel. User A immediately resumes their work. User B's Actor independently consumes messages from the <code>Receiver</code> half of the channel and writes them sequentially to its own TCP socket.</p>
    <p>By relying entirely on lock-free message passing, we guarantee that no two users will ever block each other, allowing the chat server to scale perfectly linearly across all physical CPU cores.</p>
</section>"""

pattern = r'<section class="chapter" id="websockets">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 18 applied.")
