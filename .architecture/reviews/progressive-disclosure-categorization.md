# Progressive Disclosure Applied to Documentation Recommendations

**Date**: 2025-12-11
**Source**: Architecture Review - README.md Pragmatic Mode and Implementation Guidance Documentation
**Process**: Applied pragmatic principles to recommendations themselves

---

## Executive Summary

The architecture review identified **13 potential improvements** to README.md documentation. Rather than implementing all recommendations immediately (which would bloat README and risk violating instruction capacity constraints per ADR-005), we **applied progressive disclosure principles to the recommendations themselves**.

**Outcome**:
- **3 recommendations** → Add to README immediately (~13 lines, ~75 min total)
- **10 recommendations** → Deferred with clear triggers (tracked in deferrals.md)
- **1 structure created** → TROUBLESHOOTING.md for deferred detailed documentation

**Result**: README stays within limits (~517 lines vs. 550 target), instruction capacity maintained, all concerns addressed pragmatically.

---

## Categorization Methodology

For each recommendation, we assessed:

**Necessity Score (0-10)**:
- 0-3: Nice to have, speculative value
- 4-7: Valuable, some evidence of need
- 8-10: Critical, clear current need

**Complexity Score (0-10)**:
- 0-3: Small addition (< 10 lines, < 30 min)
- 4-7: Medium addition (10-50 lines, 30-120 min)
- 8-10: Large addition (> 50 lines, > 2 hours)

**Ratio**: Complexity / Necessity
- < 0.5: Strong candidate for "add now"
- 0.5-1.0: Consider for "add now" if high necessity
- 1.0-1.5: Defer unless critical
- > 1.5: Definitely defer

**Evidence of Need**:
- User questions? How many?
- Observed confusion? How often?
- Blocking adoption? Evidence?
- Speculative? (No evidence yet)

---

## Category A: Add to README Immediately

These recommendations have **high necessity + low complexity + ratio < 0.5**:

### 1. Expand Security Exemptions (Security Specialist - Critical)

**Scores**: N=9/10, C=3/10, Ratio=0.33 ✅

**What**: Expand README Pragmatic Mode section to explicitly list 4 exemption categories with examples:
- Security-critical features (authentication, authorization, encryption, input validation)
- Data integrity (database transactions, data validation, backup strategies)
- Compliance requirements (GDPR, HIPAA, PCI-DSS, audit logging)
- Accessibility (WCAG compliance, screen reader support)

**Why Add Now**:
- Security-conscious organizations need to see protections upfront
- Current one-sentence mention insufficient to build confidence
- Blocking adoption due to concerns about "pragmatic" meaning
- High user impact, prevents hesitation

**Implementation**: Replace "Exemptions for Critical Areas: Security and compliance remain rigorous" with bulleted list (~8 lines)

**Effort**: 30 minutes

**Status**: Ready to implement

---

### 2. Add Feature Interaction Note (Systems Architect - High)

**Scores**: N=7/10, C=2/10, Ratio=0.29 ✅

**What**: Add 2-3 sentences explaining how Pragmatic Mode and Implementation Guidance interact when both enabled.

**Why Add Now**:
- Natural user question: "Will pragmatic mode challenge my configured practices?"
- Prevents confusion about feature compatibility
- Low complexity, high clarity value
- Builds confidence in enabling both features

**Implementation**: Add to end of Pragmatic Mode section or beginning of Implementation Guidance section:

> "When using both Pragmatic Mode and Implementation Guidance together, pragmatic mode respects your configured security practices and methodological choices while challenging unnecessary complexity in other areas. The pragmatic enforcer ensures implementations remain simple while still following your team's documented standards for security, testing, and code quality."

**Effort**: 15 minutes

**Status**: Ready to implement

---

### 3. Validate Performance Claims (Performance Specialist - Important)

**Scores**: N=7/10, C=2/10, Ratio=0.29 ✅

**What**: Add footnotes linking performance claims ("90% prompt reduction", "20x faster") to validation methodology in ADRs.

**Why Add Now**:
- Strengthens credibility for quantified benefits
- Simple addition (footnote references)
- Addresses potential skepticism
- Low complexity, high value

**Implementation**:
- After "90% prompt reduction": add superscript "¹"
- After "20x faster implementation": add superscript "²"
- At bottom of section:
  - "¹ See ADR-004 § Validation for measurement methodology"
  - "² See ADR-002 § Implementation Results for measurement details"

**Effort**: 30 minutes (includes link verification)

**Status**: Ready to implement

---

**Category A Total**:
- **Lines Added**: ~13 (8 + 3 + 2)
- **Time Required**: ~75 minutes
- **README Size After**: ~517 lines (within 550 target)
- **Instruction Capacity**: Maintained (< 150 instructions)

---

## Category B: Create Structure for Deferred Documentation

### TROUBLESHOOTING.md Created

**Purpose**: Home for detailed documentation that shouldn't be in README due to progressive disclosure principles (ADR-005).

**Sections Created** (to be populated when triggers hit):
1. **How AI Assistants Use These Features** - AI capabilities, parsing, error handling
2. **Common Errors** - Error scenarios and resolutions
3. **Configuration Maintenance** - Lifecycle guidance
4. **Advanced Prompt Patterns** - Power user commands

**Link from README**: Add reference to TROUBLESHOOTING.md in documentation resources section.

**Effort**: 2 hours (structure + initial content + linking)

**Status**: ✅ Complete (created at `/TROUBLESHOOTING.md`)

---

## Category C: Deferred with Clear Triggers

These recommendations are **tracked in deferrals.md** with specific, measurable trigger conditions:

### Deferred - Medium Priority (4 items)

1. **AI Assistant Capabilities Documentation** (N=6, C=6, Ratio=1.0)
   - Trigger: 5+ user questions about AI behavior
   - Status: 0 questions as of 2025-12-11

2. **Advanced Prompt Patterns** (N=5, C=3, Ratio=0.6)
   - Trigger: 5+ user questions about "Can I implement as [member]?"
   - Status: 0 questions as of 2025-12-11

3. **Error Handling Documentation** (N=6, C=5, Ratio=0.83)
   - Trigger: 5+ support requests about configuration errors
   - Status: 0 errors reported as of 2025-12-11

4. **Configuration Maintenance Guidance** (N=6, C=5, Ratio=0.83)
   - Trigger: 3+ projects with stale configs OR 6+ months since launch
   - Status: Features recently launched, configs fresh

### Deferred - Low Priority (6 items)

5. **"When NOT to Use" Anti-Patterns** (N=5, C=3, Ratio=0.6)
   - Trigger: 3+ incidents of inappropriate feature use
   - Status: 0 incidents as of 2025-12-11

6. **Command Variations Expansion** (N=4, C=2, Ratio=0.5)
   - Trigger: Users request more command examples
   - Status: 0 requests as of 2025-12-11

7. **Multi-Language Configuration Examples** (N=6, C=2, Ratio=0.33)
   - Trigger: 3+ users ask about multi-language configuration
   - Status: 0 questions as of 2025-12-11

8. **Progressive Disclosure Performance Benefits** (N=4, C=2, Ratio=0.5)
   - Trigger: Users ask why documentation structured this way
   - Status: 0 questions as of 2025-12-11

9. **Config Parsing Performance Clarification** (N=3, C=1, Ratio=0.33)
   - Trigger: User asks about config parsing performance
   - Status: 0 concerns as of 2025-12-11

10. **Version Consistency Verification** (N=4, C=2, Ratio=0.5)
    - Trigger: Quarterly documentation review cycle
    - Status: Address during next quarterly review

---

## Pragmatic Analysis of This Decision

**Meta-Application**: We applied pragmatic mode principles to documentation recommendations themselves.

### Before Progressive Disclosure

**All Recommendations Implemented**:
- README: 504 + 60-100 lines = 564-604 lines
- Risk: Exceeds 550-line target, violates instruction capacity
- Contradicts: Our own progressive disclosure principles (ADR-005)
- Time: ~5-7 hours for all implementations
- Value: Mixed - some high value, some speculative

### After Progressive Disclosure

**Categorized Approach**:
- README: 504 + 13 lines = 517 lines ✅ (within target)
- Instruction capacity: Maintained ✅ (< 150 instructions)
- TROUBLESHOOTING.md: Created for deferred items ✅
- Deferrals tracked: 10 items with clear triggers ✅
- Time investment: ~3 hours (75 min immediate + 2 hrs structure)
- Value: Maximized (high-value items implemented, speculative deferred)

### Pragmatic Score

**Comprehensive Documentation Approach**:
- Necessity: 6/10 (some items valuable, many speculative)
- Complexity: 7/10 (60-100 lines, significant effort)
- Ratio: 1.17 (acceptable but not optimal)

**Progressive Disclosure Approach** (selected):
- Necessity: 8/10 (addresses real concerns, respects constraints)
- Complexity: 3/10 (minimal README additions, structure for future)
- Ratio: 0.375 ✅ (well below 1.5 threshold)

**Conclusion**: Progressive disclosure approach is **more pragmatic** - addresses current needs without over-engineering documentation.

---

## Validation: Self-Application of Pragmatic Principles

This categorization exercise demonstrates that **pragmatic mode principles apply to documentation** just as they apply to code:

1. ✅ **Challenge Scope**: Questioned whether ALL recommendations needed NOW
2. ✅ **Calculate Ratio**: Applied necessity/complexity scoring to each
3. ✅ **Propose Simpler Alternative**: TROUBLESHOOTING.md instead of README bloat
4. ✅ **Track Deferrals**: Clear triggers for each deferred item
5. ✅ **Cost of Waiting**: Low for most items (users haven't asked yet)
6. ✅ **Evidence-Based**: Trigger conditions are measurable, not speculative

**The Meta-Insight**: If pragmatic mode helps us make better decisions about *documenting* pragmatic mode, that's powerful evidence it works for code too.

---

## Next Steps

### Immediate Implementation (0-2 weeks)

1. **Expand Security Exemptions** in README (30 min)
   - Location: README.md lines 428-452 (Pragmatic Mode section)
   - Replace one-sentence mention with 4-category bulleted list
   - Owner: Security Specialist perspective

2. **Add Feature Interaction Note** (15 min)
   - Location: End of Pragmatic Mode or start of Implementation Guidance
   - 2-3 sentences clarifying feature cooperation
   - Owner: Systems Architect perspective

3. **Validate Performance Claims** (30 min)
   - Location: Both sections (Pragmatic Mode, Implementation Guidance)
   - Add footnotes linking to ADR validation sections
   - Owner: Performance Specialist perspective

4. **Link TROUBLESHOOTING.md from README** (10 min)
   - Add reference in documentation resources or getting help section
   - Single line: "For troubleshooting and advanced usage, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)"

**Total Effort**: ~85 minutes
**Total Lines Added**: ~14
**README Final Size**: ~518 lines (within 550 target)

### Monthly Monitoring

- Review deferrals.md for triggered conditions
- Check GitHub issues/discussions for:
  - User questions matching trigger conditions
  - Configuration errors being reported
  - Requests for advanced patterns
  - Any confusion about features

### Quarterly Review (Q1 2026)

- Re-evaluate all deferred items
- Update trigger conditions based on actual usage patterns
- Consider whether any low-priority items can be cancelled
- Review deferral hit rate (target: < 40%)

---

## Metrics

### Deferral Tracking

**Total Deferrals**: 22 framework-wide (12 pragmatic mode implementation + 10 README documentation)
**Hit Rate Target**: < 40% (most deferrals should remain unneeded)
**Current Hit Rate**: 0% (0 of 22 triggered)

### Documentation Efficiency

**README Instruction Density**:
- Before Review: ~100 instructions (estimated)
- After Category A: ~108 instructions (estimated)
- Target: < 150 instructions
- Status: ✅ Within limits

**Progressive Disclosure Success**:
- 10 of 13 recommendations (77%) deferred with triggers
- Prevents 60-100 lines of speculative documentation
- Saves 4-6 hours of documentation effort
- Maintains instruction capacity compliance

---

## Related Documents

- **Source Review**: [.architecture/reviews/readme-pragmatic-implementation-docs.md](.architecture/reviews/readme-pragmatic-implementation-docs.md)
- **Deferrals**: [.architecture/deferrals.md](.architecture/deferrals.md) (10 new entries added)
- **TROUBLESHOOTING**: [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md) (structure created)
- **ADR-005**: [.architecture/decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md](.architecture/decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)

---

**Categorization Complete**: 2025-12-11
**Next Review**: Monthly deferral check, quarterly comprehensive review
**Success Metric**: Deferral hit rate < 40% validates progressive approach
