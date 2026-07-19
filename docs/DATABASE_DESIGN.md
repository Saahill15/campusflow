# CampusFlow Database Design

This document describes the PostgreSQL database design for CampusFlow, a reusable Event Management Platform built for colleges. It explains what the database contains and why each design decision supports scalability, reliability, and future expansion.

## 1. Database Philosophy

### Why PostgreSQL
PostgreSQL is chosen for its maturity, strong relational capabilities, transactional integrity, extensibility, and support for advanced querying. It provides reliable data consistency and is well-suited for structured event, user, registration, and audit data.

### Why normalization
The schema is normalized to reduce redundancy, preserve data integrity, and make updates predictable. Proper normalization ensures event and user entities remain consistent, while enabling rich relationships across colleges, committees, registrations, and analytics.

### Why scalability
CampusFlow must support multiple colleges, thousands of users, and increasing event complexity. The design prioritizes scalable data patterns, efficient indexing, and a clean separation of concerns so the database can grow without requiring architecture changes.

### Why consistency
Consistency is essential for event registration, attendance verification, payment status, and certificate issuance. The design uses relational constraints, controlled business rules, and auditability to maintain accurate event state.

## 2. Core Modules

The database is organized around core modules that correspond to platform capabilities.

- Authentication
- Users
- Colleges
- Departments
- Committees
- Events
- Registrations
- Payments
- Passes
- QR Codes
- Attendance
- Certificates
- Volunteers
- Sponsors
- Announcements
- Notifications
- Gallery
- Feedback
- Reports
- Settings
- Audit Logs

## 3. Entity Definitions

### Authentication
**Purpose**: manage user credentials and session-related status.
**Owner**: Users module.
**Relationships**: linked to User.
**Important Fields**: email, password hash, verified_at, last_login_at.
**Business Rules**: email must be unique; verification is required before protected actions.
**Future Expansion**: multi-factor authentication, identity providers.

### Users
**Purpose**: represent individuals using CampusFlow.
**Owner**: platform.
**Relationships**: college, registration, volunteer assignment, committee membership, attendance, certificates.
**Important Fields**: name, email, phone, role, profile metadata.
**Business Rules**: one active user per email; role determines access.
**Future Expansion**: institutional identity, OAuth logins, profile badges.

### Colleges
**Purpose**: represent institutions that host events.
**Owner**: platform.
**Relationships**: departments, events, administrators.
**Important Fields**: name, campus address, timezone, status.
**Business Rules**: college must exist before event creation.
**Future Expansion**: multi-campus support, college-level analytics.

### Departments
**Purpose**: organize academic or administrative units within a college.
**Owner**: college.
**Relationships**: college, committees, organizers.
**Important Fields**: name, description.
**Business Rules**: a department belongs to one college.
**Future Expansion**: department-specific event categories.

### Committees
**Purpose**: represent event planning teams and ownership structures.
**Owner**: organizers.
**Relationships**: department, users, events.
**Important Fields**: name, role, chair, status.
**Business Rules**: committees may own multiple events.
**Future Expansion**: committee performance and history.

### Events
**Purpose**: capture event details, schedule, capacity, and status.
**Owner**: organizers.
**Relationships**: college, committee, registrations, volunteers, announcements, payments, sponsors.
**Important Fields**: title, description, start/end time, capacity, location, published_at, status.
**Business Rules**: events may only be published by authorized organizers; capacity cannot be exceeded.
**Future Expansion**: event templates, multi-day events.

### Registrations
**Purpose**: record user sign-ups for events.
**Owner**: event.
**Relationships**: user, event, payment, pass, attendance.
**Important Fields**: status, registered_at, ticket_type, approval_status.
**Business Rules**: one registration per user per event; registration may require payment or approval.
**Future Expansion**: waitlist handling, multiple ticket tiers.

### Payments
**Purpose**: track transaction status for paid events.
**Owner**: registration.
**Relationships**: registration, event, user.
**Important Fields**: amount, currency, status, provider_reference.
**Business Rules**: payment status must align with registration status.
**Future Expansion**: refunds, invoicing, payment gateway reconciliation.

### Passes
**Purpose**: generate and store digital event access passes.
**Owner**: registration.
**Relationships**: registration, user, event, QR code.
**Important Fields**: pass_code, issued_at, expires_at, status.
**Business Rules**: passes are created after confirmed registration.
**Future Expansion**: wallet integration.

### QR Codes
**Purpose**: support event entry verification.
**Owner**: passes.
**Relationships**: pass, registration, attendance.
**Important Fields**: qr_payload, scanned_at, status.
**Business Rules**: each QR code is unique and single-use per event session.
**Future Expansion**: dynamic QR rotation.

### Attendance
**Purpose**: record event presence and check-in data.
**Owner**: event operations.
**Relationships**: registration, user, event, volunteer.
**Important Fields**: checked_in_at, verifier_id, status.
**Business Rules**: attendance marks are created only after QR validation.
**Future Expansion**: session-level attendance tracking.

### Certificates
**Purpose**: manage issuance of participation or achievement certificates.
**Owner**: event.
**Relationships**: registration, user, event.
**Important Fields**: certificate_id, issued_at, status.
**Business Rules**: certificates are issued only after attendance criteria are met.
**Future Expansion**: certificate verification and digital signatures.

### Volunteers
**Purpose**: coordinate volunteer participation and assignments.
**Owner**: event.
**Relationships**: user, event, registration, tasks.
**Important Fields**: role, shift, status.
**Business Rules**: volunteers may have assignment records separate from attendee registrations.
**Future Expansion**: volunteer performance metrics.

### Sponsors
**Purpose**: represent event sponsors and partners.
**Owner**: event.
**Relationships**: event, college.
**Important Fields**: name, tier, contribution.
**Business Rules**: sponsors may be associated with one or more events.
**Future Expansion**: sponsor entitlement and visibility.

### Announcements
**Purpose**: store event and platform communication messages.
**Owner**: organizer.
**Relationships**: event, user segments.
**Important Fields**: title, body, published_at.
**Business Rules**: announcements may target registered attendees or broader audiences.
**Future Expansion**: notification scheduling.

### Notifications
**Purpose**: capture all notification events sent to users.
**Owner**: platform.
**Relationships**: user, announcement, event.
**Important Fields**: channel, status, sent_at.
**Business Rules**: notifications are recorded for audit and retry purposes.
**Future Expansion**: in-app notification center.

### Gallery
**Purpose**: store event media assets and galleries.
**Owner**: event.
**Relationships**: event, user uploads.
**Important Fields**: asset_url, caption, media_type.
**Business Rules**: gallery items belong to a specific event.
**Future Expansion**: user-submitted galleries.

### Feedback
**Purpose**: collect post-event feedback and ratings.
**Owner**: event.
**Relationships**: event, user, registration.
**Important Fields**: rating, comments, submitted_at.
**Business Rules**: feedback is associated with attendance.
**Future Expansion**: sentiment analysis.

### Reports
**Purpose**: store generated event reports and analytics snapshots.
**Owner**: administrator.
**Relationships**: event, college.
**Important Fields**: report_type, generated_at, summary.
**Business Rules**: reports are derived from transactional data.
**Future Expansion**: custom report metadata.

### Settings
**Purpose**: store platform and event configuration.
**Owner**: platform/college.
**Relationships**: college, event, user.
**Important Fields**: key, value, scope.
**Business Rules**: settings may be scoped globally, per college, or per event.
**Future Expansion**: managed feature flags.

### Audit Logs
**Purpose**: record changes to important entities.
**Owner**: platform.
**Relationships**: user, entity reference.
**Important Fields**: action, old_value, new_value, ip_address.
**Business Rules**: audit logs are immutable and retained for compliance.
**Future Expansion**: audit search capabilities.

## Database Naming Standards

CampusFlow uses consistent PostgreSQL naming conventions across the entire database. These standards are the official reference for all tables, columns, indexes, constraints, and migration artifacts.

- Use `snake_case` for all database objects: tables, columns, indexes, constraints, and migration names.
- Use singular table names for entities, for example `user`, `event`, `registration`, and `certificate`.
- Use `id` as the primary key column name for UUID primary keys on major entities.
- Name foreign keys with the referenced entity followed by `_id`, for example `user_id`, `event_id`, `registration_id`.
- Name junction tables with a predictable combination of related entities, for example `user_event`, `event_committee`, `event_volunteer`.
- Use standard timestamp field names across entities:
  - `created_at`
  - `updated_at`
  - `deleted_at`
  - `verified_at`
  - `approved_at`
  - `published_at`
- Name indexes with the prefix `ix_`, for example `ix_event_start_time`, `ix_registration_user_id_event_id`.
- Name unique constraints with the prefix `uq_`, for example `uq_user_email`, `uq_event_slug`.
- Name foreign key constraints with the prefix `fk_`, for example `fk_registration_user_id_user`, `fk_event_committee_id_committee`.
- Name primary key constraints with the prefix `pk_`, for example `pk_user`, `pk_event`.
- Name check constraints with the prefix `ck_`, for example `ck_event_capacity_positive`, `ck_registration_status_valid`.
- Use descriptive migration names in kebab-case that reflect the change, for example `create_event_table`, `add_registration_status`, `rename_user_phone`.

## 4. Relationships

CampusFlow entities form a clear relational graph.

### Core Relationship Flow
College
↓
Departments
↓
Committees
↓
Events
↓
Registrations
↓
Passes
↓
Attendance

### One-to-One
- User to Authentication record.
- Registration to Pass (in a one-pass-per-registration model).

### One-to-Many
- College to Departments.
- College to Events.
- Event to Registrations.
- Event to Announcements.
- Event to Volunteers.
- Event to Sponsors.
- Registration to Payments.
- Registration to Attendance records.

### Many-to-Many
- Users to Committees through committee membership.
- Events to Sponsors through sponsorship agreements.
- Events to Volunteers through assignments.

## 5. UUID Strategy

### Why UUID
UUIDs provide globally unique identifiers, avoid collision across distributed systems, and support multi-tenant data patterns. They remove the need for coordination when creating IDs across services.

### Where UUID should be used
- Primary keys for core entities such as users, colleges, events, registrations, passes, and certificates.
- Public-facing IDs for shareable resources.

### Public IDs
Public IDs should be UUID-based and non-sequential to prevent enumeration.

### Internal IDs
Internal references also use UUIDs for consistency, while natural keys remain in separate business fields.

## 6. Timestamp Strategy

### created_at
Tracks when a record was first created.

### updated_at
Tracks the most recent modification.

### deleted_at
Marks soft delete time for recoverable entities.

### verified_at
Indicates when a user or record was verified.

### approved_at
Indicates when approvals were granted.

### published_at
Indicates when events or announcements became public.

Timestamps are stored in UTC to avoid timezone ambiguity and support cross-college operations.

## 7. Soft Delete Strategy

### Why
Soft delete preserves history, supports recovery, and avoids accidental data loss. It also enables auditability for event operations.

### Which entities support it
- Users
- Events
- Registrations
- Announcements
- Gallery items
- Certificates
- Volunteers
- Sponsors
- Feedback

### Recovery
Soft-deleted records remain queryable with explicit filters and can be restored if needed. This supports administrative recovery workflows.

## 8. Index Strategy

### Primary Keys
Every core entity uses a UUID primary key.

### Foreign Keys
Foreign key fields should be indexed to support joins and lookups.

### Search
Searchable fields such as user email, event title, and sponsor name should be indexed appropriately.

### Email
Unique index on user email for authentication and lookup.

### QR Code
Index QR payload fields to enable fast validation during check-in.

### Registration
Index event and user registration combinations for quick existence checks.

### Payments
Index payment references and status for reconciliation.

### Certificates
Index event and user certificate records for retrieval.

### Indexing philosophy
Index fields used in WHERE, JOIN, and ORDER BY clauses. Avoid over-indexing; balance read performance with write cost.

## 9. Constraints

### Unique
Enforce uniqueness on natural keys such as user email, event slug, and registration pairings.

### Check
Use check constraints for valid statuses, capacity bounds, and date relationships.

### Foreign Keys
Enforce referential integrity between related entities.

### Cascade Rules
Use cascade deletes selectively, primarily for fully dependent child records. Prefer soft delete and explicit cleanup for important data.

### Business Constraints
Enforce business rules such as one registration per user per event, capacity limits, and certificate issuance conditions.

## 10. Data Lifecycle

### Creation
Records are created with audit fields and default statuses.

### Update
Updates are tracked via updated_at and validated against business rules.

### Archive
Old or inactive event data may be archived in application-level workflows, preserving the live dataset.

### Soft Delete
Soft deletes mark records without removing them, supporting recovery and historical analysis.

### Permanent Delete
Permanent deletes occur only when required for data retention policies or cleanup, with logging and authorization.

## 11. Audit Strategy

### Audit Logs
Audit logs capture changes to important entities.

### Who changed what
Record the user or system actor responsible for the change.

### When
Capture timestamps for each audit entry.

### Old Value
Record the previous value before the update.

### New Value
Record the new value after the update.

### IP
Capture the requesting IP address when available.

### Device
Capture user agent or device metadata when relevant.

## 12. Security

### Sensitive Fields
Protect fields such as password hashes, payment references, and PII.

### Encryption
Use encryption for sensitive data at rest when supported by the database platform and storage layer.

### Password Storage
Store only salted and hashed passwords using strong password hashing.

### Payment Data
Do not store raw payment card data. Store only necessary provider references and status.

### PII
Limit storage of personally identifiable information and protect it with strict access controls.

## 13. Backup Strategy

### Daily
Daily backups for recent recovery points.

### Weekly
Weekly full backups for historical recovery.

### Monthly
Monthly snapshots for long-term retention.

### Point-in-Time Recovery
Support point-in-time recovery for critical data restoration.

## 14. Scaling Strategy

### 10 Users
A single database instance handles development and early production load.

### 1,000 Users
Scale read performance with indexes and optimize queries; use connection pooling.

### 10,000 Users
Introduce query optimization, partitioning strategies, and stronger caching for registration and analytics workloads.

### 100,000 Users
Scale database infrastructure with read replicas, sharding considerations, and efficient archival of old event data.

The database design supports growth through efficient schema patterns and clear operational practices.

## 15. Future Expansion

### Multiple Colleges
Support multiple colleges with separate ownership and event boundaries.

### Multiple Campuses
Support campus-level organization and location-specific events.

### Multi-Tenant SaaS
Design the schema to support multi-tenant isolation and shared platform capabilities.

### Mobile App
Support mobile clients with efficient read models and event access patterns.

### Marketplace
Support sponsor and partner marketplace data without overloading event transaction tables.

### Event Ticketing
Support ticket tiers, pricing, and seat assignment with normalized event registration structures.

### AI Analytics
Enable AI analytics through clean event, attendance, and feedback data models.

## 16. Database Standards

### Naming
Use descriptive names for tables and columns.

### Pluralization
Use plural table names for collections of entities.

### Snake Case
Use snake_case for table and column names.

### Foreign Keys
Use consistent foreign key naming, such as `entity_id`.

### Indexes
Name indexes clearly and align them with the fields they cover.

### Migrations
Use Alembic for schema evolution and keep migration history in source control.

### Constraints
Enforce integrity with appropriate database constraints.

## 17. Entity Summary Table

| Entity Name | Purpose | Primary Relationships |
| --- | --- | --- |
| Authentication | Manage credentials and verification | user |
| Users | Represent platform users | college, registrations, attendance, certificates |
| Colleges | Represent institutions | departments, events |
| Departments | Organize college units | college, committees |
| Committees | Manage event planning teams | department, events, users |
| Events | Represent events | college, committee, registrations, volunteers |
| Registrations | Track event sign-ups | user, event, payment, pass |
| Payments | Track transaction status | registration, event, user |
| Passes | Generate event access passes | registration, qr_code |
| QR Codes | Support scan verification | pass, attendance |
| Attendance | Record check-ins | registration, event, volunteer |
| Certificates | Manage issued certificates | registration, user, event |
| Volunteers | Coordinate volunteer roles | user, event |
| Sponsors | Track event sponsors | event, college |
| Announcements | Store communication content | event, user segment |
| Notifications | Track notification delivery | user, announcement |
| Gallery | Store event media assets | event, user |
| Feedback | Capture event feedback | user, event, registration |
| Reports | Store analytics snapshots | event, college |
| Settings | Store configuration values | college, event, user |
| Audit Logs | Track entity changes | user, entity reference |

## Final Database Philosophy

CampusFlow’s database should remain maintainable and extensible for the next five years by following relational discipline, UUID identity, auditability, and scalable design patterns. It should preserve event and user history while allowing growth across colleges, event types, and usage volumes.

The database should be designed for clarity: every entity should have a clear purpose, every relationship should be explicit, and every business rule should be enforced at the data layer where possible. Soft deletes and audit logs should protect the platform from accidental loss and support recovery.

Above all, the database should be a reliable foundation for the product. It should enable product teams to build new event workflows, mobile experiences, sponsor capabilities, and analytics without requiring schema rewrites. CampusFlow’s data design should make expansion feel natural, not risky.