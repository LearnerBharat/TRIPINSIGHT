# Updating Place Descriptions in TripInsight

This guide explains how to update all place descriptions in the TripInsight database to ensure they are between 90-100 words.

## Files Included

1. `update_descriptions_simple.py` - The main script that updates all place descriptions
2. `update_place_descriptions.py` - An alternative script that attempts to use web searches for more accurate descriptions
3. `update_mahabaleshwar.py` - A script specifically for updating the Mahabaleshwar description

## How to Run

### Method 1: Update All Descriptions (Recommended)

This method will update all place descriptions in the database to ensure they're between 90-100 words:

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python update_descriptions_simple.py
```

### Method 2: Update with Web Search (Requires Internet)

This method attempts to use web searches to get more accurate descriptions:

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python update_place_descriptions.py
```

Note: This method requires an internet connection and may take longer to run.

### Method 3: Update Mahabaleshwar Only

This method updates only the Mahabaleshwar description:

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python update_mahabaleshwar.py
```

## What the Scripts Do

The scripts:

1. Check the current word count of each place description
2. If the description is already between 90-100 words, it's left unchanged
3. If the description is too short or too long, a new description is generated
4. The new description is saved to the database

The descriptions are generated based on the place type (hill station, beach, heritage, etc.) and include the place name, city, and state.

## After Running the Scripts

After running the scripts, you should be able to:

1. See the updated descriptions in the Django admin panel
2. View them on the Explore page of the TripInsight website
3. Each description will be between 90-100 words

## Customizing Descriptions

If you want to customize a specific place's description:

1. Open the Django admin panel at http://127.0.0.1:8000/admin/
2. Log in with your admin credentials
3. Navigate to the Places section
4. Find the place you want to update
5. Edit the description field
6. Save the changes

Make sure your custom description is between 90-100 words for consistency.