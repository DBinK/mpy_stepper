import _thread
import time
import math
from machine import Pin, PWM, Timer

class StepperMotor:
    MODE_SPEED = 0
    MODE_POSITION = 1
    
    def __init__(self, step_pin, dir_pin=1, min_speed=8, max_speed=500):
        # 硬件资源初始化
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.s_pin = Pin(step_pin, Pin.OUT)
        self.d_pin = Pin(dir_pin, Pin.OUT)
        self.pwm = PWM(self.s_pin, duty_u16=0)  # 初始关闭PWM
        
        # 公共配置
        self.mode = self.MODE_SPEED
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.current_speed = 0
        self.target_position = 0
        self.current_position = 0
        
        # 位置模式专用属性
        self._stop_flag = False
        self._active_thread = None

    def set_mode(self, mode):
        """模式切换核心方法"""
        if mode == self.mode:
            return
        
        # 先停止当前模式
        if self.mode == self.MODE_SPEED:
            self.pwm.duty_u16(0)
        else:
            self._stop_motion()
        
        # 初始化新模式
        self.mode = mode
        if mode == self.MODE_POSITION:
            print(f"[{self.step_pin}] 切换到位置模式")
            self._init_position_mode()
        else:
            print(f"[{self.step_pin}] 切换到速度模式")
            self._init_speed_mode()

    def _init_speed_mode(self):
        """速度模式初始化"""
        self.pwm.duty_u16(32768)

    def _init_position_mode(self):
        """位置模式初始化"""
        self.pwm.duty_u16(0)  # 关闭PWM
        self.s_pin.off()      # 确保步进脉冲为低

    def move(self, value):
        """
        统一移动接口
        :param value: 速度模式下为转速（Hz），位置模式下为目标位置
        """
        if self.mode == self.MODE_SPEED:
            self._set_speed(value)
        else:
            self._move_to_position(value)

    # 速度模式方法 ----------------------------------
    def _set_speed(self, speed):
        """设置转速（Hz）"""
        self.current_speed = speed
        if abs(speed) < self.min_speed:
            self.pwm.duty_u16(0)
            return
            
        self.d_pin.value(1 if speed > 0 else 0)
        clamped_speed = max(self.min_speed, min(abs(speed), self.max_speed))
        self.pwm.freq(clamped_speed)
        self.pwm.duty_u16(32768)

    # 位置模式方法 ----------------------------------
    def _move_to_position(self, target):
        """非阻塞式移动到目标位置"""
        if self._active_thread:
            self._stop_motion()
            
        steps = target - self.current_position
        self._active_thread = _thread.start_new_thread(
            self._position_worker, (abs(steps), 100)  # 100为默认速度
        )

    def _position_worker(self, steps, speed):
        """位置控制线程"""
        self._stop_flag = False
        direction = steps > 0
        self.d_pin.value(1 if direction else 0)
        
        for _ in range(abs(steps)):
            if self._stop_flag:
                break
                
            self.s_pin.on()
            time.sleep(0.5 / speed)
            self.s_pin.off()
            time.sleep(0.5 / speed)
            
            self.current_position += 1 if direction else -1
            
        self._active_thread = None

    def _stop_motion(self):
        """停止位置模式运动"""
        if self._active_thread:
            self._stop_flag = True
            while self._active_thread:
                time.sleep(0.01)

# 使用示例
if __name__ == "__main__":
    motor = StepperMotor(step_pin=8, dir_pin=1)
    
    # 速度模式演示
    motor.set_mode(StepperMotor.MODE_SPEED)
    motor.move(200)  # 200Hz正转
    time.sleep(2)
    motor.move(-150) # 150Hz反转
    
    # 位置模式演示
    motor.set_mode(StepperMotor.MODE_POSITION)
    motor.move(500)  # 移动500步
    time.sleep(3)
    motor.move(0)    # 返回原点