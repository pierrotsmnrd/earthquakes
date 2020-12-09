from datetime import datetime
import json

import pandas as pd
import panel as pn
import geoviews as gv
from functools import partial
import param

import holoviews as hv
from holoviews.streams import Pipe
from bokeh.models import HoverTool
from geoviews import dim

from pdb import set_trace as bp

gv.extension('bokeh')
hv.extension('bokeh')
pn.extension()


class EarthquakesDashboard(param.Parameterized):

    def __init__(self, doc, df, **params):
        super().__init__(**params)

        # https://panel.holoviz.org/user_guide/Param.html
        # print(pn.state.location.query_params)

        self.current_doc = doc
        self.df = df

        self.data_stream = Pipe({'earthquakes': [], 'distrib': []})

        self.full_app = None
        self.layout = None

        self.df_cities = pd.read_json("../data/viz/cities.json")

        with open("../data/viz/zooms.json", "r") as f:
            self.zooms = json.loads(f.read())

        self.cmap = 'plasma'  # 'viridis'  # 'plasma'
        self.scale_factor = 2
        self.width = 400 * self.scale_factor
        self.height = 400 * self.scale_factor

        self.mag_min = self.df["mag"].min()
        self.mag_max = self.df["mag"].max()

        # Bounding box, to restrict to earthquakes in an area
        # It's stored in zooms.json as : top left coord, bottom right cood
        # i.e : max_lat, min_lon, min_lat, max_lon
        self.bbox = None

        self.framewise = True

        # UI
        # plots
        self.main_plot = None

        # other UI elements
        self.build_ui_elements()

        self.reload_earthquakes_map()

    def build_ui_elements(self):

        # Background selector
        self.background_selector = pn.widgets.Select(
            name='Fond de carte', options=['Sombre', 'Clair', 'Relief'])

        self.background_selector.param.watch(
            self.reload_earthquakes_map, ['value'], onlychanged=True)

        # Date range selector
        date_start = datetime.strptime(self.df["time"].min().split("T")[
            0], "%Y-%m-%d").date()
        date_end = datetime.strptime(self.df["time"].max().split("T")[
            0], "%Y-%m-%d").date()

        self.date_slider = pn.widgets.DateRangeSlider(
            name='Période',
            start=date_start,
            end=date_end,
            value=(date_start + (date_end - date_start) / 2, date_end),
            bar_color="#0000FF"
        )
        self.date_slider.param.watch(
            self.reload_earthquakes_map, ['value'], onlychanged=True)

        # Magnitude range
        self.mag_slider = pn.widgets.RangeSlider(
            name='Magnitude',
            start=self.mag_min,
            end=self.mag_max,
            value=(3, self.mag_max),
            bar_color="#0000FF"
        )
        self.mag_slider.param.watch(
            self.reload_earthquakes_map, ['value'], onlychanged=True)

        self.zooms_selector = pn.widgets.Select(
            name='Zoom sur des périodes et zones : ',
            options=['Aucun'] + list(self.zooms.keys())
        )
        self.zooms_selector.param.watch(
            self.reload_earthquakes_map, ['value'], onlychanged=True)

    def earthquakes_data(self):

        df_time_start = self.date_slider.value[0].strftime("%Y-%m-%d")
        df_time_end = self.date_slider.value[1].strftime("%Y-%m-%d")

        filter_dt = (self.df['time'] >= df_time_start) & (
            self.df['time'] <= df_time_end)

        filter_mag = (self.df['mag'] >= self.mag_slider.value[0]) & (
            (self.df['mag'] <= self.mag_slider.value[1]))

        df_selection = self.df[filter_dt & filter_mag]

        if self.bbox is not None:
            max_lat, min_lon, min_lat, max_lon = self.bbox

            filter_lat = df_selection["lat"].between(min_lat, max_lat)
            filter_lon = df_selection["lon"].between(min_lon, max_lon)
            df_selection = df_selection[filter_lat & filter_lon]

        distrib = df_selection['mag'].value_counts(bins=12, sort=False)

        return {"earthquakes": df_selection, "distrib": distrib}

    def background_plot(self, data):

        if self.background_selector.value == "Relief":
            background = gv.tile_sources.EsriTerrain
        elif self.background_selector.value == "Clair":
            background = gv.tile_sources.CartoLight
        else:
            background = gv.tile_sources.CartoMidnight

        background = background.opts(width=self.width,
                                     height=self.height,
                                     framewise=self.framewise)
        # if self.bbox is not None:
        #    max_lat, min_lon, min_lat, max_lon = self.bbox
        #    background = background.opts(xlim=(min_lon, max_lon),
        #                                 ylim=(min_lat, max_lat),)

        self.background = background

        return background

    def cities_plot(self):

        if self.background_selector.value == "Sombre":
            color = "white"
        else:
            color = "black"

        cities_points = gv.Points(self.df_cities, ['lon', 'lat'], ['name'])

        cities_label = gv.Labels(cities_points).opts(
            text_font_size='8pt',
            text_color=color,
            text_align='left',
            xoffset=5000,
            yoffset=-5000
        )
        cities_dots = gv.Points(cities_points).opts(
            size=5,
            color=color,
        )

        return (cities_dots*cities_label).opts(framewise=self.framewise,)

    def earthquakes_plot(self, data):

        print(len(data["earthquakes"]), " earthquakes")
        earthquakes_points = gv.Points(data["earthquakes"],
                                       ['lon', 'lat'], ['mag', 'depth', 'time']
                                       )

        tooltips = [
            ('Latitude', '@lat'),
            ('Longitude', '@lon'),
            ('Profondeur', '@depth{safe} km'),
            ('Magnitude', '@mag{safe}'),
            ('Date et heure (UTC)', '@time{%Y-%m-%d %H:%M:%S}'),
        ]
        hover = HoverTool(tooltips=tooltips,
                          formatters={"@lat": 'printf', '@time': 'datetime'})

        earthquakes_plot = earthquakes_points.opts(size=dim('mag')*5,  # fixed size : 10
                                                   fill_color='mag',
                                                   cmap=self.cmap,
                                                   width=self.width,
                                                   height=self.height,
                                                   global_extent=False,
                                                   tools=[hover],
                                                   framewise=self.framewise,
                                                   xlabel="Longitude",
                                                   ylabel="Lattitude",
                                                   colorbar=True
                                                   )

        return earthquakes_plot

    def distrib_block(self, data):

        if isinstance(data['distrib'], list):
            return hv.Histogram(([], [])).opts(xlim=(self.mag_min, self.mag_max),
                                               ylim=(0, 500),
                                               framewise=self.framewise,
                                               toolbar=None
                                               )

        edges = data['distrib'].keys().values
        edges = [e.left for e in edges] + [edges[-1].right]

        ylim = max(data['distrib'].values) * 1.1

        return hv.Histogram((edges, data['distrib'].values))\
            .opts(xlim=(self.mag_min, self.mag_max),
                  ylim=(0, ylim),
                  xlabel="Magnitude",
                  ylabel="Occurences",
                  framewise=self.framewise,
                  toolbar=None,
                  )

    def details_block(self):

        with open("../data/viz/details.md") as f:
            details = f.read()

        return pn.pane.Markdown(details)

    def build_layout(self):

        background_plot = hv.DynamicMap(self.background_plot,
                                        streams=[self.data_stream])

        earthquakes_plot = hv.DynamicMap(self.earthquakes_plot,
                                         streams=[self.data_stream])

        distrib_block = hv.DynamicMap(self.distrib_block,
                                      streams=[self.data_stream])

        self.main_plot = (earthquakes_plot *
                          background_plot *
                          self.cities_plot()
                          ).opts(toolbar="above", active_tools=["pan", "wheel_zoom"],  framewise=self.framewise)

        result = pn.Row(
            pn.Column(self.main_plot),
            pn.Column(pn.Spacer(height=20),
                      self.background_selector,
                      self.date_slider,
                      self.mag_slider,
                      pn.Spacer(height=20),
                      distrib_block,
                      pn.Spacer(height=20),
                      self.zooms_selector,
                      self.details_block()
                      )

        )

        self.layout = result
        return result

    def reload_layout(self):
        self.full_app[1] = self.build_layout()

    def reload_earthquakes_map(self, event=None):

        if event is not None:

            if event.obj == self.background_selector:
                self.current_doc.add_next_tick_callback(self.reload_layout)
                return

            elif event.obj == self.zooms_selector:

                if self.zooms_selector.value == "Aucun":
                    self.bbox = None
                    self.mag_slider.value = (3, 5)
                    self.date_slider.value = (
                        self.date_slider.start,  self.date_slider.end)

                else:
                    zoom = self.zooms[self.zooms_selector.value]

                    self.bbox = zoom['bbox']
                    self.date_slider.value = (datetime.strptime(zoom["start"], "%Y-%m-%d"),
                                              datetime.strptime(zoom["end"], "%Y-%m-%d"))

                    self.mag_slider.value = (self.mag_min, self.mag_max)

                return

        self.current_doc.add_next_tick_callback(
            partial(self.data_stream.send, self.earthquakes_data()))

    def panel(self):
        """display the full app"""

        self.build_layout()

        title = pn.pane.Markdown(
            "## Séismes autour de Strasbourg depuis 2000", width=self.width)

        self.full_app = pn.panel(
            pn.Column(
                pn.Row(title, pn.Spacer(width=200)),
                self.layout
            ))

        return self.full_app
