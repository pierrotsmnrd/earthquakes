# earthquakes_strasbourg
A dashboard to visualise earthquakes around Strasbourg between 2000 and 2020. 

![preview of the dashboard](imgs/screenshot.png)


## Context

A abnormal seismic activity has been recently recorded near  <a href="https://goo.gl/maps/7NRzCfcGYbbnUZzT9" target="_blank">Strasbourg, France</a>.

These unusual earthquakes may have been caused by boreholes made during the exploration phase of a geothermal energy project. 

The goal of this dashboard is to display the earthquakes around Strasbourg for the last 20 years (2000-2020). 

##  Data

To make a good dashboard, you need good data.  
I used the webservices of <a href="https://www.seismicportal.eu/" target="_blank">www.seismicportal.eu</a>.

The dataset is built in 2 steps :
- collect the raw data from the webservice : `python scrapping/download_json.py`
- aggregate the json files into a csv file : `python scrapping/build_dataset.py`


## Dashboard

The dashboard is made with Holoviz (using Holoviews, Geoviews and Panel) with the Bokeh backend.

## Questions ? 

- If you'd like to display the same dashboard over another area
- If you have any question on how to use this dashboard
- If you have suggestions on how to improve it

Then please contact me <a href="https://www.linkedin.com/in/pierreoliviersimonard/" target="_blank">on LinkedIn</a> or <a href="https://twitter.com/pierrotsmnrd" target="_blank">on Twitter</a>.

Pull requests are appreciated !
