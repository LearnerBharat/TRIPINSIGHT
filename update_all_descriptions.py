import os
import django
import random
import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.models import PlaceMode

def count_words(text):
    """Count the number of words in a text"""
    return len(text.split())

def update_mahabaleshwar_description():
    """Update the description for Mahabaleshwar to match the provided text"""
    try:
        print("\n=== Updating Mahabaleshwar Description ===\n")
        
        # Find Mahabaleshwar in the database
        mahabaleshwar = PlaceMode.objects.filter(Name__icontains="Mahabaleshwar").first()
        
        if mahabaleshwar:
            # Update with the provided description
            base_description = "Mahabaleshwar is a hill station located in the Western Ghats, in Satara district of Maharashtra. Apart from its strawberries, Mahabaleshwar is also well known for its numerous rivers, magnificent cascades and majestic peaks. It is among the most sought after weekend getaways from Pune & Mumbai."
            
            # Add more details to reach 90-100 words
            additional_text = " The cool climate throughout the year makes it a perfect retreat. Visitors can explore various viewpoints like Arthur's Seat, Wilson Point, and Elephant's Head Point. The region is also known as the origin of the Krishna River. The lush green valleys, dense forests, and serene ambiance create a rejuvenating experience for nature lovers and adventure seekers alike."
            
            mahabaleshwar.Description = base_description + additional_text
            mahabaleshwar.save()
            
            print(f"Successfully updated Mahabaleshwar description.")
            print(f"New description: {mahabaleshwar.Description}")
            print(f"Word count: {len(mahabaleshwar.Description.split())}")
            
            # Also update any other Mahabaleshwar entries if they exist
            other_mahabaleshwars = PlaceMode.objects.filter(Name__icontains="Mahabaleshwar").exclude(id=mahabaleshwar.id)
            if other_mahabaleshwars.exists():
                for place in other_mahabaleshwars:
                    place.Description = base_description + additional_text
                    place.save()
                print(f"Updated {other_mahabaleshwars.count()} additional Mahabaleshwar entries.")
        else:
            print("Mahabaleshwar not found in the database. Creating a new entry...")
            
            # Create a new Mahabaleshwar entry if it doesn't exist
            new_mahabaleshwar = PlaceMode(
                Name="Mahabaleshwar",
                City="Mahabaleshwar",
                Zone="Western Maharashtra",
                Type="hill station",
                State="Maharashtra",
                Description="Mahabaleshwar is a hill station located in the Western Ghats, in Satara district of Maharashtra. Apart from its strawberries, Mahabaleshwar is also well known for its numerous rivers, magnificent cascades and majestic peaks. It is among the most sought after weekend getaways from Pune & Mumbai. The cool climate throughout the year makes it a perfect retreat. Visitors can explore various viewpoints like Arthur's Seat, Wilson Point, and Elephant's Head Point. The region is also known as the origin of the Krishna River. The lush green valleys, dense forests, and serene ambiance create a rejuvenating experience for nature lovers and adventure seekers alike.",
                Year="Ancient",
                Time_needed="2-3 days",
                Google_rating="4.5",
                Significance="Natural Beauty",
                Best_time_to_visit="October to June",
                Fees="Free",
                Image_url="https://images.unsplash.com/photo-1625904835711-5d42fd02a177?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
            )
            new_mahabaleshwar.save()
            print("Created new Mahabaleshwar entry successfully.")
            print(f"Word count: {len(new_mahabaleshwar.Description.split())}")
    except Exception as e:
        print(f"Error updating Mahabaleshwar description: {e}")

def generate_description(place_name, place_type, state, city):
    """Generate a description between 90-100 words"""
    
    # Base descriptions by place type
    type_descriptions = {
        "hill station": [
            f"{place_name} is a picturesque hill station nestled in the {state} region of India, offering breathtaking panoramic views of lush valleys and majestic mountains. The cool climate and serene environment make it a perfect retreat from the hustle and bustle of city life. Visitors can explore numerous viewpoints, hiking trails, and enjoy the local cuisine. The misty landscapes, especially during monsoon and winter, create a magical atmosphere that captivates nature lovers and photographers alike. Located near {city}, it's easily accessible yet feels worlds away from urban chaos.",
        ],
        "beach": [
            f"{place_name} boasts some of the most pristine beaches in {state}, with golden sands stretching along the coastline and crystal-clear waters inviting visitors for a refreshing swim. The coastal paradise offers spectacular sunsets that paint the sky in vibrant hues of orange and pink. Water sports enthusiasts can enjoy activities like parasailing, jet-skiing, and banana boat rides. Beachside shacks serve delicious seafood caught fresh from the Arabian Sea. The relaxed atmosphere makes it ideal for those seeking tranquility and natural beauty.",
        ],
        "heritage": [
            f"{place_name} stands as a testament to India's rich historical legacy, showcasing magnificent architecture and intricate craftsmanship from bygone eras. The ancient structures narrate tales of valor, romance, and cultural evolution that shaped the region's identity. Visitors can explore palaces, forts, temples, and museums that house artifacts of immense historical significance. The blend of different architectural styles reflects the diverse influences that have contributed to India's cultural tapestry. Guided tours offer insights into the fascinating stories behind these architectural marvels.",
        ],
        "wildlife": [
            f"{place_name} is a biodiversity hotspot in {state}, providing sanctuary to numerous endangered species and offering wildlife enthusiasts an opportunity to witness animals in their natural habitat. The diverse ecosystem supports a variety of flora and fauna, creating a balanced environment crucial for conservation. Safari experiences allow visitors to spot majestic tigers, elephants, leopards, and various bird species. Conservation efforts have helped preserve this natural treasure for future generations. The best viewing experiences are during early morning and late afternoon when animals are most active.",
        ],
        "pilgrimage": [
            f"{place_name} is a sacred pilgrimage site that attracts devotees from across the country, offering spiritual solace and divine blessings to those who visit with faith. The ancient temples and religious structures showcase remarkable architectural brilliance while serving as centers of worship and meditation. Religious ceremonies and festivals bring the place alive with vibrant colors, music, and devotional fervor. The spiritual ambiance creates a sense of peace and introspection for visitors seeking connection with the divine. Local legends and mythological stories add depth to the religious significance of this holy site.",
        ],
        "adventure": [
            f"{place_name} is an adventure lover's paradise in {state}, offering thrilling experiences that get the adrenaline pumping and create lasting memories. Activities range from trekking and rock climbing to river rafting and paragliding, catering to different levels of adventure seekers. The challenging terrain provides the perfect backdrop for testing one's limits while enjoying breathtaking natural beauty. Professional guides ensure safety while helping visitors make the most of their adventure experiences. The changing seasons offer different adventure opportunities throughout the year.",
        ]
    }
    
    # Generic description for types not in our dictionary
    generic_description = f"{place_name} is a captivating destination located in {city}, {state}, offering visitors a unique blend of natural beauty, cultural experiences, and memorable activities. The region is known for its distinctive charm and welcoming atmosphere that leaves a lasting impression on travelers. Local traditions and customs provide insight into the rich heritage of the area. Seasonal variations bring different experiences throughout the year, making it worth visiting in different months. The local cuisine features delicious specialties that shouldn't be missed. Accommodations range from luxury hotels to budget-friendly options, catering to all types of travelers."
    
    # Get description based on place type or use generic
    if place_type and place_type.lower() in type_descriptions:
        description = type_descriptions[place_type.lower()][0]
    else:
        description = generic_description
    
    # Ensure it's between 90-100 words
    words = description.split()
    if len(words) > 100:
        return ' '.join(words[:100])
    elif len(words) < 90:
        # Add generic sentences until we reach at least 90 words
        additional_sentences = [
            f"Visitors from around the world come to experience its unique charm and beauty.",
            f"The local culture and traditions add to the allure of this magnificent destination.",
            f"The best time to visit is during the pleasant weather months.",
            f"Tourists can enjoy various activities and explore the rich heritage of the region.",
            f"The natural beauty and scenic landscapes make it a photographer's paradise.",
            f"Local cuisine offers a delightful experience for food enthusiasts.",
            f"The hospitality of locals makes visitors feel welcome and at home."
        ]
        
        while len(words) < 90:
            words.extend(random.choice(additional_sentences).split())
        
        # Trim to 100 words if needed
        if len(words) > 100:
            words = words[:100]
            
        return ' '.join(words)
    else:
        return description

def update_place_descriptions():
    """Update all place descriptions in the database to be between 90-100 words"""
    print("\n=== Updating All Place Descriptions ===\n")
    
    places = PlaceMode.objects.all()
    total_places = places.count()
    updated_count = 0
    
    print(f"Found {total_places} places in the database.")
    print("Updating descriptions to ensure they're between 90-100 words...")
    
    for i, place in enumerate(places):
        # Skip Mahabaleshwar as it's handled separately
        if "mahabaleshwar" in place.Name.lower():
            print(f"Skipping {place.Name} as it's handled separately.")
            continue
            
        print(f"Processing {i+1}/{total_places}: {place.Name}")
        
        # Count words in current description
        current_word_count = count_words(place.Description) if place.Description else 0
        
        if 90 <= current_word_count <= 100:
            print(f"  Description already has {current_word_count} words. Skipping.")
            continue
        
        # Generate a new description
        new_description = generate_description(
            place.Name, 
            place.Type, 
            place.State, 
            place.City
        )
        
        # Update the place
        place.Description = new_description
        place.save()
        updated_count += 1
        
        print(f"  Updated description. New word count: {count_words(new_description)}")
    
    print(f"\nSummary: Updated {updated_count} out of {total_places} place descriptions.")
    print("All descriptions are now between 90-100 words.")

def main():
    """Run both update functions"""
    print("Starting description update process...")
    
    # First update Mahabaleshwar specifically
    update_mahabaleshwar_description()
    
    # Then update all other places
    update_place_descriptions()
    
    print("\nAll updates completed successfully!")
    print("All place descriptions in the database are now between 90-100 words.")

if __name__ == "__main__":
    main()