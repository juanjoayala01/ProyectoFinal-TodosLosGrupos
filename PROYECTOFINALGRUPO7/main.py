from bs4 import BeautifulSoup
import manager as mg
import pandas as pd
from rich import print
import argparse
import requests


def nombreAhumada(url):
    response = requests.get(url)
    data = BeautifulSoup(response.content, "html.parser")
    busqueda_med = data.find_all('h3', class_='product-brand')
    return (busqueda_med[0].text)

def descripcionAhumada(url):
    response = requests.get(url)
    data = BeautifulSoup(response.content, "html.parser")
    busqueda_med = data.find_all('div', class_='value')
    try:
        return (busqueda_med[1].text)
    except:
        return ("No especifica")
   
def nombreSalcobrand(url):
    response = requests.get(url)
    data = BeautifulSoup(response.content, "html.parser")
    busqueda_med = data.find_all('h2', class_='product-info')
    return (busqueda_med[0].text)

def descripcionSalcobrand(url):
    response = requests.get(url)
    data = BeautifulSoup(response.content, "html.parser")
    busqueda_med = data.find_all('div', class_='description-area')
    return (busqueda_med[0].text)

def nombreFarmex(url):
    response = requests.get(url)
    data = BeautifulSoup(response.content, "html.parser")
    busqueda_med = data.find_all('h1', class_='page-heading')
    busqueda_med = busqueda_med[0].text.split(" ")
    return (busqueda_med[0])


def descripcionFarmex(url):
    response = requests.get(url)
    data = BeautifulSoup(response.content, "html.parser")
    busqueda_med = data.find_all('div', class_='tab-pane active')
    descripcion = ""
    for i in busqueda_med:
        descripcion = descripcion+i.text
    return (descripcion)


def main(principios_activos):
    scraper = mg.Scraper()
    scraper.get_ufPM()
    principios_activos = open(principios_activos, "r", encoding="utf-8")
    principios = principios_activos.readlines()
    principios_activos.close()
    principios = [x.strip() for x in principios]

    for principio in principios:
        print(f"Busqueda para {principio}")
        datos_au = scraper.getFarmaciaAhumada(principio)
        print()
        datos_sb = scraper.farmaciaSalcobrand(scraper.getSKUs(principio))
        print()
        datos_fe = scraper.farmEx(principio)
        print()

        datos = pd.concat([datos_au, datos_sb, datos_fe])

        # convert datos to csv
        datos.to_csv(f"{principio}.csv", index=False)

        est = mg.Estadisticas()
        max_ = est.get_max(df=datos["Precio_Venta"])
        min_ = est.get_min(df=datos["Precio_Venta"])
