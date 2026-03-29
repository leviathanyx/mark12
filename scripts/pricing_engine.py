import json, csv, os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

class PricingEngine:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.hotel_rates = self._load_csv('hotel_rates_master.csv')
        self.service_rates = self._load_csv('services_master.csv')
        self.transfer_rates = self._load_csv('transfer_rates_master.csv')
        self.markup_rates = self._load_csv('markup.csv')
        self.exchange_rates = self._load_exchange_rates()

    def _load_csv(self, filename):
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            return []
        with open(path, mode='r', encoding='utf-8-sig') as f:
            return list(csv.DictReader(f))

    def _load_exchange_rates(self):
        rows = self._load_csv('exchange_rates.csv')
        rates = {}
        for row in rows:
            rates[row['currency']] = {
                'to_eur': float(row['rate_to_eur']),
                'to_local': float(row['rate_to_local'])
            }
        return rates

    def get_exchange_rate(self, from_curr, to_curr):
        if from_curr == to_curr:
            return 1.0

        # All rates are relative to EUR in the CSV
        if from_curr == 'EUR':
            amount_in_eur = 1.0
        else:
            amount_in_eur = self.exchange_rates[from_curr]['to_eur']

        if to_curr == 'EUR':
            return amount_in_eur
        else:
            return amount_in_eur * self.exchange_rates[to_curr]['to_local']

    def convert(self, amount, from_curr, to_curr):
        if from_curr == to_curr:
            return amount
        rate = self.get_exchange_rate(from_curr, to_curr)
        return amount * rate

    def lookup_hotel(self, city, hotel_name, star):
        for row in self.hotel_rates:
            if row['city'].strip().lower() == city.strip().lower():
                if hotel_name and row[f'hotel_{star}star'].strip().lower() == hotel_name.strip().lower():
                    rate_str = row[f'rate_{star}star_pppn']
                    rate = float(rate_str) if rate_str and rate_str.strip() else 0.0
                    return rate, row['currency']
                # Fallback to first hotel in city if name is not matched
                rate_str = row[f'rate_{star}star_pppn']
                rate = float(rate_str) if rate_str and rate_str.strip() else 0.0
                return rate, row['currency']
        return None, None

    def lookup_service(self, description, city=None):
        for row in self.service_rates:
            if row['description'].strip().lower() == description.strip().lower():
                return float(row['rate']), row['currency'], row['rate_type']

        if city:
            for row in self.service_rates:
                if city.lower() in row['city'].lower() and description.strip().lower() in row['description'].strip().lower():
                    return float(row['rate']), row['currency'], row['rate_type']

        return None, None, None

    def calculate_package_pricing(self, pkg):
        target_currency = pkg.get('currency', 'EUR')
        markets = ['Premium', 'Standard']
        stars = ['3star', '4star']

        seasons = {}
        for row in self.markup_rates:
            label = row['season']
            market = row['market']
            if label not in seasons:
                seasons[label] = {'start': row['date_start'], 'end': row['date_end'], 'markups': {}}
            seasons[label]['markups'][market] = float(row['markup_factor'])

        pricing_table = {}

        for variant_name, variant in pkg['variants'].items():
            pricing_table[variant_name] = {}
            for market in markets:
                pricing_table[variant_name][market] = {}
                for season_label, season_data in seasons.items():
                    pricing_table[variant_name][market][season_label] = {
                        'date_start': season_data['start'],
                        'date_end': season_data['end']
                    }
                    mu = season_data['markups'].get(market, 1.0)

                    for star_key in stars:
                        star_val = star_key.replace('star', '')
                        total_cost_pp = 0

                        # Hotel costs (shared across all variants)
                        for h in pkg['hotels']:
                            city = h['city']
                            nights = h['nights']
                            hotel_name = h.get(f'hotel_{star_key}')
                            rate_pppn, curr = self.lookup_hotel(city, hotel_name, star_val)
                            if rate_pppn is not None:
                                cost_pp = self.convert(rate_pppn * nights, curr, target_currency)
                                total_cost_pp += cost_pp

                        # Services for this variant
                        services = []
                        if 'services' in variant:
                            services = variant['services']
                        elif 'days' in variant:
                            for day in variant['days']:
                                services.extend(day.get('services', []))

                        if variant_name == 'private':
                            pax_list = variant.get('min_pax', [8, 10, 12, 14, 16])
                            pricing_table[variant_name][market][season_label][star_key] = {}

                            vehicle_total = 0
                            if variant.get('vehicle_cost'):
                                vehicle_total = self.convert(variant['vehicle_cost']['rate'], variant['vehicle_cost']['currency'], target_currency)

                            for pax in pax_list:
                                variant_total_pp = total_cost_pp + (vehicle_total / pax)
                                for s in services:
                                    desc = s['description']
                                    rate, curr, rate_type = self.lookup_service(desc)
                                    if rate is None:
                                        rate = s.get('rate', 0)
                                        curr = s.get('currency', target_currency)
                                        rate_type = s.get('rate_type', 'PP')

                                    if rate_type == 'PP':
                                        variant_total_pp += self.convert(rate, curr, target_currency)
                                    elif rate_type == 'PI':
                                        variant_total_pp += self.convert(rate / pax, curr, target_currency)

                                pricing_table[variant_name][market][season_label][star_key][str(pax)] = round(variant_total_pp * mu, 3)
                            continue

                        # Default variant (FIT, self-drive, etc.)
                        variant_total_pp = total_cost_pp
                        for s in services:
                            desc = s['description']
                            rate, curr, rate_type = self.lookup_service(desc)
                            if rate is None:
                                rate = s.get('rate', 0)
                                curr = s.get('currency', target_currency)
                                rate_type = s.get('rate_type', 'PP')

                            if rate_type == 'PP':
                                variant_total_pp += self.convert(rate, curr, target_currency)
                            elif rate_type == 'PI':
                                variant_total_pp += self.convert(rate / 2, curr, target_currency)

                        twin = round(variant_total_pp * mu, 3)
                        single = round(variant_total_pp * mu * 2, 3)
                        child = round(twin * 0.416, 3)

                        pricing_table[variant_name][market][season_label][star_key] = {
                            'single': single,
                            'twin': twin,
                            'child': child
                        }

        return pricing_table

if __name__ == '__main__':
    import sys
    engine = PricingEngine()
    pkg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'packages', '2.1_paris_switzerland.json')
    with open(pkg_path) as f:
        pkg = json.load(f)

    pricing = engine.calculate_package_pricing(pkg)
    print(json.dumps(pricing, indent=2))
