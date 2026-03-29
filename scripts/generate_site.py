import os
import json
import glob
from jinja2 import Environment, FileSystemLoader
from pricing_engine import PricingEngine

# Directories
PACKAGES_DIR = 'packages'
OUTPUT_DIR = 'dist'
TEMPLATES_DIR = 'templates'

def main():
    # Setup directories
    os.makedirs(os.path.join(OUTPUT_DIR, 'packages'), exist_ok=True)

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    index_template = env.get_template('index.html')
    detail_template = env.get_template('detail.html')

    # Initialize Pricing Engine
    engine = PricingEngine()

    # Process packages
    json_files = glob.glob(os.path.join(PACKAGES_DIR, "*.json"))
    all_packages = []

    for f in sorted(json_files):
        with open(f, 'r') as pkg_file:
            pkg = json.load(pkg_file)

        # Skip city breaks if requested (though we'll process all multi-city ones)
        # Simple heuristic: ignore if 1 or 2 nights? User said "multi country",
        # but also said "only focus on multi country, ignore city breaks for now".
        # Let's check for "nights" > 2.
        nights = pkg.get('nights')
        if nights is None or int(nights) <= 2:
            continue

        # Calculate pricing
        pricing = engine.price_package(pkg)

        # Render detail page
        html_content = detail_template.render(pkg=pkg, pricing=pricing)
        output_path = os.path.join(OUTPUT_DIR, 'packages', f"{pkg['id']}.html")
        with open(output_path, 'w') as out_file:
            out_file.write(html_content)

        all_packages.append(pkg)
        print(f"Generated brochure: {pkg['id']} - {pkg['title']}")

    # Group packages by region for index page
    regions = {}
    for p in all_packages:
        region = p.get('region', 'other')
        if region not in regions:
            regions[region] = []
        regions[region].append(p)

    # Render index page
    index_html = index_template.render(regions=regions)
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as out_file:
        out_file.write(index_html)
    print(f"Generated index page with {len(all_packages)} packages.")

if __name__ == '__main__':
    main()
