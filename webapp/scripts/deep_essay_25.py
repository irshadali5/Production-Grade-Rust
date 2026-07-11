import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="iac">
    <div class="chapter-label">Chapter 25</div>
    <h1>Intensive Deep Dive: Directed Acyclic Graphs & Terraform State Locking</h1>

    <h2>1. The Fallacy of Imperative Infrastructure Scripts</h2>
    <p>Junior DevOps engineers often manage cloud infrastructure using bash scripts containing AWS CLI commands (e.g., <code>aws ec2 run-instances</code>). This imperative approach guarantees catastrophic state divergence. If a script fails halfway through, the infrastructure is left in a corrupted, intermediate state. Running the script a second time will attempt to create duplicate VPCs and subnets, leading to fatal CIDR block collisions.</p>

    <h2>2. Declarative State Machines & The DAG</h2>
    <p>A hyperscale system must treat infrastructure as a declarative state machine using Infrastructure as Code (IaC) tools like Terraform. You define the <strong>Desired State</strong> in HashiCorp Configuration Language (HCL). When you run <code>terraform apply</code>, Terraform parses your HCL into an Abstract Syntax Tree (AST).</p>
    <p>It then mathematically compares this Desired State against the <strong>State File</strong> (a JSON representation of the actual reality in AWS). It constructs a <strong>Directed Acyclic Graph (DAG)</strong> of the differences. The DAG calculates the exact topological execution order (e.g., it mathematically proves that a VPC must be created before the Subnet, and the Subnet before the EC2 instance). Terraform then traverses this DAG, executing the API calls with maximum concurrency.</p>

    <h2>3. The Distributed State Lock</h2>
    <p>If two DevOps engineers run <code>terraform apply</code> at the exact same millisecond, they will both generate conflicting DAGs. They will bombard the AWS API simultaneously, creating duplicate resources and permanently corrupting the State File.</p>
    <p>We eliminate this using a <strong>Distributed State Lock</strong> (typically via a DynamoDB table). Before Terraform even begins to analyze the DAG, it attempts to acquire a cryptographic lock in DynamoDB. If Engineer A acquires the lock, Engineer B's terminal instantly blocks. Terraform guarantees that infrastructure mutation is a mathematically serialized, single-threaded operation at the global cluster level, preventing race conditions in cloud provisioning.</p>
</section>"""

pattern = r'<section class="chapter" id="iac">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Intensive Deep Essay 25 applied.")
