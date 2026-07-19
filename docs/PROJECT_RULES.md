# CampusFlow Project Rules

This document is the engineering rulebook for CampusFlow. It defines the architecture, development standards, and operational expectations for the platform. Every AI-generated addition, implementation, or change must follow these rules.

## 1. Project Philosophy

CampusFlow is NOT a registration website.
CampusFlow is NOT a landing page.
CampusFlow is NOT a single-event project.

CampusFlow is a reusable, extensible Event Management Platform built for colleges. Pragyarambh '26 is the first event on the platform, not the only event. Every feature must be designed to support multiple future events, multiple organizers, and multiple campuses without changing the core architecture.

The platform should be thought of as a product foundation, not an event-specific microsite. That means every interface, data model, API route, and workflow should be built with configurability, reuse, and event-agnostic behavior in mind.

## 2. Engineering Principles

### Simplicity over cleverness
Choose the simplest solution that solves the problem. Avoid clever tricks that make the code hard to understand or maintain.

### Readability over shortcuts
Readable code is easier to review, debug, and extend. Prefer clarity and explicitness over terse or obscure syntax.

### Reusability over duplication
Avoid duplicate logic. Build reusable modules, components, and services so features can share infrastructure and behavior.

### Composition over complexity
Compose small, single-purpose pieces rather than building complex monolithic structures. Small building blocks are easier to test and reuse.

### Accessibility first
Always design and build with accessibility in mind. Every UI element, interaction, and flow should be usable by people with disabilities.

### Mobile first
Design and implement for mobile devices first, then scale up for larger screens. The mobile experience is the priority.

### Performance first
Optimize for speed and efficiency from the start. Prioritize fast load times, efficient data access, and low resource usage.

### Security by design
Treat security as a foundational requirement, not an afterthought. Validate inputs, enforce access control, and protect sensitive data.

### Progressive enhancement
Build experiences that work in simple form first, then enhance them for richer devices and environments.

### Convention over configuration
Favor consistent patterns and agreed conventions over custom configurations. Consistency reduces mistakes and accelerates onboarding.

## 3. Coding Standards

### Naming
Use clear, descriptive names for variables, functions, components, services, and files.
- Prefer nouns for types and components.
- Prefer verbs for actions and functions.
- Use consistent naming conventions across the codebase.

### Formatting
Follow consistent formatting rules across languages. Keep line lengths reasonable and preserve readable indentation. Use the existing formatter and linter configuration in the repository.

### Imports
Group imports logically: external libraries first, internal modules next, relative imports last. Avoid deeply nested relative paths by using aliases where available.

### File organization
Place files according to feature and layer. Keep related code together and avoid wide file scattering. Files should be small enough to understand quickly.

### Comments
Write comments only when they add value. Prefer clear code over comments. Use comments to explain why something exists or to clarify non-obvious decisions, not to describe what the code already expresses.

### Functions
Keep functions focused and short. Each function should do one thing. Avoid long parameter lists and prefer small helper functions when needed.

### Components
Build components with a single responsibility. Avoid components that manage unrelated concerns.

### Constants
Use named constants for repeated values, especially strings, numbers, and configuration values. Keep constants in a dedicated module when they are shared.

### Utilities
Centralize shared utilities and helpers. Avoid utility functions that are only used once unless they improve readability significantly.

### Magic numbers / strings
Avoid hardcoded values. Extract repeated values into named constants or configuration. If a value is truly one-off and obvious, document it with a short comment.

### When comments should exist
- To explain business intent or domain context.
- To document non-obvious behavior or edge-case handling.
- To clarify trade-offs or why an alternate solution was rejected.

### When comments should not exist
- To restate obvious code behavior.
- To compensate for unclear names or structure.
- To describe temporary or abandoned code without cleanup.

## 4. React Standards

### Component size
Keep components small and focused. Prefer composition of smaller presentational pieces over large container components.

### Component responsibilities
Each component should have a single responsibility: present content, manage layout, or orchestrate behavior.

### Hooks
Use hooks for stateful logic and side effects. Keep hook usage clear and avoid overusing custom hooks for trivial logic.

### Props
Pass only the data and callbacks a component needs. Keep props predictable and avoid passing large objects unless they represent a coherent domain model.

### State management
Local component state when state is isolated. Shared state only when multiple components require it. Prefer simple state containers and avoid global state unless necessary.

### Context usage
Use context for global, application-wide concerns such as theme, auth, or configuration. Avoid using context for local state that can be passed via props.

### Memoization
Use memoization only where it solves real performance problems. Prefer clean data flow over premature optimization.

### Performance
Avoid unnecessary re-renders by controlling props and state carefully. Use keys correctly, avoid passing new object literals when not needed, and keep components pure where possible.

### Avoid unnecessary re-renders
Keep components stable by minimizing prop churn. Use memoization and callback hooks judiciously, but only when they improve actual performance.

## 5. FastAPI Standards

### Routers
Organize routes by feature and version. Each router should be narrow in scope and include only related endpoints.

### Services
Keep business logic in service modules, not in route handlers. Routers should orchestrate request parsing, service invocation, and response formation.

### Dependencies
Use FastAPI dependencies to manage shared resources, database sessions, authentication, and request context.

### Authentication
Centralize authentication logic and avoid duplicating it across routes. Protect sensitive endpoints and verify access consistently.

### Validation
Use Pydantic models for request validation and response schemas. Validate inputs explicitly and fail fast on invalid data.

### Error handling
Handle errors gracefully. Return meaningful HTTP status codes and error messages without exposing internal details.

### Response models
Use explicit response models for API outputs. Keep response shape stable and predictable.

### Business logic separation
Do not place domain rules in API handlers. Keep domain logic in services, repositories, or application layers.

### Security
Validate all inputs, enforce authorization checks, and avoid trust in client-provided data.

### Clean architecture
Maintain a clear separation between API, service, data, and domain layers. Each layer should have a distinct responsibility.

## 6. Database Rules

### Use PostgreSQL
PostgreSQL is the only supported production database.

### Naming
Use clear, consistent naming conventions for tables, columns, indexes, and constraints. Prefer snake_case for database objects.

### Relationships
Model relationships explicitly. Use foreign keys and join tables for many-to-many relationships.

### Indexes
Add indexes on search and filtering fields. Avoid unnecessary indexes, but ensure queries are fast for common use cases.

### Constraints
Enforce data integrity with NOT NULL, unique constraints, foreign keys, and check constraints.

### Timestamps
Track created_at and updated_at for all major entities. Use UTC consistently.

### Soft deletes
Implement soft deletes for records that may need to be restored or audited, using a deleted_at timestamp rather than physical deletion.

### UUID usage
Use UUIDs for primary keys on public-facing or distributed entities. Use integer surrogate keys only when there is a strong performance or domain reason.

### Migration strategy
Use Alembic for schema migrations. Keep migrations small, explicit, and reversible. Never edit applied migration history.

### Normalization
Model data to avoid unnecessary duplication. Prefer normalized schemas while balancing query simplicity for performance-critical views.

## 7. API Design Rules

### REST endpoints
Design APIs as resource-based REST endpoints. Use nouns for resources and avoid action verbs in URL paths.

### Status codes
Use standard HTTP status codes consistently: 200 for success, 201 for created, 400 for client errors, 401 for unauthorized, 403 for forbidden, 404 for not found, 422 for validation errors, 500 for server errors.

### Pagination
Always paginate list results. Use cursor or page-based pagination consistently across endpoints.

### Filtering
Support filtering with clear query parameters. Keep filters predictable and documented.

### Sorting
Allow sorting by relevant fields with an explicit parameter. Default to a reasonable stable sort.

### Searching
Provide search capabilities where needed. Keep search query semantics simple and consistent.

### Versioning
Version APIs from the start. Keep versioning in the URL path and avoid breaking changes without a new version.

### Error responses
Return structured error responses with a status code, error type, and user-friendly message.

### Validation
Validate request payloads and query parameters at the API boundary.

### Response consistency
Keep response shapes consistent across related endpoints. Use shared response models where possible.

## Documentation Governance

- Every new feature must first update the relevant documentation before implementation begins.
- Documentation is the single source of truth.
- Code must follow documentation—not the other way around.
- Breaking architectural decisions require updating the appropriate document first.
- AI tools (GitHub Copilot, ChatGPT, etc.) must treat these documents as authoritative.

## 8. UI Rules

The UI must always follow:
- `DESIGN_SYSTEM.md`
- `LANDING_PAGE_UX.md`
- `LANDING_PAGE_UI_SPEC.md`

Never invent new colors.
Never invent spacing.
Never invent typography.
Never ignore the design system.

The design system is the source of truth. Every component, layout, and interaction should align with its rules.

## 9. Component Rules

Every reusable component should support:
- Loading State
- Empty State
- Success State
- Error State
- Disabled State
- Responsive Layout
- Accessibility
- Keyboard Navigation

Why:
Reusable components must behave predictably across contexts. Supporting these states ensures they work for all users and all data conditions.

## 10. Animation Rules

Animations must:
- Be subtle
- Be under 250ms
- Never block interaction
- Never reduce readability
- Respect reduced-motion settings

### Animation philosophy
Motion should enhance clarity and feel premium. Use it sparingly to guide attention, not to entertain. Respect accessibility preferences and avoid motion that distracts or causes discomfort.

## 11. Accessibility Rules

Accessibility is mandatory.

### Keyboard navigation
All interactive elements must be reachable and operable by keyboard.

### ARIA
Use ARIA attributes only when necessary and always in a correct, semantic way.

### Contrast
Ensure text and interactive elements meet accessibility contrast requirements.

### Focus
Provide visible focus styles for keyboard users.

### Touch targets
Interactive targets must be large enough for touch interactions.

### Semantic HTML
Use semantic markup for structure and meaning.

### Screen readers
Support screen readers with meaningful labels and content structure.

### Color independence
Do not rely on color alone to convey information.

### Reduced motion
Respect user preferences for reduced motion.

### Form validation
Make form errors clear, persistent, and accessible.

## 12. Performance Rules

### Lazy loading
Load non-critical assets and modules lazily.

### Image optimization
Optimize images for web delivery and use modern formats when possible.

### Route splitting
Split code by route or feature to reduce initial bundle size.

### Memoization
Memoize expensive calculations and stable component props only when needed.

### Caching
Cache API responses and assets where appropriate.

### Bundle size
Keep the bundle small and avoid pulling in large dependencies unnecessarily.

### Avoid unnecessary dependencies
Evaluate new libraries carefully. Prefer built-in solutions when they are sufficient.

### Performance budgets
Establish realistic performance budgets and keep the platform within them.

### Performance-first thinking
Design with speed in mind. Fast experiences improve adoption and retention.

## 13. Security Rules

### Authentication
Use secure authentication mechanisms and protect user sessions.

### Authorization
Enforce authorization checks on every request.

### Password hashing
Use a strong hashing algorithm and never store plaintext passwords.

### JWT
Use JWT tokens securely with proper expiration and storage.

### CSRF
Protect state-changing endpoints from CSRF attacks.

### XSS
Sanitize user input and escape output in all rendered contexts.

### SQL Injection
Never concatenate SQL strings with user input. Use parameterized queries or ORM protections.

### Rate limiting
Protect public endpoints from abuse with rate limiting or throttling.

### Input validation
Validate all input on the server side.

### Secrets management
Keep secrets in secure configuration stores. Never commit secrets to source control.

### Never trust user input
Treat all external input as untrusted. Validate, sanitize, and enforce boundaries.

## 14. Git Standards

### Branch naming
Use descriptive branch names such as `feature/<name>`, `fix/<name>`, or `chore/<name>`.

### Commit messages
Write clear, concise commit messages. Prefer conventional commit style.

### Pull request expectations
Each PR should have a clear summary, linked issue or task, and testing notes.

### Review checklist
Review for correctness, readability, testing coverage, and alignment with standards.

### Versioning
Use semantic versioning for releases where applicable.

### Release strategy
Plan releases around features and fixes. Keep release notes clear and actionable.

### Conventional commits
Follow conventional commit style for consistency and automation.

## 15. Documentation Rules

Every feature must include:
- Purpose
- Flow
- Dependencies
- Future improvements
- Known limitations

Document architectural decisions and keep documentation current. The repository should remain understandable to new team members.

## 16. Error Handling Philosophy

Errors should:
- Be descriptive
- Be user-friendly
- Never expose internal details
- Always be logged
- Support recovery

User-facing errors should explain what happened and how to proceed. Internal errors should capture enough context for debugging without leaking sensitive data.

## 17. Logging Rules

Differentiate log levels:
- Info: normal application flow.
- Warning: unexpected conditions that do not stop execution.
- Error: failures that require attention.
- Critical: system-level failures.

Never log sensitive data. Logs should support diagnosis without exposing credentials or personal information.

## 18. Testing Philosophy

### Unit Tests
Cover individual units of logic and components.

### Integration Tests
Validate behavior across modules, services, and data flows.

### End-to-End Tests
Simulate real user journeys for critical flows.

### Manual QA
Use manual verification for usability and edge cases.

### Accessibility Testing
Include accessibility checks as part of testing.

### Performance Testing
Validate that the application performs acceptably under expected conditions.

Testing is essential. Build confidence through automated coverage and manual validation.

## 19. Future Scalability

Design everything assuming:
- Multiple colleges
- Multiple organizers
- Thousands of users
- Concurrent registrations
- QR-based entry
- Digital passes
- Certificates
- Payments
- Analytics
- Notifications
- Volunteer management
- Sponsor management
- Future mobile application

Never hardcode assumptions for Pragyarambh. Build the platform as a reusable product that can support multiple events, institutions, and evolving requirements.

## 20. AI Development Rules

These rules apply to GitHub Copilot and any AI assistant.

AI must:
- Never generate duplicate logic.
- Never ignore the design system.
- Never create unnecessary complexity.
- Never introduce new libraries without justification.
- Never hardcode values that belong in configuration.
- Always prefer reusable components.
- Always explain architectural decisions when introducing major changes.
- When uncertain, preserve consistency with the existing codebase instead of inventing new patterns.

AI-generated contributions should be conservative, consistent, and aligned with existing standards.

## Final Engineering Philosophy

CampusFlow should feel like a production-grade software product in every detail. It should be maintainable, scalable, consistent, and high quality. Developers working on it should feel supported by clear rules, predictable patterns, and a shared vision.

This platform should deliver a strong developer experience: easy to understand, easy to extend, and easy to trust. Engineers should be able to build new events, workflows, and interfaces without reinventing the foundation.

Quality should not be optional. Every change should preserve the platform’s long-term sustainability and support future growth. CampusFlow should be a dependable platform that can evolve gracefully from Pragyarambh '26 to the next campus event and beyond.