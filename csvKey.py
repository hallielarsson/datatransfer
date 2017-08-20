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

    return default

  def read(self, data):
    for key in self.readKeys:
      if key in data:
        val = data[key]
        if self.value == None or self.value == "":
          self.value = data[key]
