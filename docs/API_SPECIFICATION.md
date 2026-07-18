# CampusFlow API Specification

This document defines the CampusFlow API surface. It describes every endpoint required for the platform, expected request and response behavior, error handling, versioning, and security.

## 1. API Philosophy

### REST
CampusFlow APIs follow REST principles: resources are modeled as nouns, operations use HTTP methods, and the API is centered on resource state.

### Consistency
API routes, request payloads, and response formats must be consistent across modules to make the platform predictable and easy to use.

### Predictability
The API should behave in a reliable way. Similar operations should return the same types of responses and error structures.

### Versioning
Version APIs from the start using a path-based versioning scheme, e.g. `/api/v1/`. Future breaking changes should be introduced as new versions.

### Security
All protected endpoints must require proper authentication and authorization. Sensitive operations must be restricted to the appropriate roles.

## 2. Authentication APIs

### Signup
**Purpose**: register a new user.
**Method**: POST
**Route**: `/api/v1/auth/signup`
**Authentication Required**: No
**Request Body**:
- `email` (string, required)
- `password` (string, required)
- `name` (string, required)
- `college_id` (uuid, optional)
- `role` (string, optional; default student)
**Response**:
- `user_id`
- `email`
- `name`
- `verified` false
- `message`
**Possible Errors**:
- 400 Invalid input
- 409 Email already registered
- 422 Weak password

### Verify Email
**Purpose**: confirm user email after signup.
**Method**: POST
**Route**: `/api/v1/auth/verify-email`
**Authentication Required**: No
**Request Body**:
- `token` (string, required)
**Response**:
- `verified` true
- `message`
**Possible Errors**:
- 400 Invalid token
- 404 Token expired or not found
- 422 Invalid request

### Login
**Purpose**: authenticate an existing user.
**Method**: POST
**Route**: `/api/v1/auth/login`
**Authentication Required**: No
**Request Body**:
- `email` (string, required)
- `password` (string, required)
**Response**:
- `access_token`
- `refresh_token`
- `token_type` (`Bearer`)
- `expires_in`
- `user` object
**Possible Errors**:
- 400 Invalid credentials
- 401 Unverified email
- 429 Too many attempts

### Refresh Token
**Purpose**: renew JWT access token.
**Method**: POST
**Route**: `/api/v1/auth/refresh`
**Authentication Required**: No (refresh token required in body or cookie)
**Request Body**:
- `refresh_token` (string, required)
**Response**:
- `access_token`
- `refresh_token`
- `expires_in`
**Possible Errors**:
- 400 Invalid refresh token
- 401 Expired refresh token
- 403 Revoked token

### Logout
**Purpose**: revoke authentication tokens.
**Method**: POST
**Route**: `/api/v1/auth/logout`
**Authentication Required**: Yes
**Request Body**:
- `refresh_token` (string, optional)
**Response**:
- `message`
**Possible Errors**:
- 401 Unauthorized
- 400 Invalid request

### Forgot Password
**Purpose**: initiate password reset.
**Method**: POST
**Route**: `/api/v1/auth/forgot-password`
**Authentication Required**: No
**Request Body**:
- `email` (string, required)
**Response**:
- `message`
**Possible Errors**:
- 400 Invalid email
- 404 Email not found

### Reset Password
**Purpose**: complete password reset.
**Method**: POST
**Route**: `/api/v1/auth/reset-password`
**Authentication Required**: No
**Request Body**:
- `token` (string, required)
- `new_password` (string, required)
**Response**:
- `message`
**Possible Errors**:
- 400 Invalid or expired token
- 422 Weak password

### Profile
**Purpose**: get or update current user profile.
**Method**: GET / PUT
**Route**: `/api/v1/auth/profile`
**Authentication Required**: Yes
**Request Body** (PUT):
- `name` (string, optional)
- `phone` (string, optional)
- `college_id` (uuid, optional)
- `department_id` (uuid, optional)
**Response**:
- `user` object
**Possible Errors**:
- 400 Invalid data
- 403 Forbidden
- 404 User not found

## 3. Student APIs

### Dashboard
**Purpose**: view student-specific metrics and upcoming activity.
**Method**: GET
**Route**: `/api/v1/student/dashboard`
**Authentication Required**: Yes
**Response**:
- `upcoming_events`
- `registrations`
- `passes`
- `notifications`
**Possible Errors**:
- 401 Unauthorized
- 404 Dashboard data not found

### My Events
**Purpose**: list student event registrations.
**Method**: GET
**Route**: `/api/v1/student/events`
**Authentication Required**: Yes
**Request Params**:
- `status` (string, optional)
- `page` (integer)
- `limit` (integer)
**Response**:
- `events` array
- `pagination`
**Possible Errors**:
- 401 Unauthorized

### My Passes
**Purpose**: list active and historical event passes.
**Method**: GET
**Route**: `/api/v1/student/passes`
**Authentication Required**: Yes
**Response**:
- `passes` array
**Possible Errors**:
- 401 Unauthorized

### Certificates
**Purpose**: retrieve issued certificates.
**Method**: GET
**Route**: `/api/v1/student/certificates`
**Authentication Required**: Yes
**Response**:
- `certificates` array
**Possible Errors**:
- 401 Unauthorized

### Notifications
**Purpose**: view student notifications.
**Method**: GET
**Route**: `/api/v1/student/notifications`
**Authentication Required**: Yes
**Request Params**:
- `page` (integer)
- `limit` (integer)
**Response**:
- `notifications` array
- `pagination`
**Possible Errors**:
- 401 Unauthorized

### Feedback
**Purpose**: submit event feedback.
**Method**: POST
**Route**: `/api/v1/student/feedback`
**Authentication Required**: Yes
**Request Body**:
- `event_id` (uuid, required)
- `rating` (integer, required)
- `comments` (string, optional)
**Response**:
- `feedback_id`
- `message`
**Possible Errors**:
- 400 Invalid data
- 403 Not registered
- 422 Rating out of bounds

## 4. Event APIs

### List Events
**Purpose**: retrieve discoverable events.
**Method**: GET
**Route**: `/api/v1/events`
**Authentication Required**: No
**Request Params**:
- `search` (string)
- `college_id` (uuid)
- `category` (string)
- `status` (string)
- `page`, `limit`
**Response**:
- `events` array
- `pagination`
**Possible Errors**:
- 400 Invalid query

### Featured Events
**Purpose**: retrieve curated event selections.
**Method**: GET
**Route**: `/api/v1/events/featured`
**Authentication Required**: No
**Response**:
- `events` array
**Possible Errors**:
- 404 No featured events

### Upcoming Events
**Purpose**: list upcoming events.
**Method**: GET
**Route**: `/api/v1/events/upcoming`
**Authentication Required**: No
**Request Params**:
- `college_id` (uuid)
- `page`, `limit`
**Response**:
- `events` array
**Possible Errors**:
- 400 Invalid query

### Event Details
**Purpose**: get full event information.
**Method**: GET
**Route**: `/api/v1/events/{event_id}`
**Authentication Required**: No
**Response**:
- `event` object
**Possible Errors**:
- 404 Event not found

### Register
**Purpose**: register the current user for an event.
**Method**: POST
**Route**: `/api/v1/events/{event_id}/register`
**Authentication Required**: Yes
**Request Body**:
- `ticket_type` (string, optional)
- `answers` (object, optional)
**Response**:
- `registration_id`
- `status`
- `message`
**Possible Errors**:
- 400 Invalid registration data
- 401 Unauthorized
- 403 Registration closed
- 409 Already registered
- 422 Capacity reached

### Cancel Registration
**Purpose**: cancel an event registration.
**Method**: DELETE
**Route**: `/api/v1/events/{event_id}/registrations/{registration_id}`
**Authentication Required**: Yes
**Response**:
- `message`
**Possible Errors**:
- 401 Unauthorized
- 403 Cannot cancel
- 404 Registration not found

## 5. Registration APIs

### Create Registration
**Purpose**: create a registration resource.
**Method**: POST
**Route**: `/api/v1/registrations`
**Authentication Required**: Yes
**Request Body**:
- `event_id` (uuid, required)
- `ticket_type` (string, optional)
- `promo_code` (string, optional)
**Response**:
- `registration` object
**Possible Errors**:
- 400 Invalid request
- 409 Duplicate registration

### Update Registration
**Purpose**: modify registration details.
**Method**: PATCH
**Route**: `/api/v1/registrations/{registration_id}`
**Authentication Required**: Yes
**Request Body**:
- `status` (string, optional)
- `ticket_type` (string, optional)
**Response**:
- `registration` object
**Possible Errors**:
- 400 Invalid request
- 403 Not allowed
- 404 Registration not found

### Payment Status
**Purpose**: view payment details for a registration.
**Method**: GET
**Route**: `/api/v1/registrations/{registration_id}/payment`
**Authentication Required**: Yes
**Response**:
- `payment` object
**Possible Errors**:
- 401 Unauthorized
- 404 Payment not found

### Registration Status
**Purpose**: retrieve registration state.
**Method**: GET
**Route**: `/api/v1/registrations/{registration_id}`
**Authentication Required**: Yes
**Response**:
- `registration` object
**Possible Errors**:
- 401 Unauthorized
- 404 Registration not found

### QR Generation
**Purpose**: generate QR data for a registration pass.
**Method**: POST
**Route**: `/api/v1/registrations/{registration_id}/qr`
**Authentication Required**: Yes
**Response**:
- `qr_code` object
**Possible Errors**:
- 401 Unauthorized
- 404 Registration not found
- 403 Not eligible

### Pass Download
**Purpose**: download the digital pass.
**Method**: GET
**Route**: `/api/v1/registrations/{registration_id}/pass`
**Authentication Required**: Yes
**Response**:
- `pass` object or URL
**Possible Errors**:
- 401 Unauthorized
- 404 Pass not found

## 6. Organizer APIs

### Dashboard
**Purpose**: provide organizer event metrics.
**Method**: GET
**Route**: `/api/v1/organizer/dashboard`
**Authentication Required**: Yes
**Response**:
- `events_summary`
- `registrations_summary`
- `volunteer_summary`
**Possible Errors**:
- 401 Unauthorized

### Create Event
**Purpose**: create a new event.
**Method**: POST
**Route**: `/api/v1/organizer/events`
**Authentication Required**: Yes
**Request Body**:
- `title`, `description`, `start_time`, `end_time`, `capacity`, `location`, `committee_id`, `ticket_types`
**Response**:
- `event_id`
- `event` object
**Possible Errors**:
- 400 Invalid event data
- 403 Unauthorized

### Update Event
**Purpose**: edit an existing event.
**Method**: PATCH
**Route**: `/api/v1/organizer/events/{event_id}`
**Authentication Required**: Yes
**Request Body**:
- fields to update
**Response**:
- `event` object
**Possible Errors**:
- 400 Invalid data
- 403 Unauthorized
- 404 Event not found

### Delete Event
**Purpose**: remove or archive an event.
**Method**: DELETE
**Route**: `/api/v1/organizer/events/{event_id}`
**Authentication Required**: Yes
**Response**:
- `message`
**Possible Errors**:
- 403 Unauthorized
- 404 Event not found

### Publish Event
**Purpose**: publish an event to public discovery.
**Method**: POST
**Route**: `/api/v1/organizer/events/{event_id}/publish`
**Authentication Required**: Yes
**Response**:
- `event` object
**Possible Errors**:
- 403 Unauthorized
- 404 Event not found

### Registrations
**Purpose**: list registrations for an event.
**Method**: GET
**Route**: `/api/v1/organizer/events/{event_id}/registrations`
**Authentication Required**: Yes
**Request Params**:
- `status`, `page`, `limit`
**Response**:
- `registrations` array
- `pagination`
**Possible Errors**:
- 403 Unauthorized
- 404 Event not found

### Analytics
**Purpose**: view event analytics.
**Method**: GET
**Route**: `/api/v1/organizer/events/{event_id}/analytics`
**Authentication Required**: Yes
**Response**:
- `analytics` object
**Possible Errors**:
- 403 Unauthorized
- 404 Event not found

### Announcements
**Purpose**: send event announcements.
**Method**: POST
**Route**: `/api/v1/organizer/events/{event_id}/announcements`
**Authentication Required**: Yes
**Request Body**:
- `title`, `body`, `target_audience`
**Response**:
- `announcement_id`
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized
- 404 Event not found

## 7. Volunteer APIs

### Assigned Events
**Purpose**: list events assigned to the volunteer.
**Method**: GET
**Route**: `/api/v1/volunteer/events`
**Authentication Required**: Yes
**Response**:
- `events` array
**Possible Errors**:
- 401 Unauthorized

### Attendance Scanner
**Purpose**: provide scanner configuration and status.
**Method**: GET
**Route**: `/api/v1/volunteer/scanner`
**Authentication Required**: Yes
**Response**:
- `scanner_config`
**Possible Errors**:
- 401 Unauthorized

### Check-in
**Purpose**: record attendee entry.
**Method**: POST
**Route**: `/api/v1/volunteer/check-in`
**Authentication Required**: Yes
**Request Body**:
- `qr_payload` (string, required)
- `event_id` (uuid, required)
**Response**:
- `attendance` object
**Possible Errors**:
- 400 Invalid QR
- 403 Unauthorized
- 409 Duplicate scan

### Check-out
**Purpose**: record volunteer check-out or event exit if needed.
**Method**: POST
**Route**: `/api/v1/volunteer/check-out`
**Authentication Required**: Yes
**Request Body**:
- `attendance_id` (uuid, required)
**Response**:
- `message`
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized

### Incident Report
**Purpose**: report event incidents.
**Method**: POST
**Route**: `/api/v1/volunteer/incidents`
**Authentication Required**: Yes
**Request Body**:
- `event_id`, `description`, `severity`
**Response**:
- `incident_id`
**Possible Errors**:
- 400 Invalid data
- 403 Unauthorized

## 8. Admin APIs

### Dashboard
**Purpose**: provide high-level platform metrics.
**Method**: GET
**Route**: `/api/v1/admin/dashboard`
**Authentication Required**: Yes (admin)
**Response**:
- `platform_metrics`
**Possible Errors**:
- 403 Unauthorized

### Users
**Purpose**: manage platform users.
**Method**: GET / PATCH / DELETE
**Route**: `/api/v1/admin/users` and `/api/v1/admin/users/{user_id}`
**Authentication Required**: Yes (admin)
**Response**:
- `users` or `user` object
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized

### Events
**Purpose**: manage all events.
**Method**: GET / PATCH / DELETE
**Route**: `/api/v1/admin/events` and `/api/v1/admin/events/{event_id}`
**Authentication Required**: Yes (admin)
**Response**:
- `events` or `event` object
**Possible Errors**:
- 403 Unauthorized

### Payments
**Purpose**: review payment records.
**Method**: GET
**Route**: `/api/v1/admin/payments`
**Authentication Required**: Yes (admin)
**Response**:
- `payments` array
**Possible Errors**:
- 403 Unauthorized

### Certificates
**Purpose**: manage certificates.
**Method**: GET / POST
**Route**: `/api/v1/admin/certificates`
**Authentication Required**: Yes (admin)
**Response**:
- `certificates` array
**Possible Errors**:
- 403 Unauthorized

### Reports
**Purpose**: access platform reports.
**Method**: GET
**Route**: `/api/v1/admin/reports`
**Authentication Required**: Yes (admin)
**Response**:
- `reports` array
**Possible Errors**:
- 403 Unauthorized

### Audit Logs
**Purpose**: review audit entries.
**Method**: GET
**Route**: `/api/v1/admin/audit-logs`
**Authentication Required**: Yes (admin)
**Response**:
- `audit_logs` array
**Possible Errors**:
- 403 Unauthorized

### Settings
**Purpose**: manage platform configuration.
**Method**: GET / PATCH
**Route**: `/api/v1/admin/settings`
**Authentication Required**: Yes (admin)
**Response**:
- `settings` object
**Possible Errors**:
- 403 Unauthorized

## 9. Committee APIs

### Members
**Purpose**: list and manage committee members.
**Method**: GET / POST / DELETE
**Route**: `/api/v1/committee/{committee_id}/members`
**Authentication Required**: Yes
**Response**:
- `members` array
**Possible Errors**:
- 403 Unauthorized

### Roles
**Purpose**: manage committee roles.
**Method**: GET / PATCH
**Route**: `/api/v1/committee/{committee_id}/roles`
**Authentication Required**: Yes
**Response**:
- `roles` array
**Possible Errors**:
- 403 Unauthorized

### Permissions
**Purpose**: define committee permissions.
**Method**: GET / PATCH
**Route**: `/api/v1/committee/{committee_id}/permissions`
**Authentication Required**: Yes
**Response**:
- `permissions` object
**Possible Errors**:
- 403 Unauthorized

### Departments
**Purpose**: link committees to departments.
**Method**: GET
**Route**: `/api/v1/committee/{committee_id}/departments`
**Authentication Required**: Yes
**Response**:
- `departments` array
**Possible Errors**:
- 403 Unauthorized

## 10. Notification APIs

### Email
**Purpose**: send email notifications.
**Method**: POST
**Route**: `/api/v1/notifications/email`
**Authentication Required**: Yes
**Request Body**:
- `recipient_ids`, `subject`, `body`, `event_id` optional
**Response**:
- `notification_id`
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized

### Push (Future)
**Purpose**: send push notifications.
**Method**: POST
**Route**: `/api/v1/notifications/push`
**Authentication Required**: Yes
**Possible Errors**:
- 501 Not implemented

### SMS (Future)
**Purpose**: send SMS notifications.
**Method**: POST
**Route**: `/api/v1/notifications/sms`
**Authentication Required**: Yes
**Possible Errors**:
- 501 Not implemented

### Announcements
**Purpose**: publish event announcements.
**Method**: POST
**Route**: `/api/v1/notifications/announcements`
**Authentication Required**: Yes
**Request Body**:
- `title`, `body`, `event_id`, `target_audience`
**Response**:
- `announcement_id`
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized

## 11. QR APIs

### Generate
**Purpose**: create QR payloads for passes.
**Method**: POST
**Route**: `/api/v1/qr/generate`
**Authentication Required**: Yes
**Request Body**:
- `registration_id` (uuid, required)
**Response**:
- `qr_payload`
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized

### Validate
**Purpose**: validate a QR payload.
**Method**: POST
**Route**: `/api/v1/qr/validate`
**Authentication Required**: Yes
**Request Body**:
- `qr_payload` (string, required)
**Response**:
- `valid` boolean
- `registration_id`
**Possible Errors**:
- 400 Invalid payload
- 404 QR not found
- 409 Duplicate scan

### Verify Entry
**Purpose**: confirm attendee entry.
**Method**: POST
**Route**: `/api/v1/qr/verify-entry`
**Authentication Required**: Yes
**Request Body**:
- `qr_payload` (string, required)
- `event_id` (uuid, required)
**Response**:
- `attendance_id`
- `status`
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized
- 409 Duplicate entry

### Prevent Duplicate Entry
**Purpose**: prevent repeated scans.
**Method**: GET
**Route**: `/api/v1/qr/{qr_code_id}/duplicate-check`
**Authentication Required**: Yes
**Response**:
- `duplicate` boolean
**Possible Errors**:
- 404 QR not found

### Attendance Update
**Purpose**: update attendance status.
**Method**: PATCH
**Route**: `/api/v1/qr/attendance/{attendance_id}`
**Authentication Required**: Yes
**Request Body**:
- `status` (string)
**Response**:
- `attendance` object
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized
- 404 Attendance not found

## 12. Certificate APIs

### Generate
**Purpose**: issue certificates after attendance.
**Method**: POST
**Route**: `/api/v1/certificates/generate`
**Authentication Required**: Yes
**Request Body**:
- `registration_id` (uuid, required)
**Response**:
- `certificate_id`
**Possible Errors**:
- 400 Invalid request
- 403 Unauthorized

### Download
**Purpose**: retrieve a certificate file.
**Method**: GET
**Route**: `/api/v1/certificates/{certificate_id}/download`
**Authentication Required**: Yes
**Response**:
- certificate file URL or binary response
**Possible Errors**:
- 404 Certificate not found
- 403 Unauthorized

### Verify
**Purpose**: verify a certificate authenticity.
**Method**: GET
**Route**: `/api/v1/certificates/{certificate_id}/verify`
**Authentication Required**: No
**Response**:
- `valid` boolean
- `certificate` metadata
**Possible Errors**:
- 404 Certificate not found

### Reissue
**Purpose**: reissue or regenerate a certificate.
**Method**: POST
**Route**: `/api/v1/certificates/{certificate_id}/reissue`
**Authentication Required**: Yes
**Response**:
- `certificate_id`
**Possible Errors**:
- 403 Unauthorized
- 404 Certificate not found

## 13. Report APIs

### Attendance
**Purpose**: retrieve attendance reports.
**Method**: GET
**Route**: `/api/v1/reports/attendance`
**Authentication Required**: Yes
**Response**:
- `report` object
**Possible Errors**:
- 403 Unauthorized

### Payments
**Purpose**: retrieve payment reports.
**Method**: GET
**Route**: `/api/v1/reports/payments`
**Authentication Required**: Yes
**Response**:
- `report` object
**Possible Errors**:
- 403 Unauthorized

### Registrations
**Purpose**: retrieve registration reports.
**Method**: GET
**Route**: `/api/v1/reports/registrations`
**Authentication Required**: Yes
**Response**:
- `report` object
**Possible Errors**:
- 403 Unauthorized

### Volunteers
**Purpose**: retrieve volunteer reports.
**Method**: GET
**Route**: `/api/v1/reports/volunteers`
**Authentication Required**: Yes
**Response**:
- `report` object
**Possible Errors**:
- 403 Unauthorized

### Certificates
**Purpose**: retrieve certificate reports.
**Method**: GET
**Route**: `/api/v1/reports/certificates`
**Authentication Required**: Yes
**Response**:
- `report` object
**Possible Errors**:
- 403 Unauthorized

## 14. Response Standards

### Success Format
- `status`: `success`
- `data`: object or array
- `message`: optional string

### Error Format
- `status`: `error`
- `error`: string code
- `message`: human-readable message
- `details`: optional validation details

### Validation Format
- `status`: `error`
- `error`: `validation_error`
- `message`: `Validation failed`
- `details`: field-level errors

### Pagination Format
- `page`
- `limit`
- `total`
- `pages`
- `items`

## Standard API Response Format

All CampusFlow APIs MUST use this unified response structure for every endpoint.

Successful Response

{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {},
  "meta": {}
}

Validation Error

{
  "success": false,
  "message": "Validation failed.",
  "error": {
    "code": "validation_error",
    "details": {
      "field_name": ["This field is required."]
    }
  },
  "meta": {}
}

Business Error

{
  "success": false,
  "message": "Registration already exists.",
  "error": {
    "code": "conflict",
    "details": null
  },
  "meta": {}
}

Authentication Error

{
  "success": false,
  "message": "Authentication required.",
  "error": {
    "code": "unauthorized",
    "details": null
  },
  "meta": {}
}

Server Error

{
  "success": false,
  "message": "An unexpected error occurred.",
  "error": {
    "code": "internal_server_error",
    "details": null
  },
  "meta": {}
}

Paginated Response

{
  "success": true,
  "message": "Events retrieved successfully.",
  "data": [],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 85,
      "pages": 5
    }
  }
}

### Error Object Format

- `code`: machine-readable error code
- `message`: user-friendly error message
- `details`: field-level or contextual details, or `null`

### Pagination Object Format

- `page`: current page number
- `limit`: items per page
- `total`: total items available
- `pages`: total number of pages
- `items`: number of items returned in the response

### Metadata Format

- `meta`: object carrying non-primary response data
- May include `pagination`, `request_id`, `warnings`, or other context

All CampusFlow APIs MUST use this structure for success, validation, business, authentication, and server error responses.

## 15. Status Codes

### 200 OK
Successful retrieval or update.

### 201 Created
Resource created successfully.

### 204 No Content
Successful request with no response body, such as delete operations.

### 400 Bad Request
Malformed request or invalid parameters.

### 401 Unauthorized
Authentication missing or invalid.

### 403 Forbidden
Authenticated but not allowed to perform the action.

### 404 Not Found
Resource does not exist.

### 409 Conflict
Resource state conflict, such as duplicate registration.

### 422 Unprocessable Entity
Semantic validation failed for the request.

### 429 Too Many Requests
Rate limit exceeded.

### 500 Internal Server Error
Unexpected server failure.

## 16. API Versioning

### v1
All current endpoints belong to API version v1.

### Future v2
Breaking changes will be introduced in v2 with a new path prefix `/api/v2/`.

### Deprecation Strategy
Deprecate old endpoints with advance notice, support transitional routes, and provide clear migration guidance.

## 17. Rate Limiting

### Authentication
Limit login and token refresh endpoints to protect against brute force.

### QR Validation
Rate limit QR validation to prevent abuse and protect event scanners.

### Public APIs
Apply moderate rate limits to public event discovery endpoints.

### Admin APIs
Apply stricter limits and monitoring to admin routes.

## 18. Security

### JWT
Use JWT for secure stateless authentication.

### RBAC
Enforce role-based access control for student, organizer, volunteer, and admin routes.

### Permissions
Validate permissions at every protected endpoint.

### Validation
Validate request schemas and query parameters.

### Sanitization
Sanitize all inputs to prevent injection.

### CORS
Restrict allowed origins to known frontend hosts.

### CSRF
Protect state-changing actions if using cookies.

## 19. Error Handling

### Standard Error Response
Use a consistent structure for all errors.

### Validation Errors
Return field-level details for invalid input.

### Business Errors
Return clear messages for rules such as capacity reached or duplicate registration.

### Server Errors
Return generic errors without leaking internal details.

## 20. API Summary Table

| Module | Endpoint | Method | Auth | Purpose |
| --- | --- | --- | --- | --- |
| Auth | `/auth/signup` | POST | No | Create user |
| Auth | `/auth/verify-email` | POST | No | Verify email |
| Auth | `/auth/login` | POST | No | Authenticate |
| Auth | `/auth/refresh` | POST | No | Refresh token |
| Auth | `/auth/logout` | POST | Yes | Revoke token |
| Auth | `/auth/forgot-password` | POST | No | Request reset |
| Auth | `/auth/reset-password` | POST | No | Reset password |
| Auth | `/auth/profile` | GET/PATCH | Yes | Profile management |
| Student | `/student/dashboard` | GET | Yes | Student home |
| Student | `/student/events` | GET | Yes | My events |
| Student | `/student/passes` | GET | Yes | My passes |
| Student | `/student/certificates` | GET | Yes | Certificates |
| Student | `/student/notifications` | GET | Yes | Notifications |
| Student | `/student/feedback` | POST | Yes | Submit feedback |
| Event | `/events` | GET | No | List events |
| Event | `/events/featured` | GET | No | Featured events |
| Event | `/events/upcoming` | GET | No | Upcoming events |
| Event | `/events/{id}` | GET | No | Event details |
| Event | `/events/{id}/register` | POST | Yes | Register |
| Event | `/events/{id}/registrations/{reg_id}` | DELETE | Yes | Cancel registration |
| Registration | `/registrations` | POST | Yes | Create registration |
| Registration | `/registrations/{id}` | GET/PATCH | Yes | Registration detail/update |
| Registration | `/registrations/{id}/payment` | GET | Yes | Payment status |
| Registration | `/registrations/{id}/qr` | POST | Yes | Generate QR |
| Registration | `/registrations/{id}/pass` | GET | Yes | Download pass |
| Organizer | `/organizer/dashboard` | GET | Yes | Organizer home |
| Organizer | `/organizer/events` | POST | Yes | Create event |
| Organizer | `/organizer/events/{id}` | PATCH/DELETE | Yes | Update/delete event |
| Organizer | `/organizer/events/{id}/publish` | POST | Yes | Publish event |
| Organizer | `/organizer/events/{id}/registrations` | GET | Yes | List regs |
| Organizer | `/organizer/events/{id}/analytics` | GET | Yes | Analytics |
| Organizer | `/organizer/events/{id}/announcements` | POST | Yes | Announce |
| Volunteer | `/volunteer/events` | GET | Yes | Assigned events |
| Volunteer | `/volunteer/scanner` | GET | Yes | Scanner status |
| Volunteer | `/volunteer/check-in` | POST | Yes | Check-in |
| Volunteer | `/volunteer/check-out` | POST | Yes | Check-out |
| Volunteer | `/volunteer/incidents` | POST | Yes | Incident report |
| Admin | `/admin/dashboard` | GET | Yes | Admin home |
| Admin | `/admin/users` | GET/PATCH/DELETE | Yes | User management |
| Admin | `/admin/events` | GET/PATCH/DELETE | Yes | Event management |
| Admin | `/admin/payments` | GET | Yes | Payment review |
| Admin | `/admin/certificates` | GET/POST | Yes | Certificate management |
| Admin | `/admin/reports` | GET | Yes | Reports |
| Admin | `/admin/audit-logs` | GET | Yes | Audit review |
| Admin | `/admin/settings` | GET/PATCH | Yes | Settings |
| Committee | `/committee/{id}/members` | GET/POST/DELETE | Yes | Committee members |
| Committee | `/committee/{id}/roles` | GET/PATCH | Yes | Roles |
| Committee | `/committee/{id}/permissions` | GET/PATCH | Yes | Permissions |
| Committee | `/committee/{id}/departments` | GET | Yes | Departments |
| Notifications | `/notifications/email` | POST | Yes | Send email |
| Notifications | `/notifications/push` | POST | Yes | Send push (future) |
| Notifications | `/notifications/sms` | POST | Yes | Send SMS (future) |
| Notifications | `/notifications/announcements` | POST | Yes | Publish announcement |
| QR | `/qr/generate` | POST | Yes | Generate QR |
| QR | `/qr/validate` | POST | Yes | Validate QR |
| QR | `/qr/verify-entry` | POST | Yes | Verify entry |
| QR | `/qr/{id}/duplicate-check` | GET | Yes | Duplicate check |
| QR | `/qr/attendance/{id}` | PATCH | Yes | Update attendance |
| Certificates | `/certificates/generate` | POST | Yes | Generate certificate |
| Certificates | `/certificates/{id}/download` | GET | Yes | Download certificate |
| Certificates | `/certificates/{id}/verify` | GET | No | Verify certificate |
| Certificates | `/certificates/{id}/reissue` | POST | Yes | Reissue certificate |
| Reports | `/reports/attendance` | GET | Yes | Attendance report |
| Reports | `/reports/payments` | GET | Yes | Payment report |
| Reports | `/reports/registrations` | GET | Yes | Registration report |
| Reports | `/reports/volunteers` | GET | Yes | Volunteer report |
| Reports | `/reports/certificates` | GET | Yes | Certificate report |

## Final API Philosophy

CampusFlow APIs should evolve into an enterprise-grade platform that remains simple, secure, consistent, and scalable. The API surface should reflect the product’s mission: to provide predictable, role-aware access to event, registration, attendance, and platform management data.

The platform should favor clear resource models and stable contract boundaries. API changes should be managed through versioning so integrators can adopt new capabilities without disruption. Security should be a first-class concern through JWT authentication, RBAC, input validation, and rate limiting.

As CampusFlow grows, the APIs should support multiple clients, including web, mobile, and partner integrations. They should be easy to document, test, and extend. The API design should make it possible to add new event features, notification channels, and analytics capabilities without undermining the current contract.

The ideal CampusFlow API platform should feel trusted by developers and partners: consistent in behavior, clear in intent, and reliable under load. It should enable rapid implementation while preserving long-term maintenance and operational stability.