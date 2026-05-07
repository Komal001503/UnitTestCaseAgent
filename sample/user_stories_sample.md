# User Stories

Total stories: 3

| Story ID | Title            | Description                                      | Acceptance Criteria                                                                 | Priority |
|----------|------------------|--------------------------------------------------|-------------------------------------------------------------------------------------|---------|
| US-101   | User Login       | Users should be able to log in to the application | Valid credentials → redirect to dashboard; Invalid credentials → show error message; Account locked after 5 failed attempts | High     |
| US-102   | Password Reset   | Users should be able to reset their password       | Reset email sent within 1 minute; Reset link expires after 24 hours; New password must meet complexity requirements | High     |
| US-103   | User Profile     | Users should be able to view and edit profile      | Display all profile fields; Allow editing name and email; Validate email format; Show success message on save | Medium   |

---

## Individual Stories

### US-101: User Login

**Priority:** High

**Description:** Users should be able to log in to the application

**Acceptance Criteria:**
- Valid credentials → redirect to dashboard
- Invalid credentials → show error message
- Account locked after 5 failed attempts

### US-102: Password Reset

**Priority:** High

**Description:** Users should be able to reset their password

**Acceptance Criteria:**
- Reset email sent within 1 minute
- Reset link expires after 24 hours
- New password must meet complexity requirements

### US-103: User Profile

**Priority:** Medium

**Description:** Users should be able to view and edit profile

**Acceptance Criteria:**
- Display all profile fields
- Allow editing name and email
- Validate email format
- Show success message on save
