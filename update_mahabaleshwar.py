import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.models import PlaceMode

def update_mahabaleshwar_description():
    """Update the description for Mahabaleshwar to match the provided text"""
    try:
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

if __name__ == "__main__":
    update_mahabaleshwar_description()