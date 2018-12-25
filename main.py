from spyre import server

import pandas as pd
import json
import requests
import re
import os

provinces = {1: "Vinnytsia", 13: "Mylolaevskaya", 2: "Volynskaya", 14: "Odessa", 3: "Dnepropetrovsk", 15: "Poltavska",
             4: "Donetsk", 16: "Rivne", 5: "Zhytomyr", 17: "Sumy", 6: "Transcarpathian", 18: "Ternopil",
             7: "Zaporizka", 19: "Kharkiv", 8: "Ivano-Frankivsk", 20: "Kherson", 9: "Kyiv",
             21: "Khmelnitsky", 10: "Kirovogradskaya", 22: "Cherkassy", 11: "Luhansk", 23: "Chernivtsi",
             12: "Lvivskaya", 24: "Chernigivska", 25: "Republic of Crimea"}


class WebApp(server.App):
    title = "Analys"

    inputs = [
        {
            "type": 'dropdown',
            "label": 'Take a TS',
            "options": [{"label": "VCI", "value": "VCI"},
                        {"label": "TCI", "value": "TCI"},
                        {"label": "VHI", "value": "VHI"}],
            "key": 'TS',
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "label": 'Take a province',
            "options": [{"label": name, "value": id} for id, name in provinces.items()],
            "key": 'Province',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": 'From year',
            "value": '2018',
            "key": 'from_year',
            "action_id": "refresh",
        },
        {
            "type": 'text',
            "label": 'To year',
            "value": '2018',
            "key": 'to_year',
            "action_id": "refresh",
        }
    ]

    controls = [{"type": "hidden",
                 "id": "update_data"}]

    tabs = ["Plot", "Table"]

    outputs = [{"type": "plot",
                "id": "plot",
                "control_id": "update_data",
                "tab": "Plot"},
               {"type": "table",
                "id": "table_id",
                "control_id": "update_data",
                "tab": "Table",
                "on_page_load": True}]

    def getData(self, params):
        provinceID = params['Province']
        from_year = params['from_year']
        to_year = params['to_year']
        api_url = 'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_provinceData.php?country=UKR&provinceID={}&year1={}&year2={}&type=Mean'.format(
            provinceID, from_year, to_year)
        vhiUrl = requests.get(api_url)
        normData = []
        data = str(vhiUrl.content).split('\n')[1:-1]

        for j in range(len(data)):
            data[j] = re.sub(',', ' ', data[j])
            data[j] = data[j].split(' ')
            data[j] = list(filter(lambda x: x != '', data[j]))
            data[j].insert(2, provinceID)
            data[j][0:3] = list(map(int, data[j][0:3]))
            data[j][3:] = list(map(float, data[j][3:]))
            normData.append(data[j])
        df = pd.DataFrame(normData, columns=['Year', 'Week', 'ProvinceID', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI'])
        return df

    def getPlot(self, params):
        datatype = params['TS']
        df = self.getData(params)
        plt_obj = df.plot(x='Week', y=datatype)
        plt_obj.set_ylabel(datatype)
        fig = plt_obj.get_figure()
        return fig


app = WebApp()
app.launch(port=8007)