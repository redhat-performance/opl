# ADR-009: Script-Based Deterministic Operations

## Status

Accepted

## Context

Our Claude Skills currently implement all logic as instructions in SKILL.md that guide the LLM to construct bash commands or perform operations. For deterministic operations (tasks with single correct output), this approach has limitations:

**Current Pattern (LLM-Interpreted):**
```markdown
### 2. Generate ADR Number
```bash
# Find highest ADR number
ls .architecture/decisions/adrs/ | grep -E "^ADR-[0-9]+" | sed 's/ADR-//' | sed 's/-.*//' | sort -n | tail -1
```
New ADR = next sequential number
```

**Limitations:**
- **Non-deterministic**: LLM might construct command differently each time
- **Not Testable**: Can't unit test instructions
- **Error-Prone**: LLM might make syntax errors in command construction
- **Duplication**: Same logic pattern repeated across skills
- **No Reusability**: Can't share logic between skills

**Deterministic Operations in Our Skills:**
1. ADR numbering (`create-adr`) - scan directory, find highest number, increment
2. Member listing (`list-members`) - parse YAML, format output
3. Version parsing (`architecture-review`, `specialist-review`) - validate and sanitize version numbers
4. Filename sanitization (multiple skills) - remove dangerous characters, apply kebab-case
5. File scanning (`architecture-status`) - count ADRs, list reviews, check directories

The [First Principles Deep Dive to Claude Agent Skills](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) documents using `/scripts/` directories for deterministic operations, providing:
- **Reliability**: Executable code with predictable behavior
- **Testability**: Unit tests for scripts
- **Reusability**: Scripts callable from multiple skills
- **Security**: Input validation at script entry point

Our architecture review identified this as an **enhancement opportunity** with recommendation to defer until we have 3+ scripts to justify infrastructure.

## Decision Drivers

* **Reliability**: Deterministic operations should produce consistent results
* **Testability**: Should be able to unit test logic
* **Security**: Script-based input validation reduces injection risks
* **Reusability**: Common operations shared across skills
* **Pragmatic Threshold**: Only adopt when 3+ scripts justify infrastructure
* **Deferred Implementation**: Not urgent; current approach works

## Decision

**We will adopt script-based deterministic operations when we have 3+ candidates, starting with ADR numbering as the first script.**

**Implementation will be deferred until triggered by one of:**
- Bash command construction causes bugs
- ADR numbering conflicts occur
- Third deterministic operation identified

**Script Infrastructure:**
```
.claude/skills/scripts/           # Shared script library
├── next-adr-number.sh           # Find next ADR number
├── parse-members.py             # Parse members.yml
├── sanitize-filename.sh         # Filename sanitization
├── validate-version.sh          # Version number validation
└── tests/                       # Unit tests
    ├── test-adr-numbering.sh
    ├── test-members-parser.py
    └── test-sanitization.sh
```

**Usage Pattern:**
Skills reference scripts via relative paths using `{baseDir}` placeholder (once progressive disclosure is adopted) or direct paths from skill location.

**Example (create-adr skill):**
```markdown
### 2. Generate ADR Number
```bash
{baseDir}/scripts/next-adr-number.sh
```
```

**Script Requirements:**
1. Accept sanitized inputs as arguments
2. Validate inputs at entry point
3. Return predictable output (stdout)
4. Exit with appropriate codes (0 = success, non-zero = error)
5. Include inline documentation
6. Have corresponding unit tests

**Architectural Components Affected:**
* `.claude/skills/scripts/` (new directory)
* Skills using deterministic operations (create-adr, list-members, architecture-status)
* `_patterns.md` (document script pattern)

**Interface Changes:**
* Skills call scripts via Bash tool instead of constructing commands
* Script output parsed and processed by skill logic
* No change to skill invocation or user-facing behavior

## Consequences

### Positive

* **Reliability**: Deterministic operations produce consistent results
* **Testability**: Unit tests validate script behavior
* **Reusability**: Scripts shared across multiple skills
* **Security**: Input validation centralized in scripts
* **Maintainability**: Script logic easier to modify than SKILL.md instructions
* **Debugging**: Script failures easier to diagnose than LLM command construction issues

### Negative

* **Infrastructure Overhead**: Need test framework and CI integration
* **Runtime Dependencies**: Python scripts require Python runtime
* **Complexity**: Multi-language skill implementation (Markdown + Bash + Python)
* **Learning Curve**: Contributors must understand when to use scripts vs. instructions
* **Development Overhead**: Writing and testing scripts takes longer than inline instructions

### Neutral

* **Not Universal**: Only deterministic operations become scripts; most skill logic remains instructional
* **Gradual Adoption**: Extract scripts as need emerges
* **Language Mix**: Bash for simple ops, Python for complex parsing

## Implementation

**Phase 1: Deferred Until Triggered (TBD)**

**Trigger Conditions (any one):**
1. Bash command construction causes bugs in production use
2. ADR numbering conflicts occur (race conditions, incorrect numbering)
3. Third deterministic operation identified (beyond ADR numbering and member parsing)
4. Security concern with command construction identified

**When Triggered:**

1. **Create script infrastructure**
   ```bash
   mkdir -p .claude/skills/scripts/tests
   ```

2. **Implement first script** (`next-adr-number.sh`)
   ```bash
   #!/bin/bash
   # Find next ADR number in .architecture/decisions/adrs/
   # Usage: next-adr-number.sh [path-to-adrs-dir]
   # Returns: Next ADR number (formatted as 3 digits)

   ADRS_DIR="${1:-.architecture/decisions/adrs}"

   # Validate directory exists
   if [ ! -d "$ADRS_DIR" ]; then
     echo "Error: ADR directory not found: $ADRS_DIR" >&2
     exit 1
   fi

   # Find highest ADR number
   highest=$(ls "$ADRS_DIR" | grep -E "^ADR-[0-9]+" | \
             sed 's/ADR-//' | sed 's/-.*//' | \
             sort -n | tail -1)

   # Default to 000 if no ADRs exist
   if [ -z "$highest" ]; then
     echo "001"
   else
     # Increment and format
     next=$((highest + 1))
     printf "%03d" $next
   fi
   ```

3. **Add unit tests**
   ```bash
   #!/bin/bash
   # tests/test-adr-numbering.sh

   # Test: Empty directory returns 001
   # Test: Existing ADR-001 returns 002
   # Test: Gaps in numbering (ADR-001, ADR-003) returns 004
   # Test: Non-existent directory errors appropriately
   ```

4. **Update create-adr skill** to use script

5. **Document pattern** in `_patterns.md`

**Phase 2: Expand Script Library (When 3+ Scripts Exist)**

1. Implement additional scripts (member parsing, filename sanitization)
2. Add comprehensive test suite
3. Integrate with CI/CD if available
4. Document script API in `_patterns.md`

**Phase 3: Standardize (When 5+ Scripts Exist)**

1. Create script development guide
2. Establish code review checklist for scripts
3. Consider script versioning if needed

## Alternatives Considered

### Alternative 1: Keep All Logic as LLM Instructions

**Pros:**
* No infrastructure overhead
* No runtime dependencies
* Consistent skill implementation
* Simpler mental model

**Cons:**
* Non-deterministic behavior for deterministic operations
* Not testable
* Security concerns with command construction
* Duplication across skills

**Verdict:** Rejected - reliability and testability concerns outweigh simplicity

### Alternative 2: Implement Script Library Immediately

**Pros:**
* Proactive reliability improvement
* Establish pattern before habits form
* Comprehensive testing from start

**Cons:**
* Premature infrastructure (only 1-2 candidates currently)
* No validated need - current approach working
* Development overhead without proven value
* Violates pragmatic principles (YAGNI)

**Verdict:** Rejected - wait for trigger conditions to validate need

### Alternative 3: Use MCP Tools Instead of Scripts

Model Context Protocol tools could provide deterministic operations.

**Pros:**
* Leverages existing MCP infrastructure
* Type-safe interfaces
* Better integration with Claude Code

**Cons:**
* Tighter coupling to MCP server
* More complex development (TypeScript/Node.js)
* Heavier weight than simple scripts
* Skills become less portable

**Verdict:** Rejected - scripts are simpler and more portable; MCP tools better suited for framework operations not skill helpers

## Pragmatic Enforcer Analysis

**Reviewer**: Pragmatic Enforcer
**Mode**: Strict

**Overall Decision Complexity Assessment**:
This is a textbook case of appropriate deferral. The decision recognizes that script infrastructure has value BUT waits for proven need before implementing. The trigger conditions are concrete and evidence-based.

**Decision Challenge**:

**Proposed Decision**: "Defer script-based operations until 3+ candidates exist or problems emerge with current approach"

**Necessity Assessment**: 3/10
- **Current need**: Minimal - current approach working without issues
- **Future need**: Likely if skills scale, but uncertain timeline
- **Cost of waiting**: Low - can implement when problems actually occur
- **Evidence of need**: Zero bugs, zero conflicts, zero security incidents with current approach

**Complexity Assessment**: 6/10
- **Added complexity**: Test infrastructure, multi-language codebase, script maintenance
- **Maintenance burden**: Must maintain scripts, tests, and CI integration
- **Learning curve**: Contributors must know when to script vs. instruct
- **Dependencies introduced**: Python runtime, bash, test frameworks

**Alternative Analysis**:
- "Keep instructions" considered (too conservative given reliability benefits)
- "Implement immediately" considered (premature given no validated need)
- "Use MCP tools" considered (overengineered)

Decision correctly balances these alternatives with deferred implementation.

**Simpler Alternative Proposal**:
**Maintain Current Approach Until Problems Emerge** (which is what decision proposes).

The decision is ALREADY the pragmatic approach. This is how YAGNI should be applied:
1. Recognize potential future value
2. Document the pattern
3. Wait for trigger conditions
4. Implement when justified

No further simplification needed.

**Recommendation**: ✅ **Approve decision with strong endorsement**

**Justification**:
This is exemplary pragmatic engineering. The decision:
- Acknowledges script benefits WITHOUT prematurely implementing
- Sets concrete trigger conditions (3+ scripts, bugs, conflicts)
- Documents pattern for future reference
- Defers infrastructure until proven necessary

**Trigger Monitoring**: Watch for:
- ADR numbering bugs or conflicts
- Command construction errors
- Third deterministic operation candidate
- Security concerns with bash construction

**Pragmatic Score**:
- **Necessity**: 3/10 (not needed now)
- **Complexity**: 6/10 (moderate infrastructure)
- **Ratio**: 2.0 *(Target: <1.5 for strict mode - OVER threshold, confirming deferral is correct)*

**Overall Assessment**:
**Appropriately deferred**. This decision demonstrates mature engineering judgment: recognizing a good pattern while acknowledging it's not needed yet. The ratio of 2.0 confirms complexity outweighs necessity at present. Implement when triggers fire.

## Validation

**Acceptance Criteria (When Implementation Triggered):**

- [ ] Trigger condition met (documented which one)
- [ ] `.claude/skills/scripts/` directory created
- [ ] At least one script implemented with tests
- [ ] Script successfully used by skill
- [ ] Tests pass in CI (if available) or locally
- [ ] Pattern documented in `_patterns.md`
- [ ] No regression in skill functionality

**Testing Approach (When Implemented):**
1. **Unit Tests**: Test scripts with various inputs (normal, edge cases, errors)
2. **Integration Tests**: Invoke skills using scripts, verify end-to-end behavior
3. **Security Tests**: Attempt injection attacks on script inputs
4. **Performance Tests**: Ensure scripts don't introduce latency
5. **Portability Tests**: Verify scripts work on macOS, Linux, Windows (if applicable)

## References

* [Claude Skills Deep Dive Comparison](../../comparisons/claude-skills-deep-dive-comparison.md)
* [Claude Skills Deep Dive Takeaways](../../comparisons/claude-skills-takeaways.md)
* [First Principles Deep Dive to Claude Agent Skills](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) (External)
* [ADR-007: Tool Permission Restrictions for Claude Skills](./ADR-007-tool-permission-restrictions-for-skills.md)
* [ADR-008: Progressive Disclosure Pattern for Large Skills](./ADR-008-progressive-disclosure-pattern-for-large-skills.md)

---

**Decision Date**: 2025-12-04
**Approved By**: Pragmatic Enforcer (Champion), Security Specialist, Maintainability Expert
**Implementation Target**: Deferred - trigger conditions will determine timing
