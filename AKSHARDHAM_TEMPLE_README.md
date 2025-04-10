# Adding Akshardham Temple to TripInsight

This guide explains how to add Akshardham Temple in Delhi to the TripInsight database.

## Files Included

1. `add_akshardham_temple.py` - The main script that adds Akshardham Temple to the database
2. `run_add_akshardham_temple.py` - A helper script to run the main script

## How to Run

### Method 1: Using the Run Script

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python run_add_akshardham_temple.py
```

### Method 2: Running Directly

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python add_akshardham_temple.py
```

## What the Script Does

The script adds Akshardham Temple in Delhi to the database with the following information:

- Name: Akshardham Temple
- City: Delhi
- Zone: Northern Delhi
- Type: heritage
- State: Delhi
- Description: A detailed 90-100 word description highlighting the temple's architectural beauty, cultural significance, and visitor experience
- Year: 2005
- Time needed: 4-5 hours
- Google rating: 4.8
- Significance: Religious
- Best time to visit: October to March
- Fees: ₹170 for adults (includes exhibitions)
- Image URL: A high-quality image of the temple

## Important Notes

- The script checks for existing entries to avoid duplicates
- If Akshardham Temple already exists in the database, the script will update its description
- The description is carefully crafted to be between 90-100 words, as required by the application
- The temple will appear in search results and on the Explore page after being added

## After Running the Script

After running the script, you should be able to:

1. See Akshardham Temple in the Django admin panel
2. View it on the Explore page of the TripInsight website
3. Filter it by type (heritage), state (Delhi), or significance (Religious)
4. See its details on the place details page

If you encounter any issues, please check the console output for error messages.