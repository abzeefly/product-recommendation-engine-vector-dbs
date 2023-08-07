FROM python:3.11.4-slim
# SET WORKING DIRECTORY TO /app
WORKDIR /
# COPY APP FILES
COPY /app /app
# COPY POETRY FILES
COPY pyproject.toml poetry.lock ./
# INSTALL POETRY
RUN pip install poetry
# INSTALL ALL DEPENDENCIES
RUN poetry install --no-root --no-dev
# RUN PYTHON TO TEST
CMD ["python3"]
# SET ALL ENVIRONMENT VARIABLES
ENV project_id = "<ENTER YOUR project_id>"
ENV region = "<ENTER YOUR region>"
ENV instance_name = "<ENTER YOUR instance_name>"
ENV database_user = "<ENTER YOUR database_user>"
ENV database_password = "<ENTER YOUR database_password>"
ENV database_name = "<ENTER YOUR database_name>"
# COPY credentials file
COPY credentials.json .

ENTRYPOINT ["python3", "app.py"]