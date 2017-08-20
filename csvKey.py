class CsvKey:
  writeKey = ""
  value = ""
  default= ""

  def __init__(self, *keys):
    assert len(keys) > 0
    self.writeKey = keys[0]
    self.readKeys = keys

  def getKey(self):
    return writeKey

  def tryGet(self, data):
    for key in self.readKeys:
      if key in data:
        return data[key]
    return default

  def read(self, sourceDict):
    self.value = self.tryGet(sourceDict)