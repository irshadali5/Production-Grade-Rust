import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="auth">
    <div class="chapter-label">Chapter 11</div>
    <h1>Intensive Deep Dive: Cryptographic Timing Attacks & Argon2id</h1>

    <h2>1. The Hardware Reality of Cryptographic Hashing</h2>
    <p>In legacy systems, passwords were hashed using MD5, SHA-1, or SHA-256. These algorithms were designed by the NSA to maximize throughput for data integrity checks. This speed is their fatal flaw when used for authentication. A modern NVIDIA H100 GPU contains over 14,000 CUDA cores. A cluster of these GPUs can calculate hundreds of billions of SHA-256 hashes per second.</p>
    <p>If an attacker exfiltrates your database through an SQL injection, they do not need to "decrypt" the passwords. They will simply run a brute-force dictionary attack against the hashes. Because SHA-256 is purely CPU-bound, the attacker's specialized GPU ASICs will crack 99% of your users' passwords in a matter of hours.</p>

    <h2>2. Memory-Hard Functions: The Argon2id Algorithm</h2>
    <p>To mathematically bankrupt attackers, we must abandon CPU-bound hashing and embrace <strong>Memory-Hard Functions</strong>. We utilize <strong>Argon2id</strong>, the winner of the Password Hashing Competition. Argon2id defeats GPUs not by being mathematically complex, but by monopolizing physical RAM bandwidth.</p>
    <p>The algorithm initializes a massive, customizable block of memory (e.g., a 64 Megabyte matrix). It iteratively fills this memory with pseudorandom data, and then executes highly unpredictable memory reads and writes across the entire block. Because GPUs have thousands of cores but severely limited VRAM (e.g., 80 GB), an attacker can only execute a few hundred concurrent Argon2id hashes before physically running out of memory. By tuning the memory cost parameter in Rust, we completely neutralize multi-million dollar GPU cracking rigs.</p>
    <p>Crucially, Argon2id is a hybrid algorithm. The <code>d</code> variant provides data-independent memory access (defending against side-channel cache attacks), while the <code>i</code> variant provides data-dependent access (defending against ASICs). <code>Argon2id</code> combines both for ultimate security.</p>

    <h2>3. The Physics of Side-Channel Timing Attacks</h2>
    <p>Once a password is hashed, it must be verified against the stored hash in the database. A junior developer will use a standard string comparison: <code>if input_hash == db_hash</code>. This compiles down to the <code>memcmp</code> CPU instruction.</p>
    <p><code>memcmp</code> is optimized for speed. It compares the arrays byte-by-byte from left to right. The absolute microsecond it detects a mismatch (e.g., the first character is wrong), it instantly aborts the loop and returns <code>false</code>. This early-abort optimization introduces a catastrophic cryptographic vulnerability: a <strong>Side-Channel Timing Attack</strong>.</p>
    <p>If the attacker guesses the first character correctly, the CPU must process the second character, which takes slightly longer. An attacker can send 10,000 HTTP requests, measuring the server's response time down to the nanosecond. By performing statistical regression on the network jitter, the attacker can literally guess the password character-by-character based entirely on microscopic fluctuations in CPU latency.</p>

    <h2>4. Constant-Time Bitwise Verification</h2>
    <p>We eliminate this mathematically using <strong>Constant-Time Algorithms</strong> provided by the <code>subtle</code> crate. A constant-time check does not use `if` statements or early returns. It iterates through <em>every single byte</em> of the hash array, performing a bitwise XOR (<code>^</code>) between the input byte and the database byte.</p>
    <p>It accumulates the results using a bitwise OR (<code>|</code>) into a single integer flag. Only at the very end of the loop is the flag evaluated. Whether the attacker guessed 0 characters correctly or 31 characters correctly, the CPU executes the exact same number of instructions, traversing the exact same memory pathways, consuming the exact same number of clock cycles.</p>
    <p>By forcing the execution time to be mathematically identical across all inputs, we physically sever the side-channel, rendering statistical latency analysis utterly useless.</p>
</section>"""

pattern = r'<section class="chapter" id="auth">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 11 applied.")
