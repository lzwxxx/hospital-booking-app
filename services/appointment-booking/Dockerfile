FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "./wait-for-it/wait-for-it.sh", "rabbitmq:5672", "--" , "python" , "./appointment_booking.py" ]