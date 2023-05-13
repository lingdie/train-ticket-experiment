from datetime import datetime

import pandas as pd
from prometheus_api_client import PrometheusConnect, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime


class PromClient:
    url: str
    client: PrometheusConnect

    start_time: datetime = parse_datetime("15m")
    end_time: datetime = parse_datetime("now")
    step: str = "30s"

    def __init__(
            self,
            url,
            start_time: str,
            end_time: str,
            step: str,
    ):
        self.url = url
        self.client = PrometheusConnect(url=self.url, headers=None, disable_ssl=True)
        self.start_time = parse_datetime(start_time)
        self.end_time = parse_datetime(end_time)
        self.step = step
        return

    def query_pod_cpu(self, namespace: str):
        query = "sum(rate(container_cpu_usage_seconds_total{namespace='%s'}[3m])) by (pod) * 100" % namespace

        data = self.client.custom_query_range(
            query=query,
            start_time=self.start_time,
            end_time=self.end_time,
            step=self.step
        )

        dataframe = MetricRangeDataFrame(data). \
            reset_index().set_index(["timestamp", "pod"]).rename(columns={"value": "cpu"})
        print(dataframe)
        return dataframe

    def query_pod_mem(self, namespace: str):
        query = "sum(container_memory_working_set_bytes{namespace='%s'}) by (pod)" % namespace

        data = self.client.custom_query_range(
            query=query,
            start_time=self.start_time,
            end_time=self.end_time,
            step=self.step
        )
        dataframe = MetricRangeDataFrame(data). \
            reset_index().set_index(["timestamp", "pod"]).rename(columns={"value": "mem"})
        print(dataframe)
        return dataframe

    def query_pod_network_receive(self, namespace: str):
        query = "sum(irate(container_network_receive_packets_total{namespace='%s'}[3m])) by (pod)" \
                % namespace

        data = self.client.custom_query_range(
            query=query,
            start_time=self.start_time,
            end_time=self.end_time,
            step=self.step
        )
        dataframe = MetricRangeDataFrame(data). \
            reset_index().set_index(["timestamp", "pod"]).rename(
            columns={"value": "container_network_receive_packets_rate"})
        print(dataframe)
        return dataframe

    def query_ns(self, namespace: str):
        data = pd.concat(
            [
                self.query_pod_cpu(namespace),
                self.query_pod_mem(namespace),
                self.query_pod_network_receive(namespace)
            ],
            axis=1,
            join='inner'
        )
        return data
