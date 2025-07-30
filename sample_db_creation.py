import os

# Re-create the directory after environment reset
output_dir = "data/rag_docs"
os.makedirs(output_dir, exist_ok=True)

# File contents to regenerate
documents = {
    "top_destinations.md": """# Top Destinations for Travelers

Here are some of the most visited cities around the world:
- **Paris, France**: Eiffel Tower, Louvre, Seine River
- **Tokyo, Japan**: Shibuya Crossing, Sushi, Mount Fuji
- **New York, USA**: Times Square, Broadway, Statue of Liberty
- **Rome, Italy**: Colosseum, Vatican City, Roman Forum
- **Bangkok, Thailand**: Floating Markets, Temples, Street Food
""",
    "travel_tips.md": """# General Travel Tips

- Always keep a copy of important documents.
- Notify your bank before international travel.
- Carry a power adapter for the destination country.
- Be aware of local customs and etiquette.
- Learn basic local phrases.
""",
    "itinerary_template.md": """# Sample 5-Day Itinerary Template

**Day 1**: Arrival, local orientation, short walking tour  
**Day 2**: Visit major landmarks  
**Day 3**: Cultural exploration (museums, markets)  
**Day 4**: Day trip to nearby area  
**Day 5**: Relaxation, final shopping, departure
""",
    "cuisine_guide.md": """# International Cuisine Guide

- **Italy**: Pasta, Gelato, Pizza  
- **Japan**: Ramen, Sushi, Tempura  
- **France**: Croissants, Coq au Vin, Cheese  
- **India**: Curry, Naan, Chai  
- **Mexico**: Tacos, Enchiladas, Mole
""",
    "travel_safety.md": """# Travel Safety Tips

- Keep your belongings secure and close.
- Avoid poorly lit or deserted areas at night.
- Use registered taxis or ride apps.
- Don’t flash valuables in public.
- Know emergency numbers and embassy location.
"""
}

# Write files to disk
for filename, content in documents.items():
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

# List the saved files to confirm
os.listdir(output_dir)
