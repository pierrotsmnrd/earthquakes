from datetime import datetime as dt

# Feature Engineering
import pandas as pd
from datashader.utils import lnglat_to_meters
import numpy as np

import os

# Holoviz suite
import param
import colorcet
import param as pm
import holoviews as hv
# import hvplot.pandas
import panel as pn
import datashader as ds
import geoviews as gv

import json

from bokeh.models import HoverTool, NumeralTickFormatter

# from holoviews.element import tiles as hvts
# from holoviews.operation.datashader import rasterize, shade, spread
# from collections import OrderedDict as odict

import gettext
# will be used as translation function :
_ = None

hv.extension('bokeh', logo=False)


def legend():
    colormap = colorcet.fire[::-1]

    scatter = hv.Points([{"mag": i, "y": 0, "x": i} for i in range(0, 10)],
                        vdims=['x', 'mag']).opts(cmap=colormap,
                                                 clim=(0, 9),
                                                 # tools=['hover'],
                                                 fill_color='mag',
                                                 line_color='lightgray',
                                                 size=hv.dim('mag')*2+5,
                                                 logz=False,
                                                 # alpha=128,
                                                 # width=200,
                                                 height=175,
                                                 ylim=(-1, 0.5),
                                                 xaxis=None,
                                                 yaxis=None,
                                                 toolbar=None,
                                                 colorbar=True,
                                                 colorbar_position="bottom",
                                                 colorbar_opts={
                                                     'bar_line_alpha': 1,
                                                     'border_line_alpha': 0,
                                                     'scale_alpha': 1,
                                                     'major_tick_line_alpha': 0,
                                                     'major_label_text_alpha': 0,
                                                 },
                                                 )

    labels = hv.Labels([{"mag": i, ("x", "y"): (i, -0.5)} for i in range(0, 10)],
                       ['x', 'y'],
                       'mag')

    return (scatter * labels)


def details_block(lang):

    with open(f"../data/viz/details_{lang}.md") as f:
        details = f.read()

    return pn.pane.Markdown(details)


def get_earthquakes_df():

    input_dir = '../data/viz/'
    csvs = [f for f in os.listdir('../data/viz/') if f.endswith(".csv")]

    df = None
    for csv in csvs:
        df_decade = pd.read_csv(f"{input_dir}{csv}", sep=';') \
            .astype({'time': 'datetime64[ns]'})

        if df is None:
            df = df_decade
        else:
            df = pd.concat([df, df_decade]).reset_index()

    # remove erroneous data
    df = df[(~df['mag'].isna()) & (df['mag'] > 0)]

    # some feature engineering

    # converts  lat/lon to y/x values, needed for the map
    x, y = lnglat_to_meters(df.lon, df.lat)
    df = df.join([pd.DataFrame({'easting': x}), pd.DataFrame({'northing': y})])

    # from datetime to day as a str
    df['day'] = df.time.astype('str').str.slice(0, 10)

    ''' For later
    # week in format YYYY-WW
    df['week'] = df.time.apply(
        lambda x:  '{}-{:02}'.format(x.isocalendar().year, x.isocalendar().week))
    '''

    # Keeping only cols needed for the viz
    cols = ['lat', 'lon',
            'easting', 'northing',
            'depth', 'mag',
            'day', 'time',  # 'week',
            ]
    df = df[cols]

    # print("erroneous rows left : ", len(df[df['mag'] <= 0]))
    # print("total : ", len(df))

    return df


''' For later
def histo_rect(all_mags, colormap):
    ratio = 2
    mags_bins = np.histogram(all_mags,
                             bins=[i/ratio for i in range(10*ratio)],
                             range=(0, 10),
                             density=False,  # normed=False
                             )

    data = list(zip(mags_bins[1], mags_bins[0]))

    ylim_max = max([y for (_, y) in data])

    rects_data = [{
        "x0": x,
        "y0": 1,
        "x1": x+(1/ratio),
        "y1": y+1,
        "count": y
    } for (x, y) in data if y > 0]

    tooltips = [
        ('Magnitude range', '@x0 - @x1'),
        ('Count', '@count'),
    ]
    hover = HoverTool(tooltips=tooltips)

    rects = hv.Rectangles(rects_data, vdims='count').opts(
        cmap=colormap,
        color='x1',
        logy=True,
        clim=(0.01, 10),
        xlim=(0, 10),
        ylim=(1, ylim_max*5),
        tools=[hover],
        toolbar=None,
        height=300,
        xlabel='magnitude',
        ylabel='Total count of earthquakes'
    )
    return rects
'''


class EarthquakesApp(param.Parameterized):

    date_range = param.DateRange((dt.strptime('2000-01-01', '%Y-%m-%d'),
                                  dt.strptime('2020-12-31', '%Y-%m-%d')),
                                 bounds=(dt.strptime('2000-01-01', '%Y-%m-%d'),
                                         dt.strptime('2020-12-31', '%Y-%m-%d'))
                                 )
    mag_range = param.Range(bounds=(0, 10))

    colormap = colorcet.fire[::-16]

    background = hv.DynamicMap(gv.tile_sources.CartoLight.opts(framewise=True))

    def __init__(self, lang_id, df=None, ** params):

        # Translation
        global _
        self.lang_id = lang_id if lang_id in ["en", "fr"] else "en"
        translation = gettext.translation(
            'base', localedir='../locales', languages=[self.lang_id])
        translation.install()
        _ = translation.gettext

        super(EarthquakesApp, self).__init__(**params)

        # Data
        if df is None:
            self.df = get_earthquakes_df()
        else:
            self.df = df

        # Params widgets

        # update the bounds of date_range
        self.param.date_range.bounds = (dt.strptime(self.df.day.min(), '%Y-%m-%d'),
                                        dt.strptime(self.df.day.max(), '%Y-%m-%d'))
        self.date_range = self.param.date_range.bounds

        self.date_range_widget = pn.widgets.DateRangeSlider.from_param(
            self.param.date_range,
            name=_('Date Range'))

        self.mag_range_widget = pn.widgets.RangeSlider.from_param(
            self.param.mag_range,
            start=0,
            end=10,
            step=0.5,
            value=(0, 10),
            name=('Magnitude'))

        languages_dict = {'fr': '🇫🇷', 'en': '🇬🇧/🇺🇸'}
        options = list(languages_dict.values())
        self.language_selector = pn.widgets.Select(options=options,
                                                   value=options[0] if self.lang_id == 'fr' else options[1],
                                                   size=1,
                                                   width=80)

        self.language_selector.jscallback(value='''
            window.location = location.href.split("?")[0] + "?lg=" + languages_dict[select.value] 
        ''', args={"select": self.language_selector,
                   "languages_dict": {v: k for (k, v) in languages_dict.items()}
                   }
        )

        # Dataviz elements
        self.points = hv.Points(self.df,
                                kdims=['easting', 'northing'],
                                vdims=[hv.Dimension('mag', range=(0, 9)),
                                       'lat',
                                       'lon',
                                       'depth',
                                       'time',
                                       'day'],
                                ).sort(by='mag', reverse=True)

        self.xy_stream = hv.streams.RangeXY(source=self.points)

        # self.histo_bins = [[], []]
        self.filtered_count = len(self.points)
        self.filtered = self.points.apply(self.filter_points,
                                          streams=[self.xy_stream],
                                          date_range=self.param.date_range,
                                          mag_range=self.param.mag_range
                                          )

        self.hover = self.filtered.apply(self.hover_points)
        self.shaded = hv.operation.datashader.datashade(self.filtered,
                                                        streams=[
                                                            self.xy_stream],
                                                        aggregator=ds.mean(
                                                            'mag'),
                                                        cmap=self.colormap,
                                                        clims=(0, 10),
                                                        cnorm='log',
                                                        alpha=128)

        tooltips = [(_('Lat/Lon'),              '@lat / @lon'),
                    (_('Depth'),                '@depth{safe} km'),
                    (_('Magnitude'),            '@mag{safe}'),
                    (_('Date and time (UTC)'),  '@time{%Y-%m-%d %H:%M:%S}')]

        hovertool = HoverTool(tooltips=tooltips,
                              formatters={"@lat": 'printf', '@time': 'datetime'})

        points_opts = hv.opts.Points(tools=[hovertool],
                                     cmap=self.colormap,
                                     clim=(0, 9),
                                     fill_color='mag',
                                     line_color='lightgray',
                                     size=hv.dim('mag')*2+5,
                                     logz=False,
                                     alpha=128,)

        self.main_map = (self.shaded * self.background * self.hover).opts(width=1000,
                                                                          height=600,
                                                                          xaxis=None,
                                                                          yaxis=None,
                                                                          toolbar='right',
                                                                          tools=[
                                                                              'pan', 'hover', 'wheel_zoom', 'reset'],
                                                                          active_tools=[
                                                                              "pan", "wheel_zoom"],
                                                                          ).opts(points_opts)

    def filter_points(self, points, x_range, y_range, date_range=None, mag_range=None):

        subset = points
        if date_range is not None:
            subset = points.select(time=date_range)

        if mag_range is not None:
            subset = subset.select(mag=mag_range)

        if x_range is None or y_range is None:
            return subset

        result = subset[x_range, y_range]

        self.filtered_count = len(result)

        return result

    def hover_points(self, points, max_items=1000):
        if len(points) > max_items:
            return points.iloc[:max_items, :]
        return points

    @param.depends("date_range_widget", "mag_range_widget")
    def total_count(self):
        result = f'''*{ _('Total count of earthquakes')}* : **{len(self.points)}**<br />'''

        if self.filtered_count != len(self.points):
            result += f'''*{_('displayed')}* : {self.filtered_count}'''

        return pn.pane.Markdown(result)

    '''
    @param.depends("date_range_widget", "mag_range_widget")
    def histo(self):
        try:
            all_mags = self.filtered.dimension_values('mag')
        except:
            return pn.pane.Markdown("loading")

        return histo_rect(all_mags, self.colormap)
    '''

    @param.depends("date_range_widget", "mag_range_widget")
    def count_timeline(self):

        try:
            count_df = self.filtered.dframe(
                dimensions=['mag', 'day']).groupby('day').count()
        except:
            return pn.pane.Markdown("loading")

        return hv.Scatter(count_df).opts(width=800, logy=True)

    def view(self):
        return pn.Column(

            pn.Row(
                pn.pane.Markdown(
                    f"# { _('Earthquakes since year 2000') }",
                    sizing_mode='stretch_width',
                    #style={'color': 'white'}
                ),
                pn.layout.spacer.HSpacer(),
                self.language_selector,

                background='#f0f0f0'
            ),

            pn.Row(
                pn.Column(

                    pn.layout.spacer.Spacer(height=10),
                    pn.Column(
                        self.date_range_widget,
                        self.mag_range_widget,
                        legend(),
                    ),

                    pn.layout.spacer.Spacer(height=10),

                    pn.Column(
                        # self.total_count,
                        # pn.layout.spacer.VSpacer(height=20),
                        details_block(self.lang_id),
                    ),

                ),

                self.main_map,


            ),

        )
