# ADR-010: Externalizing Senior Engineering Thinking

## Status

Accepted

## Context

A fundamental challenge in software engineering is that the most valuable architectural thinking—what senior engineers do before writing code—rarely gets documented or shared. As Obie Fernandez describes in his 2025 article "What happens when the coding becomes the least interesting part of the work," this "senior thinking" includes:

- **The Silent Checklist**: Pattern recognition questions that fire before coding begins (What kind of change is this? If this spreads, is that good? What's the blast radius?)
- **The Senior Toolkit**: Instincts for blast radius, sequencing, reversibility, social cost, and false confidence detection
- **Timing and Judgment**: Knowing not just WHAT to build but HOW and WHEN to implement it

This knowledge stays invisible because:
1. When working alone, it remains internal
2. When pairing with other seniors, it's taken for granted
3. When pairing with juniors, only fragments get explained
4. Teams rarely standardize it because it feels boundless and hard to pin down
5. **There is no significant corpus of recorded senior architectural conversations in LLM training data**

Obie notes: "Unless someone goes back in time and secretly records all the pair programming sessions that went on at Thoughtworks and Pivotal Labs and Hashrocket, there's literally no significant corpus/written record of this kind of spoken out loud thinking in existence. (Fuck, it would be so valuable though!)"

This creates a critical problem:
- Junior and mid-level engineers lack access to this thinking
- Organizations can't standardize architectural decision-making
- AI coding agents lack the training data to develop senior judgment
- The industry repeatedly re-learns the same lessons

**The insight**: When you pair program with AI coding agents, you must externalize your architectural thinking—you can't let the AI guess abstraction levels, risk tolerance, or sequencing decisions. This forced externalization makes reasoning visible in ways solo work rarely does.

The AI Software Architect framework is uniquely positioned to capture and systematize this invisible knowledge.

## Decision Drivers

* **Knowledge Capture**: Create a documented corpus of senior architectural thinking that currently doesn't exist
* **Standardization**: Enable teams to share and align on architectural decision-making approaches
* **Training Value**: Provide learning resources for junior engineers and potentially future AI systems
* **Quality Improvement**: Make architectural reasoning explicit and reviewable rather than implicit
* **Framework Evolution**: Enhance our review and ADR processes to systematically capture senior thinking patterns
* **Industry Gap**: Address the lack of documented "senior thinking" that Obie identifies

## Decision

We are enhancing the AI Software Architect framework to **systematically externalize and document senior engineering thinking patterns** that are typically invisible. This positions the framework as not just a tool for individual projects, but as **the corpus of documented senior thinking that the industry lacks**.

**Architectural Components Affected:**
* Review template (`.architecture/templates/review-template.md`)
* ADR template (`.architecture/templates/adr-template.md`)
* Architecture team members (`.architecture/members.yml`)
* Architectural principles (`.architecture/principles.md`)
* Framework documentation and positioning

**Interface Changes:**
* Add "Senior Thinking Checklist" section to review template
* Add "Implementation Strategy" section to ADR template
* Add new "Implementation Strategist" team member
* Add new "Change Impact Awareness" architectural principle
* Update framework documentation to emphasize knowledge capture value

## Consequences

### Positive

* **Creates the missing corpus**: We're building the documented record of senior thinking that Obie says doesn't exist
* **Improves decision quality**: Making reasoning explicit enables review and improvement
* **Accelerates learning**: Junior engineers can study documented architectural reasoning
* **Standardizes practice**: Teams can align on how to think about architectural decisions
* **Enhances framework value**: Positions us as solving a fundamental industry problem
* **Enables AI training**: Potential future value as training data for AI systems that need senior judgment
* **Forced deliberation**: The act of documentation slows thinking enough to catch intuition errors
* **Visible reasoning**: Makes trade-offs and assumptions explicit and debatable
* **Pattern recognition**: Accumulated ADRs and reviews become searchable knowledge base

### Negative

* **Additional documentation overhead**: Reviews and ADRs will take longer to create
* **Learning curve**: Teams need to learn to think in these structured ways
* **Potential analysis paralysis**: Too much structure could slow decision-making
* **Maintenance burden**: More documentation to keep current and relevant
* **Incomplete capture**: Can't capture every nuance of senior thinking in templates

### Neutral

* **Changes team workflows**: Architecture team members must adopt new thinking patterns
* **Expands template size**: Review and ADR templates become more comprehensive
* **Requires discipline**: Teams must commit to thorough documentation practices
* **Evolution over time**: The framework will continue to refine as we learn what works

## Implementation

### Phase 1: Enhance Core Templates

**Review Template Enhancement**
* Add "Senior Thinking Checklist" section before individual reviews
* Include questions about change characterization, spread analysis, blast radius, reversibility, timing/sequencing, social cost, and confidence assessment
* Position this as framing for all subsequent specialist reviews

**ADR Template Enhancement**
* Add "Implementation Strategy" section after Consequences
* Capture blast radius, reversibility, sequencing, social cost, and confidence level
* Make these considerations explicit parts of architectural decisions

### Phase 2: Expand Architecture Team

**Add Implementation Strategist**
* New specialist role focused on HOW and WHEN (not just WHAT)
* Specialties: change sequencing, blast radius analysis, reversibility design, team readiness assessment
* Participates in architecture reviews and ADR creation
* Brings explicit focus to timing and impact concerns

### Phase 3: Update Architectural Principles

**Add Change Impact Awareness Principle**
* Codify blast radius, reversibility, timing, and social cost as explicit architectural concerns
* Provide guidance on evaluating change impact
* Include examples and anti-patterns
* Position alongside existing principles

### Phase 4: Framework Positioning

**Update Documentation**
* Emphasize knowledge capture as core framework value
* Reference Obie's insights about missing senior thinking corpus
* Position framework as solving fundamental industry problem
* Create case studies showing framework capturing valuable architectural reasoning

## Alternatives Considered

### Alternative 1: Keep Templates Simple

**Description**: Maintain current template structure without explicit senior thinking sections

**Pros:**
* Lower overhead for creating reviews and ADRs
* Easier to learn and adopt
* Less risk of analysis paralysis

**Cons:**
* Misses opportunity to capture valuable knowledge
* Doesn't address the fundamental problem Obie identifies
* Framework remains tactical rather than strategic
* Knowledge stays implicit and hard to share

### Alternative 2: Create Separate Senior Thinking Documents

**Description**: Don't modify templates, but create separate documents that capture senior thinking patterns

**Pros:**
* Doesn't burden every review/ADR with additional structure
* Can be optional rather than mandatory
* Allows gradual adoption

**Cons:**
* Senior thinking becomes disconnected from actual decisions
* Easy to skip or forget separate documentation
* Doesn't force externalization at decision time
* Less likely to become standard practice

### Alternative 3: Implement Only Subset of Changes

**Description**: Add some elements (e.g., just blast radius) but not comprehensive senior thinking framework

**Pros:**
* Smaller scope and faster implementation
* Easier to test and refine
* Lower adoption barrier

**Cons:**
* Loses holistic view of senior thinking
* May capture wrong subset of valuable knowledge
* Harder to position framework as comprehensive solution
* Incremental approach may lack coherent narrative

## Validation

**Acceptance Criteria:**
- [x] Review template includes Senior Thinking Checklist section
- [x] ADR template includes Implementation Strategy section
- [x] Implementation Strategist added to members.yml
- [x] Change Impact Awareness added to principles.md
- [ ] All templates tested with real architectural decisions
- [ ] Team trained on using enhanced templates
- [ ] At least 3 ADRs created using new template structure
- [ ] At least 1 architecture review using enhanced template

**Testing Approach:**
* Create test ADRs using new template to validate completeness
* Conduct test architecture review with new checklist
* Gather feedback from framework users on template effectiveness
* Iterate on template structure based on real usage
* Compare quality of decisions made with vs without new sections
* Track time overhead and adjust if excessive

## References

* [Obie Fernandez - What happens when the coding becomes the least interesting part of the work (2025)](https://obie.medium.com/what-happens-when-the-coding-becomes-the-least-interesting-part-of-the-work-ab10c213c660)
* [ADR-002: Pragmatic Guard Mode](.architecture/decisions/adrs/ADR-002-pragmatic-guard-mode.md) - Related concern about preventing over-engineering
* [ADR-005: LLM Instruction Capacity Constraints](.architecture/decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md) - Context for template design
* `.architecture/principles.md` - Existing architectural principles
* `.architecture/members.yml` - Architecture team member definitions
