from smbus2 import SMBus

I2C_ADDRESS = 8

with SMBus(1) as bus:
    bus.write_i2c_block_data(I2C_ADDRESS, 0, [255,0,0])
    bus.write_i2c_block_data(I2C_ADDRESS, 3, [0,255,0])
    bus.write_i2c_block_data(I2C_ADDRESS, 6, [0,0,255])