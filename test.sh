#!/bin/bash

BASE_URL="http://127.0.0.1:8000"

USERNAME="admin_user"
PASSWORD="admin_002"

echo "=== Getting JWT Token ==="
TOKEN=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" | jq -r '.access')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "Failed to retrieve token. Check username/password."
  exit 1
fi

echo "TOKEN ACQUIRED:"
echo "$TOKEN"
echo ""

AUTH="Authorization: Bearer $TOKEN"

echo "=== Testing ROOT Route ==="
curl -s "$BASE_URL/" | jq
echo ""

echo "=== Listing Events (Public) ==="
curl -s "$BASE_URL/api/events/" | jq
echo ""

echo "=== Creating Event (Auth) ==="
EVENT_ID=$(curl -s -X POST "$BASE_URL/api/events/" \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "API Test Event",
        "description": "Automatically created test event",
        "location": "Earth",
        "start_time": "2025-12-20T18:00:00Z",
        "end_time": "2025-12-20T20:00:00Z",
        "is_public": true
      }' | jq -r '.id')

echo "Event created with ID: $EVENT_ID"
echo ""

echo "=== Getting Event Details ==="
curl -s "$BASE_URL/api/events/$EVENT_ID/" | jq
echo ""

echo "=== Creating RSVP ==="
curl -s -X POST "$BASE_URL/api/events/$EVENT_ID/rsvp/" \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"status": "Going"}' | jq
echo ""

echo "=== Creating Review ==="
curl -s -X POST "$BASE_URL/api/events/$EVENT_ID/reviews/" \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "comment": "Excellent event!"}' | jq
echo ""

echo "=== Listing RSVPs ==="
curl -s "$BASE_URL/api/events/$EVENT_ID/rsvp/" | jq
echo ""

echo "=== Listing Reviews ==="
curl -s "$BASE_URL/api/events/$EVENT_ID/reviews/" | jq
echo ""

echo "=== Filter / Search Test ==="
curl -s "$BASE_URL/api/events/?search=api" | jq
echo ""

echo "=== ALL DONE 🎉 ==="
