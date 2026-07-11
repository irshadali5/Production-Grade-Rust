import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="security">
    <div class="chapter-label">Chapter 23</div>
    <h1>Intensive Deep Dive: Elliptic Curve Diffie-Hellman & Perfect Forward Secrecy</h1>

    <h2>1. The Myth of the Internal Network</h2>
    <p>In standard microservice architectures, developers secure the perimeter using a WAF (Web Application Firewall) and TLS 1.2, but send internal traffic (e.g., from the API Gateway to the billing service) in plain text over the internal VPC. This is a catastrophic architectural flaw known as the "Soft Center." If a single internal server is compromised (perhaps via a vulnerable dependency), the attacker can deploy a packet sniffer and passively intercept all plain-text HTTP traffic, stealing database credentials and user sessions.</p>
    <p>A true production-grade system enforces <strong>Zero-Trust Networking</strong>. Every single internal microservice must communicate using End-to-End Encryption (E2EE) at the application layer, completely distrusting the physical network.</p>

    <h2>2. The Mathematics of Elliptic Curve Diffie-Hellman (ECDH)</h2>
    <p>To establish a secure cryptographic channel over a compromised network, we cannot simply send a password. The attacker sniffing the network would instantly steal it. We must use the <strong>Elliptic Curve Diffie-Hellman (ECDH)</strong> protocol.</p>
    <p>Both Rust microservices generate their own Private Key (a massive random integer). They then mathematically derive a Public Key by multiplying a known base point on a mathematical Elliptic Curve (such as <code>Curve25519</code>) by their Private Key. They exchange these Public Keys in plain text over the compromised network.</p>
    <p>Microservice A multiplies its Private Key with Microservice B's Public Key. Microservice B multiplies its Private Key with Microservice A's Public Key. Due to the commutative mathematical properties of Elliptic Curves, both calculations result in the exact same <strong>Shared Secret</strong>. The attacker, who intercepted the public keys, cannot calculate the Shared Secret. To do so, they would have to calculate the Discrete Logarithm of the Elliptic Curve—a mathematical operation that would take modern supercomputers billions of years.</p>

    <h2>3. The Catastrophe of Static Keys and Perfect Forward Secrecy (PFS)</h2>
    <p>If Microservice A and Microservice B use static, long-lived Private Keys to derive their Shared Secret, the system remains vulnerable. An attacker can deploy a packet sniffer and silently record 5 years of encrypted ciphertext. If the attacker eventually hacks the server in year 6 and steals the static Private Key, they can retroactively decrypt all 5 years of historical traffic.</p>
    <p>We completely eliminate this vulnerability by enforcing <strong>Perfect Forward Secrecy (PFS)</strong>. Our Rust microservices never use static keys for encryption. They generate completely new, <strong>Ephemeral Elliptic Curve Keypairs</strong> for <em>every single network session</em>.</p>
    <p>Once the TCP session concludes, the ephemeral Private Keys are cryptographically zeroized from RAM (using the <code>secrecy</code> crate). The keys literally cease to exist. Even if the attacker compromises the physical server the very next day and extracts the NVMe hard drives and RAM chips, they cannot decrypt the historical traffic, because the keys physically no longer exist anywhere in the universe.</p>
</section>"""

pattern = r'<section class="chapter" id="security">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 23 applied.")
