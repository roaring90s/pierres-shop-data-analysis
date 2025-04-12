import requests
import pandas as pd

# Endpoints
BASE_URL = "https://pierres-store.onrender.com"
ORDERS_ENDPOINT = f"{BASE_URL}/api/order/all"
ORDER_DETAILS_ENDPOINT = f"{BASE_URL}/api/order/details"
SEASONS = ["spring", "summer", "autumn", "winter"]

# allSeasonsProductSearch
product_lookup = {}
for season in SEASONS:
    resp = requests.get(f"{BASE_URL}/products/{season}")
    if resp.status_code == 200:
        products = resp.json()
        for product in products:
            product_lookup[product["name"]] = season  # Using name as a key

# allOrdersSearch
orders_resp = requests.get(ORDERS_ENDPOINT)
orders_data = orders_resp.json()["orders"]

# dataFinalList
rows = []

for order in orders_data:
    order_id = order["id"]
    client_name = order["name"]
    phone = order["phone"]
    email = order["email"]
    address = order["address"]
    total = order["total"]
    payment_method = order["paymentMethod"]

    # Tentando pegar os detalhes de cada pedido
    try:
        details_resp = requests.get(f"{ORDER_DETAILS_ENDPOINT}/{order_id}")
        details_resp.raise_for_status()  # Levanta um erro se o status não for 2xx (OK)
        details = details_resp.json()
        products = details["products"]

        # Processa os produtos de cada pedido
        for p in products:
            product_name = p["name"]
            quantity = p["quantity"]
            price = p["price"]
            season = product_lookup.get(product_name, "unknown")

            rows.append({
                "order_id": order_id,
                "client_name": client_name,
                "phone": phone,
                "email": email,
                "address": address,
                "payment_method": payment_method,
                "total_order_value": total,
                "product_name": product_name,
                "quantity": quantity,
                "price_unit": price,
                "total_product_value": quantity * price,
                "season": season
            })

    except requests.exceptions.RequestException as e:
        # Caso algum erro aconteça, registra o erro mas continua
        print(f"Erro ao buscar detalhes do pedido {order_id}: {e}")

# Dataframe Export
df = pd.DataFrame(rows)
df.to_excel("complete_orders.xlsx", index=False)

print("Planilha gerada com sucesso!")
