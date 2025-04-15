from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import pandas as pd
import pickle
import os
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import googlemaps
from django.http import JsonResponse
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
# Create your views here.

def index(request):
    user = request.user
    # Filter places to only show Maharashtra places
    places = PlaceMode.objects.filter(State='Maharashtra')
    
    # Get all available states, types, and significances for filter dropdowns
    all_states = PlaceMode.objects.values_list('State', flat=True).distinct().order_by('State')
    all_types = PlaceMode.objects.values_list('Type', flat=True).distinct().order_by('Type')
    all_significances = PlaceMode.objects.values_list('Significance', flat=True).distinct().order_by('Significance')
    
    return render(request, 'home-professional.html', {
        "places": places[0: 6],
        'user': user,
        'all_states': all_states,
        'all_types': all_types,
        'all_significances': all_significances
    })




def details(request, pk):
    try:
        # Get the place or return 404
        place = get_object_or_404(PlaceMode, id=pk)
        
        # Initialize variables
        recommended_places = []
        recommendation_source = "similar"
        
        # Try to get recommendations from the similarity model
        try:
            places_pickle = os.path.join(settings.MEDIA_ROOT, 'places.pkl')
            similarity_pickle = os.path.join(settings.MEDIA_ROOT, 'similarity.pkl')

            # Check if pickle files exist
            if os.path.exists(places_pickle) and os.path.exists(similarity_pickle):
                with open(places_pickle, 'rb') as f:
                    place_dict = pickle.load(f)

                with open(similarity_pickle, 'rb') as f:
                    similarity = pickle.load(f)

                name = place.Name
                # Find the place in the dataframe
                matching_places = place_dict[place_dict['Name'] == name]
                
                if not matching_places.empty:
                    place_index = matching_places.index[0]
                    
                    # Check if index is valid for similarity matrix
                    if place_index < len(similarity):
                        distances = similarity[place_index]
                        places_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:5]
                        
                        # Get recommended places, handling any that might not exist in DB
                        for i in places_list:
                            try:
                                rec_place = PlaceMode.objects.get(id=i[0])
                                recommended_places.append(rec_place)
                            except PlaceMode.DoesNotExist:
                                continue
            else:
                recommendation_source = "fallback"
        except Exception as e:
            # Log the error for debugging
            print(f"Recommendation error: {str(e)}")
            recommendation_source = "error"
        
        # If we couldn't get recommendations or not enough, fall back to random selection
        if len(recommended_places) < 3:
            # Get places with same type first
            type_recommendations = list(PlaceMode.objects.filter(Type=place.Type).exclude(id=pk).order_by('?')[:2])
            
            # Then get places from same state
            state_recommendations = list(PlaceMode.objects.filter(State=place.State).exclude(id=pk).exclude(id__in=[p.id for p in type_recommendations]).order_by('?')[:2])
            
            # Combine recommendations
            fallback_recommendations = type_recommendations + state_recommendations
            
            # If still not enough, get random places
            if len(fallback_recommendations) < 3:
                random_recommendations = list(PlaceMode.objects.exclude(id=pk)
                                             .exclude(id__in=[p.id for p in fallback_recommendations])
                                             .order_by('?')[:4-len(fallback_recommendations)])
                fallback_recommendations.extend(random_recommendations)
            
            # Use fallback recommendations
            recommended_places = fallback_recommendations
            recommendation_source = "fallback"

        # Get crowd data for the place - use select_related to reduce queries
        crowd_data = CrowdModel.objects.filter(location=place).select_related('location')
        
        # List of all months for display
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        # Get reviews for the place - use select_related to reduce queries
        reviews = TripReview.objects.filter(place=place).select_related('user').order_by('-created_at')

        # Show appropriate message based on recommendation source
        if recommendation_source == "fallback":
            messages.info(request, "We've selected some destinations you might also enjoy.")
        elif recommendation_source == "error":
            messages.info(request, "Our recommendation system is currently being updated. Here are some places you might like.")

        return render(request, 'place-details-professional.html', {
            "rec_places": recommended_places,
            "single_place": place,
            "crowd_data": crowd_data,
            "months": months,
            "reviews": reviews,
            "messages": messages.get_messages(request)
        })
    except Exception as e:
        # Log the error for debugging
        print(f"Details view error: {str(e)}")
        messages.error(request, "We couldn't load this destination. Please try again later.")
        return redirect('index')

def search_view(request):
    try:
        # Get search parameters from request
        query = request.GET.get('q', '').strip()
        state = request.GET.get('state', '').strip()
        place_type = request.GET.get('type', '').strip()
        significance = request.GET.get('significance', '').strip()
        sort_by = request.GET.get('sort', 'relevance').strip()
        offset = int(request.GET.get('offset', 0))
        is_ajax = request.GET.get('ajax', 'false').lower() == 'true'
        
        # Results per page
        results_per_page = 20

        # Track which filters were applied for better messaging
        applied_filters = []
        
        # Start with a QuerySet for more efficient database operations
        results = PlaceMode.objects.all()
        
        # Apply text search if provided - using database filtering for better performance
        if query:
            applied_filters.append(f'search term "{query}"')
            
            # First try exact matches with higher priority
            exact_matches = PlaceMode.objects.filter(
                models.Q(Name__iexact=query) |
                models.Q(City__iexact=query) |
                models.Q(State__iexact=query)
            )
            
            # Then try partial matches
            partial_matches = PlaceMode.objects.filter(
                models.Q(Name__icontains=query) |
                models.Q(City__icontains=query) |
                models.Q(State__icontains=query) |
                models.Q(Significance__icontains=query) |
                models.Q(Type__icontains=query) |
                models.Q(Description__icontains=query)
            ).exclude(id__in=exact_matches.values_list('id', flat=True))
            
            # Combine results with exact matches first
            # Use union to keep it as a QuerySet for as long as possible
            if exact_matches.exists():
                results = list(exact_matches) + list(partial_matches)
            else:
                results = list(partial_matches)
        
        # Apply filters using database operations when possible
        # Apply state filter if provided
        if state:
            applied_filters.append(f'state "{state}"')
            if isinstance(results, list):
                results = [place for place in results if place.State and place.State.lower() == state.lower()]
            else:
                results = results.filter(State__iexact=state)

        # Apply type filter if provided
        if place_type:
            applied_filters.append(f'type "{place_type}"')
            if isinstance(results, list):
                results = [place for place in results if place.Type and place.Type.lower() == place_type.lower()]
            else:
                results = results.filter(Type__iexact=place_type)
            
        # Apply significance filter if provided
        if significance:
            applied_filters.append(f'significance "{significance}"')
            if isinstance(results, list):
                results = [place for place in results if place.Significance and place.Significance.lower() == significance.lower()]
            else:
                results = results.filter(Significance__iexact=significance)

        # Convert to list if still a QuerySet for consistent handling
        if not isinstance(results, list):
            results = list(results)
            
        # Apply sorting - optimize with database sorting when possible
        if sort_by == 'rating':
            # Sort by Google rating (convert to float first if possible)
            results = sorted(
                results,
                key=lambda x: float(x.Google_rating) if x.Google_rating and x.Google_rating.replace('.', '', 1).isdigit() else 0,
                reverse=True
            )
        elif sort_by == 'name':
            # Sort by name alphabetically
            results = sorted(results, key=lambda x: x.Name.lower() if x.Name else '')
        elif sort_by == 'state':
            # Sort by state alphabetically
            results = sorted(results, key=lambda x: x.State.lower() if x.State else '')
        # Default is relevance, which is the default order from the database query

        # Check if no results found
        if not results and (query or state or place_type or significance):
            # Create a user-friendly message based on which filters were applied
            if len(applied_filters) == 1:
                message = f'No destinations found for {applied_filters[0]}. Try different search criteria or browse our featured destinations.'
            else:
                filters_text = ", ".join(applied_filters[:-1]) + " and " + applied_filters[-1] if len(applied_filters) > 1 else applied_filters[0]
                message = f'No destinations match the combination of {filters_text}. Try adjusting your filters.'

            messages.info(request, message)

            # Provide personalized recommendations if user is logged in
            if request.user.is_authenticated:
                try:
                    profile = Profile.objects.get(user=request.user)
                    if profile.fav_type:
                        recommended = list(PlaceMode.objects.filter(Type__iexact=profile.fav_type)[:8])
                        if recommended:
                            messages.info(request, f"Here are some {profile.fav_type} destinations you might enjoy based on your preferences.")
                            
                            # For AJAX requests, return JSON
                            if is_ajax:
                                return JsonResponse({
                                    'places': [serialize_place(place) for place in recommended],
                                    'count': len(recommended),
                                    'has_more': False,
                                    'no_results': True,
                                    'recommended': True
                                })
                                
                            return render(
                                request,
                                'search-page.html',
                                {
                                    'places': recommended,
                                    'query': query,
                                    'state': state,
                                    'type': place_type,
                                    'significance': significance,
                                    'sort': sort_by,
                                    'no_results': True,
                                    'recommended': True,
                                    'recommendation_type': 'personalized',
                                    'all_states': PlaceMode.objects.values_list('State', flat=True).distinct().order_by('State'),
                                    'all_types': PlaceMode.objects.values_list('Type', flat=True).distinct().order_by('Type'),
                                    'all_significances': PlaceMode.objects.values_list('Significance', flat=True).distinct().order_by('Significance'),
                                }
                            )
                except Profile.DoesNotExist:
                    pass  # Fall back to random recommendations

            # Provide some recommended places instead (random selection)
            recommended = list(PlaceMode.objects.order_by('?')[:8])
            
            # For AJAX requests, return JSON
            if is_ajax:
                return JsonResponse({
                    'places': [serialize_place(place) for place in recommended],
                    'count': len(recommended),
                    'has_more': False,
                    'no_results': True,
                    'recommended': True
                })
                
            return render(
                request,
                'search-page.html',
                {
                    'places': recommended,
                    'query': query,
                    'state': state,
                    'type': place_type,
                    'significance': significance,
                    'sort': sort_by,
                    'no_results': True,
                    'recommended': True,
                    'recommendation_type': 'general',
                    'all_states': PlaceMode.objects.values_list('State', flat=True).distinct().order_by('State'),
                    'all_types': PlaceMode.objects.values_list('Type', flat=True).distinct().order_by('Type'),
                    'all_significances': PlaceMode.objects.values_list('Significance', flat=True).distinct().order_by('Significance'),
                }
            )

        # Get all available states and types for filter dropdowns - cache these values
        all_states = PlaceMode.objects.values_list('State', flat=True).distinct().order_by('State')
        all_types = PlaceMode.objects.values_list('Type', flat=True).distinct().order_by('Type')
        all_significances = PlaceMode.objects.values_list('Significance', flat=True).distinct().order_by('Significance')
        
        # Calculate pagination
        total_results = len(results)
        paginated_results = results[offset:offset + results_per_page]
        has_more = (offset + results_per_page) < total_results
        
        # For AJAX requests, return JSON
        if is_ajax:
            return JsonResponse({
                'places': [serialize_place(place) for place in paginated_results],
                'count': total_results,
                'has_more': has_more
            })

        return render(
            request,
            'search-page.html',
            {
                'places': paginated_results,
                'query': query,
                'state': state,
                'type': place_type,
                'significance': significance,
                'sort': sort_by,
                'count': total_results,
                'all_states': all_states,
                'all_types': all_types,
                'all_significances': all_significances,
                'applied_filters': applied_filters,
                'has_more': has_more
            }
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Search error: {str(e)}")
        
        # For AJAX requests, return error JSON
        if request.GET.get('ajax', 'false').lower() == 'true':
            return JsonResponse({
                'error': 'An error occurred while processing your search.',
                'places': []
            }, status=500)
            
        messages.error(request, "An error occurred while processing your search. Please try again.")
        
        # Return a safe fallback with some popular destinations
        popular_places = list(PlaceMode.objects.all().order_by('-Google_rating')[:12])
        return render(request, 'search-page.html', {
            'places': popular_places,
            'error_occurred': True,
            'all_states': PlaceMode.objects.values_list('State', flat=True).distinct().order_by('State'),
            'all_types': PlaceMode.objects.values_list('Type', flat=True).distinct().order_by('Type'),
            'all_significances': PlaceMode.objects.values_list('Significance', flat=True).distinct().order_by('Significance'),
        })

# Helper function to serialize place objects for JSON response
def serialize_place(place):
    return {
        'id': place.id,
        'name': place.Name or '',
        'city': place.City or '',
        'state': place.State or '',
        'type': place.Type or '',
        'description': place.Description[:100] if place.Description else '',
        'rating': place.Google_rating or '',
        'image_url': place.Image_url or '',
        'significance': place.Significance or ''
    }

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

            # Validate username length and format
            import re
            if len(username) < 3:
                messages.error(request, '❌ Username must be at least 3 characters long.')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email
                })
                
            # Check username format (alphanumeric and underscore only)
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                messages.error(request, '❌ Username can only contain letters, numbers, and underscores.')
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

            # Validate email format
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                messages.error(request, '❌ Please enter a valid email address.')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email
                })

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, '❌ An account with this email already exists. Please use a different email or try logging in.')
                return render(request, 'signup.html', {
                    'username': username
                })

            # Validate password length and complexity
            if len(password1) < 8:
                messages.error(request, '❌ Password must be at least 8 characters long.')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email
                })
                
            # Check password complexity
            if not (re.search(r'[A-Z]', password1) and re.search(r'[a-z]', password1) and re.search(r'[0-9]', password1)):
                messages.error(request, '❌ Password must contain at least one uppercase letter, one lowercase letter, and one number.')
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
            
            # Create an empty profile for the user
            try:
                profile = Profile(user=user)
                profile.save()
            except Exception as profile_error:
                print(f"Error creating profile: {str(profile_error)}")
                # Continue even if profile creation fails - we'll handle it later
            
            # Log the user in
            login(request, user)
            messages.success(request, "✅ Welcome to TripInsight! Your registration was successful. Please complete your profile to get personalized recommendations.")
            return redirect('create_profile')

        except Exception as e:
            print(f"Signup error: {str(e)}")
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
    
    # Make sure next_url is a valid URL name or path
    if next_url and not next_url.startswith('/') and next_url != 'index':
        next_url = '/' + next_url
    
    # If next_url is just a name without slash, assume it's a named URL
    if next_url and not next_url.startswith('/') and next_url != 'index':
        try:
            # Try to reverse the URL name
            from django.urls import reverse
            next_url = reverse(next_url)
        except:
            # If reverse fails, default to index
            next_url = 'index'

    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            remember_me = request.POST.get('remember', False)

            # Validate inputs
            if not username or not password:
                messages.error(request, '❌ Both username and password are required.')
                return render(request, 'login-new.html', {'username': username, 'next': next_url})

            # Check if user exists first
            user_exists = User.objects.filter(username=username).exists()
            
            # Try to authenticate
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if user is active
                if not user.is_active:
                    messages.error(request, '❌ Your account has been disabled. Please contact support for assistance.')
                    return render(request, 'login-new.html', {'username': username, 'next': next_url})

                login(request, user)
                
                # Set session expiry based on remember me checkbox
                if remember_me:
                    # Session will last for 2 weeks
                    request.session.set_expiry(1209600)
                else:
                    # Session will end when browser is closed
                    request.session.set_expiry(0)
                    
                messages.success(request, f'✅ Login successful! Welcome back, {user.username}.')

                # Redirect to the next URL or home
                return redirect(next_url)
            else:
                if user_exists:
                    messages.error(request, '❌ Incorrect password. Please try again.')
                else:
                    messages.error(request, '❌ This username does not exist. Please check your username or sign up for a new account.')
                return render(request, 'login-new.html', {'username': username, 'next': next_url})

        except Exception as e:
            print(f"Login error: {str(e)}")
            messages.error(request, '❌ An error occurred during login. Please try again.')
            return render(request, 'login-new.html', {'next': next_url})

    return render(request, 'login-new.html', {'next': next_url})

# Logout View
def logout_view(request):
    try:
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            messages.success(request, f'✅ You have been successfully logged out. Thanks for visiting, {username}!')
        else:
            messages.info(request, 'You were not logged in.')

        # Get the referrer URL to redirect back to the page they came from
        referrer = request.META.get('HTTP_REFERER')
        
        # If referrer exists and is from our site, redirect there
        if referrer and request.get_host() in referrer:
            # Strip the domain part to get just the path
            from urllib.parse import urlparse
            path = urlparse(referrer).path
            return redirect(path)
            
        # Otherwise redirect to the specified next URL or home
        next_url = request.GET.get('next', 'index')
        return redirect(next_url)
    except Exception as e:
        print(f"Logout error: {str(e)}")
        messages.error(request, "An error occurred during logout.")
        return redirect('index')

# Initialize Google Maps client with API key from settings
try:
    # Get API key from settings (which now loads from .env)
    GOOGLE_MAPS_API_KEY = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
    
    if GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY.strip():
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        print("Google Maps API initialized successfully.")
    else:
        print("Google Maps API key not found or empty. Distance calculations will be disabled.")
        print("Set GOOGLE_MAPS_API_KEY in your .env file or environment variables.")
        gmaps = None
except ImportError:
    print("Google Maps library not installed. Run 'pip install googlemaps' to enable distance calculations.")
    gmaps = None
except Exception as e:
    # Log the error but don't crash the application
    print(f"Error initializing Google Maps client: {e}")
    print("Please check your API key and make sure it has the necessary permissions.")
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
            # If Google Maps API fails, provide a fallback distance calculation
            # This is a very rough estimate based on coordinates
            try:
                # Try to parse coordinates from origin and destination
                if ',' in origin and ',' in destination:
                    # Extract coordinates
                    origin_parts = origin.split(',')
                    dest_parts = destination.split(',')
                    
                    if len(origin_parts) >= 2 and len(dest_parts) >= 2:
                        try:
                            # Calculate rough distance using Haversine formula
                            from math import radians, cos, sin, asin, sqrt
                            
                            # Parse coordinates
                            lat1 = float(origin_parts[0].strip())
                            lon1 = float(origin_parts[1].strip())
                            lat2 = float(dest_parts[0].strip())
                            lon2 = float(dest_parts[1].strip())
                            
                            # Convert to radians
                            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                            
                            # Haversine formula
                            dlon = lon2 - lon1
                            dlat = lat2 - lat1
                            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                            c = 2 * asin(sqrt(a))
                            r = 6371  # Radius of Earth in kilometers
                            distance_km = c * r
                            
                            print(f"Using fallback distance calculation: {distance_km} km")
                        except Exception as e:
                            print(f"Error in fallback distance calculation: {e}")
                            distance_km = None
            except Exception as e:
                print(f"Error in fallback distance calculation: {e}")
                distance_km = None
                
            # If still no distance, return error
            if distance_km is None:
                return JsonResponse({
                    "error": "Could not calculate distance between the provided locations",
                    "status": "error",
                    "suggestion": "Please check the spelling of your origin and destination or try again later"
                }, status=400)

        # Calculate costs for different travel modes using more generic estimates
        # Car cost calculation (fuel + tolls) - more generic range
        car_cost = distance_km * random.uniform(8, 12)  # Average cost per km with some variation

        # Train cost calculation with tiered pricing - more generic ranges
        if distance_km <= 100:
            train_cost = distance_km * random.uniform(5, 7)  # Short distance
        elif distance_km <= 500:
            train_cost = distance_km * random.uniform(4, 6)  # Medium distance
        else:
            train_cost = distance_km * random.uniform(3, 5)  # Long distance

        # Air cost calculation with tiered pricing - more generic ranges
        if distance_km <= 500:
            air_cost = distance_km * random.uniform(12, 18)  # Short flights are more expensive per km
        elif distance_km <= 1000:
            air_cost = distance_km * random.uniform(10, 14)  # Medium flights
        else:
            air_cost = distance_km * random.uniform(8, 12)  # Long flights

        # Bus cost calculation - more generic range
        bus_cost = distance_km * random.uniform(2, 4)

        # Adjust costs for number of people (except car which is shared)
        train_cost *= num_people
        air_cost *= num_people
        bus_cost *= num_people

        # Accommodation cost estimate (per night) - more generic range
        accommodation_cost = random.uniform(1200, 1800) * num_people

        # Food cost estimate (per day) - more generic range
        food_cost = random.uniform(400, 600) * num_people

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
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to submit a review.")
        return redirect(f"/login?next={request.path}")

    # Get the place or return 404
    place = get_object_or_404(PlaceMode, id=pk)
    
    if request.method == "POST":
        try:
            # Get form data
            title = request.POST.get("title", "").strip()
            description = request.POST.get("description", "").strip()
            travel_medium = request.POST.get("travel_medium")
            
            # Validate required fields
            if not title:
                messages.error(request, "Please provide a title for your review.")
                return render(request, "reviewform.html", {"single_place": place})
                
            if not description:
                messages.error(request, "Please provide a description of your experience.")
                return render(request, "reviewform.html", {"single_place": place})
            
            # Check word count limit (100 words)
            word_count = len(description.split())
            if word_count > 100:
                messages.error(request, "Please limit your description to 100 words. Current count: " + str(word_count))
                return render(request, "reviewform.html", {"single_place": place})
                
            if not travel_medium:
                messages.error(request, "Please select how you traveled to this destination.")
                return render(request, "reviewform.html", {"single_place": place})
            
            # Process numeric fields with validation
            try:
                rating = int(request.POST.get("rating", 0))
                if rating < 1 or rating > 5:
                    rating = None
            except (ValueError, TypeError):
                rating = None
                
            try:
                no_of_people = int(request.POST.get("no_of_people", 1))
                if no_of_people < 1:
                    no_of_people = 1
            except (ValueError, TypeError):
                no_of_people = 1
                
            # Process cost fields with validation
            try:
                travel_cost = float(request.POST.get("travel_cost", 0))
                if travel_cost < 0:
                    travel_cost = 0
            except (ValueError, TypeError):
                travel_cost = 0
                
            try:
                accommodation_cost = float(request.POST.get("accommodation_cost", 0))
                if accommodation_cost < 0:
                    accommodation_cost = 0
            except (ValueError, TypeError):
                accommodation_cost = 0
                
            try:
                food_cost = float(request.POST.get("food_cost", 0))
                if food_cost < 0:
                    food_cost = 0
            except (ValueError, TypeError):
                food_cost = 0

            # Create TripReview object
            review = TripReview.objects.create(
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
            
            # Update user's trophy count using the new logic
            try:
                profile = Profile.objects.get(user=request.user)
                profile.update_trophies()  # Use the new method to calculate trophies
                
                # Show appropriate trophy message based on count
                review_count = TripReview.objects.filter(user=request.user).count()
                if review_count == 10:
                    messages.success(request, "🏆 Congratulations! You've earned your first trophy for submitting 10 reviews!")
                elif review_count == 25:
                    messages.success(request, "🏆 Congratulations! You've earned your second trophy for submitting 25 reviews!")
                elif review_count == 50:
                    messages.success(request, "🏆 Congratulations! You've earned your third trophy for submitting 50 reviews!")
                elif review_count == 100:
                    messages.success(request, "🏆 Congratulations! You've earned your fourth trophy for submitting 100 reviews! You're a TripInsight legend!")
                
            except Profile.DoesNotExist:
                # If user doesn't have a profile, suggest creating one
                messages.info(request, "Complete your profile to track your progress and earn trophies for your reviews!")

            messages.success(request, "✅ Your review has been submitted successfully! Thank you for sharing your experience.")

            # Redirect to the place detail page
            return redirect(reverse("details", kwargs={"pk": place.id}))
            
        except Exception as e:
            # Log the error for debugging
            print(f"Review submission error: {str(e)}")
            messages.error(request, "An error occurred while submitting your review. Please try again.")
            return render(request, "reviewform.html", {"single_place": place})

    # For GET requests, show the form
    return render(request, "reviewform.html", {
        "single_place": place,
        "travel_medium_choices": TripReview.TRAVEL_MEDIUM_CHOICES
    })

def create_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create a profile.")
        return redirect("login")
        
    if request.method == "POST":
        full_name = request.POST.get("name")
        description = request.POST.get("description")
        state = request.POST.get("state")
        city = request.POST.get("city", "")
        fav_type = request.POST.get("fav_type", "")
        fav_significance = request.POST.get("fav_significance", "")

        if not description or not state:
            messages.error(request, "Description and state are required fields.")
            return redirect("create_profile")

        # Get or create profile for the current user
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Update profile fields
        profile.state = state
        profile.city = city
        profile.description = description
        profile.fav_type = fav_type
        profile.fav_significance = fav_significance
        profile.save()

        messages.success(request, "✅ Profile created successfully! You can now get personalized recommendations.")
        return redirect("/")

    return render(request, "profile_form.html")

def profile(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to view your profile")
        return redirect("/login")
        
    # Check if user has a profile, if not redirect to create one
    if not Profile.objects.filter(user=request.user).exists():
        messages.info(request, "Please complete your profile to get personalized recommendations.")
        return redirect("/create-profile")
        
    # Get user profile
    profile = Profile.objects.get(user=request.user)
    
    # Get user reviews
    reviews = TripReview.objects.filter(user=request.user).order_by('-created_at')
    review_count = reviews.count()
    
    # Update trophies using the new logic
    profile.update_trophies()
    
    # Get trophy progress information
    trophy_progress = {
        'current_trophies': profile.trophies,
        'total_reviews': review_count,
        'next_milestone': 10 if review_count < 10 else 25 if review_count < 25 else 50 if review_count < 50 else 100 if review_count < 100 else None,
        'reviews_needed': 10 - review_count if review_count < 10 else 25 - review_count if review_count < 25 else 50 - review_count if review_count < 50 else 100 - review_count if review_count < 100 else 0,
        'progress_percentage': min(100, (review_count / 10) * 100) if review_count < 10 else 
                              min(100, ((review_count - 10) / 15) * 100) if review_count < 25 else 
                              min(100, ((review_count - 25) / 25) * 100) if review_count < 50 else 
                              min(100, ((review_count - 50) / 50) * 100) if review_count < 100 else 100
    }
    
    # Get places the user has reviewed
    reviewed_places = PlaceMode.objects.filter(id__in=reviews.values_list('place_id', flat=True)).distinct()
    
    # Get states the user has visited (based on reviews)
    visited_states = reviewed_places.values_list('State', flat=True).distinct()
    
    return render(request, "profilepage.html", {
        "profile": profile,
        "reviews": reviews,
        "count": review_count,
        "trophy_progress": trophy_progress,
        "reviewed_places": reviewed_places,
        "visited_states": visited_states,
        "messages": messages.get_messages(request)
    })

def stories(request):
    try:
        # Get filter parameters
        travel_medium = request.GET.get('travel_medium', '')
        state = request.GET.get('state', '')
        sort_by = request.GET.get('sort', 'recent')
        
        # Start with all reviews
        reviews = TripReview.objects.all()
        
        # Apply filters if specified
        if travel_medium:
            reviews = reviews.filter(travel_medium=travel_medium)
            
        if state and reviews:
            # Filter by place state
            place_ids = PlaceMode.objects.filter(State__iexact=state).values_list('id', flat=True)
            reviews = reviews.filter(place_id__in=place_ids)
        
        # Apply sorting
        if sort_by == 'recent':
            reviews = reviews.order_by('-created_at')
        elif sort_by == 'rating_high':
            reviews = reviews.order_by('-rating')
        elif sort_by == 'rating_low':
            reviews = reviews.order_by('rating')
        elif sort_by == 'cost_high':
            # Calculate total cost for sorting with error handling
            def get_total_cost(review):
                try:
                    travel = float(review.travel_cost) if review.travel_cost is not None else 0
                    accommodation = float(review.accommodation_cost) if review.accommodation_cost is not None else 0
                    food = float(review.food_cost) if review.food_cost is not None else 0
                    return travel + accommodation + food
                except (ValueError, TypeError):
                    return 0
                    
            reviews = sorted(
                reviews,
                key=get_total_cost,
                reverse=True
            )
        elif sort_by == 'cost_low':
            # Calculate total cost for sorting with error handling
            def get_total_cost(review):
                try:
                    travel = float(review.travel_cost) if review.travel_cost is not None else 0
                    accommodation = float(review.accommodation_cost) if review.accommodation_cost is not None else 0
                    food = float(review.food_cost) if review.food_cost is not None else 0
                    return travel + accommodation + food
                except (ValueError, TypeError):
                    return 0
                    
            reviews = sorted(
                reviews,
                key=get_total_cost
            )
        
        # Get all available states for filter dropdown
        all_states = PlaceMode.objects.values_list('State', flat=True).distinct().order_by('State')
        
        # Get featured reviews (highest rated)
        featured_reviews = TripReview.objects.filter(rating__isnull=False).order_by('-rating')[:3]
        
        # Get popular travel mediums
        travel_medium_counts = TripReview.objects.values('travel_medium').annotate(
            count=models.Count('travel_medium')
        ).order_by('-count')
        
        # Get user's reviews if authenticated
        user_reviews = None
        if request.user.is_authenticated:
            user_reviews = TripReview.objects.filter(user=request.user).order_by('-created_at')
        
        context = {
            "reviews": reviews,
            "featured_reviews": featured_reviews,
            "travel_medium_counts": travel_medium_counts,
            "all_states": all_states,
            "selected_medium": travel_medium,
            "selected_state": state,
            "selected_sort": sort_by,
            "travel_medium_choices": TripReview.TRAVEL_MEDIUM_CHOICES,
            "user_reviews": user_reviews
        }
        
        return render(request, "stories-new.html", context)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Stories view error: {str(e)}")
        messages.error(request, "An error occurred while loading travel stories. Please try again.")
        
        # Return a minimal context with some reviews to show
        return render(request, "stories-new.html", {
            "reviews": TripReview.objects.all().order_by('-created_at')[:10],
            "error_occurred": True
        })

def about(request):
    return render(request, "about-new.html")

def explore(request):
    try:
        # Get filter parameters from query
        place_type = request.GET.get('type', '')
        state = request.GET.get('state', '')
        significance = request.GET.get('significance', '')
        
        # Start with all places in random order
        places = PlaceMode.objects.all().order_by('?')
        
        # Apply filters if specified
        if place_type and place_type != 'all':
            places = places.filter(Type__icontains=place_type)
            
        if state and state != 'all':
            places = places.filter(State__iexact=state)
            
        if significance and significance != 'all':
            places = places.filter(Significance__iexact=significance)
        
        # Get featured places (places with highest ratings)
        # Convert Google_rating to float for proper sorting
        try:
            featured_places = sorted(
                PlaceMode.objects.all(),
                key=lambda x: float(x.Google_rating) if x.Google_rating and x.Google_rating.replace('.', '', 1).isdigit() else 0,
                reverse=True
            )[:3]
        except Exception:
            # Fallback if sorting fails
            featured_places = PlaceMode.objects.all().order_by('?')[:3]
        
        # Get popular places by state (for the state section)
        popular_states = PlaceMode.objects.values('State').annotate(
            count=models.Count('State')
        ).order_by('-count')[:6]
        
        state_highlights = {}
        for state_data in popular_states:
            state_name = state_data['State']
            if state_name:  # Ensure state name is not empty
                # Get a representative place from this state
                state_places = PlaceMode.objects.filter(State=state_name).order_by('?')[:1]
                if state_places:
                    state_highlights[state_name] = state_places[0]
        
        # Get all available types, states and significances for filter dropdowns
        all_types = PlaceMode.objects.values_list('Type', flat=True).distinct().order_by('Type')
        all_states = PlaceMode.objects.values_list('State', flat=True).distinct().order_by('State')
        all_significances = PlaceMode.objects.values_list('Significance', flat=True).distinct().order_by('Significance')
        
        # Get personalized recommendations if user is logged in
        personalized_recommendations = []
        if request.user.is_authenticated:
            try:
                profile = Profile.objects.get(user=request.user)
                if profile.fav_type:
                    personalized_recommendations = PlaceMode.objects.filter(
                        Type__iexact=profile.fav_type
                    ).order_by('?')[:4]
            except Profile.DoesNotExist:
                pass
        
        context = {
            'places': places,
            'featured_places': featured_places,
            'state_highlights': state_highlights,
            'all_types': all_types,
            'all_states': all_states,
            'all_significances': all_significances,
            'selected_type': place_type,
            'selected_state': state,
            'selected_significance': significance,
            'personalized_recommendations': personalized_recommendations
        }
        
        return render(request, "explore-page.html", context)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Explore view error: {str(e)}")
        messages.error(request, "An error occurred while loading the explore page. Please try again.")
        
        # Return a minimal context with some random places to show
        return render(request, "explore-page.html", {
            'places': PlaceMode.objects.all().order_by('?')[:12],
            'featured_places': PlaceMode.objects.all().order_by('?')[:3],
            'error_occurred': True
        })

def api_estimate_costs(request, pk):
    """
    API endpoint to estimate costs for a place based on user reviews.
    Returns JSON with cost estimates for accommodation, food, travel, and entry fee.
    """
    try:
        place = get_object_or_404(PlaceMode, id=pk)
        
        # Get all reviews for this place
        reviews = TripReview.objects.filter(place=place)
        review_count = reviews.count()
        
        if review_count > 0:
            # Calculate average costs from reviews
            avg_accommodation = reviews.aggregate(Avg('accommodation_cost'))['accommodation_cost__avg'] or 0
            avg_food = reviews.aggregate(Avg('food_cost'))['food_cost__avg'] or 0
            avg_travel = reviews.aggregate(Avg('travel_cost'))['travel_cost__avg'] or 0
            
            # Use default entry fee if Fees field is not available
            entry_fee = 0
            try:
                if hasattr(place, 'Fees') and place.Fees:
                    # Try to extract a numeric value from the Fees field
                    fees_text = str(place.Fees)
                    # Remove non-numeric characters except for decimal points
                    import re
                    fees_numeric = re.sub(r'[^0-9.]', '', fees_text)
                    if fees_numeric:
                        entry_fee = float(fees_numeric)
            except Exception as e:
                print(f"Error parsing entry fee: {str(e)}")
            
            # Calculate total cost (per person per day) - without entry fee
            total_cost = avg_accommodation + avg_food + avg_travel
            
            # Use more generic default values if any cost is zero
            if avg_accommodation == 0:
                avg_accommodation = random.uniform(1200, 1800)  # More generic accommodation cost
            
            if avg_food == 0:
                avg_food = random.uniform(600, 1000)  # More generic food cost
            
            if avg_travel == 0:
                avg_travel = random.uniform(1000, 1400)  # More generic travel cost
            
            if total_cost == 0:
                total_cost = avg_accommodation + avg_food + avg_travel
            
            return JsonResponse({
                'has_reviews': True,
                'review_count': review_count,
                'accommodation_cost': float(avg_accommodation),
                'food_cost': float(avg_food),
                'travel_cost': float(avg_travel),
                'entry_fee': float(entry_fee),
                'total_cost': float(total_cost)
            })
        else:
            # If no reviews, provide more generic default estimates
            accommodation = random.uniform(1200, 1800)
            food = random.uniform(600, 1000)
            travel = random.uniform(1000, 1400)
            total = accommodation + food + travel
            
            return JsonResponse({
                'has_reviews': True,  # Changed to true to show estimates anyway
                'review_count': 0,
                'accommodation_cost': float(accommodation),  # More generic values
                'food_cost': float(food),
                'travel_cost': float(travel),
                'entry_fee': 0.0,  # Removed from display but keeping in API for compatibility
                'total_cost': float(total)
            })
    except Exception as e:
        print(f"Error in cost estimation API: {str(e)}")
        # Return a response with more generic default values instead of an error
        accommodation = random.uniform(1200, 1800)
        food = random.uniform(600, 1000)
        travel = random.uniform(1000, 1400)
        total = accommodation + food + travel
        
        return JsonResponse({
            'has_reviews': True,
            'review_count': 0,
            'accommodation_cost': float(accommodation),
            'food_cost': float(food),
            'travel_cost': float(travel),
            'entry_fee': 0.0,  # Removed from display but keeping in API for compatibility
            'total_cost': float(total),
            'note': 'Using generic estimates'
        })
