# Private Daily Journal API

A backend-focused REST API project built using Django and Django REST Framework (DRF).

This project started as a simple CRUD journal application and gradually evolved into a deeper exploration of backend engineering — authentication systems, authorization logic, scalable API architecture, and real-world debugging.

The goal is not only building APIs, but understanding how backend systems work internally.

---

## What I have built

A fully functional private journaling API where:

- Users register and log in with JWT authentication
- Every user sees only their own journals — enforced at the database query level
- Journals support full CRUD — create, read, update, delete
- API supports search, ordering, and pagination
- A simple HTML + JavaScript frontend connects to the API
- Ownership is protected server-side — users cannot manipulate data belonging to others

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python |
| Framework | Django, Django REST Framework |
| Authentication | JWT (SimpleJWT), Session Auth |
| Database | SQLite |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Tools | Postman, DRF Browsable API, VS Code, WSL Ubuntu |

---

## Project structure

```
config/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── journals/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
│
├── users/
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── frontend/
│   ├── login.html
│   └── journals.html
│
├── db.sqlite3
└── manage.py
```

---

## API endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Register a new user |
| POST | `/api/login/` | Login — returns access and refresh tokens |
| POST | `/api/refresh/` | Get a new access token using refresh token |

### Journals

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/journals/` | List all journals (paginated) |
| POST | `/api/journals/` | Create a new journal |
| GET | `/api/journals/{id}/` | Retrieve a single journal |
| PUT | `/api/journals/{id}/` | Update a journal |
| DELETE | `/api/journals/{id}/` | Delete a journal |

### Query parameters

```
/api/journals/?search=travel          search by title or content
/api/journals/?ordering=-created_at   sort newest first
/api/journals/?page=2                 get page 2
/api/journals/?search=travel&ordering=-created_at&page=1   combine all
```

---

## Authentication system

### JWT flow

```
1. User sends POST /api/login/ with username and password
2. Django verifies credentials
3. Server generates two tokens:
   - access token  (short lived — 60 minutes)
   - refresh token (long lived  — 30 days)
4. Frontend stores both tokens
5. Every API request sends: Authorization: Bearer <access_token>
6. When access token expires — frontend sends refresh token to /api/refresh/
7. New access token issued silently — user never notices
8. Logout = frontend deletes both tokens — no backend change needed
```

### Why two tokens?

The access token travels with every single API request — higher chance of interception. So it lives for only 60 minutes. The refresh token is sent to only one endpoint, one time — much smaller attack surface. So it can safely live for 30 days.

### Token structure

Every JWT has three parts separated by dots:

```
header.payload.signature

header    → algorithm used (e.g. HS256)
payload   → user ID, expiry time, issued at
signature → cryptographic proof the token was not tampered with
```

---

## Security model

### Data isolation via get_queryset()

```python
def get_queryset(self):
    return Journal.objects.filter(
        user=self.request.user
    ).order_by('-created_at')
```

Every database query is filtered to the logged-in user's data only. If User A requests journal ID 99 which belongs to User B — it does not exist in User A's queryset. Django returns 404, not 403. This reveals less information to potential attackers.

### Server-side ownership via perform_create()

```python
def perform_create(self, serializer):
    serializer.save(user=self.request.user)
```

Journal ownership is always assigned server-side from the verified JWT token. The frontend cannot send a user field and assign journals to other users.

### Authentication vs authorization

```
Authentication = who are you?      → JWT token proves identity
Authorization  = what can you do?  → get_queryset() and IsOwner enforce access
```

Both layers are always active. Authentication happens first. Authorization happens on every data operation.

---

## Architecture concepts

### ModelViewSet

One class automatically generates five endpoints:

```python
class JournalViewSet(ModelViewSet):
    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']
```

### Filter pipeline order

Every request passes through this exact pipeline:

```
Request arrives
      ↓
get_queryset()     → security: your data only
      ↓
SearchFilter       → filter by search term if provided
      ↓
OrderingFilter     → sort results if ordering param provided
      ↓
Pagination         → slice into pages
      ↓
Serializer         → convert to JSON
      ↓
Response
```

### SearchFilter internally

```python
Q(title__icontains='travel') | Q(content__icontains='travel')
```

`icontains` = case-insensitive substring match. "Travel", "TRAVEL", "my travel diary" all match.

---

## Frontend integration

A simple HTML and JavaScript frontend connects to the Django API using `fetch()`.

```
Frontend (port 5500)              Backend (port 8000)
        |                                 |
        | GET /api/journals/              |
        | Authorization: Bearer <token>   |
        |  ─────────────────────────────→ |
        |                         JWT verified
        |                         query filtered
        |                         JSON prepared
        |  ←───────────────────────────── |
        | { count, next, results: [...] } |
        |                                 |
   renders journals                       |
```

CORS is handled via `django-cors-headers` allowing requests from `localhost:5500`.

### Frontend features

- Login with JWT — token stored in localStorage
- View all journals with search, pagination
- Create, edit, delete journal entries
- 6 switchable themes — Default, Dark, Paper, Forest, Cartoon, Galaxy
- Theme preference saved across sessions
- Keyboard shortcut: press `N` to open new entry

---

## Key learnings

### Technical

- How JWT authentication works internally — token structure, stateless verification, refresh flow
- The difference between authentication (identity) and authorization (permissions)
- How `get_queryset()` provides database-level security, not just view-level
- Why 404 is returned instead of 403 when a user requests another user's data
- How DRF filter backends form a security-first pipeline
- The difference between `auto_now` and `auto_now_add` on model fields
- How routers map HTTP methods to ViewSet actions automatically
- How CORS works and why it is needed for frontend-backend separation

### Professional

- Output matters more than effort — working code ships, perfect code never does
- Read error tracebacks carefully — they tell you exactly what went wrong
- Understand the problem fully before writing code
- Document as you build — it forces clarity of understanding

---

## Real debugging experience

During development, solved real backend issues including:

- manage.py path errors in WSL
- JWT configuration and token flow issues
- Router and ViewSet mapping errors
- AnonymousUser errors on protected endpoints
- CORS blocking frontend requests
- DateTimeField `auto_now_add` vs `auto_now` bug on `updated_at`
- Queryset filtering and ownership logic

---

## What is coming next

- PostgreSQL — replace SQLite with production database
- Docker — containerize the full project
- Swagger / OpenAPI documentation
- Token interceptor — silent refresh on 401
- Google OAuth2 login
- Deployment

---

## How to run locally

```bash
# clone the repo
git clone <your-repo-url>
cd config

# create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run migrations
python manage.py migrate

# start server
python manage.py runserver
```

API will be available at `http://127.0.0.1:8000/`

---

## Author

Subekshya Subedi
Geomatics Engineer — Backend and GIS Developer
Built as a backend engineering learning project focused on Django REST Framework, authentication systems, and scalable API architecture.