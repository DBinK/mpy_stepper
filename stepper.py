import time
import math
from machine import Pin, PWM, Timer

class StepperMotor:
    def __init__(self, step_pin, dir_pin=1, min_speed=8, max_speed=500, period=20):
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.pwm = PWM(self.step_pin, duty_u16=32768)
        self.speed = 0
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.period = period
        
        # 初始化定时器
        self.tim = Timer(-1)
        self.tim.init(period=self.period, mode=Timer.PERIODIC, callback=self._update_speed)

    def _update_speed(self, tim_callback):
        """内部速度更新方法"""
        if self.speed < abs(self.min_speed):
            self.pwm.duty_u16(0)
        else:
            self.dir_pin.value(1 if self.speed > 0 else 0)  # 设置方向
            clamped_speed = max(self.min_speed, min(self.speed, self.max_speed))  # 限制速度范围
            self.pwm.duty_u16(32768)  # 设置 50% 占空比
            self.pwm.freq(clamped_speed)  # 设置 速度
            print(f"Current step speed: {clamped_speed} Hz")

    def set_speed(self, new_speed):
        """设置电机转速"""
        self.speed = new_speed

    def stop(self):
        """立即停止电机"""
        self.speed = 0
        self.pwm.duty_u16(0)

if __name__ == "__main__":

    motor = StepperMotor(step_pin=25)
    print("Motor controller started")

    # 模拟速度控制
    try:
        for i in range(100000):
            # 生成正弦波速度曲线（范围：0-50Hz）
            target_speed = int(math.sin(i/100) * 25 + 25)
            motor.set_speed(target_speed)
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        motor.stop()
        print("\nMotor stopped safely")