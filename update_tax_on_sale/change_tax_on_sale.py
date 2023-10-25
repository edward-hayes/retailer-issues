import sys
import csv
import requests

# Function to read the CSV file and extract sale_ids
def read_csv(file_path):
    sale_ids = []
    product_ids = []
    old_tax_ids = []
    new_tax_ids = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        missing_headers = set(["sale_ids", "product_ids", "old_tax_id", "new_tax_id"]) - set(reader.fieldnames)
        if missing_headers:
            raise ValueError(f'The CSV file is missing the following headers: {", ".join(missing_headers)}')
        
        for row in reader:
            sale_ids.append(row['sale_ids'])
            product_ids.append(row['product_ids'])
            old_tax_ids.append(row['old_tax_id'])
            new_tax_ids.append(row['new_tax_id'])

        old_tax_id = old_tax_ids[0]
        new_tax_id = new_tax_ids[0]
    return sale_ids, product_ids, old_tax_id,new_tax_id

def create_product_hash_table(product_ids):
    products_hash = {product_id: True for product_id in product_ids}
    return products_hash

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

def change_tax_id(sale_json,products_hash, new_tax_id, old_tax_id):
    sale = sale_json['register_sales'][0]
    products = sale['register_sale_products']
    for product in products:
        # some products don't need to be changed and in this case the old_tax_id is the correct one. 
        # this checks to make sure the product is not in the list of products that should have the old_tax_id
        if product["tax_id"] == old_tax_id:
            if not products_hash.get(product["product_id"]):
                product["tax_id"] = new_tax_id
    return sale

def post_sale(header,url,sale_json):
    response = requests.post(url,headers=header,json=sale_json)
    if response.status_code > 399:
        print(response.text)
    response.raise_for_status()


def main():
    if len(sys.argv) != 4:
        print('To use this do: python3 change_tax_on_sale.py <CSV_FILE> <DOMAIN> <TOKEN>')
        sys.exit(1)

    csv_file = sys.argv[1]
    domain = sys.argv[2]
    token = sys.argv[3]

    try:
        sale_ids, product_ids, old_tax_id,new_tax_id = read_csv(csv_file)
        products_hash = create_product_hash_table(product_ids)
        header = make_header(token)
        post_url = make_post_url(domain)
        for sale_id in sale_ids:
            try:
                print("adjusting sale_id: ", sale_id)
                get_url = make_get_url(domain,sale_id)
                sale_json = get_sale(header,get_url)
                updated_sale_json = change_tax_id(sale_json,products_hash,new_tax_id,old_tax_id)
                post_sale(header,post_url,updated_sale_json)
            except requests.exceptions.HTTPError as e:
                print(f'Error: {e}', "skipping this sale..")
                continue

    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == "__main__":
    main()