from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Trip
from .serializers import TripSerializer
import requests
from django.conf import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@api_view(['POST'])
def calculate_route(request):
    data = request.data
    logger.info(f"Received request data: {data}")

    try:
        current_location = data['current_location']
        pickup_location = data['pickup_location']
        dropoff_location = data['dropoff_location']
        current_cycle_used = data['current_cycle_used']

        def geocode_address(address):
            api_key = settings.GEOAPIFY_API_KEY
            url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['features']:
                coords = data['features'][0]['geometry']['coordinates']
                return [coords[1], coords[0]]  # [lat, lng]
            return None

        current_coords = geocode_address(current_location)
        pickup_coords = geocode_address(pickup_location)
        dropoff_coords = geocode_address(dropoff_location)

        if not all([current_coords, pickup_coords, dropoff_coords]):
            logger.error("Geocoding failed")
            return Response(
                {"error": "Failed to geocode one or more locations"},
                status=status.HTTP_400_BAD_REQUEST
            )

        waypoints = f"{current_coords[0]},{current_coords[1]}|{pickup_coords[0]},{pickup_coords[1]}|{dropoff_coords[0]},{dropoff_coords[1]}"
        api_key = settings.GEOAPIFY_API_KEY
        routing_url = f"https://api.geoapify.com/v1/routing?waypoints={waypoints}&mode=drive&apiKey={api_key}"
        routing_response = requests.get(routing_url)
        routing_data = routing_response.json()

        if routing_response.status_code != 200 or 'features' not in routing_data:
            logger.error("Routing failed")
            return Response(
                {"error": "Failed to calculate route"},
                status=status.HTTP_400_BAD_REQUEST
            )

        route = routing_data['features'][0]
        coordinates = []
        for line in route['geometry']['coordinates']:
            for point in line:
                coordinates.append([point[1], point[0]])  # [lat, lng]

        total_distance_meters = route['properties']['distance']
        total_distance_miles = total_distance_meters / 1609.34
        total_duration_seconds = route['properties']['time']
        driving_hours = total_duration_seconds / 3600

        remaining_cycle = 70 - current_cycle_used
        days_needed = max(1, int((driving_hours + 2) // 11))
        fuel_stops_count = max(0, int(total_distance_miles // 1000))

        # Calculate approximate fuel stop coordinates (simple linear interpolation)
        fuel_stop_coordinates = []
        if fuel_stops_count > 0:
            segment_length = len(coordinates) / (fuel_stops_count + 1)
            for i in range(1, fuel_stops_count + 1):
                index = int(i * segment_length)
                if index < len(coordinates):
                    fuel_stop_coordinates.append(coordinates[index])

        log_sheets = []
        start_time = datetime.now()
        hours_per_day = min(driving_hours, 11)
        for day in range(days_needed):
            daily_hours = min(
                hours_per_day, driving_hours - day * hours_per_day)
            end_time = start_time + timedelta(hours=daily_hours)
            log_entry = {
                "day": day + 1,
                "date": start_time.strftime("%Y-%m-%d"),
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "driving_hours": daily_hours,
                "on_duty_hours": daily_hours + (2 if day == 0 or day == days_needed - 1 else 0),
                "off_duty_hours": 24 - (daily_hours + (2 if day == 0 or day == days_needed - 1 else 0)),
                "fuel_stops": min(fuel_stops_count, 1 if total_distance_miles - day * 1000 > 0 else 0)
            }
            log_sheets.append(log_entry)
            start_time = end_time + timedelta(hours=13)
            fuel_stops_count -= 1 if fuel_stops_count > 0 else 0

        trip = Trip(
            current_location=current_location,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            current_cycle_used=current_cycle_used
        )
        trip.save()

        logger.info("Route calculated successfully")
        return Response({
            "coordinates": coordinates,
            "fuel_stop_coordinates": fuel_stop_coordinates,
            "distance_miles": total_distance_miles,
            "total_hours": driving_hours + 2,
            "log_sheets": log_sheets
        })

    except KeyError as e:
        logger.error(f"Missing field: {str(e)}")
        return Response(
            {"error": f"Missing field: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        logger.error(f"Geoapify API error: {str(e)}")
        return Response(
            {"error": f"Geoapify API error: {str(e)}"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
