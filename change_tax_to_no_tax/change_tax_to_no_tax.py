import sys
import csv
import requests

# Function to read the CSV file and extract sale_ids
def read_csv(file_path):
    sale_ids = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        missing_headers = set(["sale_ids"]) - set(reader.fieldnames)
        if missing_headers:
            raise ValueError(f'The CSV file is missing the following headers: {", ".join(missing_headers)}')
        
        sale_ids = [row['sale_ids'] for row in reader]

    return sale_ids

def get_no_tax_id(domain, header):
    url = f"https://{domain}.vendhq.com/api/2.0/taxes"
    response = requests.get(url,headers=header)
    response.raise_for_status()
    data = response.json()
    rates = data['data']
    for rate in rates:
        if rate['name'] == 'No Tax':
            return rate['id']

def make_header(token):
    header = {
        "authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    return header

def make_get_url(domain,sale_id):
    url = f"https://{domain}.vendhq.com/api/register_sales/{sale_id}"
    return url

def make_post_url(domain):
    url = f"https://{domain}.vendhq.com/api/register_sales"
    return url

def get_sale(header,url):
    response = requests.get(url,headers=header)
    response.raise_for_status()
    return response.json()

def change_tax_id(sale_json, new_tax_id):
    sale = sale_json['register_sales'][0]
    products = sale['register_sale_products']
    for product in products:
            product["tax_id"] = new_tax_id
    return sale

def post_sale(header,url,sale_json):
    response = requests.post(url,headers=header,json=sale_json)
    if response.status_code > 399:
        print(response.text)
    response.raise_for_status()


def main():
    if len(sys.argv) != 4:
        print('To use this do: python3 change_tax_to_no_tax.py <CSV_FILE> <DOMAIN> <TOKEN>')
        sys.exit(1)

    csv_file = sys.argv[1]
    domain = sys.argv[2]
    token = sys.argv[3]

    try:
        sale_ids = read_csv(csv_file)
        header = make_header(token)
        post_url = make_post_url(domain)
        no_tax_id = get_no_tax_id(domain,header)
        for sale_id in sale_ids:
            try:
                print("adjusting sale_id: ", sale_id)
                get_url = make_get_url(domain,sale_id)
                sale_json = get_sale(header,get_url)
                updated_sale_json = change_tax_id(sale_json,no_tax_id)
                post_sale(header,post_url,updated_sale_json)
            except requests.exceptions.HTTPError as e:
                print(f'Error: {e}', "skipping this sale..")
                continue

    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == "__main__":
    main()