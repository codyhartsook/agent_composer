FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

ARG DEVPI_IP
ENV DEVPI_IP ${DEVPI_IP}

ARG SDK_VERSION
ENV SDK_VERSION ${SDK_VERSION}

RUN pip install --ignore-installed --index-url http://${DEVPI_IP}:3141/root/cascade_node_sdk --extra-index-url https://pypi.org/simple cascade_node_sdk==${SDK_VERSION} --trusted-host ${DEVPI_IP}

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

CMD ["python", "chatbot.py"]