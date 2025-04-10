import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.models import PlaceMode

def count_words(text):
    """Count the number of words in a text"""
    return len(text.split())

def extend_description(place):
    """Extend the description of a place by adding an additional line"""
    
    # Get current description and word count
    current_description = place.Description if place.Description else ""
    current_word_count = count_words(current_description)
    
    # Additional sentences based on place type
    type_extensions = {
        "hill station": [
            f"The {place.Name} area is known for its biodiversity, featuring rare flora and fauna that thrive in its unique microclimate.",
            f"Visitors to {place.Name} can enjoy panoramic views from various vantage points that showcase the majestic beauty of the surrounding landscape.",
            f"Local cuisine in {place.Name} offers a delightful blend of traditional flavors and fresh mountain ingredients that shouldn't be missed."
        ],
        "beach": [
            f"The pristine waters of {place.Name} are ideal for swimming and water sports, with gentle waves perfect for beginners and families.",
            f"Sunset at {place.Name} creates a spectacular display of colors that photographers and romantics find irresistible.",
            f"Local fishermen bring their fresh catch to the shores of {place.Name} daily, supplying the beachside restaurants with delicious seafood options."
        ],
        "heritage": [
            f"The intricate architectural details of {place.Name} showcase the remarkable craftsmanship and artistic vision of its creators.",
            f"Historians consider {place.Name} a significant cultural landmark that provides valuable insights into the region's rich past.",
            f"Guided tours of {place.Name} reveal fascinating stories and historical anecdotes that bring its ancient stones to life."
        ],
        "wildlife": [
            f"Conservation efforts at {place.Name} have successfully protected numerous endangered species and their natural habitats.",
            f"The diverse ecosystem of {place.Name} supports a complex food web, from tiny insects to magnificent apex predators.",
            f"Naturalists recommend visiting {place.Name} during different seasons to witness the changing behaviors of its animal inhabitants."
        ],
        "pilgrimage": [
            f"Devotees from across the country make annual journeys to {place.Name}, continuing centuries-old traditions of faith and reverence.",
            f"The spiritual atmosphere of {place.Name} creates a sense of peace and introspection that many visitors find transformative.",
            f"Religious ceremonies at {place.Name} follow ancient rituals that have been preserved through generations of dedicated practitioners."
        ],
        "adventure": [
            f"Experienced guides at {place.Name} ensure safety while helping visitors push their limits and discover new capabilities.",
            f"The challenging terrain of {place.Name} offers varying difficulty levels, making it suitable for both beginners and seasoned adventurers.",
            f"Adventure enthusiasts return to {place.Name} year after year, discovering new thrills and experiences with each visit."
        ]
    }
    
    # Generic extensions for any type
    generic_extensions = [
        f"{place.Name} has become increasingly popular with both domestic and international tourists seeking authentic experiences.",
        f"The local community around {place.Name} warmly welcomes visitors, sharing their traditions and way of life.",
        f"Recent improvements to infrastructure have made {place.Name} more accessible while preserving its natural charm and character.",
        f"Photography enthusiasts find {place.Name} particularly rewarding, with countless opportunities for capturing stunning images.",
        f"The changing seasons bring different experiences to {place.Name}, making it worth visiting multiple times throughout the year."
    ]
    
    # Choose an appropriate extension
    if place.Type and place.Type.lower() in type_extensions:
        extension = random.choice(type_extensions[place.Type.lower()])
    else:
        extension = random.choice(generic_extensions)
    
    # Add the extension to the description
    extended_description = current_description + " " + extension
    
    return extended_description

def update_all_descriptions():
    """Update all place descriptions in the database to make them longer"""
    places = PlaceMode.objects.all()
    total_places = places.count()
    updated_count = 0
    
    print(f"Found {total_places} places in the database.")
    print("Updating descriptions to make them longer...")
    
    for i, place in enumerate(places):
        print(f"Processing {i+1}/{total_places}: {place.Name}")
        
        # Extend the description
        extended_description = extend_description(place)
        
        # Update the place
        place.Description = extended_description
        place.save()
        updated_count += 1
        
        print(f"  Updated description. New word count: {count_words(extended_description)}")
    
    print(f"\nSummary: Updated {updated_count} out of {total_places} place descriptions.")
    print("All descriptions have been extended with an additional line.")

if __name__ == "__main__":
    update_all_descriptions()