#--- Base ---
FROM python:3.8

RUN apt-get update && apt-get install -y wget vim cron && rm -rf /etc/cron.*/*

RUN apt-get install -y libproj-dev proj-data proj-bin  
RUN apt-get install -y libgeos-dev  


# Copy and install requirements
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# https://stackoverflow.com/questions/60111684/geometry-must-be-a-point-or-linestring-error-using-cartopy
RUN pip3 uninstall -y shapely
RUN pip3 install shapely --no-binary shapely

COPY ./docker/update_dataset.cron /etc/cron.d/update_dataset.cron
RUN chmod 0644 /etc/cron.d/update_dataset.cron
RUN touch /var/log/update_dataset.log
RUN crontab /etc/cron.d/update_dataset.cron


WORKDIR /app
EXPOSE 5006

CMD cron && python /app/app.py 


