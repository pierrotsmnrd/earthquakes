import urllib.request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os


def download_data(url, output_filepath):

    print("downloading", url)
    response = urllib.request.urlopen(url)

    data = response.read().decode('utf-8')

    print("Writing to", output_filepath, "\n")
    with open(output_filepath, "w") as f:
        f.write(data)


if __name__ == "__main__":

    output_dir = "../data/json"

    # Example URL : all earthquakes
    # - between November 1st, 2020 and November 30th, 2020,
    # - around Strasbourg, France ( 48.5819, 7.7510  )
    # - in a radius of 2.5°
    # - output in json - a "text" output format is also available but doesn't return CSV headers, so json is more practicle
    #
    # https://www.seismicportal.eu/fdsnws/event/1/query?start=2020-11-01&end=2020-11-30&lat=48.581954779356785&lon=7.751004512233667&maxradius=2.5&format=json
    #
    # more details about this API here : https://www.seismicportal.eu/fdsn-wsevent.html
    #

    url_pattern = 'https://www.seismicportal.eu/fdsnws/event/1/query?start={start_date}&end={end_date}&lat={lat}&lon={lon}&maxradius={max_radius}&format=json'

    # start_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
    # end_date = datetime.now()

    start_date = datetime.strptime("2000-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2020-01-01", "%Y-%m-%d")

    time_interval = relativedelta(months=1)

    lat = 48.581954779356785
    lon = 7.751004512233667
    max_radius = 2.5

    current_date = start_date

    while current_date < end_date:

        p_start_date = current_date.strftime('%Y-%m-%d')

        # I have a time_interval of 1 month, start at a date like YYYY-MM-01
        # so I substrat one day so my end date is the last day of the month
        p_end_date = (current_date + time_interval -
                      timedelta(days=1)).strftime('%Y-%m-%d')

        params = {'start_date': p_start_date,
                  'end_date': p_end_date,
                  'lat': lat,
                  'lon': lon,
                  'max_radius': max_radius
                  }

        url = url_pattern.format(**params)

        output_filename = "%s_%s.json" % (p_start_date, p_end_date)

        output_filepath = os.path.join(output_dir, output_filename)

        download_data(url, output_filepath)

        current_date += time_interval
