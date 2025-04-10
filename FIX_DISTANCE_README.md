# Fixing Distance References in TripInsight

This guide explains how to fix inaccurate distance references (like "7 km away", "6 km away") in the TripInsight templates.

## The Issue

In some template files, nearby attractions are displayed with specific distance values (e.g., "7 km away"). These distances are not accurate as they are generated using a counter in the template:

```html
<div class="attraction-distance">
    <i class="fas fa-route"></i> {{ forloop.counter|add:5 }} km away
</div>
```

This creates misleading information for users, as the distances shown are not based on actual geographic data.

## The Solution

We've created a script that replaces all specific distance references with a generic "Nearby attraction" text. This is more accurate and avoids providing misleading information.

## Files Included

1. `fix_distance_references.py` - The script that fixes distance references in all template files

## How to Run

1. Open a command prompt or terminal
2. Navigate to the TripInsight project directory
3. Run the following command:

```
python fix_distance_references.py
```

## What the Script Does

The script:

1. Scans all HTML template files in the templates directory
2. Looks for patterns that indicate distance references (e.g., "X km away")
3. Replaces these references with the generic text "Nearby attraction"
4. Saves the updated files

## Manual Fix

If you prefer to fix the issue manually, you can edit the following files:

1. `templates/place-details-professional.html` - Look for the attraction-distance class and replace the distance text
2. Any other template files that might display distance information

## After Running the Script

After running the script, all distance references will be replaced with "Nearby attraction". This provides a more accurate representation of the relationship between places without specifying exact distances that might be misleading.

If you want to implement actual distance calculations in the future, you would need to:

1. Store geographic coordinates (latitude and longitude) for each place
2. Calculate actual distances between places using these coordinates
3. Update the templates to display these calculated distances

For now, the generic "Nearby attraction" text is the most accurate solution.