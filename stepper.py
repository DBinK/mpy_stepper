import time
import math
from machine import Pin, PWM, Timer

class StepperMotor:
    def __init__(self, pin_num, min_speed=1, max_speed=500):
        self.pin = Pin(pin_num, Pin.OUT)
        self.pwm = PWM(self.pin, duty_u16=32768)
        self.speed = 0
        self.min_speed = min_speed
        self.max_speed = max_speed
        
        # 初始化定时器
        self.tim = Timer(-1)
        self.tim.init(period=20, mode=Timer.PERIODIC, callback=self._update_speed)

    def _update_speed(self, tim_callback):
        """内部速度更新方法"""
        if self.speed <= 0:
            self.pwm.duty_u16(0)
        else:
            # 限制速度范围
            clamped_speed = max(self.min_speed, min(self.speed, self.max_speed))
            self.pwm.duty_u16(32768)
            self.pwm.freq(clamped_speed + 10)  # 保持原逻辑+10偏移量
            print(f"Current speed: {clamped_speed} Hz")

    def set_speed(self, new_speed):
        """设置电机转速"""
        self.speed = new_speed

    def stop(self):
        """立即停止电机"""
        self.speed = 0
        self.pwm.duty_u16(0)

if __name__ == "__main__":

    motor = StepperMotor(pin_num=25)
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