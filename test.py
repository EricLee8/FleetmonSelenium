import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import json
from threading import Thread
import threading
import random
from multiprocessing import Process


def parse_port_info(port_info):
    rows = port_info.find_all("tr")
    rtvDict = dict()
    for row in rows:
        cols = row.find_all("td")
        try:
            keyList = [x.replace(':', '') for x in list(map(lambda s: s.strip(), list(cols[0].strings))) if x != '']
            key = keyList[0] if len(keyList) > 0 else ''
            key = key.replace(')','').replace('(','').replace(' ', '_')
        except:
            key = 'Unknown'
        if key in ['LOCODE_UNCTAD', 'Local_Time', 'Port_Activity_Index', 'Port_Usage', 'Tide']:
            if key == 'Port_Activity_Index':
                try:
                    value = int(cols[1].find(class_="port-usage tooltip-bs").attrs['title'].split(" ")[-1])
                except:
                    value = None
            elif key == 'Port_Usage':
                try:
                    value = dict()
                    usages = cols[1].find(class_="port-usage").contents
                    for usage in usages:
                        try:
                            raw_usage = usage.attrs['title'].split('(')
                            usg_key = raw_usage[0].replace(',', '').replace(' ', '_')[:-1]
                            usg_value = raw_usage[1].replace(')', '')
                            value[usg_key] = usg_value
                        except:
                            pass
                except:
                    value = dict()
            else:
                try:
                    valueList = [x for x in list(map(lambda s: s.strip(), list(cols[1].strings))) if x != '']
                    value = valueList[0] if len(valueList) > 0 else ''
                except:
                    value = None
            rtvDict[key] = value  
    return rtvDict


session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
})
url = "https://www.fleetmon.com/ports/shipu_cnxsp_17142/"
response = session.get(url)
html = response.text
soup = bs(html, "html.parser")
port_inf = soup.find_all(id="port-info")[0]
print(parse_port_info(port_inf))

session.close()