FROM python:3.10.5-slim

# python steps
ARG python_binary="python3.10"
WORKDIR /usr/src
RUN ${python_binary} -m pip install -U pip
COPY requirements.txt ./requirements.txt
RUN apt-get update && apt-get install -y gcc
RUN ${python_binary} -m pip install -r ./requirements.txt
RUN ${python_binary} -m pip install fastapi==0.95.0
RUN ${python_binary} -m pip install uvicorn==0.14.0
#COPY ${context_dir}/wheels ./wheels
#RUN cd wheels && ${python_binary} -m pip install -r ./install.txt --no-deps
#
COPY ./src ./
ENV PYTHONPATH=/usr/src
CMD ["python", "rps_runner/api.py"]
