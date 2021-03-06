import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import json
from threading import Thread
import threading


DETAIL_WAIT = 60
HOME_WAIT = 20
XHR_WAIT = 10
MAX_RETRY = 3
ThreadNum = 8
HEAD_LESS = True
SERVER = False


def is_valid(s):
    return s not in [' ', '\n'] and len(s) > 1


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))


def get_urls():
    opt = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images': 2}
    opt.add_experimental_option('prefs', prefs)
    if HEAD_LESS:
        opt.add_argument('--headless')
    if SERVER:
        opt.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=opt)
    url = "https://www.fleetmon.com/ports/"
    driver.get(url)
    time.sleep(HOME_WAIT)
    asia = driver.find_element_by_id("tab_asia")
    driver.execute_script("arguments[0].click();", asia)
    time.sleep(XHR_WAIT)
    html = driver.page_source
    prefix = "https://www.fleetmon.com"
    soup = bs(html, "html.parser")
    entries = [x for x in list(soup.find(id="anchor-china").next_siblings) if x != ' '][0]
    entries = [x for x in entries if x != ' ']
    urls = [(500, "https://www.fleetmon.com/ports/hong-kong_hkhkg_10032/")] # port_size 500
    for entry in entries:
        class_ = entry.attrs["class"]
        if len(class_) < 3:
            continue
        port_url = entry.find("a").attrs["href"]
        try:
            vessel_num = int(entry.find("a").attrs["title"].split(" ")[0])
        except:
            vessel_num = 0
        if vessel_num > 10:
            urls.append((vessel_num, prefix+port_url))
    driver.close()
    return urls


def fetch_data_from_raw_html(html):
    soup = bs(html, "html.parser")
    port_inf = soup.find_all(id="port-info")[0]
    rtvDict = dict()
    rtvDict.update(parse_port_info(port_inf))
    return rtvDict


def parse_port_info(port_info):
    rows = port_info.find_all("tr")
    rtvDict = dict()
    for idx, row in enumerate(rows):
        cols = row.find_all("td")
        if idx not in [3, 4, 5]:
            try:
                keyList = [x.replace(':', '') for x in list(map(lambda s: s.strip(), list(cols[0].strings))) if x != '']
                key = keyList[0] if len(keyList) > 0 else ''
                key = key.replace(')','').replace('(','').replace(' ', '_')
            except:
                key = 'Uknown'
            try:
                valueList = [x for x in list(map(lambda s: s.strip(), list(cols[1].strings))) if x != '']
                value = valueList[0] if len(valueList) > 0 else ''
                rtvDict[key] = value
            except:
                rtvDict[key] = None
        else:
            try:
                keyList = [x.replace(':', '') for x in list(map(lambda s: s.strip(), list(cols[0].strings))) if x != '']
                key = keyList[0] if len(keyList) > 0 else ''
                key = key.replace(')', '').replace('(', '').replace(' ', '_')
            except:
                key = 'Uknown'
            try:
                if idx == 3:
                    value = cols[1].find(class_="port-usage tooltip-bs").attrs['title'].split(" ")[-1]
                    rtvDict[key] = value
                elif idx == 4:
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
                    rtvDict[key] = value
            except:
                rtvDict[key] = None
    return rtvDict


def get_in_port_list(html):
    soup = bs(html, "html.parser")
    rows = soup.find(id="vessels_in_port_table").find("tbody").find_all("tr")
    vesselList = []
    for row in rows:
        try:
            rowDict = dict()
            nameInfo = row.find(class_="name")
            country = nameInfo.find(class_="vessel-flag").attrs['alt'].split(' ')[-1]
            rowDict["Country"] = country
            strings = [s.replace(' ', '_') for s in list(nameInfo.strings) if is_valid(s)]
            if len(strings) != 3:
                rowDict["Name"], rowDict["Vessel_Type"] = "Unknown", "Unknown"
            else:
                rowDict["Name"], rowDict["Vessel_Type"] = strings[1], strings[2]
            strings = [s for s in list(row.find(class_="mmsi_callsign").strings) if is_valid(s)]
            if len(strings) == 2:
                rowDict["MMSI/CS"] = strings[1]
            elif len(strings) == 3:
                rowDict["MMSI/CS"] = strings[1] + '/' + strings[2]
            else:
                rowDict["MMSI/CS"] = "Unknown"
            strings = [s for s in list(row.find(class_="length_width_range").strings) if is_valid(s)]
            if len(strings) != 2:
                rowDict["Length_Width"] = "Unknown"
            else:
                rowDict["Length_Width"] = strings[1]
            strings = [s for s in list(row.find(class_="aisp_received sorting_1").strings) if is_valid(s)]
            if len(strings) != 3:
                rowDict["Signal_Time"] = "Unknown"
            rowDict["Signal_Time"] = strings[2]
            vesselList.append(rowDict)
        except:
            pass
    return vesselList



def get_data(url):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        })
        response = session.get(url)
        html = response.text
        port_name = url[url.find('ports')+6:url.find('_')]
        overviewDict = fetch_data_from_raw_html(html)
        session.close()
    except:
        overviewDict = {"Info": "Unknown"}
        port_name = 'Unknown'
    vesselList = []
    opt = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images': 2}
    opt.add_experimental_option('prefs', prefs)
    if HEAD_LESS:
        opt.add_argument('--headless')
    if SERVER:
        opt.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=opt)
    total_vessels = 0
    try:
        driver.get(url)
        time.sleep(DETAIL_WAIT)
        page_selector = Select(driver.find_element_by_name("vessels_in_port_table_length"))
        page_selector.select_by_value("50")
        time.sleep(2*XHR_WAIT)
        html = driver.page_source
        soup = bs(html, "html.parser")
        try:
            total_vessels = int(list(soup.find(id="vessels_in_port_table_info").strings)[0].replace(',','').split(" ")[-2])
        except BaseException as e:
            print(e)
            total_vessels = 1
        for idx in range(total_vessels // 50+1):
            html = driver.page_source
            vsl = get_in_port_list(html)
            vesselList += vsl
            next_botton = driver.find_element_by_id("vessels_in_port_table_next")
            driver.execute_script("arguments[0].click();", next_botton)
            time.sleep(XHR_WAIT)
    except:
        pass
    rtvDict = dict()
    rtvDict["Record_Time"] = get_time()
    rtvDict["Port_Name"] = port_name
    rtvDict["Total_Vessels"] = total_vessels
    rtvDict["Overview"] = overviewDict
    rtvDict['Vessels'] = vesselList
    driver.close()
    return rtvDict


def get_data_from_urlList(urls: list):
    dump_f = open("ports.json", "a")
    urls.sort(reverse=True)
    for url_tuple in urls:
        url = url_tuple[1] # 0下标是vessel_num
        num_retry = 0
        rtvd = dict()
        print(threading.current_thread().name + ": " + get_time() + ": Starting fetching data from " + url + " ...")
        while num_retry < MAX_RETRY:
            try:
                rtvd = get_data(url)
                break
            except:
                print(threading.current_thread().name + ": " + "Maximum retry exceeded...")
                rtvd = {"Info": "Unknown"}
                num_retry += 1
        print(threading.current_thread().name + ": " + get_time() + ": Writing to file " + url + ' ...')
        dump_f.write(json.dumps(rtvd) + '\n')


def get_one_round():
    print("============================================================================================")
    print(get_time() + "Starting a round!!!")
    print("============================================================================================")
    urlList = get_urls()
    site_per_thread = len(urlList) // ThreadNum + 1
    threads = []
    for i in range(1, ThreadNum + 1):
        p = Thread(target=get_data_from_urlList, name='Thread' + str(i),
                   args=[urlList[(i - 1) * site_per_thread:i * site_per_thread], ])
        threads.append(p)
        p.start()
    for p in threads:
        p.join()


def timer_task():
    try:
        get_one_round()
    except BaseException as e:
        print(e)
    timer = threading.Timer(180, timer_task)
    timer.start()


if __name__ == '__main__':
    timer_task()