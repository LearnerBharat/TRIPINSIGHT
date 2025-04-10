# Admin Panel Troubleshooting Guide

If you're having trouble accessing the admin panel at http://127.0.0.1:8000/admin/, follow these steps to diagnose and fix the issue.

## Quick Fix

Run the automated troubleshooting script:

```
python fix_admin_panel.py
```

This script will:
1. Check if the database exists and has the necessary tables
2. Apply any pending migrations
3. Check if a superuser exists and create one if needed
4. Verify that the Jazzmin admin theme is installed correctly

## Manual Troubleshooting Steps

If the automated script doesn't resolve the issue, try these steps manually:

### 1. Check if the server is running

Make sure your Django server is running. Open a command prompt and run:

```
python manage.py runserver
```

You should see output indicating that the server is running on http://127.0.0.1:8000/.

### 2. Check if migrations have been applied

Apply any pending database migrations:

```
python manage.py migrate
```

### 3. Create a superuser

If you don't have a superuser account, create one:

```
python manage.py createsuperuser
```

Follow the prompts to create a username, email, and password.

### 4. Check Jazzmin installation

The project uses the Jazzmin admin theme. Make sure it's installed:

```
pip install django-jazzmin
```

If you continue to have issues with Jazzmin, you can temporarily disable it by editing `project/settings.py` and removing or commenting out 'jazzmin' from the INSTALLED_APPS list.

### 5. Clear browser cache

Sometimes browser caching can cause issues. Try:
- Opening the admin panel in an incognito/private window
- Clearing your browser cache
- Using a different browser

### 6. Check for error messages

Look for error messages in:
- The terminal where the server is running
- Your browser's developer console (F12 in most browsers)

## Common Issues and Solutions

### "No such table: auth_user"

This indicates that migrations haven't been applied. Run:

```
python manage.py migrate
```

### "ImportError: No module named jazzmin"

The Jazzmin admin theme is not installed. Run:

```
pip install django-jazzmin
```

### "Permission denied" errors

Make sure your database file is not read-only and that your user account has permission to access it.

### Blank page or 500 error

Check the server logs for detailed error messages. This could be due to a template error or a problem with the Jazzmin theme.

## Still Having Issues?

If you're still unable to access the admin panel after trying these steps, you might need to:

1. Check if there are any custom middleware or authentication backends that could be interfering
2. Verify that the admin URLs are correctly configured in `urls.py`
3. Check if there are any network or firewall issues blocking access to localhost
4. Try running the server on a different port: `python manage.py runserver 8080`