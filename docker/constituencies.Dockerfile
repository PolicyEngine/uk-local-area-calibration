FROM python:3.10
COPY . .
RUN pip install -r requirements.txt
ARG POLICYENGINE_GITHUB_MICRODATA_AUTH_TOKEN
RUN make constituency-weights
