import asyncio
import jstyleson as json
import requests_async as requests

from cachetools.keys import hashkey
from asyncached import cached
from filecached import CacheFile

class EventTrackingChanges():
  ''' Event Tracking Changes
  name  - an unique name for event tracking changes
  fnkey - the key that identify the event handler
  kidx  - include event index to the cache key
  keys  - include values of keys in event object to the cache key
  debug - enable debug logging
  '''

  def __init__(self, name, fnkey="", kidx=True, keys=[], debug=False):
    self.name  = name
    self.fnkey = fnkey
    self.keys  = keys
    self.kidx  = kidx
    self.debug = debug
    self.cache = CacheFile(self.name, self.debug)
    self.cache_events = {}
    self.mapping_handlers = {
      "momo": self.on_momo_handler,
    }

  async def on_open(self):
    print("on_open -> STARTED")
    if self.cache.deleted():
      print("on_open -> FINISHED")
    else:
      self.cache_events = self.cache.load()
    await asyncio.sleep(0) # make sure awaited

  async def on_close(self):
    if not self.cache.deleted():
      self.cache.store(self.cache_events)
    print("on_close -> FINISHED")
    await asyncio.sleep(0) # make sure awaited

  async def on_events(self, events):
    try:
      if events:
        num_events = len(events)
        if num_events > 0:
          for i in range(0, num_events):
            await self.track_change(i, events, *tuple([events[i][key] for key in self.keys]))
    except Exception as e:
      print(e)
    await asyncio.sleep(0) # make sure awaited

  async def track_change(self, event_index, events, *args):
    @cached(cache=self.cache_events, key=lambda self, event_index, events, *args:
      hashkey(f"{self.name}-{str(event_index) if self.kidx else 'x'}-{'-'.join(map(str, args)) if self.keys else 'x'}"))
    async def _track_change(_self, event_index, events, *args):
      try:
        event = events[event_index]
        if event:
          fn = _self.mapping_handlers.get(event.get(self.fnkey, ""), _self.on_default_handler)
          if fn: await fn(event)
        _self.cache.store(_self.cache_events)
      except Exception as e:
        _self.cache.store(_self.cache_events)
        print(e)
    await _track_change(self, event_index, events, *args)

  async def on_default_handler(self, event):
    print("on_default_handler", event)
    await asyncio.sleep(0) # make sure awaited

  async def on_momo_handler(self, event):
    print("on_momo_handler", event)
    await asyncio.sleep(0) # make sure awaited
