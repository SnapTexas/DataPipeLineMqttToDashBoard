from fastapi import FastAPI,Request,Response
from fastapi.templating import Jinja2Templates

import paho.mqtt.client as mqtt
import redis
import os
from dotenv import find_dotenv,load_dotenv
app=FastAPI()
templates=Jinja2Templates(directory="Templates")
env_path=find_dotenv()
load_dotenv(env_path)

fake_data = {
    "id": "abc",
    "msg": "hello World"
}


mqtt_sub_topic=os.getenv("bridge_server_mqtt_topic")
connection_str=os.getenv("connection_str")

mqtt_port=int(os.getenv("mqtt_port"))

redis_host=os.getenv("redis_host_url")
redis_port=int(os.getenv("redis_port"))
redis_username=os.getenv("redis_username")
redis_password=os.getenv("redis_password")

mqtt_client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

redis_client=redis.Redis(
    host=redis_host,
    port=redis_port,
    decode_responses=True,
    username=redis_username,
    password=redis_password

)
count=0
def store_in_buffer_redis(client, userdata, msg):
    global count
    data=msg.payload.decode()
    key=f"data{count}"

    redis_client.set(key,data)
    if count>10:
        count=0
    else:
        count+=1
def mqtt_connection_status(client, userdata, flags, rc, properties=None):
    print("Connected to Server :",rc)
    client.subscribe(mqtt_sub_topic)

mqtt_client.connect(
    connection_str,
    mqtt_port,
    60
)
mqtt_client.on_connect=mqtt_connection_status

mqtt_client.on_message = store_in_buffer_redis

mqtt_client.loop_start()
@app.head("/")
def head_data():
    """Returns headers only, no body"""
    # You can customize headers if you want
    headers = {
        "X-Custom-Header": "Example",
        "Content-Length": str(len(str(fake_data)))  # mimic GET content length
    }
    return Response(headers=headers, status_code=200)
@app.get("/")
def read_root(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})












