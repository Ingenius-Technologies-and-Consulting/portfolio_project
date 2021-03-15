FROM ubuntu:20.04

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set dependencies
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get install -y python3-pip
RUN apt-get install -y dos2unix
RUN pip3 install --upgrade pipenv

# Set working directory and copy files
WORKDIR /usr/app/src
COPY . .
RUN ls
RUN pipenv install --system --deploy --ignore-pipfile

# Run entrypoint file
RUN dos2unix entrypoint.sh
RUN chmod +x entrypoint.sh

#RUN groupadd --gid 5000 appuser
#RUN useradd --home-dir /home/appuser --create-home --uid 5000 --gid 5000 --shell /bin/sh --skel /dev/null appuser

# Provide db grant to app user
#RUN chown appuser:appuser db.sqlite3
#USER appuser
ENTRYPOINT ["/usr/app/src/entrypoint.sh"]

