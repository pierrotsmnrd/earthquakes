#--- Base ---
FROM python:3.8

RUN apt-get update && apt-get install -y wget vim 

RUN apt-get install -y libproj-dev proj-data proj-bin  
RUN apt-get install -y libgeos-dev  


# Copy and install requirements
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# https://stackoverflow.com/questions/60111684/geometry-must-be-a-point-or-linestring-error-using-cartopy
RUN pip3 uninstall -y shapely
RUN pip3 install shapely --no-binary shapely

WORKDIR /app
EXPOSE 5006


CMD python /app/app.py 


