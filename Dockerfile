FROM python:3.10.0

WORKDIR /customerSupportSystem

# Installing system utilities
RUN apt-get update && apt-get install -y \
    curl apt-utils

# Copy the requirements
COPY requirements.txt ./

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the application files and directories
COPY . .

RUN apt-get install -y cron && touch /var/log/cron.log


CMD bash -c service cron start && python manage.py crontab add
# Serve application
CMD  gunicorn --bind :8000 customersSupportSystem.wsgi --workers 1 --timeout 120
