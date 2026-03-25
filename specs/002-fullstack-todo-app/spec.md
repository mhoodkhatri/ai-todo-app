# Feature Specification: Full-Stack Todo Web Application

**Feature Branch**: `002-fullstack-todo-app`
**Created**: 2026-03-24
**Status**: Draft
**Input**: User description: "Phase II: Transform Todo Console App into a Full-Stack Web Application — evolve the Phase I in-memory console app into a multi-user web application with persistent storage, RESTful API, responsive frontend, and user authentication."

## Clarifications

### Session 2026-03-24

- Q: The User entity includes "display name" but signup only collects email and password — where does the display name come from? → A: Add a required "display name" field to the signup form.
- Q: What should the task dashboard show when a new user has zero tasks? → A: Show an empty state message with a call-to-action to create the first task.
- Q: Should the task list sort order be codified as a requirement? → A: Fixed sort, newest first by creation date, no user-configurable sorting.
- Q: Should password validation (min 8 chars) follow the same dual-validation pattern as task input? → A: Yes, validate on both frontend and backend with clear user-facing error messages.
- Q: Should empty or whitespace-only display names be rejected during signup? → A: Yes, reject with a validation error, consistent with task title validation pattern.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration and Authentication (Priority: P1)

A new user visits the application and creates an account with their display name, email, and password. After signing up, they are automatically signed in and redirected to their personal task dashboard. On subsequent visits, they sign in with their credentials. Their session persists until they explicitly sign out. A signed-out user cannot access any task functionality and is redirected to the sign-in page.

**Why this priority**: Authentication is the foundation for all other features. Without user identity, tasks cannot be owned, isolated, or persisted per user. Every other story depends on a user being authenticated.

**Independent Test**: Can be fully tested by creating an account, signing out, and signing back in — delivers secure access control and user identity.

**Acceptance Scenarios**:

1. **Given** a visitor with no account, **When** they provide a valid display name, email, and password on the sign-up page, **Then** the system creates their account, signs them in, and redirects them to the task dashboard.
2. **Given** a registered user on the sign-in page, **When** they enter valid credentials, **Then** the system authenticates them and redirects to the task dashboard.
3. **Given** a registered user on the sign-in page, **When** they enter an incorrect password, **Then** the system displays an error message and does not grant access.
4. **Given** a signed-in user, **When** they click "Sign Out", **Then** the system ends their session and redirects to the sign-in page.
5. **Given** an unauthenticated user, **When** they attempt to access any task-related page, **Then** the system redirects them to the sign-in page.
6. **Given** a visitor on the sign-up page, **When** they enter an email already associated with an account, **Then** the system displays an appropriate error message.

---

### User Story 2 - Create and View Tasks (Priority: P1)

An authenticated user creates a new task by providing a title (required, 1–200 characters) and an optional description (up to 1,000 characters). After creation, the task appears in their task list showing the title, completion status, and creation date. The user can view all their tasks in a list that only shows tasks belonging to them — they never see another user's tasks.

**Why this priority**: Creating and viewing tasks is the core value proposition of the application. Without this, the product has no purpose beyond authentication.

**Independent Test**: Can be fully tested by signing in, creating a task, and verifying it appears in the task list with correct details.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the task dashboard, **When** they provide a title and submit the new task form, **Then** the system creates the task and displays it in the task list with status "incomplete" and the current date.
2. **Given** an authenticated user on the task dashboard, **When** they provide a title and a description and submit, **Then** the system creates the task with both title and description.
3. **Given** an authenticated user on the new task form, **When** they submit without a title, **Then** the system displays a validation error and does not create the task.
4. **Given** an authenticated user on the new task form, **When** they enter a title longer than 200 characters, **Then** the system displays a validation error.
5. **Given** an authenticated user on the new task form, **When** they enter a description longer than 1,000 characters, **Then** the system displays a validation error.
6. **Given** two authenticated users (User A and User B), **When** User A views their task list, **Then** they see only their own tasks and none of User B's tasks.

---

### User Story 3 - Update Task Details (Priority: P2)

An authenticated user selects an existing task to edit its title and/or description. The updated information is saved and immediately reflected in the task list. The user can only edit tasks they own.

**Why this priority**: Editing tasks is essential for correcting mistakes and keeping task information current, but it builds on the foundation of task creation (P1).

**Independent Test**: Can be fully tested by creating a task, editing its title and description, and verifying the changes persist.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing their task list, **When** they select a task and update its title, **Then** the system saves the change and displays the updated title.
2. **Given** an authenticated user editing a task, **When** they update the description, **Then** the system saves the change and displays the updated description.
3. **Given** an authenticated user editing a task, **When** they clear the title field and submit, **Then** the system displays a validation error and does not save.
4. **Given** an authenticated user, **When** they attempt to update a task belonging to another user, **Then** the system denies the request.

---

### User Story 4 - Mark Task as Complete/Incomplete (Priority: P2)

An authenticated user toggles the completion status of a task. A task starts as incomplete when created. The user can mark it complete and later revert it to incomplete. The task list visually distinguishes completed tasks from incomplete ones.

**Why this priority**: Tracking completion is the core purpose of a todo application. It's separated from creation because it's a distinct interaction pattern (toggle vs. form submission).

**Independent Test**: Can be fully tested by creating a task, marking it complete, verifying the visual change, and toggling it back to incomplete.

**Acceptance Scenarios**:

1. **Given** an authenticated user with an incomplete task, **When** they toggle its completion status, **Then** the task is marked as complete and visually distinguished in the list.
2. **Given** an authenticated user with a completed task, **When** they toggle its completion status, **Then** the task reverts to incomplete.
3. **Given** an authenticated user, **When** they attempt to toggle completion on another user's task, **Then** the system denies the request.

---

### User Story 5 - Delete a Task (Priority: P2)

An authenticated user permanently removes a task from their list. The system asks for confirmation before deleting. Once deleted, the task is no longer visible and cannot be recovered. The user can only delete tasks they own.

**Why this priority**: Deletion is important for list hygiene but is destructive and irreversible, so it's lower priority than creation and updates.

**Independent Test**: Can be fully tested by creating a task, deleting it with confirmation, and verifying it no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing their task list, **When** they initiate deletion of a task and confirm, **Then** the system permanently removes the task and it no longer appears in the list.
2. **Given** an authenticated user, **When** they initiate deletion but cancel the confirmation, **Then** the task remains in the list unchanged.
3. **Given** an authenticated user, **When** they attempt to delete a task belonging to another user, **Then** the system denies the request.

---

### User Story 6 - Filter Tasks by Status (Priority: P3)

An authenticated user filters their task list to show only completed tasks, only incomplete tasks, or all tasks. The filter selection is reflected in the view immediately. The default view shows all tasks.

**Why this priority**: Filtering improves usability for users with many tasks but is not critical for core functionality. All tasks are still accessible without filtering.

**Independent Test**: Can be fully tested by creating several tasks, marking some complete, and verifying each filter option shows the correct subset.

**Acceptance Scenarios**:

1. **Given** an authenticated user with both completed and incomplete tasks, **When** they select the "Completed" filter, **Then** only completed tasks are displayed.
2. **Given** an authenticated user with both completed and incomplete tasks, **When** they select the "Incomplete" filter, **Then** only incomplete tasks are displayed.
3. **Given** an authenticated user viewing a filtered list, **When** they select "All", **Then** all tasks are displayed.
4. **Given** an authenticated user with no tasks matching the selected filter, **When** the filter is applied, **Then** the system displays an empty state message.

---

### Edge Cases

- What happens when a user's session token expires while they are actively using the application? The system should redirect to the sign-in page with a message indicating the session expired.
- What happens when a user submits a task with only whitespace as the title? The system should treat it as an empty title and reject it with a validation error.
- What happens when a user submits a signup form with only whitespace as the display name? The system should treat it as empty and reject it with a validation error.
- What happens when two browser tabs submit conflicting updates to the same task simultaneously? The last write wins; the system does not need to handle optimistic concurrency for Phase II.
- What happens when the database is temporarily unavailable? The system should display a user-friendly error message rather than a raw error.
- What happens when a user attempts to access a task by its ID via URL manipulation but the task belongs to another user? The system should return a "not found" response (not "forbidden") to avoid leaking information about task existence.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow new users to create an account with display name (required, 1–100 characters), email, and password.
- **FR-002**: System MUST authenticate returning users with email and password credentials.
- **FR-003**: System MUST issue a secure token upon successful authentication and include it in all subsequent requests to the backend.
- **FR-004**: System MUST reject all task-related requests that lack a valid authentication token with an "Unauthorized" response.
- **FR-005**: System MUST allow authenticated users to create tasks with a title (required, 1–200 characters) and an optional description (maximum 1,000 characters).
- **FR-006**: System MUST validate task input on both frontend and backend, rejecting empty/whitespace-only titles, titles exceeding 200 characters, and descriptions exceeding 1,000 characters.
- **FR-007**: System MUST persist all tasks to a durable database so they survive server restarts and are available across sessions and devices.
- **FR-008**: System MUST display each user's task list showing title, completion status, and creation date.
- **FR-009**: System MUST allow authenticated users to update the title and description of their own tasks.
- **FR-010**: System MUST allow authenticated users to toggle the completion status of their own tasks.
- **FR-011**: System MUST allow authenticated users to permanently delete their own tasks after confirmation.
- **FR-012**: System MUST support filtering the task list by status: all, completed, or incomplete.
- **FR-013**: System MUST enforce user isolation — every data operation (create, read, update, delete, toggle) MUST be scoped to the authenticated user's own tasks only.
- **FR-014**: System MUST expose task operations via a RESTful API that the frontend consumes.
- **FR-015**: System MUST return "not found" (not "forbidden") when a user attempts to access another user's task, to prevent information leakage.
- **FR-016**: System MUST redirect unauthenticated users to the sign-in page when they attempt to access protected pages.
- **FR-017**: System MUST allow authenticated users to sign out, ending their session.
- **FR-018**: System MUST record creation and last-updated timestamps for every task.
- **FR-019**: System MUST provide a responsive web interface that works on desktop and mobile browsers.
- **FR-020**: System MUST display an empty state message with a call-to-action to create the first task when a user has zero tasks.
- **FR-021**: System MUST display the task list sorted by creation date, newest first. Sort order is not user-configurable.
- **FR-022**: System MUST validate authentication inputs (display name 1–100 characters, valid email format, password minimum 8 characters) on both frontend and backend, rejecting invalid input with clear user-facing error messages.

### Key Entities

- **User**: A person who uses the application. Identified by a unique ID. Has a display name (required, 1–100 characters, provided at signup), email address (unique), and account creation date. Owns zero or more tasks.
- **Task**: A unit of work owned by exactly one user. Has a title (required, 1–200 characters), optional description (up to 1,000 characters), completion status (defaults to incomplete), creation timestamp, and last-updated timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can sign up, create their first task, and view it in their list in under 2 minutes.
- **SC-002**: An authenticated user can create, update, complete, and delete a task in under 30 seconds per operation.
- **SC-003**: 100% of task operations are scoped to the authenticated user — no user can view, edit, or delete another user's tasks under any circumstance.
- **SC-004**: The application is accessible and usable on both desktop (1024px+ width) and mobile (320px+ width) viewports.
- **SC-005**: All task data persists across browser sessions, device changes, and server restarts.
- **SC-006**: Invalid inputs (empty titles, oversized text, missing authentication) are rejected with clear, user-facing error messages 100% of the time.
- **SC-007**: The task list correctly filters by completion status, showing the accurate subset of tasks for each filter option.
- **SC-008**: The application loads and renders the task list within 3 seconds on a standard broadband connection.

## Assumptions

- Users authenticate with email and password only; social login (Google, GitHub, etc.) is out of scope for Phase II.
- There is no limit on the number of tasks a user can create in Phase II. Pagination or infinite scroll may be added in later phases if needed.
- Task ordering in the list defaults to creation date (newest first). Custom ordering/sorting is out of scope for Phase II.
- Password requirements follow standard web practices: minimum 8 characters. Advanced password policies are out of scope.
- Email verification is out of scope for Phase II — accounts are immediately active upon signup.
- The "last write wins" strategy is sufficient for concurrent edits in Phase II; optimistic concurrency control is deferred to later phases.

## Scope Boundaries

### In Scope
- User registration and authentication (email/password)
- Full CRUD operations on tasks (create, read, update, delete)
- Task completion toggling
- Task list filtering by status
- Persistent database storage
- RESTful API between frontend and backend
- Responsive web UI (desktop and mobile)
- User data isolation and ownership enforcement

### Out of Scope
- Social authentication providers (Google, GitHub, etc.)
- Task categories, tags, or priorities
- Task search functionality
- Task due dates or reminders
- Task sharing or collaboration between users
- Email notifications
- Drag-and-drop task reordering
- Offline support or PWA capabilities
- Admin panel or user management
- API rate limiting (deferred to Phase IV/V)
