import json
import os
import glob

PACKAGES_DIR = 'packages'

# Example content to enrich multi-country packages
# A real AI would generate these dynamically, but we'll use a mapping or general logic
enrichment_data = {
    "1.2": {
        "top_experiences": ["Afternoon Tea in London", "Touring Old Trafford in Manchester", "Walking the Royal Mile in Edinburgh", "Loch Ness Cruise from Inverness"],
        "top_food": ["Fish and Chips", "Haggis in Scotland", "Manchester Tart", "Cullen Skink"],
        "unique_highlights": ["Travel through the heart of the UK via high-speed rail", "Explore both the bustling cities and the serene Highlands", "Stay in handpicked 3* and 4* hotels"],
        "day_descriptions": {
            "Day 1": "Welcome to London! Arrive at the airport where a private transfer awaits to whisk you to your central hotel. Spend the evening soaking in the city's vibrant atmosphere.",
            "Day 2": "Explore the iconic sights of London with a flexible Hop-on Hop-off tour. Cruise along the Thames and marvel at the Big Ben, the London Eye, and the Tower of London.",
            "Day 3": "A free day to discover London's hidden gems. Perhaps visit the British Museum or enjoy a world-class West End show.",
            "Day 4": "Board a train to Manchester, the vibrant heart of the North. Check into your hotel and explore the city's rich industrial heritage and legendary music scene.",
            "Day 5": "A day for football fans or history buffs. Visit the Old Trafford stadium or explore the Manchester Museum of Science and Industry.",
            "Day 6": "Travel north by rail into Scotland, arriving in its historic capital, Edinburgh. Walk the cobbled streets of the Old Town and see the majestic Edinburgh Castle.",
            "Day 7": "Discover Edinburgh's charm with a sightseeing tour. Explore the Royal Mile or climb Arthur's Seat for breathtaking panoramic views.",
            "Day 8": "Journey into the Highlands as you take the train to Inverness. Known as the 'Gateway to the Highlands', it's the perfect base for exploring Loch Ness.",
            "Day 9": "Experience the rugged beauty of the Isle of Skye and the iconic Eilean Donan Castle on a guided excursion through the stunning Scottish landscape.",
            "Day 10": "Travel south to Glasgow, a city renowned for its Victorian architecture and vibrant arts scene. Enjoy a final evening of Scottish hospitality.",
            "Day 11": "After a final breakfast, enjoy some last-minute shopping before heading to the airport for your departure."
        }
    },
    "2.1": {
        "top_experiences": ["Sunset at the Eiffel Tower", "Cruise on Lake Lucerne", "Chocolate tasting in Zurich"],
        "top_food": ["Croissants in Paris", "Cheese Fondue in Lucerne", "Zürcher Geschnetzeltes in Zurich"],
        "unique_highlights": ["A romantic journey from the City of Light to the Swiss Alps", "Panoramic train travel across international borders", "Luxury stays in central 4-star hotels"],
        "day_descriptions": {
            "Day 1": "Arrive in Paris, the most romantic city in the world. A private transfer takes you to your hotel, followed by a free evening to stroll along the Seine.",
            "Day 2": "Take a comprehensive city tour including the Eiffel Tower and a relaxing Seine cruise. See the Louvre and the Arc de Triomphe from the comfort of a luxury coach.",
            "Day 3": "A day at leisure in Paris. Explore Montmartre's artist district or indulge in some high-end shopping at the Galeries Lafayette.",
            "Day 4": "Bid adieu to Paris and board a high-speed train to Lucerne, Switzerland. Nestled on the shores of Lake Lucerne, this city is a mountain-lover's paradise.",
            "Day 5": "Ascend the world's first revolving cable car to the summit of Mount Titlis. Enjoy snow and ice activities all year round before returning to Lucerne.",
            "Day 6": "Spend a free day exploring Lucerne. Walk across the Chapel Bridge or take a leisurely boat trip on the crystal-clear waters of the lake.",
            "Day 7": "Take a short train ride to Zurich, Switzerland's largest city and financial hub. Discover its charming Old Town (Altstadt) and vibrant lakeside promenades.",
            "Day 8": "Enjoy a final morning in Zurich before your departure. Don't forget to pick up some world-famous Swiss chocolates!"
        }
    },
    "10.3": {
        "top_experiences": ["Chasing the Northern Lights by cruise", "Husky or Reindeer Sledding", "Exploring the Arctic fjords"],
        "top_food": ["King Crab", "Reindeer Stew", "Cloudberry desserts"],
        "unique_highlights": ["Stay deep within the Arctic Circle during the magical winter season", "Multiple chances to witness the Aurora Borealis", "Iconic landmarks like the Arctic Cathedral"],
        "day_descriptions": {
            "Day 1": "Arrive in Tromsø, the 'Paris of the North'. After checking in, embark on an evening cruise in search of the elusive Northern Lights, far from the city's light pollution.",
            "Day 2": "Discover Tromsø Island on a guided tour, featuring the stunning Arctic Cathedral. Later, enjoy a night of Sami culture and reindeer sledding under the starlit sky.",
            "Day 3": "An adrenaline-filled day as you head out on a snowmobile safari through the frozen wilderness. Experience the silence and scale of the Arctic landscape.",
            "Day 4": "Set sail on a whale-watching tour to witness the ocean's giants in their natural habitat. In the evening, relax in one of Tromsø's cozy Arctic bars.",
            "Day 5": "Enjoy a final Arctic morning before your private transfer to the airport for your flight home."
        }
    }
}

def enrich_package(filepath):
    with open(filepath, 'r') as f:
        pkg = json.load(f)

    pkg_id = pkg.get('id')
    # Focus on multi-city (nights > 2 or nights != something specific for city breaks)
    # The user said "multi country", which usually means several cities or across borders.
    # We'll enrich if we have data for it.

    if pkg_id in enrichment_data:
        data = enrichment_data[pkg_id]
        pkg['top_experiences'] = data['top_experiences']
        pkg['top_food'] = data['top_food']
        pkg['unique_highlights'] = data['unique_highlights']

        # Merge day descriptions into variant if possible
        if 'regular_fit' in pkg.get('variants', {}):
            pkg['variants']['regular_fit']['day_descriptions'] = data['day_descriptions']

        with open(filepath, 'w') as f:
            json.dump(pkg, f, indent=2)
        return True
    return False

def main():
    json_files = glob.glob(os.path.join(PACKAGES_DIR, "*.json"))
    enriched_count = 0
    for f in json_files:
        if enrich_package(f):
            enriched_count += 1
            print(f"Enriched {f}")
    print(f"Total packages enriched: {enriched_count}")

if __name__ == '__main__':
    main()
