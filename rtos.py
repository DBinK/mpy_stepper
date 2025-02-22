

import _thread #导入线程模块
import time

from machine import Pin, PWM, Timer


step_pin = Pin(8, Pin.OUT)
dir_pin = Pin(0, Pin.OUT)

#线程函数
def _step(step, speed):
    for i in range(step):
        print(f"step: {i}, speed: {speed} Hz")
        step_pin.on()
        time.sleep((1 / speed) / 2)
        step_pin.off()
        time.sleep((1 / speed) / 2)
        
def do_step(step, speed):
    _thread.start_new_thread(_step,(step, speed,)) #开启线程2，参数必须是元组

if __name__ == '__main__':
    do_step(100, 1)
    do_step(100, 2)
    do_step(100, 4)
    do_step(100, 7)
    do_step(100, 9)

