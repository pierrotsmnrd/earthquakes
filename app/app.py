import pandas as pd
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

from earthquakes_dashboard import EarthquakesDashboard


def seismes_doc(doc):

    # load the data
    df = pd.read_csv("../data/viz/earthquakes.csv", sep=";")

    # build the dashboard
    dashboard = EarthquakesDashboard(doc=doc, df=df)

    doc.add_root(dashboard.panel().get_root())


if __name__ == "__main__":

    allowed_urls = ["127.0.0.1:80"]

    server = Server({'/seismes': seismes_doc,
                     },
                    io_loop=IOLoop(),
                    allow_websocket_origin=["*"],
                    autoreload=True
                    )

    server.start()
    server.io_loop.start()
