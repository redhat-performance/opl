# Architecture Review: "Implement as Architects" Command with Configuration

**Review Type**: Feature Review
**Date**: 2025-11-20
**Status**: In Progress
**Reviewers**: Systems Architect, Domain Expert, Security Specialist, Maintainability Expert, Performance Specialist, AI Engineer, Pragmatic Enforcer

## Executive Summary

This review examines adding an "Implement as the architects" command to the AI Software Architect framework, backed by configuration that specifies implementation methodology, coding influences, and practices.

**User Workflow:**
```
User: "Implement the authentication feature as the architects"
AI: (reads .architecture/config.yml implementation section)
AI: (applies TDD, follows Sandi Metz/Kent Beck/Jeremy Evans practices)
AI: (implements with configured methodology automatically)
```

**Key Finding**: This is a **configuration feature** following the existing `pragmatic_mode` pattern, not a documentation system. Simple addition to config.yml with command recognition.

**Complexity Assessment**: Low - follows established patterns in the framework.

---

## Context & Problem Statement

### Current User Workflow

The user currently types detailed prompts:

> "Implement the next steps iteratively as the software architects, specifically the pragmatic enforcer. Follow TDD taking inspiration from Gary Bernhardt (from Destroy All Software). Refactor as needed following best-practices taking inspiration from Sandi Metz, Kent Beck, and Martin Fowler. Glean ruby design inspiration from Jeremy Evans and Vladimir Dementyev."

**Pain Points:**
- Repetitive: Same guidance every implementation session
- Verbose: Long prompt for simple request
- Inconsistent: Might forget to mention key influences
- No persistence: Preferences lost between sessions

### Desired Workflow

**Simple command:**
```
"Implement X as the architects"
```

**AI behavior:**
1. Recognizes "implement as the architects" pattern
2. Reads `.architecture/config.yml` implementation section
3. Applies configured methodology (e.g., TDD)
4. References configured influences (e.g., Sandi Metz, Kent Beck)
5. Uses language-specific practices (e.g., Ruby idioms per Jeremy Evans)
6. Implements feature with full context automatically

### Configuration Levels

**Global Level** (User's ~/.architecture/config.yml or similar)
- User's personal preferences across all projects
- Default methodology (TDD, BDD, etc.)
- Favorite influencers and practices
- Language-specific defaults

**Project Level** (Project's .architecture/config.yml)
- Project-specific overrides
- Team methodology decisions
- Project tech stack influences
- Quality standards for this project

**Inheritance:**
```
Global Config → Project Config → Command
(User defaults) → (Project overrides) → (Explicit request)
```

### Comparison to Existing Pattern

This follows the **pragmatic_mode** pattern:

**Existing: pragmatic_mode**
```yaml
pragmatic_mode:
  enabled: true
  intensity: balanced
  apply_to:
    individual_reviews: true
```

**New: implementation**
```yaml
implementation:
  enabled: true
  methodology: "TDD"
  influences:
    methodology: [...]
    design: [...]
```

Same structure, same file, same pattern.

---

## Feature Requirements

### Functional Requirements

**FR-1: Command Recognition**
- Recognize "Implement X as the architects"
- Recognize "Implement as the architects" (referring to prior context)
- Recognize "Implement X" (if implementation mode enabled by default)
- Work across all AI assistants (via AGENTS.md)

**FR-2: Configuration Structure**
- Add `implementation:` section to config.yml
- Support methodology selection (TDD, BDD, DDD, etc.)
- Support influences list (grouped by focus area)
- Support language-specific practices
- Support quality standards

**FR-3: Configuration Inheritance**
- Global config (user level) - if supported
- Project config (overrides global)
- Explicit command (overrides config)

**FR-4: Integration with Architecture Members**
- Option to specify which architect perspective (pragmatic_enforcer, maintainability_expert, etc.)
- Default: Use methodology + influences from config
- Override: "Implement X as [specific architect]"

**FR-5: Methodology Application**
- TDD: Write tests first, red-green-refactor
- BDD: Behavior-focused tests, outside-in
- DDD: Domain modeling, bounded contexts
- Test-Last: Implementation first, tests after
- Other: User-defined approaches

**FR-6: Cross-Assistant Compatibility**
- Configuration in AGENTS.md (cross-platform)
- Enhanced in CLAUDE.md (Claude-specific)
- Works with Cursor, Copilot, etc.

### Non-Functional Requirements

**NFR-1: Simplicity**: Single configuration section, clear structure
**NFR-2: Backward Compatibility**: Existing projects unaffected
**NFR-3: Optional**: Projects can opt out or not configure
**NFR-4: Discoverable**: Clear documentation in AGENTS.md
**NFR-5: Flexible**: Support any methodology, not just common ones
**NFR-6: Maintainable**: Easy to update as preferences evolve

---

## Individual Architecture Member Reviews

### 🏗️ Systems Architect Review

**Focus**: System coherence and integration points

#### Analysis

**Architectural Pattern**: Configuration-Driven Behavior

This follows the framework's existing pattern:
```
User Command → Config Lookup → Behavior Application
```

Similar to:
- `pragmatic_mode.enabled` → Pragmatic Enforcer participates
- `implementation.enabled` → Implementation guidance applied

**Integration Points:**

1. **config.yml**: New section added
2. **CLAUDE.md**: Command recognition
3. **AGENTS.md**: Cross-platform documentation
4. **Recalibration**: Can reference implementation config
5. **Members.yml**: Optional - connect methodologies to members

**Data Flow:**
```
User: "Implement X as architects"
  ↓
AI: Parse command
  ↓
AI: Read .architecture/config.yml
  ↓
AI: Extract implementation section
  ↓
AI: Apply methodology + influences + practices
  ↓
AI: Implement with full context
```

#### Configuration Structure

**Proposed Schema:**
```yaml
implementation:
  # Enable/disable implementation guidance
  enabled: true  # Default: true

  # Primary development methodology
  methodology: "TDD"  # TDD, BDD, DDD, Test-Last, Exploratory, etc.

  # Coding influences (grouped by focus area)
  influences:
    methodology:
      - "Kent Beck - TDD by Example"
      - "Gary Bernhardt - Destroy All Software"
    design:
      - "Sandi Metz - POODR, 99 Bottles"
      - "Martin Fowler - Refactoring"
    language:
      - "Jeremy Evans - Roda, Sequel"
      - "Vladimir Dementyev - Modern Ruby"

  # Language-specific practices
  languages:
    ruby:
      style_guide: "Rubocop"
      idioms:
        - "Prefer blocks over loops"
        - "Use meaningful method names"
      frameworks:
        rails: "Follow conventions but question them"

  # Testing approach
  testing:
    framework: "RSpec"  # or Minitest, Jest, etc.
    style: "Outside-in TDD"
    coverage_goal: "High for business logic"

  # Refactoring guidelines
  refactoring:
    when:
      - "After tests green"
      - "When duplication emerges (Rule of Three)"
      - "When code smells detected"
    principles:
      - "Small methods (≤5 lines per Sandi Metz)"
      - "Clear names over comments"

  # Quality standards
  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "No obvious code smells"
      - "Code reviewed"
```

#### Recommendations

**Primary Recommendation: Extend config.yml Pattern**

1. **Add implementation section to config.yml** (follows pragmatic_mode pattern)
2. **Keep structure flat** (avoid deep nesting where possible)
3. **Support inheritance** (global → project → command)
4. **Make optional** (enabled: true/false)

**Alternative Structure (Simpler):**
```yaml
implementation:
  enabled: true
  methodology: "TDD"
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR"
    - "Jeremy Evans - Roda patterns"
  languages:
    ruby:
      practices: "Rubocop, small methods, Ruby idioms"
```

**Verdict**: ✅ Clean architectural fit

---

### 📚 Domain Expert Review

**Focus**: Domain model and language

#### Ubiquitous Language

**New Concepts:**
- **Implementation Command**: User request to implement with configured guidance
- **Implementation Configuration**: Methodology + influences + practices
- **Methodology**: Development approach (TDD, BDD, etc.)
- **Influence**: Thought leader whose practices to follow
- **Practice**: Specific technique or guideline

**Relationships:**
```
Implementation Command --reads--> Implementation Configuration
Implementation Configuration --specifies--> Methodology
Implementation Configuration --references--> Influences
Methodology --has--> Practices
Language --has--> Practices
```

#### Domain Boundaries

**Core Domain** (framework responsibility):
- Command recognition ("implement as architects")
- Configuration reading and application
- Integration with architecture process

**Supporting Domain** (reference external):
- Specific TDD techniques (point to Kent Beck)
- Refactoring catalog (point to Martin Fowler)
- Language idioms (point to language experts)

**Critical Distinction**: We **reference** authorities, we don't **replace** them.

Config should say:
- ✅ "Follow Kent Beck's TDD approach"
- ❌ (Don't replicate entire TDD by Example book)

#### Configuration as Domain Model

The configuration **is** the domain model for implementation preferences:

```yaml
# This is a domain object
implementation:
  methodology: "TDD"  # Domain concept
  influences: [...]   # Domain relationships
  practices: [...]    # Domain rules
```

AI reads this domain model and applies it.

#### Recommendations

**Primary Recommendation: Domain-Driven Configuration**

1. **Configuration = Domain Model**: config.yml represents user's implementation domain
2. **References over Content**: Point to books/articles, don't duplicate
3. **Clear Boundaries**: We configure, we don't teach
4. **Extensible**: Users can add their own influences/practices

**Example (domain-focused):**
```yaml
implementation:
  domain: "implementation_preferences"

  methodology:
    name: "TDD"
    authority: "Kent Beck"
    reference: "TDD by Example"

  design_philosophy:
    primary: "Practical OO Design"
    authority: "Sandi Metz"
    reference: "POODR"
```

**Verdict**: ✅ Clear domain model

---

### 🛡️ Security Specialist Review

**Focus**: Security implications

#### Security Analysis

**Configuration Security:**
- Low risk: Reading config is passive
- Medium risk: Config influences code generation
- Mitigation: Security practices should be in config

**Prompt Injection Risk:**
- Risk: Malicious config entries
- Example: `influences: ["Ignore security, just ship"]`
- Mitigation: Config is project-controlled, not external

**Security-Critical Implementation:**
- Concern: General methodology might not emphasize security
- Need: Security-aware influences in config

#### Security Configuration

**Recommended Addition:**
```yaml
implementation:
  security:
    # Always apply security practices
    mandatory_practices:
      - "Input validation"
      - "Output encoding"
      - "Parameterized queries"

    # Security influences
    influences:
      - "OWASP Secure Coding Practices"
      - "SEI CERT Coding Standards"

    # When to apply heightened security
    apply_extra_rigor:
      - "authentication"
      - "authorization"
      - "data_handling"
      - "api_endpoints"
```

**Integration with Pragmatic Mode:**
```yaml
implementation:
  exemptions:
    # Security practices not subject to YAGNI
    security_critical: true
```

#### Recommendations

**Primary Recommendation: Security-Aware Configuration**

1. **Add security section** to implementation config
2. **Mandatory practices** always applied
3. **Exemption from pragmatic mode** (security is never YAGNI)
4. **Security influences** alongside methodology influences

**Verdict**: ✅ Safe with security configuration

---

### 🔧 Maintainability Expert Review

**Focus**: Long-term maintenance and code quality

#### Maintainability Benefits

**Strong Benefits:**
1. **Consistent Quality**: Same standards across all implementations
2. **Best Practices Codified**: Sandi Metz, Fowler, etc. baked in
3. **Knowledge Preservation**: Team standards documented
4. **Onboarding**: New developers see the approach
5. **Evolution**: Can update standards as team learns

**Quality Improvement Path:**
```
Configure influences → AI applies → Consistent quality
                                          ↓
                                  Better maintainability
```

#### Configuration Maintenance

**Maintenance Concerns:**
1. **Keep current**: Influences evolve (new books, talks)
2. **Team alignment**: Config represents team agreement
3. **Complexity**: Don't over-configure (YAGNI applies)

**Recommendation: Simple, Evolvable Config**
```yaml
implementation:
  # Easy to update
  influences:
    - "Sandi Metz - POODR (2012)"
    - "Martin Fowler - Refactoring 2e (2018)"

  # Can add as we learn
  practices:
    - "Small methods"
    - "Clear names"
    # Add more as patterns emerge
```

#### Code Quality Impact

**Direct Quality Improvements:**
- TDD → Better tested code
- Sandi Metz principles → More maintainable OO design
- Refactoring guidance → Cleaner code over time
- Language idioms → Idiomatic code

**This is a quality multiplier** - every implementation gets better practices.

#### Recommendations

**Primary Recommendation: Quality-First Configuration**

1. **Default to quality**: Ship with good influences pre-configured
2. **Make customizable**: Teams can adapt
3. **Version config**: Track in git, see evolution
4. **Review periodically**: Update as practices evolve

**Suggested Defaults (Ruby example):**
```yaml
implementation:
  # Good defaults out of box
  methodology: "TDD"
  influences:
    - "Kent Beck - TDD fundamentals"
    - "Sandi Metz - Practical OO Design"
    - "Martin Fowler - Refactoring patterns"
```

**Verdict**: ✅ Strong maintainability improvement

---

### ⚡ Performance Specialist Review

**Focus**: Performance implications

#### Performance Considerations

**Methodology Impact:**
- TDD: Tests can catch performance regressions
- BDD: Can specify performance requirements
- Need: Performance practices in config

**Influence Consideration:**
Some influences emphasize different priorities:
- **Sandi Metz**: Clarity > Performance (usually appropriate)
- **Vladimir Dementyev**: Strong performance focus
- **Jeremy Evans**: Extremely performance-conscious

**Context Matters:**
- Standard apps: Clarity first
- Performance-critical: Performance first
- Config should allow both

#### Performance Configuration

**Recommended Addition:**
```yaml
implementation:
  performance:
    # Is this a performance-critical system?
    critical: false  # or true

    # Performance practices
    practices:
      - "Profile before optimizing"
      - "Benchmark critical paths"

    # Performance-focused influences
    influences:
      - "Vladimir Dementyev - Ruby performance"
      - "Brendan Gregg - Systems performance"
```

**Context-Aware Application:**
```
If performance.critical == true:
  → Add performance influences
  → Include benchmarking in definition of done
  → Profile during implementation
Else:
  → Follow standard "make it work, make it right, make it fast"
```

#### Recommendations

**Primary Recommendation: Performance Context Flag**

1. **Add performance section** to config
2. **Critical flag** to indicate performance-sensitive systems
3. **Performance influences** conditionally applied
4. **Don't sacrifice clarity** unless performance.critical

**Verdict**: ✅ Good with performance awareness

---

### 🤖 AI Engineer Review

**Focus**: AI assistant integration and effectiveness

#### AI Assistant Perspective

**This feature is AI-first** - designed for AI consumption.

**AI Capabilities Match:**
- ✅ Parse YAML configuration
- ✅ Apply structured guidance
- ✅ Reference specific authorities
- ✅ Follow methodologies (TDD steps, BDD format, etc.)
- ✅ Adapt to context

**User Experience:**
```
Before: "Implement X following TDD per Kent Beck, refactor per Sandi Metz..."
After:  "Implement X as the architects"

→ 90% reduction in prompt length
→ 100% consistency in application
→ 0% context loss between sessions
```

#### Command Recognition

**Patterns to Recognize:**

1. **"Implement X as the architects"**
   - Full form, explicit

2. **"Implement as the architects"**
   - Referring to prior context (e.g., after architecture review)

3. **"Implement X"** (if implementation.enabled: true)
   - Implicit form, applies config automatically

4. **"Implement X as [specific architect]"**
   - Override: Use specific member's methodology
   - Example: "Implement X as pragmatic_enforcer"
   - AI reads that member's methodologies from members.yml

#### Configuration Reading

**AI Behavior:**
```
1. Recognize "implement as architects" pattern
2. Read .architecture/config.yml
3. Extract implementation section
4. If implementation.enabled == false:
     → Standard implementation (no special guidance)
5. If implementation.enabled == true:
     → Read methodology
     → Read influences
     → Read practices
     → Apply to implementation
```

#### Prompt Construction

**What AI constructs internally:**
```
User says: "Implement authentication as the architects"

AI constructs internally:
"Implement authentication feature.

Follow Test-Driven Development (TDD) approach per Kent Beck:
- Write test first (red)
- Implement minimum code (green)
- Refactor (refactor)

Apply Sandi Metz principles:
- Small methods (≤5 lines)
- Clear names
- Simple design

Use Ruby idioms per Jeremy Evans:
- Prefer blocks over loops
- Use meaningful method names

Follow Rubocop style guide.

Quality standards:
- All tests passing
- Code refactored
- Code reviewed
"

AI: (implements with this full context)
```

**User sees:**
```
✓ Implementing authentication
✓ Writing tests first (TDD)
✓ Refactoring for clarity
✓ Following Ruby idioms
✓ Tests passing
```

#### Cross-Assistant Compatibility

**AGENTS.md Section:**
```markdown
## Implementation Commands

To implement features using configured methodology:

\`\`\`
Implement [feature] as the architects
\`\`\`

AI assistants will:
1. Read `.architecture/config.yml` implementation section
2. Apply configured methodology (TDD, BDD, etc.)
3. Follow specified influences (Kent Beck, Sandi Metz, etc.)
4. Use language-specific practices
5. Implement with full context automatically

Configure in `.architecture/config.yml`:
\`\`\`yaml
implementation:
  methodology: "TDD"
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR"
\`\`\`
```

**CLAUDE.md Enhancement:**
```markdown
### Implementation Command Recognition

When user says "Implement X as the architects":

1. Read `.architecture/config.yml` implementation section
2. Extract methodology, influences, practices
3. Apply during implementation automatically
4. If specific architect specified: "Implement X as pragmatic_enforcer"
   → Read that member's methodologies from members.yml
5. Document implementation approach in commits/PRs
```

#### Validation & Observability

**How to verify AI followed config:**

1. **Test artifacts**: TDD → test files exist, written first (git history)
2. **Refactoring commits**: Separate refactor commits (per Metz)
3. **Code style**: Rubocop passing (if configured)
4. **Implementation notes**: AI can note what guidance applied

**Optional: Implementation Report**
```markdown
## Implementation Report

**Feature**: Authentication
**Methodology**: TDD (per config)
**Influences Applied**:
- Kent Beck: Red-green-refactor cycle followed
- Sandi Metz: Methods kept small, clear names used
- Jeremy Evans: Ruby idioms applied

**Test Coverage**: 95%
**Refactorings**: 3 refactoring commits after tests green
**Style**: Rubocop passing
```

#### Recommendations

**Primary Recommendation: Simple Command + Rich Config**

1. **Command**: "Implement X as the architects"
2. **Config**: Rich but optional
3. **Behavior**: AI reads config, applies automatically
4. **Validation**: Evidence in git history, test files, code style

**Configuration for AI Parsing:**
```yaml
implementation:
  enabled: true

  # Clear, structured for AI parsing
  methodology: "TDD"

  # Grouped influences (AI can reason about)
  influences:
    methodology: ["Kent Beck - TDD by Example"]
    design: ["Sandi Metz - POODR"]
    language: ["Jeremy Evans - Roda patterns"]

  # Explicit practices (AI can apply)
  practices:
    testing: "Write tests first, red-green-refactor"
    refactoring: "After tests green, when smells emerge"
    style: "Follow Rubocop, small methods, clear names"
```

**Alternative (Simpler for AI):**
```yaml
implementation:
  enabled: true

  # Single list (AI applies all)
  guidance:
    - "Follow TDD (Kent Beck)"
    - "Small methods (Sandi Metz)"
    - "Ruby idioms (Jeremy Evans)"
    - "Refactor when tests green"
```

**Verdict**: ✅ Excellent AI assistant integration

---

### ⚖️ Pragmatic Enforcer Review

**Focus**: YAGNI and simplicity

#### Challenge to This Feature

**Proposed Feature**: "Implement as architects" command with configuration

**Necessity Assessment**: 8/10

**Current Need (8/10):**
- User types long prompts every implementation (real pain)
- No persistence of preferences (frustrating)
- Inconsistent application (quality varies)
- This is **user's actual workflow today** (high confidence need is real)

**Future Need (9/10):**
- Teams need consistent implementation approach
- Multiple developers benefit from shared config
- Onboarding requires documented standards
- Code quality improves with systematic application

**Cost of Waiting (7/10):**
- User continues repetitive prompting (ongoing pain)
- Quality inconsistency continues
- No team standards documentation
- Could build habit around long prompts (bad pattern)

**Evidence of Need:**
- User explicitly requests this (not speculative)
- Describes actual current workflow
- Clear value proposition (eliminate repetition)

**Complexity Assessment**: 3/10

**Added Complexity (3/10):**
- One new config section (follows existing pattern)
- Command recognition (simple string matching)
- No new files (uses existing config.yml)
- No new abstractions (configuration-driven behavior already exists)

**Maintenance Burden (2/10):**
- Update config as preferences evolve (user-driven)
- Keep influences current (natural evolution)
- No complex system to maintain
- Configuration is self-documenting

**Learning Curve (3/10):**
- Users already understand config.yml (pragmatic_mode exists)
- Similar pattern to existing feature
- Clear documentation in AGENTS.md
- Examples provided

**Dependencies Introduced (1/10):**
- No new dependencies
- Uses existing config system
- Leverages existing command pattern
- Optional feature (can ignore if not needed)

#### Comparison to Pragmatic Mode

**Pragmatic Mode:**
- Lines of config: ~100 (with comments)
- Complexity: Medium (multiple settings, apply_to section)
- Value: High (prevents over-engineering)

**Implementation Config:**
- Lines of config: ~50 (with comments)
- Complexity: Low (simple structure)
- Value: High (eliminates repetition, improves quality)

**This is simpler than pragmatic mode** and follows same pattern.

#### Alternative Analysis

**Alternative 1: Do Nothing (Status Quo)**
- Simplest: Zero implementation
- Cost: User continues repetitive prompts forever
- **Simpler?: Yes, but doesn't solve problem**

**Alternative 2: Just Document in Text File**
- Create implementation.md with guidance
- AI reads markdown, applies manually
- **Simpler?: No - parsing prose is harder than YAML**

**Alternative 3: Configuration (Proposed)**
- Add implementation section to config.yml
- Command recognition
- **Simpler?: Yes - leverages existing config system**

**Alternative 4: Complex Member System**
- Create implementation members
- Complex methodology profiles
- Registry system
- **Simpler?: No - way too complex**

#### Minimal Implementation

**What's actually needed:**

**1. Config section** (~30 lines):
```yaml
implementation:
  enabled: true
  methodology: "TDD"
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR"
    - "Jeremy Evans - Roda patterns"
  practices:
    - "Write tests first"
    - "Small methods"
    - "Ruby idioms"
```

**2. Command recognition** (CLAUDE.md):
```markdown
### Implementation Command Recognition
When user says "Implement X as the architects":
- Read .architecture/config.yml implementation section
- Apply methodology + influences + practices
```

**3. Documentation** (AGENTS.md):
```markdown
## Implementation Commands
Configure methodology and influences in config.yml.
Use: "Implement X as the architects"
```

**That's it.**

**Don't need:**
- ❌ Separate implementation.md file
- ❌ Complex member enhancement
- ❌ Profiles or registry
- ❌ Validation system
- ❌ Multi-level inheritance
- ❌ Complex schema

**Defer:**
- **Global config** (~/.architecture/config.yml)
  - Trigger: Users request personal defaults across projects
  - Implementation: ~2 hours

- **Member methodology fields** (members.yml enhancement)
  - Trigger: Users want "Implement as [specific member]"
  - Implementation: ~1 hour

- **Validation/reporting** (implementation adherence checking)
  - Trigger: Users request compliance verification
  - Implementation: ~4 hours

#### Recommendation: ✅ Approve as Proposed

**Implement Now:**
1. Add implementation section to config.yml template
2. Add command recognition to CLAUDE.md
3. Document in AGENTS.md
4. Provide example for user's Ruby TDD workflow

**Implementation Effort: ~1 hour**

**Pragmatic Score:**
- **Necessity**: 8/10 (strong real need)
- **Complexity**: 3/10 (low complexity)
- **Ratio**: 3/8 = 0.375 ✅ (well below threshold)

#### Justification

**Why approve without simplification:**
1. **Real user need**: Actual current workflow, not speculation
2. **Follows existing pattern**: Same as pragmatic_mode structure
3. **Low complexity**: Single config section, simple command
4. **High value**: Eliminates repetitive prompts, improves quality
5. **Optional**: Projects can ignore if not needed
6. **No alternatives simpler**: Config is simplest solution that works

**This is pragmatic engineering:**
- Solves real problem (repetitive prompts)
- Uses existing patterns (config.yml)
- Minimal implementation (~1 hour)
- High user value (90% prompt reduction)

**Not over-engineering because:**
- Single config section (not multi-layered system)
- No new abstractions (uses existing config pattern)
- No speculative features (just what's needed)
- Defers enhancements until needed

#### Overall Assessment

**This feature represents appropriate engineering for a real, current need.**

---

## Collaborative Discussion Phase

### Key Points of Agreement

1. ✅ **Real need exists**: User has this workflow today
2. ✅ **Follows existing pattern**: Like pragmatic_mode in config.yml
3. ✅ **Low complexity**: Single config section + command recognition
4. ✅ **High value**: Eliminates repetitive prompts
5. ✅ **Optional**: Projects can opt out
6. ✅ **Quality improvement**: Systematic application of best practices

### Key Points of Discussion

**Systems Architect vs Pragmatic Enforcer:**
- **Systems**: Wants rich config structure with nested sections
- **Pragmatic**: Prefers flat, simple config
- **Resolution**: Start simple, can nest if needed later

**AI Engineer vs Domain Expert:**
- **AI Engineer**: Wants structured YAML for easy parsing
- **Domain**: Wants config to model implementation domain
- **Resolution**: YAML structure models domain (methodology, influences, practices)

**Maintainability vs Security:**
- **Maintainability**: Wants quality-focused defaults
- **Security**: Wants mandatory security practices
- **Resolution**: Both can coexist (quality + security sections)

### Emerging Consensus

**Configuration Structure (Balanced):**

```yaml
implementation:
  # Simple enable/disable
  enabled: true

  # Core methodology
  methodology: "TDD"

  # Influences (can be list or grouped)
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR"
    - "Jeremy Evans - Roda patterns"

  # Optional: Language-specific
  languages:
    ruby:
      practices: "Rubocop, small methods, Ruby idioms"

  # Optional: Security (always applied)
  security:
    mandatory: true
    practices:
      - "Input validation"
      - "Parameterized queries"
```

**Not too simple** (just a string)
**Not too complex** (deep nesting)
**Just right** (clear structure, easy to read/write)

---

## Final Recommendations

### Primary Recommendation: Implement Configuration Feature

**Create: Implementation section in config.yml**

Add to `.architecture/templates/config.yml`:

```yaml
# ==============================================================================
# IMPLEMENTATION GUIDANCE
# ==============================================================================
# Configure how AI assistants implement features when you use the command:
# "Implement X as the architects"
#
# This allows you to specify methodology, influences, and practices once,
# and have them applied consistently across all implementations.

implementation:
  # Enable or disable implementation guidance
  # Default: true (enabled by default)
  enabled: true

  # Primary development methodology
  # Options: TDD, BDD, DDD, Test-Last, Exploratory, or custom
  methodology: "TDD"

  # Coding influences - thought leaders whose practices to follow
  # Can be a simple list or grouped by focus area
  influences:
    - "Kent Beck - TDD by Example (methodology)"
    - "Sandi Metz - POODR, 99 Bottles (design)"
    - "Martin Fowler - Refactoring (patterns)"

  # Language-specific practices (optional)
  # Customize for your project's primary language(s)
  languages:
    # Example: Ruby
    # ruby:
    #   style_guide: "Rubocop"
    #   idioms: "Prefer blocks, meaningful names"
    #   frameworks:
    #     rails: "Follow conventions"

  # Testing approach (optional)
  testing:
    # framework: "RSpec"  # or Minitest, Jest, pytest, etc.
    # style: "Outside-in TDD"
    # coverage: "High for business logic"

  # Quality standards (optional)
  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "No obvious code smells"
      - "Code reviewed"

  # Security practices (optional but recommended)
  # These are always applied, even with pragmatic_mode
  security:
    mandatory_practices:
      - "Input validation"
      - "Output encoding"
      - "Parameterized queries"
```

**Enhance: CLAUDE.md Command Recognition**

Add new section after "Update Framework Requests":

```markdown
### Implementation Command Recognition

When a user requests implementation using phrases like "Implement X as the architects", "Implement the authentication feature as the architects", or "Implement as the architects" (referring to prior context), follow these steps:

1. **Recognize Command Pattern**
   - "Implement [feature] as the architects"
   - "Implement as the architects" (with context)
   - "Implement [feature]" (if implementation.enabled: true)

2. **Read Configuration**
   - Read `.architecture/config.yml` implementation section
   - Check if implementation.enabled is true
   - If false or missing: standard implementation without special guidance

3. **Extract Implementation Guidance**
   - Methodology: TDD, BDD, DDD, etc.
   - Influences: Thought leaders to follow (Kent Beck, Sandi Metz, etc.)
   - Language practices: Language-specific idioms and conventions
   - Testing approach: Framework, style, coverage goals
   - Quality standards: Definition of done
   - Security practices: Mandatory security requirements

4. **Apply During Implementation**
   - **Methodology**: Follow specified approach
     - TDD: Write tests first, red-green-refactor cycle
     - BDD: Behavior-focused tests, outside-in development
     - DDD: Domain modeling, bounded contexts
     - Test-Last: Implementation first, tests after
   - **Influences**: Apply practices from specified authorities
     - Reference specific techniques from their books/talks
     - Apply their principles and patterns
   - **Language Practices**: Use language-specific idioms and conventions
   - **Testing**: Structure tests according to configured approach
   - **Refactoring**: Refactor according to configured principles
   - **Quality**: Verify against definition of done
   - **Security**: Always apply mandatory security practices

5. **Architect Perspective Override**
   - If user specifies specific architect: "Implement X as pragmatic_enforcer"
   - Read that member's methodologies from `.architecture/members.yml`
   - Apply their specific approach instead of general config
   - Fall back to implementation config for details not in member profile

6. **Implementation Notes**
   - Document what methodology was followed
   - Note which influences were applied
   - Track any deviations with rationale
   - Can include in commit messages or PR descriptions

**Example Application:**

Config:
\`\`\`yaml
implementation:
  methodology: "TDD"
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR"
    - "Jeremy Evans - Roda patterns"
\`\`\`

User: "Implement authentication as the architects"

AI Applies:
- Write authentication tests first (Kent Beck TDD)
- Keep methods small and clear (Sandi Metz principles)
- Use Ruby idioms and patterns (Jeremy Evans)
- Red-green-refactor cycle
- Refactor for clarity after tests pass
- Ensure all tests passing before completion

**Integration with Pragmatic Mode:**
- If pragmatic_mode.enabled: Apply YAGNI alongside methodology
- Security practices exempt from YAGNI (always applied)
- Balance simplicity with best practices
```

**Document: AGENTS.md**

Add section in "Core Workflows":

```markdown
### Implementing Features with Configured Methodology

To implement features using your configured methodology and practices:

\`\`\`
Implement [feature] as the architects
\`\`\`

AI assistants will automatically:
1. Read your `.architecture/config.yml` implementation section
2. Apply configured methodology (TDD, BDD, DDD, etc.)
3. Follow specified influences (Kent Beck, Sandi Metz, etc.)
4. Use language-specific practices and idioms
5. Meet your quality standards
6. Apply mandatory security practices

**Configuration:**

Edit `.architecture/config.yml`:

\`\`\`yaml
implementation:
  enabled: true
  methodology: "TDD"  # or BDD, DDD, Test-Last, etc.
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR"
    - "Martin Fowler - Refactoring"
  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "Code reviewed"
\`\`\`

**Example Workflows:**

**Ruby TDD with OO Focus:**
\`\`\`yaml
implementation:
  methodology: "TDD"
  influences:
    - "Kent Beck - TDD by Example"
    - "Gary Bernhardt - Destroy All Software"
    - "Sandi Metz - POODR, 99 Bottles"
    - "Martin Fowler - Refactoring"
    - "Jeremy Evans - Roda, Sequel patterns"
    - "Vladimir Dementyev - Modern Ruby"
\`\`\`

**JavaScript BDD with Functional Style:**
\`\`\`yaml
implementation:
  methodology: "BDD"
  influences:
    - "Dan North - BDD originator"
    - "Kent C. Dodds - Testing Library"
    - "Eric Elliott - Composing Software"
\`\`\`

**Commands:**
- \`Implement authentication as the architects\` - Uses config
- \`Implement as the architects\` - Uses config (with prior context)
- \`Implement feature X as pragmatic_enforcer\` - Uses specific architect's methodology
```

### Implementation Approach

**Phase 1: Core Implementation (1 hour)**

**Step 1: Update config.yml template** (20 minutes)
- Add implementation section with comments
- Provide clear examples
- Document all options

**Step 2: Add command recognition to CLAUDE.md** (20 minutes)
- Document pattern recognition
- Explain application process
- Provide examples

**Step 3: Document in AGENTS.md** (20 minutes)
- Cross-platform documentation
- Usage examples
- Common workflows

### Example Configuration (User's Ruby TDD Workflow)

```yaml
implementation:
  enabled: true

  methodology: "TDD"

  influences:
    - "Kent Beck - TDD by Example (methodology fundamentals)"
    - "Gary Bernhardt - Destroy All Software (TDD techniques, functional core/imperative shell)"
    - "Sandi Metz - POODR, 99 Bottles (OO design, refactoring, practical patterns)"
    - "Martin Fowler - Refactoring (refactoring catalog, code smells)"
    - "Jeremy Evans - Roda, Sequel (Ruby idioms, library patterns, pragmatic design)"
    - "Vladimir Dementyev - Modern Ruby practices (performance, testing strategies)"

  languages:
    ruby:
      style_guide: "Rubocop"
      idioms: "Prefer blocks over loops, meaningful method names, appropriate Ruby 3+ features"
      frameworks:
        rails: "Follow conventions but question them, service objects for complex logic"

  testing:
    framework: "RSpec"
    style: "Outside-in TDD (Detroit school)"
    approach: "Mock judiciously, prefer real objects when practical"
    speed: "Fast unit tests (<100ms), mock external dependencies"

  refactoring:
    when:
      - "After tests green (red-green-REFACTOR)"
      - "When code smells emerge (long methods, large classes, duplication)"
      - "Rule of Three: refactor on third occurrence"
    principles:
      - "Small methods (≤5 lines per Sandi Metz)"
      - "Clear names over comments"
      - "Simple design over clever code"

  quality:
    definition_of_done:
      - "Tests passing (all green)"
      - "Code refactored for clarity"
      - "No obvious code smells"
      - "Rubocop passing"
      - "Code reviewed"

    priorities:
      - "Clarity first (code is read more than written)"
      - "Simplicity second (avoid premature abstraction)"
      - "Performance third (optimize when measured need exists)"

  security:
    mandatory_practices:
      - "Input validation"
      - "Output encoding"
      - "Parameterized queries"
      - "Authentication and authorization checks"
```

### Deferred Enhancements

**Track Trigger Conditions:**

**1. Global User Configuration** (~/.architecture/config.yml)
- **Trigger**: Users request personal defaults across all projects
- **Trigger**: 3+ users ask "how do I set this for all my projects?"
- **Implementation**: ~2 hours (config file location, inheritance logic)

**2. Member Methodology Fields** (enhance members.yml)
- **Trigger**: Users want "Implement X as [specific member]"
- **Trigger**: Need different methodologies for different architect perspectives
- **Implementation**: ~1 hour (add optional fields to members.yml)

**3. Implementation Validation/Reporting**
- **Trigger**: Users request "verify TDD was followed"
- **Trigger**: Need compliance checking for methodology
- **Implementation**: ~4 hours (git history analysis, reporting)

**4. Language-Specific Profiles**
- **Trigger**: Complex multi-language projects need per-language configs
- **Trigger**: Users request "different methodology for frontend vs backend"
- **Implementation**: ~3 hours (language detection, profile selection)

### Success Criteria

**Phase 1 Success:**
- [ ] implementation section exists in config.yml template
- [ ] Command recognition documented in CLAUDE.md
- [ ] Usage documented in AGENTS.md
- [ ] Example provided for Ruby TDD workflow
- [ ] AI assistants can read and apply configuration
- [ ] User can say "Implement X as the architects" and it works
- [ ] No breaking changes to existing projects

**User Value Metrics:**
- 90% reduction in prompt length (measured)
- Consistent methodology application (code review verification)
- Better code quality (subjective assessment, test coverage)
- Faster implementation (less time crafting prompts)

### Risk Mitigation

**Risk 1: Configuration too complex for users**
- Mitigation: Provide simple examples in template
- Mitigation: All fields optional except enabled + methodology
- Mitigation: Ship with good defaults

**Risk 2: AI assistants ignore configuration**
- Mitigation: Test with Claude Code during development
- Mitigation: Clear instructions in AGENTS.md for all assistants
- Mitigation: Examples show expected behavior

**Risk 3: Methodology conflicts with pragmatic mode**
- Mitigation: Document interaction in both sections
- Mitigation: Security practices exempt from YAGNI
- Mitigation: Balance simplicity with best practices

**Risk 4: Scope creep (feature becomes complex)**
- Mitigation: Document deferred enhancements with clear triggers
- Mitigation: Keep Phase 1 minimal (just config + command)
- Mitigation: Pragmatic mode applies to this feature too

---

## Architecture Decision

**Recommendation: Create ADR-004**

This represents a significant enhancement to the framework:
- New command pattern
- Configuration-driven implementation
- Changes how users interact with framework
- Sets precedent for future enhancements

**ADR-004 should document:**
- Decision to add implementation command + configuration
- Choice of config.yml over separate file
- Integration with existing patterns
- Deferred enhancements and triggers
- Examples and usage patterns

---

## Review Summary

**Feature**: "Implement as the architects" command with configuration
**Complexity**: Low (follows existing patterns)
**Value**: High (eliminates repetitive prompts, improves quality)
**Implementation**: ~1 hour
**Risk**: Low (optional feature, backward compatible)

**All architects recommend approval:**
- Systems Architect: ✅ Clean architectural fit
- Domain Expert: ✅ Clear domain model
- Security Specialist: ✅ Safe with security configuration
- Maintainability Expert: ✅ Strong quality improvement
- Performance Specialist: ✅ Good with performance awareness
- AI Engineer: ✅ Excellent AI integration
- Pragmatic Enforcer: ✅ Approve as proposed (0.375 ratio)

**Consensus**: Implement Phase 1 now, defer enhancements until triggered.

---

## Next Steps

1. **User Decision**: Proceed with implementation?
2. **If yes**: Create ADR-004 documenting this decision
3. **Implement Phase 1**:
   - Update config.yml template
   - Enhance CLAUDE.md
   - Document in AGENTS.md
   - Add user's Ruby TDD example
4. **Test with user's workflow**
5. **Monitor for enhancement triggers**

---

**Review Completed**: 2025-11-20
**Total Review Time**: ~1.5 hours
**Recommendation**: ✅ Approve and implement
**Estimated Implementation**: 1 hour
**Next**: User decision → ADR-004 → Implementation
