
# Event Management API

A Django REST Framework–based API for managing events, RSVPs, and reviews. Users can create events, RSVP, and leave reviews.


---

## 📸 Application Screenshots

### RSVP Panel
<p align="center">
  <img src="Photos/Admin.png" alt="Admin Panel" width="80%">
  <br>
  <em>Administrator interface for managing the entire system</em>
</p>

### AdminUser Dashboard
<p align="center">
  <img src="Photos/Dashboard.png" alt="Dashboard" width="80%">
  <br>
  <em>User dashboard showing events, RSVPs, and statistics</em>
</p>


### Events Page
<p align="center">
  <img src="Photos/Home.png" alt="Home Page" width="80%">
  <br>
  <em>Landing page with event highlights and navigation</em>
</p>

### Users Management
<p align="center">
  <img src="Photos/Users.png" alt="Users Management" width="80%">
  <br>
  <em>User management panel for administrators</em>
</p>

---
## Features

- JWT-based authentication  
- Create, update, and delete events  
- RSVP management and reviews  
- Private/public events  
- Permission-based access control  
- Search, filter, and pagination  

---s

## Models

### UserProfile
- full_name, bio, location, profile_picture  

### Event
- title, description, organizer, location, start/end time, is_public  

### RSVP
- event, user, status (Going/Maybe/Not Going)  

### Review
- event, user, rating (1–5), comment  

---

## API Endpoints

### Authentication

| Method | Endpoint               | Description          |
|--------|-----------------------|--------------------|
| POST   | `/api/token/`         | Obtain JWT token    |
| POST   | `/api/token/refresh/` | Refresh JWT token   |

### Events

| Method | Endpoint               | Description                 |
|--------|------------------------|----------------------------|
| GET    | `/api/events/`         | List public events          |
| POST   | `/api/events/`         | Create event (auth)         |
| GET    | `/api/events/{id}/`    | Event details               |
| PUT    | `/api/events/{id}/`    | Update event (organizer)    |
| PATCH  | `/api/events/{id}/`    | Partial update (organizer)  |
| DELETE | `/api/events/{id}/`    | Delete event (organizer)    |

### RSVP & Reviews

| Method | Endpoint                          | Description           |
|--------|----------------------------------|---------------------|
| POST   | `/api/events/{event_id}/rsvp/`   | RSVP to event        |
| GET    | `/api/events/{event_id}/rsvp/`   | List RSVPs           |
| PATCH  | `/api/events/{event_id}/rsvp/{pk}/` | Update RSVP status |
| POST   | `/api/events/{event_id}/reviews/` | Add review          |
| GET    | `/api/events/{event_id}/reviews/` | List reviews        |

---

## Quick Setup

```bash
git clone https://github.com/Aanushka001/Event-Management-API.git
cd Event-Management-API

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser --username admin_001 --email admin@example.com
-- Password: admin_002

python manage.py runserver
````

API available at: `http://127.0.0.1:8000/`

---

## Usage Examples

### Obtain JWT Token

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_001", "password": "admin_002"}'
```

### Create an Event

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Tech Meetup","description":"Monthly tech discussion","location":"NY","start_time":"2025-12-15T18:00:00Z","end_time":"2025-12-15T20:00:00Z","is_public":true}'
```

---

## Search & Filtering

* `/api/events/?search=tech`
* `/api/events/?location=New York`
* `/api/events/?is_public=true`
* `/api/events/?ordering=start_time`

---

## Permissions

* **IsOrganizerOrReadOnly** — Only organizers can edit/delete events
* **IsInvitedToPrivateEvent** — Only invited users can access private events
* **IsOwnerOrReadOnly** — Users may edit only their own RSVPs/reviews

---

## Technologies

* Django 5.2.9
* Django REST Framework
* djangorestframework-simplejwt
* django-filter
* SQLite (default)

