# Europe Incoming — FIT Brochure & Pricing System

A modern system to manage FIT package pricing and generate "Apple-esque" HTML brochures, replacing traditional PDF brochures with engaging, high-quality content.

## 🚀 Deployment

The site is automatically built and deployed to **GitHub Pages** whenever changes are pushed to the `main` or `feature/*` branches.

**The Automated Build Process includes:**
1.  **Enrichment:** `scripts/enrich_packages.py` adds high-quality descriptions and local favorite experiences to multi-country itineraries.
2.  **Pricing Calculation:** `scripts/pricing_engine.py` calculates real-time rates based on the latest CSV data.
3.  **Site Generation:** `scripts/generate_site.py` renders the static site using Jinja2 templates.
4.  **Verification:** `scripts/test_outputs.py` ensures the generated HTML is structurally sound and contains all required data.

## 🛠 Maintenance & Updates

To update prices or itinerary content, follow these simple steps:

### 1. Update Pricing (CSVs)
Modify the files in the `data/` directory:
- `hotel_rates_master.csv`: Update PPPN rates for hotels.
- `services_master.csv`: Update per-person rates for attractions and trains.
- `transfer_rates_master.csv`: Update per-group cab rates (system automatically divides by 2 for per-person cost).
- `exchange_rates.csv`: Update currency conversion rates.

### 2. Update Itineraries (JSONs)
Modify or add new package JSON files in the `packages/` directory. The system will automatically:
- Calculate the correct seasonal pricing (15% Winter / 20% Summer).
- Apply the 20% Arctic destination markup exception.
- Handle GBP/EUR currency switches.

### 3. Local Development & Preview
To see your changes locally before pushing:
1.  **Install dependencies:** `pip install -r requirements.txt`
2.  **Enrich packages:** `python scripts/enrich_packages.py`
3.  **Build the site:** `PYTHONPATH=scripts python scripts/generate_site.py`
4.  **Preview:** Open `dist/index.html` in your browser.

## 🖋 Content Guidelines
- **Day-by-Day Descriptions:** Aim for 80-100 words per day. Use specific local details (hidden gems, neighborhood favorites) rather than generic tourist highlights.
- **Top Experiences & Food:** Avoid "obvious" items like the Eiffel Tower or generic Pizza. Research local-favorite dining spots, street food, and unique cultural activities.
