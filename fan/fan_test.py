import subprocess
import time

def fan_on():
    subprocess.run(["sudo", "pinctrl", "FAN_PWM", "op", "dl"], check=True)

def fan_off():
    subprocess.run(["sudo", "pinctrl", "FAN_PWM", "op", "dh"], check=True)

def fan_auto():
    subprocess.run(["sudo", "pinctrl", "FAN_PWM", "a0"], check=True)

def fan_status():
    return subprocess.check_output(["sudo", "pinctrl", "FAN_PWM"], text=True)

def cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        return int(f.read().strip()) / 1000.0

if __name__ == "__main__":
    print("CPU 温度:", cpu_temp(), "℃")
    fan_on()
    print("风扇已强制开启，5 秒后关闭")
    time.sleep(5)
    fan_off()
    print("风扇已强制关闭，5 秒后恢复自动")
    time.sleep(5)
    fan_auto()
    print("已恢复内核自动温控")