from smbus2 import SMBus

from config import Config

class I2C:
  @classmethod
  def init(cls):
    cls.bus = SMBus(Config.I2C_BUS)