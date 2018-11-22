# this is for creating the tariffs and save them in the json file the json file then can be read from the API
import json
import io

AllTariffs = [{"Tariff Code": "T00001",
               "Provider": "AGL",
               "Type": "Flat_rate",
               "State": "NSW",
               "Name": "AGL Flat Rate",
               "Year": "2017/18",
               "Discount (%)": 15,
               "ProviderType": "Retailer",
               "Parameters": {"Daily":
                              {"Value": 0.924, "Unit": "$/day"},
                              "Energy":
                                  {"Value": 0.3, "Unit": "$/kWh"},
                              "FiT":
                                  {"Value": 0.1, "Unit": "$/kWh"}}},
              {"Tariff Code": "T00002",
               "Provider": "Energy Australia",
               "Type": "TOU",
               "State": "NSW",
               "Name": "Energy Australia TOU",
               "Year": "2017/18",
               "Discount (%)": 20,
               "ProviderType": "Retailer",
               "Parameters": {"Daily":
                              {"Value": 0.824, "Unit": "$/day"},
                              "Energy": {'Peak': {"Value": 0.5, "Unit": "$/kWh",
                                                  "Month": [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                                  "Weekday": True, "Weekend": True,
                                                  "TimeIntervals": {'T1': ['14:00', '20:00'],
                                                                    'T2': ['21:00', '22:00']}},
                                         'Off Peak': {"Value": 0.1, "Unit": "$/kWh",
                                                      "Month": [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                                      "Weekday": True, "Weekend": True,
                                                      "TimeIntervals": {'T1': ['00:00', '14:00'],
                                                                        'T2': ['20:00', '21:00'],
                                                                        'T3': ['22:00', '00:00']}}},
                              "FiT": {"Value": 0.1, "Unit": "$/kWh"}}}]
AllTariffs = json.dumps(AllTariffs)
# to_unicode = str

with io.open('AllTariffs.json', 'w', encoding='utf8') as outfile:
    outfile.write(str(AllTariffs))
