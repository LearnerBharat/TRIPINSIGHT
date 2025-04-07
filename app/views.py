from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import pandas as pd
import pickle
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import googlemaps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
# Create your views here.

def index(request):
    user = request.user
    places = PlaceMode.objects.all()
    return render(request, 'home-professional.html', {"places" : places[0: 3], 'user': user})




def details(request, pk):
    try:
        place = get_object_or_404(PlaceMode, id=pk)
        places_pickle = os.path.join(settings.MEDIA_ROOT, 'places.pkl')
        similarity_pickle = os.path.join(settings.MEDIA_ROOT, 'similarity.pkl')

        try:
            with open(places_pickle, 'rb') as f:
                place_dict = pickle.load(f)

            with open(similarity_pickle, 'rb') as f:
                similarity = pickle.load(f)

            name = place.Name
            # Handle case where place name might not be in the pickle file
            if not place_dict[place_dict['Name'] == name].empty:
                place_index = place_dict[place_dict['Name'] == name].index[0]
                distances = similarity[place_index]
                places_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:5]
                recommended_places = [PlaceMode.objects.get(id=i[0]) for i in places_list]
            else:
                # Fallback if place not found in recommendation system
                recommended_places = PlaceMode.objects.exclude(id=pk).order_by('?')[:4]
        except (FileNotFoundError, KeyError, IndexError, EOFError) as e:
            # Handle pickle file errors gracefully
            recommended_places = PlaceMode.objects.exclude(id=pk).order_by('?')[:4]
            messages.warning(request, "Some recommendations may not be available at the moment.")

        crowd_data = CrowdModel.objects.filter(location=place)
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        reviews = TripReview.objects.filter(place=place)

        return render(request, 'place-details-professional.html', {
            "rec_places": recommended_places,
            "single_place": place,
            "crowd_data": crowd_data,
            "months": months,
            "reviews": reviews,
            "messages": messages.get_messages(request)
        })
    except Exception as e:
        messages.error(request, f"We couldn't load this destination. Please try again later.")
        return redirect('index')

def search_view(request):
    try:
        query = request.GET.get('q', '').strip()
        state = request.GET.get('state', '').strip()
        place_type = request.GET.get('type', '').strip()

        results = PlaceMode.objects.all()

        # Apply filters
        if query:
            results = results.filter(
                models.Q(Name__icontains=query) |
                models.Q(City__icontains=query) |
                models.Q(State__icontains=query) |
                models.Q(Significance__icontains=query) |
                models.Q(Type__icontains=query)
            )

        if state:
            results = results.filter(State__iexact=state)

        if place_type:
            results = results.filter(Type__iexact=place_type)

        # Check if no results found
        if not results.exists() and (query or state or place_type):
            if query and not state and not place_type:
                message = f'No destinations found for "{query}". Try a different search term or browse our featured destinations.'
            elif state and not query and not place_type:
                message = f'No destinations found in {state}. Try a different state or browse our featured destinations.'
            elif place_type and not query and not state:
                message = f'No {place_type} destinations found. Try a different category or browse our featured destinations.'
            else:
                message = 'No destinations match your search criteria. Try adjusting your filters.'

            messages.info(request, message)

            # Provide some recommended places instead
            recommended = PlaceMode.objects.order_by('?')[:8]  # Random selection
            return render(
                request,
                'search-page.html',
                {
                    'places': recommended,
                    'query': query,
                    'state': state,
                    'type': place_type,
                    'no_results': True,
                    'recommended': True
                }
            )

        return render(
            request,
            'search-page.html',
            {
                'places': results,
                'query': query,
                'state': state,
                'type': place_type,
                'count': results.count()
            }
        )
    except Exception as e:
        messages.error(request, "An error occurred while processing your search. Please try again.")
        return render(request, 'search-page.html', {'places': PlaceMode.objects.all()[:12]})

def signup_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')

            # Validate all fields are provided
            if not username or not email or not password1 or not password2:
                messages.error(request, '❌ All fields are required. Please fill in all the information.')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email
                })

            # Validate username length
            if len(username) < 3:
                messages.error(request, '❌ Username must be at least 3 characters long.')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email
                })

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, '❌ This username is already taken. Please choose a different username.')
                return render(request, 'signup.html', {
                    'email': email
                })

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, '❌ An account with this email already exists. Please use a different email or try logging in.')
                return render(request, 'signup.html', {
                    'username': username
                })

            # Validate password length
            if len(password1) < 8:
                messages.error(request, '❌ Password must be at least 8 characters long.')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email
                })

            # Check if passwords match
            if password1 != password2:
                messages.error(request, '❌ Passwords do not match. Please make sure both passwords are identical.')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email
                })

            # Create user
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            login(request, user)
            messages.success(request, "✅ Welcome to TripInsight! Your registration was successful. Please complete your profile to get personalized recommendations.")
            return redirect('create_profile')

        except Exception as e:
            messages.error(request, '❌ An error occurred during registration. Please try again.')
            return render(request, 'signup.html')

    return render(request, 'signup.html')

# Login View
def login_view(request):
    # If user is already logged in, redirect to home
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('index')

    # Get the next parameter if it exists
    next_url = request.GET.get('next', 'index')

    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')

            # Validate inputs
            if not username or not password:
                messages.error(request, '❌ Both username and password are required.')
                return render(request, 'login-new.html', {'username': username, 'next': next_url})

            # Check if user exists first
            if not User.objects.filter(username=username).exists():
                messages.error(request, '❌ This username does not exist. Please check your username or sign up for a new account.')
                return render(request, 'login-new.html', {'username': username, 'next': next_url})

            # Try to authenticate
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if user is active
                if not user.is_active:
                    messages.error(request, '❌ Your account has been disabled. Please contact support for assistance.')
                    return render(request, 'login-new.html', {'username': username, 'next': next_url})

                login(request, user)
                messages.success(request, '✅ Login successful! Welcome back, ' + user.username + '.')

                # Redirect to the next URL or home
                return redirect(next_url)
            else:
                messages.error(request, '❌ Incorrect password. Please try again or use the forgot password option.')
                return render(request, 'login-new.html', {'username': username, 'next': next_url})

        except Exception as e:
            messages.error(request, '❌ An error occurred during login. Please try again.')
            return render(request, 'login-new.html', {'next': next_url})

    return render(request, 'login-new.html', {'next': next_url})

# Logout View
def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'✅ You have been successfully logged out. Thanks for visiting, {username}!')
    else:
        messages.info(request, 'You were not logged in.')

    # Redirect to the page they came from, or home if not available
    next_url = request.GET.get('next', 'index')
    return redirect(next_url)

# Initialize Google Maps client with API key
# Note: In production, this key should be stored in environment variables
try:
    gmaps = googlemaps.Client(key="AIzaSyAyUAkmbw3LUmZy5w15DmMFaVh3x-utvHw")
except Exception as e:
    # Log the error but don't crash the application
    print(f"Error initializing Google Maps client: {e}")
    gmaps = None

def get_distance(origin, destination):
    """
    Calculate the distance between two locations using Google Maps Distance Matrix API.

    Args:
        origin (str): The starting location (address, city, coordinates)
        destination (str): The ending location (address, city, coordinates)

    Returns:
        float or None: Distance in kilometers, or None if calculation failed
    """
    # If Google Maps client initialization failed, return None
    if gmaps is None:
        return None

    # Validate inputs
    if not origin or not destination:
        return None

    try:
        # Make API request
        result = gmaps.distance_matrix(
            origins=origin,
            destinations=destination,
            mode="driving",
            units="metric"
        )

        # Check if we got a valid response
        if not result or "rows" not in result or not result["rows"]:
            return None

        # Extract distance information
        element = result["rows"][0]["elements"][0]

        if element["status"] == "OK" and "distance" in element:
            distance = element["distance"]["value"]  # Distance in meters
            return round(distance / 1000, 2)  # Convert to kilometers and round to 2 decimal places
        else:
            # Handle various error statuses
            status = element.get("status", "UNKNOWN_ERROR")
            print(f"Distance calculation failed with status: {status}")
            return None

    except Exception as e:
        print(f"Error fetching distance: {e}")
        return None

@csrf_exempt
def estimate_cost(request):
    """
    API endpoint to estimate travel costs based on origin and destination.

    Expected POST data:
    {
        "origin": "City or address",
        "destination": "City or address",
        "num_people": 1 (optional)
    }

    Returns JSON with estimated costs for different travel modes.
    """
    if request.method != "POST":
        return JsonResponse({
            "error": "Only POST method is allowed",
            "status": "error"
        }, status=405)

    try:
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "error": "Invalid JSON data",
                "status": "error"
            }, status=400)

        # Extract and validate parameters
        origin = data.get("origin", "").strip()
        destination = data.get("destination", "").strip()

        # Validate required fields
        if not origin or not destination:
            return JsonResponse({
                "error": "Origin and destination are required",
                "status": "error"
            }, status=400)

        # Parse and validate number of people
        try:
            num_people = int(data.get("num_people", 1))
            if num_people < 1:
                num_people = 1
            elif num_people > 20:  # Set a reasonable upper limit
                num_people = 20
        except (ValueError, TypeError):
            num_people = 1

        # Get distance between origin and destination
        distance_km = get_distance(origin, destination)

        if distance_km is None:
            return JsonResponse({
                "error": "Could not calculate distance between the provided locations",
                "status": "error",
                "suggestion": "Please check the spelling of your origin and destination"
            }, status=400)

        # Calculate costs for different travel modes
        # Car cost calculation (fuel + tolls)
        car_cost = distance_km * 10

        # Train cost calculation with tiered pricing
        if distance_km <= 100:
            train_cost = distance_km * 6
        elif distance_km <= 500:
            train_cost = distance_km * 5
        else:
            train_cost = distance_km * 4

        # Air cost calculation with tiered pricing
        if distance_km <= 500:
            air_cost = distance_km * 15  # Short flights are more expensive per km
        elif distance_km <= 1000:
            air_cost = distance_km * 12
        else:
            air_cost = distance_km * 10

        # Bus cost calculation
        bus_cost = distance_km * 3

        # Adjust costs for number of people (except car which is shared)
        train_cost *= num_people
        air_cost *= num_people
        bus_cost *= num_people

        # Accommodation cost estimate (per night)
        accommodation_cost = 1500 * num_people

        # Food cost estimate (per day)
        food_cost = 500 * num_people

        # Return the estimates
        return JsonResponse({
            "status": "success",
            "distance_km": distance_km,
            "car_cost": int(car_cost),
            "train_cost": int(train_cost),
            "air_cost": int(air_cost),
            "bus_cost": int(bus_cost),
            "accommodation_cost": int(accommodation_cost),
            "food_cost": int(food_cost),
            "currency": "INR",
            "num_people": num_people,
            "note": "These are rough estimates and actual costs may vary"
        })

    except Exception as e:
        # Log the error for debugging
        print(f"Error in estimate_cost: {str(e)}")

        return JsonResponse({
            "error": "An error occurred while estimating costs",
            "status": "error",
            "details": str(e)
        }, status=500)

# def submit_trip_review(request, pk):
#     if request.user.is_authenticated:
#         place = PlaceMode.objects.get(id=pk)
#         if request.method == "POST":
#             title = request.POST.get("title")
#             description = request.POST.get("description")
#             travel_medium = request.POST.get("travel_medium")
#             travel_cost = request.POST.get("travel_cost")
#             accommodation_cost = request.POST.get("accommodation_cost")
#             food_cost = request.POST.get("food_cost")
#             rating = request.POST.get("rating")


#             # Create TripReview object
#             TripReview.objects.create(
#                 title=title,
#                 description=description,
#                 travel_medium=travel_medium,
#                 travel_cost=travel_cost,
#                 accommodation_cost=accommodation_cost,
#                 food_cost=food_cost,
#                 user=request.user,
#                 place=place,
#                 rating=rating
#             )

#             messages.success(request, "Your trip review has been submitted!")
#             return redirect(reverse("submit_trip_review", kwargs={"pk": place.id}))  # Redirect to the same page or another
#     else:
#         return redirect("/login")
#     return render(request, "reviewform.html", {"single_place": place}) 

def submit_trip_review(request, pk):
    if not request.user.is_authenticated:
        return redirect("/login")

    place = get_object_or_404(PlaceMode, id=pk)  # Ensures place exists

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        travel_medium = request.POST.get("travel_medium")
        travel_cost = request.POST.get("travel_cost")
        accommodation_cost = request.POST.get("accommodation_cost")
        food_cost = request.POST.get("food_cost")
        rating = request.POST.get("rating")
        no_of_people = request.POST.get("no_of_people", 1)  # Default to 1 if not provided

        # Create TripReview object
        TripReview.objects.create(
            title=title,
            description=description,
            travel_medium=travel_medium,
            travel_cost=travel_cost,
            accommodation_cost=accommodation_cost,
            food_cost=food_cost,
            user=request.user,
            place=place,
            rating=rating,
            no_of_people=no_of_people
        )

        messages.success(request, "✅ Your review has been submitted successfully! Thank you for sharing your experience.")

        # Redirect to the place detail page with a parameter to indicate a successful submission
        return redirect(reverse("details", kwargs={"pk": place.id}))

    return render(request, "reviewform.html", {"single_place": place})

def create_profile(request):
    if request.method == "POST":
        full_name = request.POST.get("name")
        description = request.POST.get("description")
        state = request.POST.get("state")

        if not full_name or not description or not state:
            messages.error(request, "All fields are required.")
            return redirect("create_profile")

        user = request.user if request.user.is_authenticated else None

        profile, created = ProfileModel.objects.get_or_create(user=user)
        profile.state = state
        profile.description = description
        profile.save()

        messages.success(request, "Profile created successfully!")
        return redirect("/")

    return render(request, "profile_form.html")

def profile(request):
    if request.user.is_authenticated:
        if not ProfileModel.objects.filter(user=request.user).exists():
            return redirect("/create-profile")
        profile = ProfileModel.objects.get(user=request.user)
        reviews = None
        review_count = 0
        trophies = 0
        if TripReview.objects.filter(user=request.user).exists():
            reviews = TripReview.objects.filter(user=request.user)
            review_count = reviews.count()
            trophies = int(review_count / 2)
        return render(request, "profilepage.html", {
            "trophies": trophies,
            "profile": profile,
            "reviews": reviews,
            "count": review_count,
            "messages": messages.get_messages(request)
        })
    else:
        messages.error(request, "Please login to view your profile")
        return redirect("/login")

def stories(request):
    reviews = TripReview.objects.all()
    return render(request, "stories-new.html", {"reviews": reviews})

def about(request):
    return render(request, "about-new.html")

def explore(request):
    # Get filter type from query parameters
    place_type = request.GET.get('type')

    # Filter places if a type is specified
    if place_type and place_type != 'all':
        places = PlaceMode.objects.filter(Type__icontains=place_type)
    else:
        places = PlaceMode.objects.all()

    # Get featured places (places with highest ratings)
    featured_places = PlaceMode.objects.all().order_by('-Google_rating')[:3]

    context = {
        'places': places,
        'featured_places': featured_places
    }

    return render(request, "explore-page.html", context)
