This retailer has a number of sales that for a subset of products the wrong tax is listed. The tax _amount_ is correct but we need to change the label. However we don't want to change all products' taxes, just a subset of products that had a specific wrong tax.

Using https://docs.vendhq.com/reference/createupdateregistersale in order to achieve this

This script takes a list of sale_ids and product_ids and for each sale
1. Fetches that sale from /api/0.9/register_sales/<sale_id>
2. Checks each product in the sale against the list of product_ids.
3. If the product is in the list of product_ids and the product has a "wrong" tax id, change it to the correct one.
4. Posts the updated sale_json to /api/0.9/register_sales

### USAGE
```
python3 change_tax_on_sale.py </path/to/csv> <domain> <token>
```

csv should be in the following format (see example csv in this folder)
```
+----------+--------------+------------+------------+
| sale_ids | product_ids  | old_tax_id | new_tax_id |
+----------+--------------+------------+------------+
| <sale1>  | <product_id> | <tax_uuid> | <tax_uuid> |
+----------+--------------+------------+------------+
| <sale2>  | <product_id> |            |            |
+----------+--------------+------------+------------+
| <sale3>  | <product_id> |            |            |
+----------+--------------+------------+------------+
| <sale4>  | <product_id> |            |            |
+----------+--------------+------------+------------+
```
