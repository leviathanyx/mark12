import json
import os
import glob

PACKAGES_DIR = 'packages'

# Enriched data for multi-country packages
# Using researched specific local experiences and foods
# Requirements: 80-100 words per day description, no generic AI-style "best of"
enrichment_data = {
    "1.2": {
        "top_experiences": [
            "A Friday night at The Tamil Prince in Islington for the best desi-pub food in London.",
            "Exploring the Victorian sewers and the Crossness Pumping Station (The Cathedral on the Marsh).",
            "A pint and a pie at The Old Wellington, Manchester's oldest building, tucked next to modern skyscrapers.",
            "Hiking the Water of Leith Walkway in Edinburgh for a serene forest escape within the city."
        ],
        "top_food": [
            "Deep-fried Mars Bar at a local Edinburgh chippy (it's a real local dare).",
            "Bury Black Pudding from a traditional market stall in Manchester.",
            "Salt Beef Bagel from Beigel Bake on Brick Lane, London (open 24/7).",
            "Cullen Skink (creamy smoked haddock soup) at a quiet Leith waterfront bistro."
        ],
        "unique_highlights": [
            "Travel by the 'Flying Scotsman' route along the rugged East Coast rail line.",
            "Stay in a converted Victorian townhouse in the heart of Manchester's Northern Quarter.",
            "Private 'Black Cab' tour of London's hidden legal inns and secret courtyards."
        ],
        "day_descriptions": {
            "Day 1": "Upon arrival at London Heathrow, avoid the crowded Heathrow Express and settle into your private transfer that winds through the historic leafy suburbs of West London. Your journey concludes at a boutique hotel in the heart of Bloomsbury, a neighborhood famous for its literary history and quiet garden squares. After checking in, take a leisurely stroll to the nearby Lamb's Conduit Street, a refined local favorite for independent shops and cozy wine bars like Noble Rot. Spend your first evening soaking in the sophisticated yet understated atmosphere of intellectual London before a restful night's sleep in your elegant surroundings.",
            "Day 2": "Instead of the standard tourist loop, use your flexible pass to head south of the river to the Borough Market early in the morning to catch the local traders before the crowds arrive. Sample artisanal cheeses and freshly baked sourdough before hopping on a Thames Clipper—the local's river bus—to glide past the Tower of London towards Greenwich. Spend the afternoon exploring the painted hall at the Old Royal Naval College, often called Britain's Sistine Chapel. End your day with a sunset walk up to the Royal Observatory for a panoramic view of the Canary Wharf skyline glowing across the water.",
            "Day 3": "Today is about the hidden side of the West End. Start with a visit to the Sir John Soane's Museum in Lincoln's Inn Fields, an eccentric treasure trove of art and antiquities that remains exactly as the architect left it in 1837. Later, wander through the historic Seven Dials neighborhood, ducking into Neal's Yard for a burst of color and a healthy lunch at one of the hidden cafes. As evening approaches, find your way to a traditional candlelit pub in Soho, like The French House, where half-pints are the tradition and the walls are steeped in the history of bohemians and writers.",
            "Day 4": "Board a high-speed Avanti West Coast train at Euston Station, leaving the capital behind for the industrial-cool vibe of Manchester. The journey takes you through the rolling green hills of the Midlands, arriving at Manchester Piccadilly in just over two hours. After a short transfer to your hotel, head straight for the Northern Quarter. This isn't the Manchester of postcards; it's a grid of red-brick warehouses filled with record stores, independent galleries, and the iconic Afflecks Palace. Spend your afternoon uncovering street art in the back alleys and enjoying a craft beer at a local brewery taproom like Cloudwater or Northern Monk.",
            "Day 5": "Dedicate your morning to the People's History Museum, a deeply moving look at the cradle of British democracy and the labor movement, located in a beautifully restored Edwardian pump house. For lunch, skip the chains and head to the Armenian Taverna, a subterranean local gem that has been serving authentic khorovadz and khinkali for over fifty years. In the afternoon, take a short tram ride to the Salford Quays to see The Lowry and the Imperial War Museum North, marveling at the futuristic architecture of MediaCityUK. Finish the day with a walk along the canals of Castlefield, where Roman ruins meet Victorian viaducts.",
            "Day 6": "Travel north by rail through the dramatic landscapes of the Lake District and the Scottish Borders, arriving in Edinburgh, the 'Athens of the North.' As your train pulls into Waverley Station, the sight of the Scott Monument and the craggy heights of Arthur's Seat will take your breath away. After checking into your hotel, avoid the Royal Mile's tourist shops and head instead to the New Town. Walk along the elegant Georgian terraces of Queen Street and discover the hidden Dean Village, a former grain milling hamlet nestled in a deep valley by the Water of Leith, feeling worlds away from the city center.",
            "Day 7": "Start your day with a hike up the Salisbury Crags for a rugged perspective of the city without the crowds of the main castle. Descend into the Southside neighborhood for a traditional Scottish breakfast at a local 'greasy spoon' before visiting the Surgeons' Hall Museums, one of the oldest and most fascinating medical collections in the world. Spend your afternoon in the neighborhood of Stockbridge, browsing the local Sunday market or visiting the botanical gardens. In the evening, head to a traditional folk bar like Sandy Bell's for a 'wee dram' and the chance to hear authentic live Scottish fiddle music in an intimate setting.",
            "Day 8": "Journey into the true heart of the Highlands as you board the train for Inverness. This route is one of the most scenic in Britain, passing through the wild Cairngorms National Park where you might spot red deer from your window. Upon arrival in Inverness, the Highland capital, take a walk along the Ness Islands, a series of small, wooded islands connected by Victorian footbridges in the middle of the River Ness. It's a favorite local spot for a quiet evening stroll. Enjoy dinner at a riverside bistro featuring locally caught salmon or Highland venison before retiring to your comfortable hotel.",
            "Day 9": "Today's excursion takes you across the bridge to the misty Isle of Skye. While many tourists rush the main sites, your guide will take you to the quieter corners of the island, perhaps a hidden fairy pool or a remote coastal lookout where the Cuillin mountains drop dramatically into the Atlantic. Visit the iconic Eilean Donan Castle on the way back, but take time to explore the small village of Plockton nearby, known as the 'Jewel of the Highlands' for its palm trees and sheltered bay. This long day in the wild will leave you with a profound sense of Scotland's ancient and rugged soul.",
            "Day 10": "Take the scenic train south to Glasgow, Scotland's largest and most vibrant city. Often overlooked in favor of Edinburgh, Glasgow offers a gritty, authentic charm and world-class Victorian architecture. Visit the Kelvingrove Art Gallery and Museum, a stunning red sandstone building housing everything from a Spitfire to a Salvador Dalí masterpiece. Spend your afternoon in the West End, exploring the cobbled lanes of Ashton Lane and the sprawling grounds of the University of Glasgow, which looks remarkably like Hogwarts. Enjoy a final Scottish feast in a Finnieston restaurant, the city's coolest foodie hub, before your final night in Scotland.",
            "Day 11": "Enjoy a final morning in Glasgow, perhaps visiting the Willow Tea Rooms designed by the legendary Charles Rennie Mackintosh for a truly authentic Glaswegian experience. Browse the independent shops of the Merchant City before your private transfer takes you to Glasgow International Airport. As you fly home, you'll carry memories not just of the famous landmarks, but of the quiet canal walks, the hidden basement restaurants, and the rugged, mist-covered landscapes that define the true spirit of the United Kingdom and Scotland. Safe travels on your journey home, and we hope to see you back in the Highlands soon."
        }
    },
    "2.1": {
        "top_experiences": [
            "A sunset walk along the Promenade Plantée, the world's first elevated park built on an old railway viaduct.",
            "Exploring the hidden 'Passages Couverts'—19th-century glass-roofed shopping arcades tucked between buildings.",
            "A private boat trip on Lake Lucerne to the tiny village of Bauen, accessible only by water or a single narrow road.",
            "Dining at a 'Zunfthaus' (Guild House) in Zurich for a taste of medieval history and rich, traditional Swiss cuisine."
        ],
        "top_food": [
            "Freshly shucked oysters from a stall in the Marché d'Aligre, Paris.",
            "Lozärner Chügelipastete (a savory puff pastry filled with veal and mushrooms) in a traditional Lucerne tavern.",
            "Luxemburgerli (miniature macarons) from the legendary Sprüngli on Zurich's Bahnhofstrasse.",
            "Zürcher Geschnetzeltes with crispy Rösti, the ultimate Zurich comfort food."
        ],
        "unique_highlights": [
            "Cross the border from France to Switzerland on the TGV Lyria, watching the landscape transition from vineyards to Alps.",
            "Stay in a boutique hotel in Paris's Marais district, a neighborhood of medieval streets and hidden courtyards.",
            "Exclusive access to a private chocolate atelier in Lucerne for a hands-on tasting and making session."
        ],
        "day_descriptions": {
            "Day 1": "Arrive at Paris Charles de Gaulle and skip the chaotic RER train for your private transfer directly to the Marais. This historic district, once the city's aristocratic heart, is now a vibrant blend of medieval architecture, chic boutiques, and hidden Jewish heritage. After settling into your hotel, wander to the Place des Vosges, the oldest planned square in Paris, and find a quiet corner under the vaulted arcades. Enjoy your first Parisian evening at a neighborhood bistro like Chez Janou, famous for its lively atmosphere and legendary chocolate mousse served from a massive shared bowl. The city of light awaits your discovery.",
            "Day 2": "Instead of the crowded Eiffel Tower platforms, start your day at the Trocadéro gardens for the best view of the Iron Lady as the sun hits the steel. Join a local-led walking tour of the hidden passages near the Palais Royal, where 19th-century elegance survives in boutique shops and historic bookstores. For lunch, head to the Enfants Rouges, the oldest covered market in Paris, to sample authentic street food from around the world alongside local Parisians. Spend your afternoon in the quiet gardens of the Musée Rodin, where the famous 'Thinker' sits among blooming roses and peaceful pathways, far from the city's bustle.",
            "Day 3": "Today is for exploring the artistic soul of Montmartre, but beyond the caricaturists of Place du Tertre. Follow the winding backstreets to find the 'Lapin Agile' cabaret and the city's only remaining vineyard, the Clos Montmartre. Visit the Musée de la Vie Romantique, a hidden gem at the foot of the hill with a charming tea garden. In the evening, enjoy a sunset cruise on the Seine, but opt for a smaller, private boat that allows you to glide under the historic bridges with a glass of champagne, watching the city's monuments illuminate one by one in a spectacular display of light and shadow.",
            "Day 4": "Board the sleek TGV Lyria at Gare de Lyon for a high-speed journey into the heart of Switzerland. As the train leaves the French countryside, watch through the panoramic windows as the landscape transforms into the dramatic peaks and crystal-clear lakes of the Swiss Alps. You'll arrive in Lucerne by mid-afternoon, where the iconic Chapel Bridge and the surrounding snow-capped mountains create a scene straight from a fairytale. After a short walk to your lakeside hotel, take a gentle stroll along the quay, enjoying the fresh alpine air and the sound of the lake lapping against the stone walls before a traditional Swiss dinner.",
            "Day 5": "Ascend the heights of Mount Titlis via the world's first revolving cable car, the Titlis Rotair. At the summit, 3,020 meters above sea level, walk across the Cliff Walk, Europe's highest suspension bridge, for heart-stopping views of the glacier. After a morning of snow and ice, return to Lucerne and spend your afternoon exploring the local side of the city. Visit the Musegg Wall, the well-preserved medieval ramparts with nine historic towers that offer a panoramic view over the town and the lake. It's a favorite local spot for a quiet walk away from the main tourist squares in the old town.",
            "Day 6": "Take a scenic boat trip across Lake Lucerne to the base of the Bürgenstock mountain. Instead of the luxury resort, take the historic funicular up to the ridge for a hike along the Felsenweg, a spectacular path carved into the cliff face. For lunch, find a remote mountain 'Gasthaus' for a plate of Alpine macaroni (Älplermagronen) with applesauce, a true local comfort dish. Return to Lucerne in the late afternoon and spend some time in the quiet courtyards of the Franciscan Church or browse the local craft shops in the narrow alleys of the Hirschenplatz. The evening is yours to enjoy the serene lakeside atmosphere.",
            "Day 7": "A short, scenic train ride takes you to Zurich, Switzerland's sophisticated financial capital. While often seen as just a business hub, Zurich's Altstadt (Old Town) is a maze of charming streets and historic guild houses. Visit the Fraumünster Church to see the stunning stained-glass windows by Marc Chagall, then head to the Lindenhof, a quiet hilltop park that was once a Roman fort and offers the best view over the Limmat River. Spend your afternoon in the trendy Zurich West district, where old shipping containers and industrial warehouses have been transformed into a vibrant hub of design, art, and local culinary innovation in the Viadukt market.",
            "Day 8": "On your final morning in Switzerland, take a leisurely walk along the shores of Lake Zurich, watching the local rowing clubs and the distant Alps. Visit a local bakery for a fresh 'Gipfeli' (Swiss croissant) before heading to the world-famous Bahnhofstrasse for some last-minute shopping—or simply to admire the high-end window displays. Your private transfer will then take you to Zurich International Airport for your flight home. As you depart, you'll reflect on a journey that took you from the romantic streets of Paris to the majestic peaks of the Swiss Alps, leaving you with a deep appreciation for the diverse beauty of Europe."
        }
    },
    "10.3": {
        "top_experiences": [
            "A Friday night at Bardus Bistro, where the menu changes weekly based on what the local fishermen bring in.",
            "A visit to the 'Polaria' aquarium to see the bearded seals, followed by a local brew at Mack's, the world's northernmost brewery.",
            "An evening 'Aurora Chase' with a small, local guide who uses satellite data to find the clearest skies far from any tourists.",
            "Exploring the Arctic-Alpine Botanical Garden, the world's northernmost, even in the middle of a snowy winter."
        ],
        "top_food": [
            "Tørrfisk (dried cod) prepared in the traditional northern style with bacon and pea puree.",
            "Reindeer burger at Bardus—a local culinary 'must have' for any visitor to the north.",
            "King Crab fresh from the Barents Sea, served simply with lemon and homemade mayonnaise.",
            "Mølje—a traditional winter dish of cod, liver, and roe that is the soul of northern Norwegian coastal culture."
        ],
        "unique_highlights": [
            "Stay in a traditional 'Rorbu' (fisherman's cabin) converted into a cozy, high-end Arctic retreat.",
            "Cross the Arctic Circle by air and feel the immediate change in the light and the crispness of the air.",
            "A private visit to a Sami family's winter camp for an authentic exchange about life in the extreme north."
        ],
        "day_descriptions": {
            "Day 1": "Arrive in Tromsø, a city nestled among majestic fjords and snow-capped peaks deep within the Arctic Circle. After your private transfer to your central hotel, head to the quayside to see the historic wooden houses that have survived centuries of Arctic winters. As darkness falls, embark on a Northern Lights Cruise. Unlike the crowded bus tours, this small boat glides silently away from the city lights, providing a peaceful and stable platform for witnessing the Aurora Borealis dancing across the dark Arctic sky. Enjoy a hot bowl of traditional reindeer soup on deck while the captain shares tales of the sea and the magical lights above.",
            "Day 2": "Explore Tromsø Island on a guided tour that goes beyond the main sights. Visit the Arctic Cathedral with its stunning glass mosaic, then head to the Southern tip of the island to walk through the Telegrafbukta park, a favorite local spot for seeing the winter sun struggle to rise above the horizon. In the afternoon, prepare for a Night Reindeer Sledding adventure. You'll travel to a remote Sami camp where you'll be greeted by a local family. After a traditional meal in a 'Lavvu' (Sami tent) around a roaring fire, experience the silent magic of reindeer sledding through the frozen wilderness under a canopy of stars and, if luck is with you, the glowing green Aurora.",
            "Day 3": "Today is for high-octane adventure as you head out on a Snowmobile Safari. You'll be driven into the heart of the Lyngen Alps, where the mountains rise vertically from the deep blue fjords. After a safety briefing, you'll pilot your snowmobile across frozen lakes and through snow-covered forests, reaching high plateaus with breathtaking panoramic views. This is the true Arctic wilderness, far from any roads or buildings. For lunch, enjoy a simple but hearty meal prepared over an open fire in the snow before heading back to Tromsø for a relaxing evening in one of the city's cozy cafes, perhaps sampling a local Arctic craft beer.",
            "Day 4": "Set sail on a Whale Watching tour to witness the ocean's giants in their natural habitat. During the winter months, humpback whales and orcas follow the herring into the fjords surrounding Tromsø. This responsible tour uses a silent electric engine to minimize disturbance to the animals, allowing for a truly intimate and respectful encounter. Spend your afternoon at the Polar Museum, housed in a 19th-century wharf house, which tells the gripping stories of Arctic explorers and seal hunters. For your final dinner in the north, head to Fiskekompaniet for the freshest seasonal seafood, including the legendary Arctic king crab, served with a modern Norwegian twist.",
            "Day 5": "Enjoy a final Arctic morning in Tromsø. Take a ride on the Fjellheisen cable car to the top of Mount Storsteinen for a last, spectacular view of the city, the islands, and the surrounding mountains bathed in the soft, ethereal light of the polar winter. Browse the local shops for authentic Sami silver jewelry or high-quality Norwegian woolens before your private transfer takes you to Tromsø Airport. As you fly south, you'll carry with you the profound silence of the frozen fjords and the memory of the lights that dance in the northern sky, a journey that has touched the very soul of the Arctic."
        }
    }
}

def enrich_package(filepath):
    with open(filepath, 'r') as f:
        pkg = json.load(f)

    pkg_id = pkg.get('id')
    # Focus only on multi-country/multi-city packages with nights > 2
    nights = pkg.get('nights')
    if nights is None or int(nights) <= 2:
        return False

    if pkg_id in enrichment_data:
        data = enrichment_data[pkg_id]
        pkg['top_experiences'] = data['top_experiences']
        pkg['top_food'] = data['top_food']
        pkg['unique_highlights'] = data['unique_highlights']

        # Merge day descriptions into regular_fit variant
        if 'variants' in pkg and 'regular_fit' in pkg['variants']:
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
    print(f"Total multi-country packages enriched with long-form content: {enriched_count}")

if __name__ == '__main__':
    main()
