import os
import pandas as pd
import numpy as np
import operator
from collections import Counter
from functools import reduce
from math import log, log10


dir_path = os.path.dirname(os.path.realpath(__file__))


class BayesCovid:
    def __init__(self, kategoriRawan, province):
        self.kategoriRawan = kategoriRawan
        self.datasetsHarian = pd.read_csv(
            "{}/result/harian_{}.csv".format(dir_path, province.lstrip().lower())
        )
        self.datasetsRawan = pd.read_csv(
            "{}/result/rawan_{}.csv".format(dir_path, province.lstrip().lower())
        )
        self.labelRow = []

    def get_wilayah(self):
        if self.kategoriRawan == "high":
            rawan = 1000
            nSembuh = 500
            nDeath = 100
        elif self.kategoriRawan == "medium":
            rawan = 500
            nSembuh = 200
            nDeath = 50
        else:
            rawan = 100
            nSembuh = 100
            nDeath = 10

        countConfirmed = self.datasetsHarian[
            self.datasetsHarian["Penambahan_Harian_Kasus_Terkonf"] >= rawan
        ].count()

        countSembuh = self.datasetsHarian[
            self.datasetsHarian["Penambahan_Harian_Kasus_Sembuh"] <= nSembuh
        ].count()

        countDeath = self.datasetsHarian[
            self.datasetsHarian["Penambahan_Harian_Kasus_Meningg"] >= nDeath
        ].count()
        Active = self.datasetsHarian["Kasus_Aktif_Akumulatif"].sum()

        tempRows = []
        for row in self.datasetsRawan.itertuples():
            tempRows.append(row.kabupaten)

        sam_bad = self.datasetsRawan[
            (self.datasetsRawan["kategori"] == self.kategoriRawan)
        ]

        unique_wilayah = list(set(tempRows))

        total = 0
        dicttemp = []
        for row in list(set(tempRows)):
            length = len(sam_bad[sam_bad["kabupaten"] == row])

            data = sam_bad[sam_bad["kabupaten"] == row]
            data.drop("FID", axis=1, inplace=True)

            dlist = []
            for cdata in data.itertuples():
                dlist.append(
                    {
                        "kecamatan": cdata.kecamatan,
                        "lat": cdata.lat,
                        "long": cdata.lon,
                        "kategori": cdata.kategori,
                    }
                )

            dicttemp.append(
                {"length": length, "kota": row, "data": dlist,}
            )
            total += length

        resultJSON = []
        for dtitem in dicttemp:
            if dtitem["length"] != 0:
                result = dtitem["length"] / total
            else:
                result = 0

            if int(total) == 0:
                total = 1

            result_countConfirmed = 0
            if int(countConfirmed.values[0]) != 0:
                result_countConfirmed = int(countConfirmed.values[0]) / total

            result_countSembuh = 0
            if int(countSembuh.values[0]) != 0:
                result_countSembuh = countSembuh.values[0] / total

            result_countDeath = 0
            if int(countDeath.values[0]) != 0:
                result_countDeath = countDeath.values[0] / total

            result_active = 0
            if int(Active) != 0 or int(total) != 0:
                result_active = Active / total
            dtitem.update(
                {
                    "terkonfirmasi": result_countConfirmed,
                    "sembuh": result_countSembuh,
                    "kematian": result_countDeath,
                    "kasus_aktif": result_active,
                    "result": result,
                }
            )

            onlist = [
                result,
                result_countConfirmed,
                result_countSembuh,
                result_countDeath,
                result_active,
            ]
            to_logs = []
            for dtlist in onlist:
                dtlist = "%.3f".format(dtlist) % dtlist
                if float(dtlist) == 0.0:
                    dtlist = 0.001

                to_logs.append(float(dtlist))

            conv_logs = []
            for dtlist in to_logs:
                xlog = log10(dtlist)
                conv_logs.append(xlog)

            output = sum(conv_logs)
            dtitem.update({"output": output})
            resultJSON.append(dtitem)

        return resultJSON

    def distribution(self, result_data: list):

        kategori = []
        for dt in self.datasetsRawan.itertuples():
            if dt.kategori == "high":
                kategori.append(dt.kategori)
            elif dt.kategori == "medium":
                kategori.append(dt.kategori)
            else:
                kategori.append(dt.kategori)

        # Total kategori
        sen = Counter(kategori)
        pieChartKategori = {
            "tinggi": {
                "count": sen["high"],
                "percentage": round(sen["high"] * 100 / len(kategori), 2),
            },
            "sedang": {
                "count": sen["medium"],
                "percentage": round(sen["medium"] * 100 / len(kategori), 2),
            },
            "rendah": {
                "count": sen["low"],
                "percentage": round(sen["low"] * 100 / len(kategori), 2),
            },
        }

        barChart = []
        for x in result_data:
            barChart.append(
                {
                    "kota": x["kota"],
                    "value": x["terkonfirmasi"]
                    + x["sembuh"]
                    + x["result"]
                    + x["kematian"],
                }
            )

        return pieChartKategori, barChart

    def filter_rawan(self):
        if self.kategoriRawan == "high":
            rawan = 1000
            nSembuh = 500
            nDeath = 100
        elif self.kategoriRawan == "medium":
            rawan = 500
            nSembuh = 200
            nDeath = 50
        else:
            rawan = 100
            nSembuh = 100
            nDeath = 10

        countConfirmed = self.datasetsHarian[
            self.datasetsHarian["Penambahan_Harian_Kasus_Terkonf"] >= rawan
        ].count()
        countSembuh = self.datasetsHarian[
            self.datasetsHarian["Penambahan_Harian_Kasus_Sembuh"] <= nSembuh
        ].count()
        countDeath = self.datasetsHarian[
            self.datasetsHarian["Penambahan_Harian_Kasus_Meningg"] >= nDeath
        ].count()

        tempRows = []
        for row in self.datasetsRawan.itertuples():
            tempRows.append(row.kabupaten)

        sam_bad = self.datasetsRawan[
            (self.datasetsRawan["kategori"] == self.kategoriRawan)
        ]

        datum = []
        for row in list(set(tempRows)):
            vars1 = (
                sam_bad.groupby(["FID", "kecamatan", "provinsi", "lat", "lon"])
                .agg({"kategori": len, "kabupaten": lambda x: x == row})
                .reset_index()
            )
            datum.append(vars1)

        datum = pd.concat(datum)
        if datum.shape[0] == 0:
            return 0

        label = datum[datum["kabupaten"] == True]
        for row in label.values.tolist():
            self.labelRow.append(row)

        rate = datum["kabupaten"].count()
        kabupaten_x = datum[datum["kabupaten"] == True].sum()
        # print()
        # print(label)
        # print()
        # print(kabupaten_x)

        result_kabupaten_x = kabupaten_x["kabupaten"] / rate
        result_countConfirmed = countConfirmed.values[0] / rate
        result_countSembuh = countSembuh.values[0] / rate
        result_countDeath = countDeath.values[0] / rate
        # print(kabupaten_x)
        # print(result_kabupaten_x, rate)
        # print(result_countConfirmed)
        # print(result_countSembuh)
        # print(result_countDeath)

        onlist = [
            result_kabupaten_x,
            result_countConfirmed,
            result_countSembuh,
            result_countDeath,
        ]
        to_logs = []
        for dtlist in onlist:
            dtlist = "%.3f".format(dtlist) % dtlist
            if float(dtlist) == 0.0:
                dtlist = 0.001

            to_logs.append(float(dtlist))

        conv_logs = []
        for dtlist in to_logs:
            xlog = log10(dtlist)
            conv_logs.append(xlog)
        return sum(conv_logs)


# obj = BayesCovid("low", "DKI Jakarta")
# data = obj.get_wilayah()
# obj.distribution(data)


# obj2 = BayesCovid("low", "Aceh")
# obj2.filter_rawan()
# obj2.label()
# bb = [a, b]
# bb.sort()
# print(bb)
