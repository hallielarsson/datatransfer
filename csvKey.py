class CsvKey:

  def __init__(self, *keys):
    assert len(keys) > 0
    self.writeKey = keys[0]
    self.readKeys = keys
    self.value = ""

  def getKey(self):
    return writeKey

    return default

  def read(self, data):
    for key in self.readKeys:
      if key in data:
        val = data[key].rstrip()
        if self.value == None or self.value.rstrip() == "":
          self.value = str(val)

  def setIfEmpty(self, value):
    if self.value == "" or self.value == None:
      self.value = value

