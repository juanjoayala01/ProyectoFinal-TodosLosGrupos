from urllib import response
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from rich import print



class Estadisticas():
    def __init__(self):
        self.max = 0
        self.min = 0
        self.media = 0
    
    def get_max(self, df):
        self.max = df.max()
        return self.max

    def get_min(self, df):
        self.min = df.min()
        return self.min

      
class Scraper():
    def __init__(self):
        pass

    def getUF(self):
        url = "https://www.mindicador.cl/api/uf"
        response = requests.get(url)
        response = json.loads(response.text.encode("utf-8"))
        return response['serie'][0]['valor']




    def getSKUs(self, query):
        params = {"requests": [{
            "indexName": "sb_variant_production",
            "query": query
        }]
        }
        url = "https://gm3rp06hjg-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia+for+JavaScript+%284.8.5%29%3B+Browser+%28lite%29&x-algolia-api-key=51f403f1055fee21d9e54d028dc19eba&x-algolia-application-id=GM3RP06HJG"
        response = requests.post(url, json=params)

        skus = []
        for hit in response.json()['results'][0]['hits']:
            skus.append(hit['sku'])
        return [skus, query]


    def farmaciaSalcobrand(self, skus):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'}
        itemIds = ",".join(skus[0])

        resp = requests.get(
            f"https://api.retailrocket.net/api/1.0/partner/602bba6097a5281b4cc438c9/items/?itemsIds={itemIds}&format=json", headers=headers)

        rows = []
        _UF = self.getUF()
        print(f"Resultados: {len(resp.json())}")
        for item in resp.json():
            precioUF2CLP = item['Price'] / _UF
            url2 = item['Url']
            row = ["Farmacia Salcobrand", item['Vendor'], float(item['OldPrice']), float(item['Price']), float(precioUF2CLP), url2]
            rows.append(row)

        df = pd.DataFrame(rows, columns=["Farmacia", "Nombre", "Precio_Original", "Precio_Venta", "Precio_Venta_UF", "Url"])
        print(df)
        return df
