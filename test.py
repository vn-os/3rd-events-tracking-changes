import asyncio
import jstyleson as json
from time import sleep

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
print = pp.pprint

tranList  = {}
file_path = R"sample.json"
with open(file_path, "r", encoding="utf8") as f:
  tranList = json.load(f)["momoMsg"]["tranList"]

from events_tracking_changes import EventTrackingChanges
etc = EventTrackingChanges(name="sample", kidx=False, keys=["user", "tranId"], debug=True)
asyncio.run(etc.on_open())

n = len(tranList)
for i in range(1, n):
  print("".center(80, "-"))
  events = tranList[0:i]
  asyncio.run(etc.on_events(events))
  sleep(3)

asyncio.run(etc.on_close())
