from prom import PromClient

if __name__ == '__main__':
    client = PromClient(url="http://120.26.82.149:30721/", start_time="30m", end_time="now", step="10s")
    ds = client.query_ns("train-ticket")
    ds.to_csv("./data/pod.csv")
