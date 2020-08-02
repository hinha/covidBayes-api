import os
from sanic import Sanic
from sanic.response import json
from requestdata import scrape
from datasets import BayesCovid

app = Sanic(__name__)


@app.route("/api/v1/search", methods=["GET"])
async def search(request):
    try:
        query = request.args
        kota = query.get("kota", None)
        if not kota:
            return json({"message": "missing parameter query"}, 400)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file1 = os.path.isfile(
            dir_path + "/result/harian_{}.csv".format(kota.lstrip().lower())
        )
        file2 = os.path.isfile(
            dir_path + "/result/rawan_{}.csv".format(kota.lstrip().lower())
        )
        if not file1 and not file1:
            scrape(kota)
            if not file1 and not file1:
                return json({"message": "not valid query parameter"}, 400)

        return json({"message": "ok"})
    except Exception as e:
        print(e)
        return json({"message": "something went wrong"}, 500)


@app.route("/api/v1/data.json", methods=["GET"])
async def dataJSON(request):
    query = request.args
    try:
        kota = query.get("kota", None)
        kategori = query.get("kategori", None)
        if not kota:
            return json({"message": "missing parameter query"}, 400)

        resultOffset = query.get("resultOffset", False)
        dataTable = query.get("dataTable", None)
        dataChart = query.get("dataChart", None)
        if resultOffset:
            if kategori is None:
                kategori_default = "medium"
            else:
                kategori_default = kategori
            rowData = BayesCovid(kategori_default, kota)

            data = rowData.get_wilayah()
            if dataTable:
                return json({"data": data}, 200)

            if dataChart:
                data_chart = rowData.distribution(data)
                return json({"data": {"pie": data_chart[0], "bar": data_chart[1]}}, 200)

        return json({"data": []}, 400)
    except Exception as e:
        print(e)
        return json({"message": "something went wrong"}, 500)


# https://thevirustracker.com/free-api?countryTimeline=ID
# https://covid19.mathdro.id/api/countries/ID
# http://api.coronatracker.com/v3/analytics/newcases/country?countryCode=ID&startDate=2020-04-01&endDate=2020-05-01


app.run(host="0.0.0.0")
