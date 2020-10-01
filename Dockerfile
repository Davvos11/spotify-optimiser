# Source it from the python dockerfile
FROM python:3.8.5
# Copy over the current directory structure, make sure token.txt exists!
COPY . /spotify-optimiser

# Install the requirements
RUN pip install pipenv
RUN cd /spotify-optimiser && pipenv install --system --deploy --ignore-pipfile

# Run the bot
ENTRYPOINT [ "/spotify-optimiser/run.sh" ]
