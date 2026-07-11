import re

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

essay = """<section class="chapter" id="setup">
    <div class="chapter-label">Chapter 01</div>
    <h1>Expert Toolchain: Nix Flakes, LLVM, & mold</h1>

    <h2>1. The Catastrophe of Imperative Environments</h2>
    <p>Before writing a single line of Rust code, we must architect the environment in which that code compiles. The industry standard approach for onboarding a new engineer is an imperative document, often titled <code>README.md</code> or <code>setup.sh</code>. This document typically contains a sequence of state-mutating commands:</p>
    <ul>
        <li><code>curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh</code></li>
        <li><code>sudo apt-get install libpq-dev openssl-dev</code></li>
        <li><code>cargo install sqlx-cli</code></li>
    </ul>
    <p>This imperative model is the root cause of the "Works on My Machine" anti-pattern, a catastrophic failure mode in distributed engineering teams. When Developer A runs this script on January 1st, they download Rust version 1.75. When Developer B joins the team and runs the exact same script on June 1st, they download Rust version 1.79. Furthermore, Developer A is running Ubuntu 22.04 with an outdated version of OpenSSL, while Developer B is running macOS Sonoma using Homebrew's edge-release OpenSSL.</p>
    <p>When the application compiles flawlessly for Developer A but fails to link against the cryptography library for Developer B, the engineering team loses days of velocity attempting to debug the divergence. In a production-grade system, the development environment cannot be an implicit, shifting state. It must be a pure, mathematical function.</p>

    <h2>2. Functional Package Management: The Nix Paradigm</h2>
    <p>To eliminate environmental divergence, we abandon imperative scripts and adopt <strong>Nix</strong>. Nix is a purely functional package manager. It treats packages and environments exactly like functions in a purely functional programming language (such as Haskell). If a function's inputs are identical, its output is guaranteed to be mathematically identical, regardless of when or where it is executed.</p>
    <p>In the Nix ecosystem, every single dependency—ranging from the Rust compiler itself down to the specific version of <code>glibc</code> and the bash shell used during compilation—is declared as an input. Nix calculates a cryptographic hash (typically SHA-256) of this entire dependency graph. The resulting binary is stored in the <code>/nix/store</code> under a directory named after this hash (e.g., <code>/nix/store/a4b3c2d1...-rustc-1.80.0</code>).</p>
    <p>Because Nix components are strictly isolated by their cryptographic hashes, they cannot conflict. You can have 50 different versions of OpenSSL installed on the same machine, and Nix will surgically link your Rust project to the exact byte-for-byte version you specified in your configuration.</p>

    <h2>3. Nix Flakes: Hermetic Reproducibility</h2>
    <p>While classic Nix is powerful, it still relied on global channels (like <code>nixpkgs-unstable</code>), which could mutate over time. To achieve absolute, hermetic reproducibility, we utilize <strong>Nix Flakes</strong>. A Flake explicitly pins the exact git revision of the Nix package repository (e.g., <code>nixpkgs</code>) in a <code>flake.lock</code> file. This guarantees that 10 years from now, executing the flake will result in the exact same binary environment.</p>

    <h3>3.1 Constructing the Flake</h3>
    <p>Below is the complete implementation of a production-grade <code>flake.nix</code>. This flake utilizes the <code>fenix</code> overlay, which allows us to declaratively specify a Rust toolchain directly from Mozilla's upstream repositories without relying on <code>rustup</code>. We also inject <code>mold</code>, <code>clang</code>, and Postgres dependencies directly into the shell.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">flake.nix</span><span class="code-lang">nix</span></div>
    <pre><span class="cmt"># flake.nix</span>
{
  description = "Production-Grade Rust Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    fenix = {
      url = "github:nix-community/fenix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, fenix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        
        <span class="cmt"># We utilize fenix to parse a standard rust-toolchain.toml file.</span>
        <span class="cmt"># This provides a bridge for developers who haven't installed Nix yet,</span>
        <span class="cmt"># allowing them to still use rustup locally while Nix users get the pure environment.</span>
        toolchain = fenix.packages.${system}.fromToolchainFile {
          file = ./rust-toolchain.toml;
          <span class="cmt"># The SHA256 hash guarantees the toolchain download is never tampered with.</span>
          sha256 = "sha256-s1MutIG0IMZ423CjeA...";
        };
      in
      {
        devShells.default = pkgs.mkShell {
          <span class="cmt"># buildInputs defines the packages available in the isolated environment</span>
          buildInputs = with pkgs; [
            toolchain
            mold        <span class="cmt"># Modern linker for sub-second compilation</span>
            clang       <span class="cmt"># Required for linking C-dependencies</span>
            pkg-config  <span class="cmt"># Used by build.rs scripts to find C-libraries</span>
            openssl     <span class="cmt"># Cryptographic primitives</span>
            postgresql  <span class="cmt"># For the sqlx CLI</span>
          ];

          <span class="cmt"># shellHook executes immediately upon entering the environment</span>
          shellHook = ''
            export RUST_BACKTRACE=1
            export LD_LIBRARY_PATH=${pkgs.openssl.out}/lib:$LD_LIBRARY_PATH
            echo "Entering Hermetic Rust Environment. Powered by Nix."
          '';
        };
      }
    );
}</pre></div>

    <p>To enter this environment, a developer simply runs <code>nix develop</code> in their terminal. Nix will automatically parse the <code>flake.lock</code>, download the exact cryptographic revisions of every package, build them in isolated sandboxes, and drop the developer into a bash shell where <code>cargo</code> and <code>rustc</code> are mapped perfectly.</p>

    <h2>4. The Rust Compilation Pipeline and LLVM</h2>
    <p>Once our environment is perfectly stable, we must understand how our code is actually converted into machine instructions. The Rust compiler (<code>rustc</code>) does not directly emit assembly language for your Intel or ARM CPU. It is a frontend architecture that relies heavily on <strong>LLVM (Low Level Virtual Machine)</strong>.</p>
    
    <h3>4.1 AST, HIR, and MIR</h3>
    <p>When you execute <code>cargo build</code>, the compiler parses your raw text files into an <strong>Abstract Syntax Tree (AST)</strong>. It then lowers this AST into the <strong>High-Level Intermediate Representation (HIR)</strong>, where type inference and trait resolution occur. Finally, it lowers the HIR into the <strong>Mid-Level Intermediate Representation (MIR)</strong>.</p>
    <p>MIR is arguably the most important stage of Rust compilation. It is a Control Flow Graph (CFG) where all complex Rust syntax (like <code>for</code> loops and <code>match</code> statements) has been desugared into basic blocks and <code>goto</code> jumps. It is within the MIR that the infamous <strong>Borrow Checker</strong> operates. By analyzing the flow of data across the MIR basic blocks, the Borrow Checker mathematically proves that no references outlive their underlying data and that no mutable references alias each other.</p>
    
    <h3>4.2 LLVM IR and Optimization Passes</h3>
    <p>Once the MIR is proven safe, <code>rustc</code> translates it into <strong>LLVM IR (Intermediate Representation)</strong>. LLVM IR is a highly typed, SSA (Static Single Assignment) assembly language. This IR is passed to the LLVM backend, which performs aggressive optimization passes.</p>
    <p>LLVM will unroll loops, inline function calls, dead-code eliminate branches that are mathematically proven to be unreachable, and vectorize mathematical operations using CPU SIMD instructions (like AVX-512). The output of the LLVM backend is a collection of object files (<code>.o</code>), containing the raw machine code instructions for your specific CPU architecture.</p>

    <h2>5. The Linker Bottleneck: Why We Use `mold`</h2>
    <p>Generating the object files is highly parallelizable. If your Rust workspace has 50 crates, the compiler can spawn 50 threads and instruct LLVM to generate object files for each crate simultaneously. The true performance bottleneck occurs in the final step: <strong>Linking</strong>.</p>

    <h3>5.1 The Sequential Nature of GNU `ld`</h3>
    <p>The linker must take thousands of independent object files and stitch them together into a single executable binary. It must parse the symbol tables of each object file and resolve external references. If Crate A calls a function in Crate B, the linker must calculate the exact memory address of the function in Crate B and inject that address into the machine code of Crate A.</p>
    <p>The default GNU linker (<code>ld</code>) was designed decades ago. It performs this symbol resolution sequentially on a single thread. For massive Rust monorepos, this sequential linking phase can take upwards of 15 to 30 seconds. This completely destroys the developer feedback loop. A developer changes a single line of code, compiles, and sits idle for 30 seconds waiting for the linker.</p>

    <h3>5.2 Sub-second Linking with `mold`</h3>
    <p>To restore developer velocity, we swap the default linker for <code>mold</code>. Created by Rui Ueyama (the original author of the LLVM <code>lld</code> linker), <code>mold</code> is a modern, mathematically optimized linker designed specifically for massively parallel multi-core systems.</p>
    <p>Instead of processing object files sequentially, <code>mold</code> utilizes a highly optimized thread-pool. It maps the object files directly into memory using <code>mmap</code>, parses the symbol tables concurrently, and uses lock-free hash tables to resolve symbol references. By saturating all available CPU cores, <code>mold</code> can link multi-gigabyte Rust binaries in mere milliseconds.</p>

    <h3>5.3 Configuring Cargo for `mold`</h3>
    <p>To instruct Cargo to use <code>mold</code>, we do not need to alter our source code. We simply modify the global Cargo configuration file (<code>.cargo/config.toml</code>) at the root of our workspace.</p>

    <div class="code-block"><div class="code-header"><span class="code-filename">.cargo/config.toml</span><span class="code-lang">toml</span></div>
    <pre><span class="cmt"># Force cargo to use the mold linker via clang</span>
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

[target.aarch64-apple-darwin]
<span class="cmt"># Apple Silicon uses zld or lld natively, but mold (sold) is available</span>
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

<span class="cmt"># Enable incremental compilation for faster iteration</span>
[build]
incremental = true</pre></div>

    <p>By combining the hermetic reproducibility of Nix Flakes with the sub-second linking speed of <code>mold</code>, we construct a development toolchain that is mathematically immune to environmental divergence and operates at the absolute physical limits of compilation speed. This is the foundation upon which we will build our production system.</p>
</section>"""

pattern = r'<section class="chapter" id="setup">.*?</section>'
content = re.sub(pattern, essay, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Deep Essay expansion applied to Chapter 01.")
