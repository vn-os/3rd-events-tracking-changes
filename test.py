import asyncio
import jstyleson as json
from time import sleep

tranList  = {}
file_path = R"sample.json"
with open(file_path, "r", encoding="utf8") as f:
  tranList = json.load(f)["momoMsg"]["tranList"]

from events_tracking_changes import EventTrackingChanges

class MomoCronJob(EventTrackingChanges):
  def __init__(self):

    handlers = {
      "momo": self.on_received_money_handler,
    }

    super().__init__(
      name="momo-cron-job",
      fnkey="partnerCode",
      hdlrs=handlers,
      kidx=False,
      keys=["user", "tranId"],
      debug=True,
    )

  async def on_received_money_handler(self, event):
    if self.debug:
      print("on_received_money_handler", json.dumps(event, indent=2))
    await asyncio.sleep(0)  # make sure awaited

momo_cron_job = MomoCronJob()

asyncio.run(momo_cron_job.start())

for i in range(1, len(tranList)):
  print("".center(80, "-"))
  events = tranList[0:i]
  asyncio.run(momo_cron_job.process(events))
  sleep(3)

asyncio.run(momo_cron_job.stop())
