import random
import asyncio
import requests
import json
import os
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))


class Covid:
    CONNECT_TIMEOUT = 90

    def __init__(self, city):
        self.query_city = city
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "PostmanRuntime/7.26.2",
            # "Accept": "*/*",
            # "Accept-Encoding": "gzip, deflate, br",
            # "Connection": "keep-alive",
            # "Cache-Control": "no-cache",
        }
        self.max_page = 3

    def covidHarianProvinsi(self):
        point = 0
        url = """https://services5.arcgis.com/VS6HdKS0VfIhv8Ct/ArcGIS/rest/services/Statistik_Harian_per_Provinsi_COVID19_Indonesia_Rev/FeatureServer/0/query?where=1%3D1+and+%22tanggal%22+%3E+date+%272020-7-01+00%3A00%3A00%27+AND+%22tanggal%22+%3C+date+%272020-8-30+00%3A00%3A00%27+and+%22provinsi%22+%3D+%27{0}%27&objectIds=&time=&resultType=none&outFields=*&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset={point}&resultRecordCount=&sqlFormat=standard&f=json&token="""

        dataTemp = []
        for x in range(0, self.max_page):
            ex = url.format(self.query_city, point=point)
            print(ex)
            resp = self.get_body(ex)

            if resp:
                if resp["features"]:

                    for data in resp["features"]:
                        init = data["attributes"]
                        dataTemp.append(init)

                point += 50

        dtframe = pd.DataFrame(dataTemp)
        dtframe.to_csv(
            "{}/result/harian_{}.csv".format(dir_path, self.query_city.lstrip().lower())
        )

    def covidKecamatanRawan(self):
        point = 0
        url = """https://services5.arcgis.com/VS6HdKS0VfIhv8Ct/ArcGIS/rest/services/Kecamatan_Rawan_COVID19/FeatureServer/0/query?where=1%3D1+and+%22provinsi%22+%3D+%27{0}%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=true&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset={point}&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=false&quantizationParameters=&sqlFormat=standard&f=json&token="""

        for x in range(0, self.max_page):
            ex = url.format(self.query_city, point=point)

            resp = self.get_body(ex)
            if not resp:
                return None

            if resp["features"]:
                dataTemp = []
                for data in resp["features"]:
                    init = data["attributes"]
                    dataTemp.append(init)

            point += 50
        dtframe = pd.DataFrame(dataTemp)
        dtframe.to_csv(
            "{}/result/rawan_{}.csv".format(dir_path, self.query_city.lstrip().lower())
        )

    def get_body(self, *args, **kwargs):
        """Retrieve text from url. Return text as string or None if no data present """
        resp = self.safe_get(*args, **kwargs)

        if resp is not None:
            data = json.loads(resp)
            if "features" in data:
                if not data["features"]:
                    return None
                return data
            else:
                return None

    def safe_get(self, *args, **kwargs):
        while True:
            try:
                response = self.session.get(
                    timeout=self.CONNECT_TIMEOUT, *args, **kwargs
                )

                if response.status_code == 200:
                    return response.text
                else:
                    return None
            except (KeyboardInterrupt):
                raise

            except Exception as e:
                raise


def scrape(query):
    obj = Covid(query)
    obj.covidHarianProvinsi()
    obj.covidKecamatanRawan()

