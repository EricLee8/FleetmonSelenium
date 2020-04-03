from bs4 import BeautifulSoup as bs


def fetch_data_from_raw_html(port_name, html):
    soup = bs(html, "html.parser")
    port_inf = soup.find_all(id="port-info")[0]
    rtvDict = dict()
    rtvDict["port_name"] = port_name
    rtvDict.update(parse_port_info(port_inf))
    return rtvDict

def parse_port_info(port_info):
    rows = port_info.find_all("tr")
    rtvDict = dict()
    for idx, row in enumerate(rows):
        cols = row.find_all("td")
        if idx not in [3, 4, 5]:
            keyList = [x.replace(':', '') for x in list(map(lambda s: s.strip(), list(cols[0].strings))) if x != '']
            key = keyList[0] if len(keyList) > 0 else ''
            valueList = [x for x in list(map(lambda s: s.strip(), list(cols[1].strings))) if x != '']
            value = valueList[0] if len(valueList) > 0 else ''
            rtvDict[key] = value
        else:
            keyList = [x.replace(':', '') for x in list(map(lambda s: s.strip(), list(cols[0].strings))) if x != '']
            key = keyList[0] if len(keyList) > 0 else ''
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
    return rtvDict

if __name__ == "__main__":
    htmltmp = open("html.txt", "r", encoding='UTF-8').read()
    print(fetch_data_from_raw_html("XiaMen", htmltmp))