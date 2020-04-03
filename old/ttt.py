import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time


def get_urls():
    driver = webdriver.Chrome()
    url = "https://www.fleetmon.com/ports/"
    driver.get(url)
    time.sleep(10)
    asia = driver.find_element_by_id("tab_asia")
    asia.click()
    time.sleep(5)
    html = driver.page_source
    prefix = "https://www.fleetmon.com"
    # htmltmp = open("html.txt", "r", encoding='UTF-8').read()
    soup = bs(html, "html.parser")
    entries = [x for x in list(soup.find(id="anchor-china").next_siblings) if x != ' '][0]
    entries = [x for x in entries if x != ' ']
    urls = []
    for entry in entries:
        class_ = entry.attrs["class"]
        if len(class_) < 3:
            continue
        size = int(class_[2].replace("size_", ""))
        port_url = entry.find("a").attrs["href"]
        urls.append((size, prefix+port_url))
    urls.sort(reverse=True)
    driver.close()
    return urls

print(get_urls())


#
#
# def get_in_port_list(html):
#     soup = bs(html, "html.parser")
#     rows = soup.find(id="vessels_in_port_table").find("tbody").find_all("tr")
#     vesselList = []
#     for row in rows:
#         rowDict = dict()
#         nameInfo = row.find(class_="name")
#         country = nameInfo.find(class_="vessel-flag").attrs['alt'].split(' ')[-1]
#         rowDict["Country"] = country
#         strings = [s.replace(' ', '_') for s in list(nameInfo.strings) if is_valid(s)]
#         if len(strings) != 3:
#             rowDict["Name"], rowDict["Vessel_Type"] = "Unknown", "Unknown"
#         else:
#             rowDict["Name"], rowDict["Vessel_Type"] = strings[1], strings[2]
#         strings = [s for s in list(row.find(class_="mmsi_callsign").strings) if is_valid(s)]
#         if len(strings) == 2:
#             rowDict["MMSI/CS"] = strings[1]
#         elif len(strings) == 3:
#             rowDict["MMSI/CS"] = strings[1] + '/' + strings[2]
#         else:
#             rowDict["MMSI/CS"] = "Unknown"
#         strings = [s for s in list(row.find(class_="length_width_range").strings) if is_valid(s)]
#         if len(strings) != 2:
#             rowDict["Length_Width"] = "Unknown"
#         else:
#             rowDict["Length_Width"] = strings[1]
#         strings = [s for s in list(row.find(class_="aisp_received sorting_1").strings) if is_valid(s)]
#         if len(strings) != 3:
#             rowDict["Signal_Time"] = "Unknown"
#         rowDict["Signal_Time"] = strings[2]
#         vesselList.append(rowDict)
#     return vesselList
#
#
# htmltmp = open("html.txt", "r", encoding='UTF-8').read()
# vsl = get_in_port_list(htmltmp)
# print(len(vsl))
# for ele in vsl:
#     print(ele)

# soup = bs(htmltmp, "html.parser")
# rows = soup.find(id="vessels_in_port_table").find("tbody").find_all("tr")
# vesselList = []
# for row in rows:
#     rowDict = dict()
#     nameInfo = row.find(class_="name")
#     country = nameInfo.find(class_="vessel-flag").attrs['alt'].split(' ')[-1]
#     rowDict["Country"] = country
#     strings = [s.replace(' ','_') for s in list(nameInfo.strings) if s != ' ']
#     if len(strings) != 3:
#         continue
#     rowDict[strings[0]], rowDict["Vessel_Type"] = strings[1], strings[2]
#     strings = [s for s in list(row.find(class_="mmsi_callsign").strings) if s != ' ']
#     if len(strings) != 3:
#         continue
#     rowDict[strings[0]] = strings[1] + '/' + strings[2]
#     strings = [s for s in list(row.find(class_="length_width_range").strings) if s != ' ']
#     if len(strings) != 2:
#         continue
#     rowDict["Length_Width"] = strings[1]
#     strings = [s for s in list(row.find(class_="aisp_received sorting_1").strings) if s != ' ']
#     if len(strings) != 3:
#         continue
#     rowDict["Signal_Time"] = strings[2]
#     vesselList.append(rowDict)
#     print(rowDict)


