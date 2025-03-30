# Amherst Lost & Found

This is a Django-based web application for managing lost and found items at Amherst College. Users can report lost items, submit found items, and search for items in the database.

## Features
- Submit lost or found items with details and images.
- Search and filter items by keywords, location, and status.
- User authentication for secure access.

## Setup
1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run migrations with `python manage.py migrate`.
4. Start the development server using `python manage.py runserver`.

## Folder Structure
- `items/`: Contains the main app for managing items.
- `accounts/`: Handles user authentication and profiles.
- `static/`: Stores static files like CSS and JavaScript.
- `templates/`: Contains HTML templates for the app.
