# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Teamglade is a free online collaboration platform for sharing files and messages in teams. Built with Django 4.1.2 and PostgreSQL.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r teamglade/requirements.txt

# Run database migrations
python teamglade/manage.py migrate

# Create admin user
python teamglade/manage.py createsuperuser
```

### Running the Application
```bash
# Start development server
python teamglade/manage.py runserver

# Collect static files (for production)
python teamglade/manage.py collectstatic
```

### Testing
```bash
# Run all tests
python teamglade/manage.py test accounts rooms

# Run tests for specific app
python teamglade/manage.py test accounts
python teamglade/manage.py test rooms

# Run specific test class or method
python teamglade/manage.py test accounts.tests.test_view_signup.SignupViewTests
python teamglade/manage.py test rooms.tests.test_view_home.HomeViewTests.test_home_view_status_code
```

### Database
```bash
# Create migrations after model changes
python teamglade/manage.py makemigrations

# Apply migrations
python teamglade/manage.py migrate

# Access Django shell
python teamglade/manage.py shell
```

## Architecture

### Project Structure
- **teamglade/teamglade/** - Main Django project configuration (settings, root URLs)
- **teamglade/accounts/** - User authentication, signup, password reset, email confirmation
- **teamglade/rooms/** - Core collaboration features (rooms, topics, file sharing)

### Apps

#### accounts
Handles user authentication and account management:
- Custom authentication flows (signup, login, password reset)
- Email confirmation system with token-based verification
- User profile updates (username, email, password)
- Uses Django's built-in auth views where possible

#### rooms
Core collaboration functionality:
- Room management (teams/groups)
- Topic creation (messages with file attachments)
- File sharing with multiple file uploads
- Invite system via email
- Read/unread tracking for topics

### Data Models

**Custom User Model:** `rooms.RoomUser` (extends `AbstractUser`)
- `invite_code` - Unique code for room invitations
- `member_of` - ForeignKey to Room (for invited members)
- Users can either **own** a room (`Room.created_by`) or be **members** (`RoomUser.member_of`)

**Room**
- Owned by one user (`created_by`)
- Has many members (via `RoomUser.member_of` reverse relation)
- Contains many topics

**Topic**
- Belongs to a Room
- Created by a RoomUser
- Has title and message (max 1000 chars)
- Tracks which users have read it (`was_read_by` - ManyToMany)
- Can have multiple file attachments

**File**
- Attached to a Topic
- Uploaded to 'uploads/' directory
- Automatically deleted from filesystem when File instance is deleted (via pre_delete signal)

### Key Implementation Details

**Custom User Model Configuration:**
```python
AUTH_USER_MODEL = "rooms.RoomUser"
LOGIN_REDIRECT_URL = 'room'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
```

**Room Access Pattern:**
- Users access "their room" which is either:
  1. A room they created (`user.rooms.first()`)
  2. A room they're a member of (`user.member_of`)
- The `get_user_room()` helper function in views handles this logic

**File Upload Handling:**
- Custom `MultipleFileField` and `MultipleFileInput` in `rooms/forms.py` for handling multiple files
- Files are created separately after Topic creation in views
- File model has `filename()` method to get basename for display

**Email Invite System:**
- Generates unique invite codes using `uuid4()`
- Sends email with registration link containing the invite code
- Invited users can create account and are automatically added to the room

**Topic Read Tracking:**
- Topics have `was_read_by` ManyToMany field
- When a user views a topic, they're added to this field
- Room view shows which topics are unread for the current user

### Environment Configuration

Settings load from `DO_prod.env` file (DigitalOcean production environment):
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DJANGO_ALLOWED_HOSTS` - Space-separated allowed hosts
- `CSRF_TRUSTED_ORIGINS` - Space-separated trusted origins
- Database settings: `DATABASE_ENGINE`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`
- Email settings: `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, etc.
- `STATIC_URL`, `MEDIA_ROOT`, `MEDIA_URL`
- `LOGS_DIR` - Directory for log files

### Logging

Configured for the accounts app with two handlers:
- `accounts_security.log` - WARNING level and above (security-related events)
- `accounts.log` - INFO level and above (general account activities)

Both use rotating file handlers (5MB max, 10 backups).

## Docker Support

Dockerfile available in `teamglade/` directory:
- Base image: Python 3.10 (Bullseye)
- Exposes port 8000
- Production deployment typically uses Gunicorn (included in requirements.txt)
