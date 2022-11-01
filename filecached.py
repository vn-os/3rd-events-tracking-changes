import os, pickle

class CacheFile(object):
  ''' Cache File
  '''

  cache_dir = ".cache"
  cache_ext = ".cache"
  cache_del = ".deled"

  def __init__(self, cache_file, debug=False):
    if not os.path.exists(self.cache_dir): os.makedirs(self.cache_dir)
    self.cache_file = os.path.join(self.cache_dir, cache_file + self.cache_ext)
    self.debug = debug
  
  def load(self):
    cache_object = {}
    try:
      if os.path.exists(self.cache_file):
        with open(self.cache_file, "rb+") as f:
          cache_object = pickle.load(f)
          if self.debug: print(f"restored states from cache file at '{self.cache_file}'")
    except Exception as e: print(e)
    return cache_object

  def store(self, cache_object):
    if self.deleted(): return False
    try:
      with open(self.cache_file, "wb+") as f:
        pickle.dump(cache_object, f)
        if self.debug: print(f"stored states to cache file at '{self.cache_file}'")
    except Exception as e: print(e)
    return True
  
  def delete(self):
    try:
      if os.path.exists(self.cache_file):
        tmp = self.cache_file + self.cache_del
        os.rename(self.cache_file, tmp) # os.remove(self.cache_file)
        if self.debug: print(f"archived cache file at '{tmp}'")
      self.cache_object = None
    except Exception as e: print(e)

  def deleted(self):
    return os.path.exists(self.cache_file + self.cache_del)
