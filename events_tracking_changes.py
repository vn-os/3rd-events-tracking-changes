import asyncio
import jstyleson as json
import requests_async as requests

from cachetools.keys import hashkey
from .asyncached import cached
from .filecached import CacheFile

class EventTrackingChanges():
  ''' Event Tracking Changes
  name - an unique name for event tracking changes
  key_contains_handler_names - the key that identify the event handler
  mapping_handlers - a mapping of handler names and their class methods
  use_event_index_in_cache_key - include event index to the cache key
  use_additional_keys_in_cache_key - include their values in event object to the cache key
  enable_debug_logging - enable debug logging
  '''

  def __init__(self, name,
    key_contains_handler_names="",
    mapping_handlers={},
    use_event_index_in_cache_key=True,
    use_additional_keys_in_cache_key=[],
    enable_debug_logging=False):
    self.name  = name
    self.fkey  = key_contains_handler_names
    self.keys  = use_additional_keys_in_cache_key
    self.kidx  = use_event_index_in_cache_key
    self.debug = enable_debug_logging
    self.handlers = mapping_handlers
    self.cache_events = {}
    self.cache = CacheFile(self.name, self.debug)

  async def start(self):
    if not self.cache.deleted():
      self.cache_events = self.cache.load()
    await asyncio.sleep(0) # make sure awaited

  async def stop(self):
    if not self.cache.deleted():
      self.cache.store(self.cache_events)
    await asyncio.sleep(0) # make sure awaited

  async def process(self, events):
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
          fn = _self.handlers.get(event.get(self.fkey, ""), _self.on_default_handler)
          if fn: await fn(event)
        _self.cache.store(_self.cache_events)
      except Exception as e:
        _self.cache.store(_self.cache_events)
        print(e)
    await _track_change(self, event_index, events, *args)

  async def on_default_handler(self, event):
    if self.debug: print("on_default_handler", event)
    await asyncio.sleep(0) # make sure awaited
