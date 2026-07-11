import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="k8s">
    <div class="chapter-label">Chapter 28</div>
    <h1>Intensive Deep Dive: Control Plane Physics & `cgroups`</h1>

    <h2>1. The Illusion of the Pod</h2>
    <p>Kubernetes (K8s) is the apex of distributed container orchestration, but to truly understand it, you must understand the Linux Kernel. A Kubernetes "Pod" does not physically exist. A Pod is not a Virtual Machine. It has no hardware boundaries.</p>
    <p>A Pod is a mathematical illusion maintained by the kernel using <strong>Linux Namespaces</strong>. When the Kubelet starts a Rust binary, it isolates it using namespaces. The <code>PID</code> namespace intercepts all system calls and lies to the binary, telling it that it is Process ID 1. The <code>Network</code> namespace assigns the binary a virtual ethernet device (<code>veth</code>) with its own isolated IP address. The Rust application believes it is running on a dedicated server, but it is actually just a heavily restricted process sharing the host's kernel.</p>
    
    <h2>2. Resource Exhaustion and `cgroups v2`</h2>
    <p>If the Rust application suffers a memory leak and attempts to consume all 128GB of the physical server's RAM, it would crash every other Pod on the node. The Kubelet prevents this using <strong>cgroups v2 (Control Groups)</strong>.</p>
    <p>The Kubelet creates a strict mathematical boundary in the kernel's memory controller for that specific Pod's Process Tree. If you set a Kubernetes memory limit of 500MB, the kernel monitors every single page of RAM allocated by your Rust process. The absolute microsecond the application attempts to allocate 500MB + 1 byte, the kernel's OOM Killer physically terminates the process with extreme prejudice. This guarantees mathematical isolation of resources.</p>

    <h2>3. The Reconciliation Loop State Machine</h2>
    <p>The core genius of Kubernetes is the Control Plane (the API Server, Controller Manager, and <code>etcd</code>). It does not operate via imperative commands (like "deploy this app"). It operates as a continuous, asynchronous state machine known as the <strong>Reconciliation Loop</strong>.</p>
    <p>You provide a declarative YAML file representing the <strong>Desired State</strong> (e.g., "I want exactly 5 replicas of the Rust API"). The Controller Manager constantly queries the <code>etcd</code> database to determine the <strong>Actual State</strong>. If a physical EC2 instance catches fire and dies, the Actual State drops to 3 replicas.</p>
    <p>The Controller calculates the mathematical delta between Desired (5) and Actual (3). It then immediately executes commands to force reality to match the desired state by scheduling 2 new Pods onto healthy nodes. By relying entirely on asynchronous state reconciliation instead of imperative commands, K8s achieves absolute, mathematically robust self-healing.</p>
</section>"""

pattern = r'<section class="chapter" id="k8s">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 28 applied.")
