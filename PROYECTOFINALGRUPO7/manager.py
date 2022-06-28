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
    
    def get_mean(self, df):
        self.media = df.mean()
        return self.media

    def get_std(self, df):
        self.std = df.std()
        return self.std
    
    def get_median(self, df):
        self.median = df.median()
        return self.median

    def get_var(self, df):
        self.var = df.var()
        return self.var
    
    def get_skew(self, df):
        self.skew = df.skew()
        return self.skew

    def get_kurtosis(self, df):
        self.kurtosis = df.kurtosis()
        return self.kurtosis
    
    def get_quantiles(self, df):
        self.quantiles = df.quantile([0.25, 0.5, 0.75])
        return str(self.quantiles)

    def get_variance(self, df):
        self.variance = df.var()
        return self.variance
    
    def get_mode(self, df):
        self.mode = df.mode()
        return self.mode

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

    def getFarmaciaAhumada(self, medicamento):
        l = []

        web = "https://www.farmaciasahumada.cl/catalogsearch/result/?q="
        url = web + medicamento

        contador = 0
        _UF = self.getUF()
        while(True):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            mainList = soup.find(
                class_='products list items product-items').find_all("li")
            searchCount = soup.find(class_='left-search-count').string
            print(searchCount if searchCount == 0 else "", end="")
            for tag in mainList:
                sub = tag.select(
                    "li > div > div[class~='product-item-details']")[0]
                cash_venta = sub.select(
                    "span[class~='price-final_price']  span[class='price']")[0].string
                cash_orig = sub.select(
                    "span[data-price-type='oldPrice'] > span[class='price']")
                if (len(cash_orig) == 0):
                    cash_orig = cash_venta
                else:
                    cash_orig = cash_orig[0].string
                precioUF2CLP = float(cash_venta.replace("$","").replace(".","")) / _UF
                cash_orig = cash_orig.replace("$","").replace(".","")
                cash_venta = cash_venta.replace("$","").replace(".","")
                url2 = sub.select("strong > a")[0].get("href")
                row = ["Farmacia Ahumada", medicamento, float(cash_orig), float(cash_venta), float(precioUF2CLP), url2]
                l.append(row)
                contador += 1
            try:
                siguiente = soup.find_all(class_='items pages-items')[-1]
                siguiente = siguiente.select("li[class~='pages-item-next'] > a")
                if (len(siguiente) > 0):
                    url = siguiente[0].attrs['href']
                else:
                    break
            except:
                break

        df = pd.DataFrame(l, columns=["Farmacia", "Nombre", "Precio_Original", "Precio_Venta", "Precio_Venta_UF", "Url"])
        print(df)
        return df
    
    def farmEx(self, medicamento):
        l = []
        pagina = 1
        flag = True
        _UF = self.getUF()
        while flag:
            url = f"https://farmex.cl/search?page={pagina}&q={medicamento}+-tag%3Adelete&type=product"
            # print(url)
            response = requests.get(url=url)
            soup = BeautifulSoup(response.text, "html.parser")
            mainList = soup.find_all(class_='pc-inner')[:-2]
            for tag in mainList:
                try:
                    cash_orig = None
                    cash_venta = float(tag.select("span[class~='price']")[0].string.replace("$","").replace(".","").replace(" ",""))
                except:
                    try:
                        cash_orig = tag.select("span[class~='price-compare']")[0].string.replace("$","").replace(".","").replace(" ","")
                        cash_venta = float(tag.select("span[class~='price-sale']")[0].string.replace("$","").replace(".","").replace(" ",""))
                    except:
                        flag = False
                precioUF2CLP = cash_venta / _UF
                url2 = 'https://farmex.cl' + tag.select("h5[class~='product-name']")[0].find('a', href=True)['href']
                row = ["Farmacia Farmex", medicamento, float(cash_orig) if cash_orig != None else cash_orig, float(cash_venta), float(precioUF2CLP), url2]
                l.append(row)
            pagina += 1

        df = pd.DataFrame(l, columns=["Farmacia", "Nombre", "Precio_Original", "Precio_Venta", "Precio_Venta_UF", "Url"])
        print(df)
        return df

    def get_ufPM(self):
        url = "https://www.bcentral.cl/inicio"
        response = requests.get(url)
        data = BeautifulSoup(response.content, "html.parser")
        fecha = data.find_all('p', class_='basic-text f-opensans-semibold c-beige-nb-1 fs-1 mb-1 text-center text-lg-left')
        fecha = fecha[0].text.replace(" de ", "/")
        mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
            "Noviembre", "Diciembre"]
        for i in range(len(mes)):
            if mes[i] in fecha:
                indice = i + 1
                fecha = fecha.replace(mes[i], f"{i + 1}")
        uf = data.find_all('p', class_='basic-text fs-2 f-opensans-bold text-center c-blue-nb-2')
        uf = uf[0].text
        uf = uf.replace(".", "")[1:]
        if indice < 10:
            fecha = fecha[0:3] + "0" + fecha[3:]
        lista = [fecha, float(uf.replace(",", ""))]
        df = pd.DataFrame(lista)
        nombre="parÃ¡metros.csv"
        df.to_csv(nombre, encoding='utf-8', header=False, index=False)
        return
    
