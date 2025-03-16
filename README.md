# Trip Planning and Logging System

## Overview

This project is a web application designed to assist drivers and logistics companies in planning trips and maintaining daily log sheets. Built with Django (backend) and React (frontend), it calculates optimal routes, includes fuel stops, and generates driver log sheets compliant with standard formats (e.g., 70-hour/8-day rules for property-carrying drivers). The system integrates with the Geoapify API for geocoding and routing.

- **Backend**: Django REST Framework with API endpoints for route calculation and trip management.

- **Features**:
  - Calculate routes with starting, middle, and end points.
  - Add fuel stops every 1000 miles.
  - Generate daily log sheets for multi-day trips.
  - Visualize routes on a map using Leaflet.

## Prerequisites

- Python 3.8+
- Node.js 14.x+
- pip (Python package manager)
- npm or yarn (JavaScript package manager)
- Git (for version control)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/uno36/trip-planning-logging.git
cd trip-planning-logging
```

### 2. Backend Setup
#### Install Dependencies
```bash
cd trip-backend
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the `trip-backend` directory and add the following:
```
GEOAPIFY_API_KEY=your_geoapify_api_key_here
DEBUG=True
SECRET_KEY=your_django_secret_key_here# Or your preferred database URL
```

- Obtain a Geoapify API key from [Geoapify](https://www.geoapify.com/) and replace `your_geoapify_api_key_here`.
- Generate a Django `SECRET_KEY` using `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` or an online generator.

#### Apply Migrations
```bash
python manage.py migrate
```

#### Run the Development Server
```bash
DATABASE_URL=sqlite:///db.sqlite3  
python manage.py runserver
```
The backend will be available at `http://localhost:8000`.


## API Endpoints

The backend provides the following RESTful endpoints:

### 1. `POST /api/calculate_route/`
- **Description**: Calculates a trip route, including coordinates, fuel stops, and daily log sheets.
- **Request Body**:
  ```json
  {
    "current_location": "string",  // e.g., "New York, NY"
    "pickup_location": "string",   // e.g., "Chicago, IL"
    "dropoff_location": "string",  // e.g., "Los Angeles, CA"
    "current_cycle_used": "integer" // e.g., 10
  }
  ```
- **Response** (Success - `200 OK`):
  ```json
  {
    "coordinates": [[latitude, longitude], ...],  // Array of route coordinates
    "fuel_stop_coordinates": [[latitude, longitude], ...],  // Fuel stop coordinates
    "distance_miles": float,  // Total distance in miles
    "total_hours": float,     // Total driving hours + 2 (pickup/dropoff)
    "log_sheets": [
      {
        "day": integer,       // Day number
        "date": "string",     // Date in YYYY-MM-DD format
        "start_time": "string", // Start time in HH:MM format
        "end_time": "string",  // End time in HH:MM format
        "driving_hours": float, // Hours driving
        "on_duty_hours": float, // Total on-duty hours (includes pickup/dropoff)
        "off_duty_hours": float, // Off-duty hours
        "fuel_stops": integer   // Number of fuel stops for the day
      }
    ]
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Missing fields or geocoding failure.
  - `503 Service Unavailable`: Geoapify API error.
  - `500 Internal Server Error`: Unexpected server error.

### 2. `GET /api/trips/`
- **Description**: Lists all saved trips (via `TripViewSet`).
- **Response** (Success - `200 OK`):
  ```json
  [
    {
      "id": integer,
      "current_location": "string",
      "pickup_location": "string",
      "dropoff_location": "string",
      "current_cycle_used": integer,
      "created_at": "string"  // ISO datetime
    }
  ]
  ```
- **Error Responses**: Standard Django REST Framework errors (e.g., `404 Not Found` if no trips exist).

### 3. `POST /api/trips/`
- **Description**: Creates a new trip (via `TripViewSet`).
- **Request Body**:
  ```json
  {
    "current_location": "string",
    "pickup_location": "string",
    "dropoff_location": "string",
    "current_cycle_used": integer
  }
  ```
- **Response** (Success - `201 Created`): Same as `GET /api/trips/` single object.
- **Error Responses**: `400 Bad Request` for invalid data.

## Assumptions
- **Driver Type**: Property-carrying driver with a 70-hour/8-day cycle.
- **Conditions**: No adverse driving conditions.
- **Fuel Stops**: One fuel stop every 1000 miles, none if less than 1000 miles.
- **Pickup/Drop-off**: 1 hour each for pickup and drop-off, added to total hours.

## Project Structure

```
trip-planning-logging/
├── trip-backend/           # Django backend
│   ├── trip/              # Main app
│   │   ├── migrations/
│   │   ├── models.py      # Trip model
│   │   ├── serializers.py # TripSerializer
│   │   ├── views.py       # API views (calculate_route, TripViewSet)
│   │   ├── urls.py        # URL configuration
│   ├── manage.py
│   ├── requirements.txt

├── README.md
```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make changes and commit (`git commit -m "Description of changes"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, contact [emmanuelutofa@gmail.com](mailto:emmanuelutofa@gmail.com).

## Acknowledgments
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Geoapify](https://www.geoapify.com/)
---

