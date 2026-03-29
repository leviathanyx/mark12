import json, os, glob
from pricing_engine import PricingEngine

PACKAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'packages')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'packages.json')

def build_packages():
    engine = PricingEngine()
    consolidated_packages = []

    package_files = glob.glob(os.path.join(PACKAGES_DIR, '*.json'))

    for pkg_path in package_files:
        print(f"Processing {os.path.basename(pkg_path)}...")
        with open(pkg_path, 'r', encoding='utf-8') as f:
            try:
                pkg = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding {pkg_path}: {e}")
                continue

        try:
            new_pricing = engine.calculate_package_pricing(pkg)
        except Exception as e:
            print(f"Error calculating pricing for {pkg_path}: {e}")
            continue

        for variant_name, pricing in new_pricing.items():
            if variant_name in pkg['variants']:
                pkg['variants'][variant_name]['pricing'] = pricing

        new_validity = []
        labels_seen = set()
        # Extract validity from the first market/season found in the calculated pricing
        found_validity = False
        for variant_name, variant_pricing in new_pricing.items():
            for market, market_pricing in variant_pricing.items():
                for season_label, season_pricing in market_pricing.items():
                    if season_label not in labels_seen:
                        new_validity.append({
                            "label": season_label.capitalize(),
                            "start": season_pricing['date_start'],
                            "end": season_pricing['date_end']
                        })
                        labels_seen.add(season_label)
                found_validity = True
                break
            if found_validity: break

        if new_validity:
            pkg['validity'] = new_validity

        with open(pkg_path, 'w', encoding='utf-8') as f:
            json.dump(pkg, f, indent=2)

        consolidated_packages.append({
            "id": pkg.get('id'),
            "name": pkg.get('title'),
            "region": pkg.get('region'),
            "duration": f"{pkg.get('nights', 0)} nights / {pkg.get('days', 0)} days" if pkg.get('days') else f"{pkg.get('nights', 0)} nights",
            "cities": [h['city'] for h in pkg.get('hotels', [])],
            "description": pkg.get('description', ''),
            "pricing": new_pricing
        })

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"packages": consolidated_packages}, f, indent=2)

    print(f"Successfully built {len(consolidated_packages)} packages. Output: {OUTPUT_FILE}")

if __name__ == '__main__':
    build_packages()
