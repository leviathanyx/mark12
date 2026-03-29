import json
import csv
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

class PricingEngine:
    def __init__(self):
        self.hotels_data = self._load_csv(os.path.join(DATA_DIR, 'hotel_rates_master.csv'))
        self.services_data = self._load_csv(os.path.join(DATA_DIR, 'services_master.csv'))
        self.transfers_data = self._load_csv(os.path.join(DATA_DIR, 'transfer_rates_master.csv'))
        self.exchange_rates = self._load_exchange_rates()
        self.arctic_keywords = ['tromso', 'tromsø', 'kiruna', 'rovaniemi', 'abisko', 'lapland', 'rovaniemi']

    def _load_csv(self, path):
        if not os.path.exists(path):
            return []
        with open(path, encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _load_exchange_rates(self):
        rates = {}
        # Default rates based on common values and provided CSV hints
        # We'll use rate_to_eur from the CSV
        path = os.path.join(DATA_DIR, 'exchange_rates.csv')
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rates[row['currency']] = float(row['rate_to_eur'])

        # Override/Ensure core ones
        if 'EUR' not in rates: rates['EUR'] = 1.0
        # If GBP rate_to_eur is 1.0 in CSV but we know 1.15 is a common conversion,
        # but the CSV also has 1.15 in rate_to_local.
        # Actually, let's look at the CSV again.
        # GBP, 1.0, 1.15.
        # If we assume 1 GBP = 1.15 EUR, then rate_to_eur should be 1.15.
        if rates.get('GBP') == 1.0:
            rates['GBP'] = 1.15 # Better default if CSV is placeholder

        return rates

    def get_exchange_rate(self, from_cur, to_cur):
        if from_cur == to_cur: return 1.0
        from_to_eur = self.exchange_rates.get(from_cur, 1.0)
        to_to_eur = self.exchange_rates.get(to_cur, 1.0)
        return from_to_eur / to_to_eur

    def is_arctic(self, pkg):
        cities = [h['city'].lower() for h in pkg.get('hotels', [])]
        for city in cities:
            if any(k in city for k in self.arctic_keywords):
                return True
        return False

    def get_target_currency(self, pkg):
        # "uk and uk+dublin packages priced in gbp and rest all in euro"
        hotels = pkg.get('hotels', [])
        if not hotels: return 'EUR'

        has_uk = False
        for h in hotels:
            city = h['city'].lower()
            # Find city in hotel_rates_master to see country
            for hd in self.hotels_data:
                if hd['city'].lower() == city:
                    if hd['country'] == 'United Kingdom':
                        has_uk = True
                        break
            if has_uk: break

        if has_uk: return 'GBP'
        return 'EUR'

    def find_hotel_rate(self, city, star):
        for h in self.hotels_data:
            if h['city'].lower() == city.lower():
                rate = h.get(f'rate_{star}star_pppn')
                if rate and rate.strip():
                    return float(rate), h['currency']
        return None, None

    def find_service_rate(self, description, city=None):
        desc_lower = description.lower().strip()
        # Try exact or partial match in services
        for s in self.services_data:
            s_desc = s['description'].lower().strip()
            if s_desc == desc_lower or s_desc in desc_lower or desc_lower in s_desc:
                return float(s['rate']), s['currency'], s['rate_type']

        # Try matching in transfers
        for t in self.transfers_data:
            # Match if city matches and description contains 'transfer' and 'airport' or 'station'
            if city and t['city'].lower() == city.lower():
                if 'transfer' in desc_lower:
                    if 'airport' in desc_lower and ('airport' in t['from'].lower() or 'airport' in t['to'].lower()):
                        return float(t['rate_eclass_pi']), t['currency'], 'PI'
                    if 'station' in desc_lower and ('station' in t['from'].lower() or 'station' in t['to'].lower()):
                        return float(t['rate_eclass_pi']), t['currency'], 'PI'

        return None, None, None

    def price_package(self, pkg):
        target_cur = self.get_target_currency(pkg)
        is_arctic = self.is_arctic(pkg)

        results = {
            'id': pkg.get('id'),
            'title': pkg.get('title'),
            'currency': target_cur,
            'regular_fit': self.price_variant(pkg, 'regular_fit', target_cur, is_arctic),
            'private': self.price_variant(pkg, 'private', target_cur, is_arctic)
        }
        return results

    def price_variant(self, pkg, variant_name, target_cur, is_arctic):
        if variant_name not in pkg.get('variants', {}):
            return None

        variant = pkg['variants'][variant_name]
        pricing = {}

        seasons = ['winter', 'summer']
        if pkg.get('winter_only'):
            seasons = ['winter']

        for season in seasons:
            # Markup: 15% winter (1.15), 20% summer (1.20). Arctic 20% always.
            markup = 1.20 if (season == 'summer' or is_arctic) else 1.15

            pricing[season] = {}
            for star in ['3', '4']:
                hotel_total_adult = 0
                service_total_adult = 0
                transfer_total_adult = 0

                # Calculate Hotel Costs
                for h in pkg.get('hotels', []):
                    nights = h.get('nights', 0)
                    rate_pppn, cur = self.find_hotel_rate(h['city'], star)
                    if rate_pppn is not None:
                        hotel_total_adult += self.get_exchange_rate(cur, target_cur) * rate_pppn * nights
                    else:
                        # Fallback to JSON
                        val = h.get(f'rate_{star}star')
                        json_rate = float(val) if val is not None else 0.0
                        div = 2.0 if h.get('rate_type') == 'PI' else 1.0
                        # If JSON rate is total for stay, we use it as is (divided by 2 if PI)
                        # We assume JSON rate is already per-person-total if PP or per-room-total if PI
                        hotel_total_adult += self.get_exchange_rate(h.get('currency', target_cur), target_cur) * (json_rate / div)

                # Calculate Service Costs
                services = variant.get('services', [])
                for s in services:
                    desc = s.get('description', '')
                    # We might need the city for matching transfers
                    # Often Day 1 transfer is for the first city
                    city = pkg.get('hotels', [{}])[0].get('city')

                    rate, cur, rtype = self.find_service_rate(desc, city)
                    if rate is None:
                        rate = float(s.get('rate', 0))
                        cur = s.get('currency', target_cur)
                        rtype = s.get('rate_type', 'PP')

                    if rtype == 'PP':
                        service_total_adult += self.get_exchange_rate(cur, target_cur) * rate
                    else:
                        # PI - divide by 2 for adult per-person
                        transfer_total_adult += self.get_exchange_rate(cur, target_cur) * (rate / 2.0)

                # Final Pricing Calculation
                # Adult price includes everything
                adult_total_cost = hotel_total_adult + service_total_adult + transfer_total_adult
                twin_price = adult_total_cost * markup

                # Child Price: 39% of adult (hotel + services only, no transfers)
                child_total_cost = (hotel_total_adult + service_total_adult) * 0.39
                child_price = child_total_cost * markup

                # Single Price: Estimate (Double the hotel portion)
                single_total_cost = (hotel_total_adult * 2) + service_total_adult + transfer_total_adult
                single_price = single_total_cost * markup

                pricing[season][f'{star}star'] = {
                    'twin': round(twin_price, 2),
                    'child': round(child_price, 2),
                    'single': round(single_price, 2)
                }
        return pricing

def main():
    engine = PricingEngine()
    if len(sys.argv) > 1:
        pkg_path = sys.argv[1]
        if os.path.exists(pkg_path):
            with open(pkg_path) as f:
                pkg = json.load(f)
            print(json.dumps(engine.price_package(pkg), indent=2))
        else:
            print(f"File not found: {pkg_path}")
    else:
        print("Usage: python pricing_engine.py <package_json_path>")

if __name__ == '__main__':
    main()
