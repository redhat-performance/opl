# Pragmatic Mode Integration for Architecture Reviews

This document describes how to integrate Pragmatic Enforcer analysis when pragmatic mode is enabled in `.architecture/config.yml`.

## When to Include Pragmatic Analysis

**Check Configuration**: Read `.architecture/config.yml`:

```yaml
pragmatic_mode:
  enabled: true
  intensity: strict | balanced | lenient
  applies_to:
    - reviews
    - adrs
    - implementation
```

**If `pragmatic_mode.enabled == true` AND `reviews` is in `applies_to`**: Include Pragmatic Enforcer as a reviewer.

---

## Pragmatic Enforcer Review Format

The Pragmatic Enforcer reviews each member's recommendations through a YAGNI (You Aren't Gonna Need It) lens.

### After Each Member's Review

Add this analysis section immediately following each member's recommendations:

```markdown
#### Pragmatic Enforcer Analysis

**Reviewer**: Pragmatic Enforcer
**Mode**: [Strict | Balanced | Lenient]

[For each recommendation from this member, apply pragmatic analysis]

##### Recommendation: [Recommendation Title]

**Necessity Assessment** (0-10):
- **Current need**: [Is this addressing a current, concrete problem?]
- **Future need**: [Likelihood and timeframe for actually needing this]
- **Cost of waiting**: [What breaks if we defer? What's the cost of implementing later?]
- **Evidence of need**: [What concrete evidence justifies this now?]
- **Score**: [X/10]

**Complexity Assessment** (0-10):
- **Added complexity**: [What complexity does this introduce?]
- **Maintenance burden**: [Ongoing cost to maintain this]
- **Learning curve**: [Impact on team understanding]
- **Dependencies introduced**: [New dependencies or abstractions]
- **Score**: [X/10]

**Simpler Alternative**:
[Propose a simpler approach that meets current actual requirements, or explain why this is already minimal]

**Pragmatic Recommendation**:
- ✅ **Implement now**: [Clear current need, appropriate complexity]
- ⚠️ **Simplified version**: [Implement minimal version, defer bells and whistles]
- ⏸️ **Defer**: [Wait for trigger conditions]
- ❌ **Skip**: [Not needed, over-engineering]

**Justification**: [Clear reasoning for recommendation]

**If Deferring**:
- **Trigger conditions**: [What would trigger implementing this?]
- **Minimal viable alternative**: [What's the simplest thing that could work now?]

**Pragmatic Score**:
- Necessity: [X/10]
- Complexity: [X/10]
- Ratio: [Complexity/Necessity = X.X]

**Target Ratios by Mode**:
- Strict: <1.0 (complexity should be less than necessity)
- Balanced: <1.5 (moderate complexity acceptable for clear need)
- Lenient: <2.0 (higher complexity tolerated for strategic value)

**Assessment**: [Appropriate engineering | Over-engineering | Under-engineering]
```

---

## Pragmatic Mode Intensity Levels

### Strict Mode (Ratio Target: <1.0)

**Philosophy**: Only implement what's absolutely necessary right now.

**Approach**:
- Challenge every abstraction
- Defer anything speculative
- Require concrete evidence of current need
- Favor simple, direct solutions
- Question best practices if not clearly applicable

**Use When**: Tight timeline, small team, MVP, prototyping

### Balanced Mode (Ratio Target: <1.5)

**Philosophy**: Implement current needs thoughtfully with reasonable future considerations.

**Approach**:
- Allow appropriate abstractions
- Defer obvious speculation
- Accept moderate complexity for clear benefits
- Balance pragmatism with code quality
- Apply best practices when they add clear value

**Use When**: Normal development, sustainable pace, balanced priorities

### Lenient Mode (Ratio Target: <2.0)

**Philosophy**: Allow strategic complexity for longer-term benefits.

**Approach**:
- Permit forward-looking designs
- Accept abstractions for anticipated growth
- Allow higher complexity for strategic value
- Consider longer time horizons
- Apply best practices proactively

**Use When**: Building platforms, long-term projects, infrastructure

---

## Examples of Pragmatic Analysis

### Example 1: Caching Layer Recommendation (Balanced Mode)

**Original Recommendation**: "Add Redis caching layer for all database queries"

**Pragmatic Analysis**:

**Necessity Assessment**: 7/10
- Current need: Page load times are 500ms, target is <200ms
- Future need: Traffic growing 20% monthly
- Cost of waiting: User experience degrading, churn risk
- Evidence: Metrics show 60% of queries are duplicate reads
- Score: 7/10

**Complexity Assessment**: 6/10
- Added complexity: New Redis dependency, cache invalidation logic
- Maintenance: Cache coherency, Redis ops, monitoring
- Learning curve: Team familiar with Redis
- Dependencies: Redis server, connection pooling
- Score: 6/10

**Simpler Alternative**:
Start with application-level caching (LRU cache in memory) for hot queries only. Add Redis when in-memory is insufficient.

**Pragmatic Recommendation**: ⚠️ **Simplified version**

**Justification**: Current need is clear (7/10) but complexity is moderate (6/10). Start simpler with in-memory caching for most impactful queries. This delivers 80% of benefit with 30% of complexity. Upgrade to Redis when evidence shows memory caching is insufficient.

**Pragmatic Score**:
- Necessity: 7/10
- Complexity: 6/10
- Ratio: 0.86 (<1.5 threshold = acceptable if simplified)

**Assessment**: Appropriate engineering with simplification

---

### Example 2: Microservices Architecture (Balanced Mode)

**Original Recommendation**: "Split monolith into 12 microservices"

**Pragmatic Analysis**:

**Necessity Assessment**: 3/10
- Current need: Monolith works, no deployment bottlenecks
- Future need: "Might scale better" - speculative
- Cost of waiting: None - can extract services when bottlenecks emerge
- Evidence: No concrete scaling problems, 2-person team
- Score: 3/10

**Complexity Assessment**: 9/10
- Added complexity: Service boundaries, inter-service communication, distributed tracing, API versioning
- Maintenance: 12 services to deploy, monitor, debug
- Learning curve: Team inexperienced with distributed systems
- Dependencies: Service mesh, API gateway, distributed monitoring
- Score: 9/10

**Simpler Alternative**:
Keep monolith. Extract services only when you have concrete evidence of bottlenecks. Start with 1-2 services for proven pain points.

**Pragmatic Recommendation**: ❌ **Skip**

**Justification**: Massive complexity (9/10) with minimal current need (3/10). This is premature optimization and over-engineering. Wait for actual scaling problems before adding distributed systems complexity.

**If Deferring**:
- **Trigger conditions**: Deploy time >30 min, scaling bottlenecks measured, >5 developers working in same code
- **Minimal alternative**: Keep monolith, use modules for internal boundaries

**Pragmatic Score**:
- Necessity: 3/10
- Complexity: 9/10
- Ratio: 3.0 (>> 1.5 threshold = over-engineering)

**Assessment**: Over-engineering - defer

---

### Example 3: Security Vulnerability Fix (Any Mode)

**Original Recommendation**: "Fix SQL injection vulnerability in login endpoint"

**Pragmatic Analysis**:

**Necessity Assessment**: 10/10
- Current need: Critical security vulnerability
- Future need: N/A - needed now
- Cost of waiting: Data breach, compliance violation
- Evidence: Security audit found SQL injection
- Score: 10/10

**Complexity Assessment**: 2/10
- Added complexity: Use parameterized queries (standard practice)
- Maintenance: Reduces maintenance risk
- Learning curve: None - team knows parameterized queries
- Dependencies: None
- Score: 2/10

**Simpler Alternative**: None - this IS the simple solution

**Pragmatic Recommendation**: ✅ **Implement now**

**Justification**: Critical necessity (10/10) with minimal complexity (2/10). No debate - implement immediately.

**Pragmatic Score**:
- Necessity: 10/10
- Complexity: 2/10
- Ratio: 0.2 (<< 1.5 threshold)

**Assessment**: Essential engineering

---

## Integration in Collaborative Discussion

During collaborative discussion, the Pragmatic Enforcer should:

1. **Challenge Complexity**: Question whether proposed solutions are minimal
2. **Require Evidence**: Ask for concrete evidence of need, not speculation
3. **Propose Simplifications**: Suggest simpler alternatives for consideration
4. **Balance Views**: Acknowledge when complexity is justified
5. **Set Priorities**: Help team focus on high-impact, low-complexity wins

### Example Discussion Snippet

```markdown
**Security Specialist**: "We should implement zero-trust architecture across all services."

**Pragmatic Enforcer**: "I see the security value, but that's significant complexity. What's the current threat? Can we start with authentication boundaries on public APIs first, then expand if we see attack patterns?"

**Security Specialist**: "Fair point. We have had unauthorized access attempts on the admin API but internal services haven't been targeted. Starting with API gateway auth would address 90% of current risk."

**Systems Architect**: "Agreed - that's a more measured approach. Zero-trust can be part of our roadmap once we have evidence it's needed."
```

---

## Exemptions from Pragmatic Analysis

Certain recommendations should NOT be challenged by pragmatic mode:

1. **Security Vulnerabilities**: Critical security fixes always implement
2. **Compliance Requirements**: Legal/regulatory requirements are non-negotiable
3. **Accessibility Issues**: User accessibility is not optional
4. **Data Loss Risks**: Anything preventing data loss is critical
5. **Explicit User Request**: If user specifically asked for something, honor it

**In config.yml**:
```yaml
pragmatic_mode:
  exemptions:
    - security
    - compliance
    - accessibility
    - data_loss_prevention
```

---

## Summary

Pragmatic mode adds a critical YAGNI perspective to architecture reviews:

- ✅ Prevents over-engineering
- ✅ Focuses team on current actual needs
- ✅ Identifies simpler alternatives
- ✅ Provides evidence-based decision framework
- ⚠️ Must be balanced with quality and foresight
- ⚠️ Not a blanket "no" to all abstractions

Use pragmatic analysis to ensure architecture reviews lead to appropriate, not excessive, engineering.
