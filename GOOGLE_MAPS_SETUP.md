# Google Maps API Setup for TripInsight

This guide explains how to set up the Google Maps API for TripInsight.

## Why Google Maps API is Needed

TripInsight uses Google Maps API for:
- Distance calculations between locations
- Geocoding (converting addresses to coordinates)
- Displaying maps for destinations

## Setup Instructions

### 1. Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Geocoding API
   - Distance Matrix API
4. Create credentials to get your API key
   - Go to "Credentials" in the left sidebar
   - Click "Create Credentials" and select "API key"
   - Copy the generated API key

### 2. Configure TripInsight with Your API Key

Run the setup script:

```bash
python setup_api_key.py
```

When prompted, paste your Google Maps API key.

### 3. Restart the Server

After configuring your API key, restart the Django server:

```bash
python manage.py runserver
```

You should no longer see the "Google Maps API key not found" warning message.

## Troubleshooting

If you encounter issues:

1. **API Key Not Working**: Make sure you've enabled all the required APIs in the Google Cloud Console
2. **Billing**: Some Google Maps API features require billing to be enabled on your Google Cloud account
3. **Quota Limits**: Check if you've exceeded your API quota limits

## Security Notes

- Never commit your API key to version control
- TripInsight stores your API key in the `.env` file, which should be in your `.gitignore`
- For production, consider using environment variables on your server