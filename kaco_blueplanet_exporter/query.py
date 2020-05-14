import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from typing import Dict
from kaco_blueplanet_exporter.states import states

session = requests.Session()

number_of_solar_strings = 2
number_of_ac_phases = 3


def get_solar_data(url: str, username: str, password: str) -> Dict:
    auth = (
        requests.auth.HTTPBasicAuth(username, password)
        if (username and password)
        else None
    )
    output_data = session.get(url, auth=auth)

    data = output_data.content.decode("utf-8").split(";")

    date = datetime.utcfromtimestamp(int(data[0]))  # 0

    dc_power = []

    for i in range(1, number_of_solar_strings + 1):  # 1, 2, 6, 7
        p = float(data[i])
        r = (
            (p / (65535.0 / 1600.0))
            * (
                (float(data[i + number_of_solar_strings + number_of_ac_phases]))
                / (65535.0 / 200.0)
            )
            / 1000.0
        )
        dc_power.append(r)

    current_kw_dc = sum(dc_power)

    current_kw_ac = float(data[11]) / (65535.0 / 100000.0) / 1000.0  # 11
    temp = float(data[12]) / 100

    state = states[int(data[13])]  # 13

    data_dict = {
        "date": date.isoformat(),
        "status": state,
        "status_code": int(data[13]),
        "generator_ac_power_kW": current_kw_ac,
        "generator_dc_power_kW": current_kw_dc,
        "temperature": temp,
    }
    for i in range(number_of_solar_strings):
        data_dict[f"gen_dc_{i+1}"] = dc_power[i]
    return data_dict
