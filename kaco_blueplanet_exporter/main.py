import time
from datetime import datetime

from prometheus_client.core import (
    GaugeMetricFamily,
    REGISTRY,
    StateSetMetricFamily,
)
from prometheus_client.exposition import start_http_server
from prometheus_client.gc_collector import GC_COLLECTOR
from prometheus_client.platform_collector import PLATFORM_COLLECTOR
from prometheus_client.process_collector import PROCESS_COLLECTOR

from kaco_blueplanet_exporter.config import get_config
from kaco_blueplanet_exporter.query import get_solar_data
from kaco_blueplanet_exporter.states import states


class CustomCollector(object):
    url = get_config("url_to_scrape")
    username = get_config("http_basic_username")
    password = get_config("http_basic_password")

    def collect(self):
        data = get_solar_data(self.url, self.username, self.password)

        g = GaugeMetricFamily(
            "ac_power_generated_kw",
            "The amount of power sent to the grid",
            value=data["generator_ac_power_kW"],
        )
        yield g

        g = GaugeMetricFamily(
            "dc_power_generated_kw",
            "The amount of power generated",
            value=data["generator_dc_power_kW"],
        )
        yield g

        g = GaugeMetricFamily(
            "temperature",
            "The temperature of the inverter unit",
            value=data["temperature"],
        )
        yield g

        g = GaugeMetricFamily(
            "datetime",
            "The datetime the record was taken",
            value=int(datetime.now().timestamp()),
        )
        yield g

        ss = {
            states[sta]: True if data["status"] == states[sta] else False
            for sta in states
        }
        s = StateSetMetricFamily("state", "The state of the inverter", ss)
        yield s
        #
        # c = CounterMetricFamily("HttpRequests", "Help text", labels=["app"])
        # c.add_metric(["example"], 2000)
        # yield c


if __name__ == "__main__":
    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(GC_COLLECTOR)

    REGISTRY.register(CustomCollector())
    start_http_server(int(get_config("local_port")))
    while True:
        time.sleep(1)


#
# url_to_scrape = "https://solar.d.sawrc.com/realtime.csv"
# auth = httpx.BasicAuth("root", "shimopa55l!nk")
#
# "Time;Udc1[V];Idc1[A];Pdc1[W];Udc2[V];Idc2[A];Pdc2[W];Uac1[V];Iac1[A];Uac2[V];Iac2[A];Uac3[V];Iac3[A];Pdc[W];Pac[W];Tsys[C]"
#
# output_data = httpx.get(url_to_scrape, auth=auth)
#
# data = output_data.content.decode("utf-8").split(";")
#
#
# acCount = 3
# dcCount = 2
# length = 14
# # int(data[0]) * 1000
#
# date = datetime.utcfromtimestamp(int(data[0]))  # wrong? #0
#
# pow2 = []
#
# for i in range(1, 3):  # 1, 2, 6, 7
#     p = float(data[i])
#     r = (
#         (p / (65535.0 / 1600.0))
#         * ((float(data[i + 2 + 3])) / (65535.0 / 200.0))
#         / 1000.0
#     )
#     pow2.append(r)
#
# kw_dc_1 = pow2[0]
# kw_dc_2 = pow2[1]
# current_kw_dc = sum(pow2)
#
# current_kw_ac = float(data[11]) / (65535.0 / 100000.0) / 1000.0  # 11
#
# state = states[int(data[13])]  # 13
#
# data_dict = {
#     "status": state,
#     "status_code": data[13],
#     "generator_ac_power_kW": current_kw_ac,
#     "generator_dc_power_kW": current_kw_dc,
#     "gen_dc_1": kw_dc_1,
#     "gen_dc_2": kw_dc_2,
#
# }
# pass
# # var fields = data.split(';');
# # var  tDate = new Date(fields[0] * 1000);
# #
# # var  tmpMonth = (tDate.getUTCMonth() + 1);
# # var  tmpAMPM = 'AM';
# #
# # var  tmpHours24 = (tDate.getUTCHours());
# # var  tmpHours12 = tmpHours24;
# #
# # if ($('#rtDbgMsg').attr('checked'))
# # logAddMsg("->: " + data);
# #
# # if (tmpHours12 > 12)
# #     {
# #         tmpHours12 = tmpHours12 - 12;
# #     tmpAMPM = 'PM';
# #     }
# #
# #     var
# #     dateString = datumsFormat.replace('d', String(tDate.getUTCDate()).pad(2, '0'))
# #     .replace('m', String(tmpMonth).pad(2, '0'))
# #     .replace('y', tDate.getUTCFullYear())
# #     .replace('h', String(tmpHours24).pad(2, '0'))
# #     .replace('H', String(tmpHours12).pad(2, '0'))
# #     .replace('i', String(tDate.getUTCMinutes()).pad(2, '0'))
# #     .replace('s', String(tDate.getUTCSeconds()).pad(2, '0'))
# #     .replace('n', tmpAMPM);
# #     $('#today').html(dateString);
# # for (var t = 1; t <= this.dcCount; t++)
# #         {
# #             gen.push(roundCommaSeparated(((fields[t] / (65535.0 / 1600.0)) * ((fields[t] + this.dcCount + this.acCount]) / (65535.0 / 200.0)) / 1000.0), 2));
# #         }
# #
# #         gen = ["0,00", "0,00"]
# #         $('#nowValueGen').html(gen.join(' kW<br/>') + ' kW');
# #         # raund x , ot 2 decimal places
# #         $('#nowValueIn').html(roundCommaSeparated((fields[fields.length - 3] / (65535.0 / 100000.0) / 1000.0), 2) + ' kW');
# #
# #         var st = fields[fields.length - 1].trim();
# #
# #         if (this.state[st])
# #         {
# #             $('#nowValueState').html(this.state[st]);
# #         }
# #         else
# #         {
# #             $('#nowValueState').html(unbekannt);
# #         }
