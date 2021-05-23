import urllib.request
import urllib.parse
from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import os
import json

from pdb import set_trace as bp


def download_json(url, output_filepath):

    print("downloading", url)
    response = urllib.request.urlopen(url)

    data = response.read().decode('utf-8')

    print("Writing to", output_filepath, "\n")
    with open(output_filepath, "w") as f:
        f.write(data)

    json_data = json.loads(data)
    return json_data


def get_start_date(output_dir):
    max_year = max([d for d in os.listdir(output_dir) if d.isdigit()])
    year_dir = os.path.join(output_dir, max_year)

    latest_file = max([d for d in os.listdir(year_dir) if d.endswith(".json")])

    latest_date = datetime.strptime(
        latest_file[:10], "%Y-%m-%d")

    return latest_date


if __name__ == "__main__":

    output_dir = "../data/json"
    os.makedirs(output_dir, exist_ok=True)

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

    start_date = get_start_date(output_dir)
    end_date = datetime.now()

    time_interval = timedelta(days=1)

    # Strasbourg
    # url_pattern = 'https://www.seismicportal.eu/fdsnws/event/1/query?start={start_date}&end={end_date}&lat={lat}&lon={lon}&maxradius={max_radius}&format=json'
    # area_name = "Strasbourg"
    # lat = 48.581954779356785
    # lon = 7.751004512233667
    # max_radius = 2.5

    # Worldwide
    url_pattern = 'https://www.seismicportal.eu/fdsnws/event/1/query?format=json&start={start_date}&end={end_date}&offset={offset}&limit=1000'
    #url_pattern += urllib.parse.urlencode(params)

    '''
       algo :

           totalcount = None
           while offset < data["metadata"]["totalcount"]:        
               download for 1 day, worldwide, offset = 0
               offset += len(data["features"])
               if totalcount is None:
                   total=data["metadata"]["totalcount"]

       '''
    current_date = start_date
    while current_date <= end_date:

        offset = 1
        totalcount = None

        year_dir = os.path.join(
            output_dir, current_date.strftime('%Y'))
        os.makedirs(year_dir, exist_ok=True)

        p_start_date = current_date.strftime('%Y-%m-%d')
        p_end_date = (current_date + time_interval).strftime('%Y-%m-%d')

        while totalcount is None or offset < totalcount:

            # bp()
            params = {'start_date': p_start_date,
                      'end_date': p_end_date,
                      'offset': offset
                      }

            url = url_pattern.format(**params)

            print(f"{p_start_date} -> {p_end_date} offset {offset}")
            print(url)
            print("\n")

            output_filename = "%s_%s_%s.json" % (
                p_start_date, p_end_date, offset)

            output_filepath = os.path.join(year_dir,  output_filename)

            json_data = download_json(url, output_filepath)

            offset += len(json_data["features"])

            if totalcount is None:
                totalcount = json_data["metadata"]["totalCount"]

        current_date += time_interval
