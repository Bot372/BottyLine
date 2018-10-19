import json
import numpy as np


x = {
  "name": "John",
  "age": 30,
  "married": True,
  "divorced": False,
  "children": ("Ann","Billy"),
  "pets": None,
  "cars": [
    {"model": "BMW 230", "mpg": 27.5},
    {"model": "Ford Edge", "mpg": 24.1}
  ]
}

# convert into JSON:

messegae = {
            "events": [{"type": "message", "replyToken": "be031b9c998c4dcc95482d790998e8d4",
                   "source": {"userId": "U5ecd214f1c2ed4ef31f14b313f09c843", "type": "user"},
                   "timestamp": 1539935317913,
                   "message": {"type": "audio", "id": "8739182464882"}}]}



hehe = messegae['events']

y = json.dumps(messegae)
event = json.dumps(messegae['events'] )
event =  event[event.find("userId") + 10 : len(event) ]
event = event[0 : event.find("type") - 4 ]
# the result is a JSON string:
print(  event )


