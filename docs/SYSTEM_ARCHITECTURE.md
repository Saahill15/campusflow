# CampusFlow System Architecture

This document describes how CampusFlow is architected as a scalable, reusable Event Management Platform for colleges. It explains the system structure, responsibilities of each layer, core flows, security posture, and architectural decisions.

## 1. Architecture Philosophy

CampusFlow is designed as a modular platform, not a single-event solution. Modularity enables the platform to evolve, reuse capabilities, and adapt to new event formats without reworking the core.

### Why modular?
A modular system isolates features, reduces coupling, and allows teams to evolve individual capabilities independently. It supports cleaner boundaries between UI, business logic, and data.

### Why feature-first architecture?
Feature-first architecture organizes code and services around the product domain, not technical layers. This approach keeps event-related behavior and workflows coherent as the platform grows.

### Why separation of concerns?
Separation of concerns makes the system easier to understand, maintain, and extend. UI, API, services, persistence, and external integrations each have distinct responsibilities.

### Why scalability matters?
CampusFlow must support multiple events, organizers, and institutions. Scalability ensures the platform can handle concurrent registrations, attendance verification, analytics, and future mobile usage without becoming fragile.

## 2. High-Level Architecture

### System flow
Browser
↓
React + Vite
↓
API Gateway
↓
FastAPI
↓
Service Layer
↓
Repository Layer
↓
PostgreSQL
↓
External Services

### Responsibilities
- Browser: client-side rendering, user interaction, offline-aware UI.
- React + Vite: fast development, modular frontend architecture, optimized builds.
- API Gateway: request handling, authentication, rate limiting, routing.
- FastAPI: HTTP API surface, request validation, dependency injection.
- Service Layer: domain orchestration, business logic, feature workflows.
- Repository Layer: data access, persistence abstractions, query management.
- PostgreSQL: durable relational storage, transactional integrity, event data modeling.
- External Services: email, cloud storage, analytics, notifications, hosted infrastructure.

## 3. Frontend Architecture

### Pages
Pages represent top-level routes and application screens. They map to major platform views such as event discovery, event details, registration, dashboard, and admin sections.

### Layouts
Layouts define shared page structure and common UI patterns, such as authenticated shells, event pages, and admin layouts.

### Components
Components are reusable UI building blocks: buttons, cards, forms, modals, and navigation.

### Hooks
Hooks encapsulate reusable client-side behavior, such as data fetching, form state, API integration, and session handling.

### Contexts
Contexts provide application-wide state for auth, theme, event context, and shared configuration.

### Services
Frontend services abstract API interaction, client-side caching, and transformation of backend responses.

### Utilities
Utilities include formatting helpers, validation helpers, and small shared functions used across the UI.

### Assets
Assets include images, icons, fonts, and static metadata. They are managed separately from application logic.

### Routing
Client-side routing defines page navigation, protected route guards, and deep-linked event pages.

### State Management
State is primarily managed locally and via context for shared application state. Global state is kept minimal and synchronized with backend data.

## 4. Backend Architecture

### Routers
Routers define the API endpoints grouped by feature and version. They keep the API surface organized and extensible.

### Controllers
Controllers translate request data into service calls and format responses. They remain thin and focused on API concerns.

### Services
Service modules contain business logic and workflows. They orchestrate domain behavior such as registration, attendance tracking, and notifications.

### Repositories
Repositories handle persistence, abstract SQLAlchemy access, and encapsulate data queries.

### Schemas
Pydantic schemas validate request payloads and define response shapes. They enforce API contracts.

### Models
SQLAlchemy models define the persistent data structure and relationships for core entities.

### Dependencies
Dependencies manage reusable request-scoped resources such as database sessions, current user context, and configuration.

### Authentication
JWT authentication secures the backend API and validates user identity for protected routes.

### Middleware
Middleware handles cross-cutting concerns: authentication, logging, request validation, metrics, and error mapping.

### Background Tasks
Background tasks manage asynchronous work such as sending emails, generating passes, and processing analytics events.

## 5. Database Architecture

### Core Entities
Core entities include events, users, registrations, passes, QR codes, attendance records, volunteers, committees, sponsors, notifications, and certificates.

### Relationships
Relationships are explicit and normalized. Events connect to organizers, attendees, volunteer assignments, and venue data. Registrations link users to events.

### Ownership
Ownership models define who controls events and resources: college admins own institutions, organizers own events, and committee heads own committees.

### Audit Fields
Entities include audit fields such as created_at, updated_at, created_by, and updated_by to support traceability.

### Soft Deletes
Use soft deletes for recoverable entities. Soft delete fields such as deleted_at preserve history without removing records.

### Indexes
Indexes support event discovery, registration lookups, QR validation, and reporting queries. Critical filters and joins are indexed.

### UUID Strategy
Use UUIDs for primary keys on public and distributed entities to avoid leakage and support multi-tenant scaling.

### Migration Strategy
Use Alembic for schema migrations. Maintain migration history in source control and keep changes incremental and reversible.

## 6. Authentication Flow

### Guest
A guest can browse public event info without authenticating.

### Signup
Guests sign up with email and password or an equivalent enrollment path.

### Email Verification
After sign-up, users receive a verification step to confirm their identity.

### Login
Verified users log in with credentials.

### JWT
Successful login issues a JWT for API authentication.

### Refresh Token
Use refresh tokens to renew access tokens securely without forcing frequent re-login.

### Protected Routes
Protected routes validate JWTs and enforce authorization based on role and permissions.

## 7. Registration Flow

### Student
A registered student initiates the flow.

### Open Event
The student views event details and eligibility.

### Register
The student submits a registration request.

### Payment
If required, the student completes payment through a secure flow.

### Pass Generation
Upon successful registration, the system generates a digital pass.

### QR Code
The pass includes a unique QR code for check-in.

### Email
The student receives confirmation and pass details via email.

### Dashboard
The student can view registration status and event passes from their dashboard.

## 8. Event Management Flow

### Organizer
Organizers interact with event management tools.

### Create Event
An organizer creates event details, capacity, and schedule.

### Publish
The organizer publishes the event to make it discoverable.

### Manage Registrations
The organizer monitors registrations and manages attendee lists.

### Announcements
The organizer sends updates to registered attendees.

### Analytics
The organizer reviews registration and attendance metrics.

## 9. QR Verification Flow

### Scan
A volunteer or staff member scans a pass QR code.

### Validate
The system validates the QR code against registration and pass status.

### Attendance
Successful validation marks attendance.

### Duplicate Prevention
The system detects repeated scans and prevents double entry.

### Success
A confirmation is provided to the verifier and attendee.

## 10. Notification Architecture

### Email
Email is the primary notification channel for confirmations, reminders, and updates.

### Push (Future)
Future push notifications can deliver event reminders and real-time updates.

### SMS (Future)
Future SMS support can provide critical alerts and verification codes.

### In-app
In-app notifications support announcements and status updates within the UI.

## 11. Storage Architecture

### Images
Store event and gallery images in cloud storage.

### Payment Proof
Store payment-related documents and receipts securely.

### Certificates
Generate certificates and store them as downloadable assets.

### Passes
Store generated digital passes and QR payloads.

### QR Codes
Persist QR code metadata for verification and auditing.

### Event Assets
Store event-related files, brochures, and display assets.

## 12. Security Architecture

### Authentication
Use JWT for stateless authentication and secure API access.

### Authorization
Implement role-based access control for restricted actions.

### RBAC
Enforce permissions based on user role: student, volunteer, organizer, admin.

### Rate Limiting
Apply rate limits to protect APIs from abuse.

### Validation
Validate all input at the API boundary.

### Encryption
Encrypt sensitive data in transit and at rest where required.

### Secrets
Store secrets securely in managed environment variables and secret stores.

### Audit Logs
Capture audit logs for key actions, especially event and registration management.

## 13. Scalability Strategy

### Horizontal Scaling
Design servers and services to scale horizontally behind load balancers.

### Caching
Cache frequently accessed data and responses where appropriate.

### Async Tasks
Move non-critical work to asynchronous background tasks.

### Pagination
Paginate list endpoints to avoid large payloads.

### Queue System (Future)
Introduce queueing for heavy workflows like notifications and reporting.

### CDN
Use a CDN for frontend assets and static content.

## 14. Monitoring

### Logging
Capture structured logs for API requests, errors, and business events.

### Metrics
Collect metrics for performance, usage, and reliability.

### Error Tracking
Use error tracking to surface exceptions and operational issues.

### Health Checks
Implement health checks for frontend, backend, and external dependencies.

### Performance Monitoring
Monitor latency, throughput, and resource usage.

## 15. Deployment Architecture

### Development
A local development stack supports frontend, backend, and database environments.

### Staging
A staging environment mirrors production for validation and testing.

### Production
Production runs on Vercel for the frontend and Render for the backend, using Neon PostgreSQL for the database.

### CI/CD
Continuous integration validates builds and tests before deployment.

### Environment Variables
Use environment variables for configuration and environment-specific settings.

### Secrets Management
Store secrets securely and avoid committing sensitive information.

## 16. Future Expansion

### Mobile App
Future mobile applications will consume the same backend APIs and share authentication flows.

### Microservices (if needed)
If complexity grows, split domain areas into services while preserving data consistency.

### GraphQL (future)
Evaluate GraphQL for optimized data fetching if frontends demand it.

### Public API
Expose a public API for partner integrations and college systems.

### College Federation
Enable federated colleges with separate event catalogs and shared identity.

### Sponsor Portal
Offer sponsors a dedicated interface for partnerships and analytics.

### Volunteer App
Create a volunteer mobile interface for task management and event check-in.

## 17. Architecture Decision Records (ADR)

### ADR: Why React + Vite
- Decision: use React with Vite for the frontend.
- Context: frontend needs modern, lightweight tooling and fast developer feedback.
- Alternatives considered: Next.js, CRA, Svelte.
- Reason for selection: Vite offers minimal configuration, fast hot reload, and modern build output while React provides component reusability.
- Consequences: the frontend remains decoupled from backend rendering and can deploy independently.

### ADR: Why FastAPI
- Decision: use FastAPI for the backend.
- Context: backend needs a fast, Python-based API framework with strong typing.
- Alternatives considered: Flask, Django, Express.
- Reason for selection: FastAPI provides request validation, dependency injection, async support, and excellent developer ergonomics.
- Consequences: the API is maintainable and capable of scaling with async workloads.

### ADR: Why PostgreSQL
- Decision: use PostgreSQL for persistence.
- Context: event data requires transactional integrity, relational modeling, and reliability.
- Alternatives considered: MySQL, MariaDB, NoSQL.
- Reason for selection: PostgreSQL is robust, supports complex queries, and is a strong fit for relational event and user data.
- Consequences: the platform gains a stable database foundation with rich indexing and transaction support.

### ADR: Why SQLAlchemy
- Decision: use SQLAlchemy as the ORM.
- Context: backend needs a mature Python ORM with support for PostgreSQL.
- Alternatives considered: raw SQL, Tortoise ORM, Django ORM.
- Reason for selection: SQLAlchemy provides explicit control over queries, a broad community, and compatibility with Alembic migrations.
- Consequences: database access remains powerful and explicit without losing ORM convenience.

### ADR: Why JWT Authentication
- Decision: use JWT for authentication.
- Context: platform requires stateless session handling across frontend and backend.
- Alternatives considered: session cookies, OAuth, API keys.
- Reason for selection: JWT supports a clean token-based flow suitable for single-page apps and mobile clients.
- Consequences: token management and refresh must be handled securely.

### ADR: Why Feature-Based Folder Structure
- Decision: organize code by feature rather than layer.
- Context: the platform will grow with many event-related capabilities.
- Alternatives considered: layered structure.
- Reason for selection: feature-based structure keeps related code together and eases onboarding.
- Consequences: teams can iterate on features with less cross-folder context switching.

### ADR: Why Modular Services
- Decision: build services as modular domains.
- Context: event management includes multiple workflows and business rules.
- Alternatives considered: a monolithic service layer.
- Reason for selection: modular services improve maintainability and allow incremental expansion.
- Consequences: the platform can evolve without massive rewrites.

### ADR: Why UUID Primary Keys
- Decision: use UUIDs for primary keys.
- Context: the platform may support distributed events and multitenancy.
- Alternatives considered: integer IDs.
- Reason for selection: UUIDs avoid collision and support distributed creation patterns.
- Consequences: primary keys are stable and globally unique, though they are less human-friendly.

### ADR: Why Neon PostgreSQL
- Decision: use Neon for PostgreSQL hosting.
- Context: the platform needs a managed, cloud-native database service.
- Alternatives considered: AWS RDS, Azure Database for PostgreSQL.
- Reason for selection: Neon offers serverless scaling, strong compatibility, and modern cloud storage separation.
- Consequences: database infrastructure is managed and can scale with event load.

### ADR: Why Vercel + Render
- Decision: host frontend on Vercel and backend on Render.
- Context: the platform requires streamlined deployment for both UI and API.
- Alternatives considered: Netlify, AWS Elastic Beanstalk, DigitalOcean.
- Reason for selection: Vercel and Render provide strong hosting for frontend and backend with minimal DevOps overhead.
- Consequences: the architecture remains decoupled and deployment pipelines are simplified.

## Final Architecture Philosophy

CampusFlow should evolve from a single college event platform into a scalable, multi-tenant ecosystem. The architecture should remain modular, with clear boundaries between frontend, backend, data, and external services. It should support multiple colleges, multiple events, and multiple user roles without sacrificing clarity or performance.

The platform should feel resilient to change. New event types, notification channels, or mobile clients should plug into the existing architecture rather than force a redesign. The system should prioritize reliable data flow, secure authentication, and reusable services.

Over time, CampusFlow should become the platform that colleges trust for event operations, while still being easy for developers to extend. It should balance a product mindset with engineering discipline: simple where possible, modular where necessary, and always built with the next stage of growth in mind.