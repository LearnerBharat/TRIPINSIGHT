import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.models import PlaceMode

def add_akshardham_temple():
    """Add Akshardham Temple to the database"""
    try:
        # Check if Akshardham Temple already exists
        existing_temple = PlaceMode.objects.filter(Name__icontains="Akshardham Temple").first()
        
        if existing_temple:
            print("Akshardham Temple already exists in the database. Updating description...")
            
            # Update the description with an extended version
            existing_temple.Description = """Akshardham Temple in Delhi is a stunning showcase of India's rich cultural heritage and spirituality. Inaugurated in 2005, this architectural marvel is dedicated to Bhagwan Swaminarayan. Made from intricately carved pink sandstone and white marble, the temple features breathtaking sculptures, domes, and pillars depicting deities, saints, and historical figures. The complex includes a mesmerizing musical fountain, an IMAX-style film on Swaminarayan's life, and a peaceful boat ride showcasing 10,000 years of Indian achievements. Surrounded by serene gardens, Akshardham is not just a temple — it's an immersive journey through India's art, wisdom, and devotion, leaving visitors inspired and awed. The main monument, built without steel, spans 141 feet high, 316 feet wide, and 370 feet long, with 234 ornately carved pillars, 9 domes, and 20,000 statues of India's spiritual personalities."""
            
            # Update other fields
            existing_temple.Google_rating = "4.8"
            existing_temple.Image_url = "https://images.unsplash.com/photo-1548013146-72479768bada?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
            existing_temple.map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3501.2714010929!2d77.27494231508096!3d28.6526638824072!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390ce35b9975b1fb%3A0x69a09f265ef3b22a!2sAkshardham!5e0!3m2!1sen!2sin!4v1627281260782!5m2!1sen!2sin"
            existing_temple.save()
            
            print(f"Successfully updated Akshardham Temple description.")
            print(f"Word count: {len(existing_temple.Description.split())}")
            
        else:
            print("Akshardham Temple not found in the database. Creating a new entry...")
            
            # Create a new Akshardham Temple entry
            new_temple = PlaceMode(
                Name="Akshardham Temple",
                City="Delhi",
                Zone="Northern Delhi",
                Type="heritage",
                State="Delhi",
                Description="""Akshardham Temple in Delhi is a stunning showcase of India's rich cultural heritage and spirituality. Inaugurated in 2005, this architectural marvel is dedicated to Bhagwan Swaminarayan. Made from intricately carved pink sandstone and white marble, the temple features breathtaking sculptures, domes, and pillars depicting deities, saints, and historical figures. The complex includes a mesmerizing musical fountain, an IMAX-style film on Swaminarayan's life, and a peaceful boat ride showcasing 10,000 years of Indian achievements. Surrounded by serene gardens, Akshardham is not just a temple — it's an immersive journey through India's art, wisdom, and devotion, leaving visitors inspired and awed. The main monument, built without steel, spans 141 feet high, 316 feet wide, and 370 feet long, with 234 ornately carved pillars, 9 domes, and 20,000 statues of India's spiritual personalities.""",
                Year="2005",
                Time_needed="4-5 hours",
                Google_rating="4.8",
                Significance="Religious",
                Best_time_to_visit="October to March",
                Fees="₹170 for adults (includes exhibitions)",
                Image_url="https://images.unsplash.com/photo-1548013146-72479768bada?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
                map_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3501.2714010929!2d77.27494231508096!3d28.6526638824072!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390ce35b9975b1fb%3A0x69a09f265ef3b22a!2sAkshardham!5e0!3m2!1sen!2sin!4v1627281260782!5m2!1sen!2sin"
            )
            new_temple.save()
            print("Created new Akshardham Temple entry successfully.")
            print(f"Word count: {len(new_temple.Description.split())}")
    except Exception as e:
        print(f"Error adding/updating Akshardham Temple: {e}")

if __name__ == "__main__":
    print("Starting to add Akshardham Temple to the database...")
    add_akshardham_temple()
    print("Process completed.")