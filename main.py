import requests as r
from threading import Thread
import os
import uuid
import time
import datetime

with open("limiteds.txt", "r") as f:
    limiteds = f.read().replace(" ", "").split(",")

with open("cookie.txt", "r") as f:
    cookie = f.read()


user_id = r.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}).json()["id"]
x_token = ""
def get_x_token():
    global x_token

    x_token = r.post("https://auth.roblox.com/v2/logout",
                     cookies={".ROBLOSECURITY": cookie}).headers["x-csrf-token"]
    print("Logged in. / Sesion iniciada correctamente")

    while 1:
        # Gets the x_token every 4 minutes.
        x_token = r.post("https://auth.roblox.com/v2/logout",
                         cookies={".ROBLOSECURITY": cookie}).headers["x-csrf-token"]
        time.sleep(248)


def buy(json, itemid, productid):
    print("Iniciando spameo de compra en el limitado...")

    data = {
        "collectibleItemId": itemid,
        "expectedCurrency": 1,
        "expectedPrice": 0,
        "expectedPurchaserId": user_id,
        "expectedPurchaserType": "User",
        "expectedSellerId": json["creatorTargetId"],
        "expectedSellerType": "User",
        "idempotencyKey": "FurrycalityFetchingService",
        "collectibleProductId": productid
    }

    while 1:
        data["idempotencyKey"] = str(uuid.uuid4())
        bought = r.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{itemid}/purchase-item", json=data,
            headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie})

        if bought.reason == "Too Many Requests":
            print("Ah ocurrido un error en el limite de solicitudes, intentado denuevo en breve...")
            time.sleep(0.5)
            continue

        try:
            bought = bought.json()
        except:
            print(bought.reason)
            print("Error al decodificar el Json durante la compra del item")
            continue

        if not bought["purchased"]:
            print(f"Fallo en comprar el limitado, intenta denuevo - Info: {bought} - {data}")
        else:
            print(f"Se compro correctamente el limitado! - Info: {bought} - {data}")

        info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                      json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                      headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie})
        try:
            left = info.json()["data"][0]["unitsAvailableForConsumption"]
        except:
            print(f"Fallo en obtener el stock - Full log: {info.text} - {info.reason}")
            left = 0

        if left == 0:
            print("No se pudo comprar el limitado, mejor suerte la proxima")
            return


# Get collectible and product id for all the limiteds.
Thread(target=get_x_token).start()

print("UGCatcher by Furrycality™#1234\nWeb: https://rblx.furrycality.pw (Soon!)\nDiscord server: (Soon!)")
while x_token == "":
    time.sleep(0.01)

# https://apis.roblox.com/marketplace-items/v1/items/details
# https://catalog.roblox.com/v1/catalog/items/details

cooldown = 60/(39/len(limiteds))-0.8
while 1:
    start = time.perf_counter()
    print("\n")

    for limited in limiteds:
        try:
            info = r.post("https://catalog.roblox.com/v1/catalog/items/details",
                           json={"items": [{"itemType": "Asset", "id": int(limited)}]},
                           headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie}).json()["data"][0]
        except KeyError:
            print("Ratelimit! Waiting for next minute to start / Ratelimited! Esperando el siguiente minuto para reiniciar")
            time.sleep(60-int(datetime.datetime.now().second))
            continue

        if info.get("priceStatus", "") != "Off Sale" and info.get("collectibleItemId") is not None:
            productid = r.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                   json={"itemIds": [info["collectibleItemId"]]},
                   headers={"x-csrf-token": x_token}, cookies={".ROBLOSECURITY": cookie})

            try:
                productid = productid.json()[0]["collectibleProductId"]
            except:
                print(f"Something went wrong whilst getting the product id / Algo ha salido mal obteniendo el id del articulo - Logs - {productid.text} - {productid.reason}")
                continue

            buy(info, info["collectibleItemId"], productid)

    taken = time.perf_counter()-start
    if taken < cooldown:
        time.sleep(cooldown-taken)

    os.system("cls")
    print("UGCatcher by Furrycality™#1234\nWeb: https://rblx.furrycality.pw (Soon!)\nDiscord server: (Soon!)\n\nRealizando tareas solicitadas\n\n"
          "Checkeo completado.\n"
          f"Tiempo tomado: {round(time.perf_counter()-start, 3)}\n"
          f"Tiempo sin delay: {round(cooldown, 3)}")