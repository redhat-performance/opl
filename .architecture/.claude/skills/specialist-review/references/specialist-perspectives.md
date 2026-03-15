# Specialist Perspectives - Review Guidance

This document provides detailed guidance for conducting reviews from each specialist's unique perspective.

## Table of Contents

1. [General Review Approach](#general-review-approach)
2. [Core Specialists](#core-specialists)
3. [Technology Specialists](#technology-specialists)
4. [Creating New Specialists](#creating-new-specialists)

---

## General Review Approach

All specialist reviews should follow these principles:

### Stay Focused

**Do**:
- Laser-focus on your domain of expertise
- Deep-dive within your specialty
- Provide expert-level insights

**Don't**:
- Stray into other specialists' domains
- Provide surface-level general comments
- Dilute expertise by being too broad

### Be Specific

**Always include**:
- Exact file paths and line numbers
- Concrete code examples
- Specific recommendations

**Example**:
- ❌ "The authentication is insecure"
- ✅ "The authentication in `src/auth/login.ts:45` uses MD5 hashing, which is cryptographically broken. Migrate to bcrypt with salt rounds ≥12."

### Provide Context

**Explain**:
- Why this matters (impact)
- Industry standards or best practices
- Trade-offs of recommendations
- Effort required

### Be Actionable

**Every concern should include**:
- What's wrong
- Where it is (file:line)
- Impact if not fixed
- Specific fix with implementation approach
- Effort estimate

---

## Core Specialists

These specialists are part of the framework's core team.

### Security Specialist

**Role**: Identifies security vulnerabilities, threats, and risks.

**Focus Areas**:
- **Authentication**: Login mechanisms, password handling, session management
- **Authorization**: Access control, permissions, role-based access
- **Input Validation**: XSS, SQL injection, command injection prevention
- **Data Protection**: Encryption at rest/transit, PII handling, secrets management
- **OWASP Top 10**: Cross-check against current OWASP vulnerabilities
- **Compliance**: GDPR, HIPAA, PCI-DSS requirements
- **API Security**: Rate limiting, CORS, API keys, OAuth flows
- **Dependencies**: Known CVEs in libraries

**Review Checklist**:
- [ ] Authentication mechanism reviewed
- [ ] Authorization boundaries checked
- [ ] All user inputs validated
- [ ] Sensitive data encrypted
- [ ] Secrets not hardcoded
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Rate limiting implemented
- [ ] Dependencies scanned for CVEs

**Severity Levels**:
- **Critical**: Exploitable vulnerability, immediate data breach risk
- **High**: Security weakness requiring prompt attention
- **Medium**: Security concern to address in near term
- **Low**: Security improvement opportunity

**Example Concerns**:
```
1. **SQL Injection Vulnerability** (Severity: Critical)
   - **Issue**: User input directly interpolated into SQL query
   - **Location**: `src/db/users.js:23`
   - **Impact**: Attacker can read/modify/delete any database record
   - **Fix**: Use parameterized queries with prepared statements
   - **Code**:
     ```javascript
     // Current (VULNERABLE)
     const query = `SELECT * FROM users WHERE email = '${email}'`;

     // Recommended (SAFE)
     const query = 'SELECT * FROM users WHERE email = ?';
     db.query(query, [email]);
     ```
```

**Best Practices to Reference**:
- OWASP Secure Coding Practices
- CWE (Common Weakness Enumeration)
- NIST guidelines
- Industry security standards

---

### Performance Specialist

**Role**: Optimizes system performance, scalability, and resource utilization.

**Focus Areas**:
- **Query Optimization**: Database query efficiency, indexes, N+1 queries
- **Caching**: Cache strategies, TTL, invalidation, cache hits
- **Resource Utilization**: CPU, memory, disk I/O, network
- **Bottlenecks**: Profiling, hotspots, performance critical paths
- **Load Handling**: Concurrency, async operations, connection pooling
- **Scalability**: Horizontal/vertical scaling, load balancing
- **Frontend Performance**: Bundle size, lazy loading, rendering

**Review Checklist**:
- [ ] Database queries optimized
- [ ] Proper indexing in place
- [ ] N+1 query problems identified
- [ ] Caching opportunities evaluated
- [ ] Async operations for I/O
- [ ] Resource usage profiled
- [ ] Scalability concerns addressed
- [ ] Frontend bundle size reasonable

**Metrics to Measure**:
- Response time (p50, p95, p99)
- Throughput (requests/second)
- Database query time
- Cache hit rate
- Memory usage
- CPU utilization

**Example Concerns**:
```
1. **N+1 Query Problem** (Severity: High)
   - **Issue**: Loading users in loop triggers 1000+ database queries
   - **Location**: `src/controllers/orders.js:45-52`
   - **Impact**: 15-second page load time, database overload
   - **Fix**: Use eager loading to fetch all users in single query
   - **Code**:
     ```javascript
     // Current (INEFFICIENT - N+1 queries)
     const orders = await Order.findAll();
     for (const order of orders) {
       order.user = await User.findById(order.userId); // N queries!
     }

     // Recommended (EFFICIENT - 1 query)
     const orders = await Order.findAll({
       include: [{ model: User }]
     });
     ```
   - **Expected Improvement**: 15s → 0.3s (50x faster)
```

---

### Domain Expert

**Role**: Ensures architecture accurately represents business domain and concepts.

**Focus Areas**:
- **Domain Models**: Entities, value objects, aggregates
- **Business Logic**: Rules, workflows, calculations
- **Ubiquitous Language**: Consistent terminology
- **Bounded Contexts**: Clear domain boundaries
- **Business Rules**: Validation, invariants, constraints
- **Semantic Accuracy**: Code reflects domain accurately

**Review Checklist**:
- [ ] Domain concepts clearly modeled
- [ ] Business logic in domain layer (not scattered)
- [ ] Ubiquitous language used consistently
- [ ] Bounded contexts well-defined
- [ ] Business rules enforced
- [ ] Domain invariants protected

**Example Concerns**:
```
1. **Anemic Domain Model** (Severity: Medium)
   - **Issue**: `Order` class is data container with no business logic
   - **Location**: `src/models/Order.js`
   - **Impact**: Business logic scattered in controllers, hard to maintain
   - **Fix**: Move order calculation and validation into Order class
   - **Code**:
     ```javascript
     // Current (ANEMIC)
     class Order {
       constructor(items) {
         this.items = items;
       }
     }
     // Business logic in controller
     const total = order.items.reduce((sum, item) => sum + item.price, 0);

     // Recommended (RICH DOMAIN MODEL)
     class Order {
       constructor(items) {
         this.items = items;
       }

       calculateTotal() {
         return this.items.reduce((sum, item) => sum + item.price, 0);
       }

       applyDiscount(discount) {
         if (discount < 0 || discount > 1) {
           throw new InvalidDiscountError();
         }
         // Domain logic stays with domain object
       }
     }
     ```
```

---

### Maintainability Expert

**Role**: Ensures code is maintainable, evolvable, and understandable.

**Focus Areas**:
- **Code Quality**: Readability, clarity, simplicity
- **Technical Debt**: Code smells, anti-patterns, cruft
- **Documentation**: Comments, READMEs, inline docs
- **Testability**: Unit tests, test coverage, mocking
- **Complexity**: Cyclomatic complexity, coupling, cohesion
- **Refactoring**: Opportunities to improve structure

**Review Checklist**:
- [ ] Code is readable and clear
- [ ] Functions/methods are focused
- [ ] Complexity is reasonable
- [ ] Technical debt identified
- [ ] Tests exist and are meaningful
- [ ] Documentation is adequate
- [ ] Code smells flagged

**Code Smells to Watch For**:
- Long methods (>20-30 lines)
- Large classes (>300 lines)
- Deep nesting (>3 levels)
- Duplicate code
- Magic numbers
- God objects
- Feature envy

**Example Concerns**:
```
1. **God Class Anti-pattern** (Severity: Medium)
   - **Issue**: `UserService` has 45 methods handling auth, profile, notifications, billing
   - **Location**: `src/services/UserService.js` (1,200 lines)
   - **Impact**: Hard to understand, test, modify; violates single responsibility
   - **Fix**: Split into focused services
   - **Recommended Structure**:
     ```
     src/services/
     ├── AuthenticationService.js    (login, logout, sessions)
     ├── UserProfileService.js       (profile CRUD)
     ├── NotificationService.js      (user notifications)
     └── BillingService.js           (user billing)
     ```
   - **Benefit**: Each service <300 lines, single responsibility, easier testing
```

---

### Systems Architect

**Role**: Evaluates overall system coherence, patterns, and architectural decisions.

**Focus Areas**:
- **Architecture Patterns**: MVC, CQRS, Event Sourcing, Microservices
- **Component Interaction**: How pieces fit together
- **Separation of Concerns**: Proper layering and boundaries
- **Scalability**: System design for growth
- **Integration**: External system connections
- **Consistency**: Architectural principles applied consistently

**Review Checklist**:
- [ ] Architecture pattern appropriately applied
- [ ] Components properly separated
- [ ] Dependencies flow correctly
- [ ] Scalability considered
- [ ] Integration points well-designed
- [ ] Architectural principles followed

---

### AI Engineer

**Role**: Reviews AI/ML integration, LLM applications, and agent systems.

**Focus Areas**:
- **LLM Integration**: Prompt design, context management, token efficiency
- **Agent Orchestration**: Multi-agent coordination, task decomposition
- **Evaluation**: Metrics, benchmarks, quality assessment
- **Observability**: Logging, tracing, debugging AI behavior
- **RAG Systems**: Retrieval strategies, context relevance
- **Prompt Engineering**: Template design, chain-of-thought, few-shot

**Review Checklist**:
- [ ] Prompts are well-designed and tested
- [ ] Context windows managed efficiently
- [ ] Evaluation metrics defined
- [ ] Observability implemented
- [ ] Error handling for AI failures
- [ ] Cost management (token usage)

---

## Technology Specialists

Add these when reviewing technology-specific code.

### JavaScript Expert

**Focus**: Modern JavaScript/TypeScript, async patterns, ES6+, Node.js

**Key Areas**:
- Promises, async/await usage
- Error handling patterns
- Module system (ESM/CommonJS)
- TypeScript type safety
- Memory leaks in closures
- Event loop understanding

**Common Issues**:
- Unhandled promise rejections
- Callback hell
- Blocking the event loop
- Type assertions bypassing safety
- Improper this binding

---

### Python Expert

**Focus**: Pythonic code, PEP compliance, async patterns

**Key Areas**:
- PEP 8 style compliance
- Type hints (mypy)
- Generator/iterator usage
- Context managers
- Async/await patterns
- Package structure

**Common Issues**:
- Non-Pythonic code
- Mutable default arguments
- Global state misuse
- Blocking I/O in async code
- Import cycles

---

### Ruby Expert

**Focus**: Ruby idioms, Rails conventions, metaprogramming

**Key Areas**:
- Ruby idioms and patterns
- Rails conventions
- Metaprogramming (when/when not)
- ActiveRecord usage
- Gem dependencies
- RuboCop compliance

**Common Issues**:
- Fighting Rails conventions
- N+1 queries in ActiveRecord
- Overuse of metaprogramming
- Callback hell in models
- Fat controllers

---

### Go Expert

**Focus**: Idiomatic Go, concurrency, simplicity

**Key Areas**:
- Goroutines and channels
- Error handling (not panic)
- Interface design
- Context usage
- Standard library preference
- Concurrency patterns

**Common Issues**:
- Goroutine leaks
- Ignoring errors
- Overuse of interfaces
- Improper context propagation
- Not following Go conventions

---

### Rust Expert

**Focus**: Ownership/borrowing, memory safety, zero-cost abstractions

**Key Areas**:
- Ownership rules
- Lifetime annotations
- Error handling (Result)
- Unsafe code justification
- Async Rust patterns
- Zero-copy optimizations

**Common Issues**:
- Fighting the borrow checker
- Unnecessary clones
- Unsafe code without documentation
- Blocking in async functions
- Not leveraging zero-cost abstractions

---

## Creating New Specialists

When a specialist doesn't exist in `.architecture/members.yml`:

### Step 1: Define the Specialist

Create a new member entry:

```yaml
- id: [specialist_id]  # e.g., graphql_specialist
  name: "[Person Name]"
  title: "[Specialist Title]"
  specialties:
    - "[Primary specialty]"
    - "[Secondary specialty]"
    - "[Tertiary specialty]"
  disciplines:
    - "[Discipline 1]"
    - "[Discipline 2]"
  skillsets:
    - "[Skill 1]"
    - "[Skill 2]"
  domains:
    - "[Domain 1]"
    - "[Domain 2]"
  perspective: "[One sentence describing their unique viewpoint]"
```

### Step 2: Define Their Focus

Document what this specialist reviews:
- Primary focus areas
- Key concerns
- Review checklist
- Common issues
- Best practices to reference

### Step 3: Add to Team

Update `.architecture/members.yml` with the new specialist.

Inform user: "I've added [Name] ([Title]) to your architecture team."

---

## Review Quality Guidelines

### Excellent Reviews Include

1. **Specific Issues**: File paths, line numbers, code snippets
2. **Impact Analysis**: Why it matters, what breaks if not fixed
3. **Concrete Solutions**: Exact recommendations with code examples
4. **Effort Estimates**: Small/Medium/Large for each recommendation
5. **Priority**: Critical/High/Medium/Low severity
6. **Context**: Industry standards, best practices cited
7. **Trade-offs**: Acknowledge when recommendations have costs

### Avoid

1. **Vague Concerns**: "Code is messy" → Be specific
2. **Out of Domain**: Security specialist shouldn't review performance
3. **Surface-Level**: Provide deep expert-level insights
4. **No Solutions**: Every concern needs actionable fix
5. **Missing Context**: Explain why, not just what

---

## Reference Templates

For the complete review document structure, see [../assets/specialist-review-template.md](../assets/specialist-review-template.md).

For member YAML format, see the setup-architect skill's member template.
