# Adding Maharashtra Tourist Places to TripInsight

This guide explains how to add the top 50 tourist places in Maharashtra to the TripInsight database.

## Files Included

1. `add_maharashtra_places.py` - The main script that adds the places to the database
2. `run_add_maharashtra_places.py` - A helper script to run the main script

## How to Run

### Method 1: Using the Run Script

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python run_add_maharashtra_places.py
```

### Method 2: Running Directly

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python add_maharashtra_places.py
```

## What the Script Does

The script adds 50 popular tourist places in Maharashtra to the database, including:

- Mahabaleshwar
- Ajanta and Ellora Caves
- Panchgani
- Lavasa
- Shirdi
- And many more...

For each place, the script adds the following information:
- Name
- City
- Zone
- Type (hill station, beach, heritage, etc.)
- State
- Description
- Year
- Time needed to visit
- Google rating
- Significance
- Best time to visit
- Fees
- Image URL

## Important Notes

- The script checks for existing places to avoid duplicates
- Each place is properly configured with all necessary fields
- The places are linked to the database and will appear in the admin panel
- You can access and edit these places through the Django admin interface

## After Running the Script

After running the script, you should be able to:

1. See the new places in the Django admin panel
2. View them on the Explore page of the TripInsight website
3. Filter them by type, state, etc.
4. See their details on the place details page

If you encounter any issues, please check the console output for error messages.