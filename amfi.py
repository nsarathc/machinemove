import requests as req
import datetime

from bs4 import BeautifulSoup


def get_amcs():
    resp = req.get("http://www.amfiindia.com/nav-history-download")
    if resp.status_code == 404:
        raise ValueError("Unable to get data.  Try later." + resp.request.url)

    soup = BeautifulSoup(resp.text, "html.parser")
    theSelect = soup.find("select", class_="select")

    amcList = []
    for amc in theSelect.findAll("option"):
        if amc.attrs['value'] == "":
            pass
        else:
            amcList.append((int(amc.attrs['value']), amc.get_text()))

    for c in sorted(amcList):
        print c[0], "  ", c[1]

get_amcs()
