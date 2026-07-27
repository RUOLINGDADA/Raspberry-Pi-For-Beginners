#!/usr/bin/env python3
import subprocess
import time
import sys

# ===== 可调参数 =====
TEMP_ON = 45.0        # 达到此温度开启风扇（℃）
TEMP_OFF = 40.0       # 低于此温度关闭风扇（℃）
CHECK_INTERVAL = 5    # 检查间隔（秒）
PIN_NAME = "FAN_PWM"  # 树莓派 5 板载风扇 PWM 引脚名

def set_fan(on: bool):
    """低电平有效：dl = 开启，dh = 关闭"""
    state = "dl" if on else "dh"
    subprocess.run(
        ["sudo", "pinctrl", PIN_NAME, "op", state],  # 加上 sudo
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def get_cpu_temp() -> float:
    """读取 CPU 温度，优先 sysfs，失败则用 vcgencmd"""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read().strip()) / 1000.0
    except Exception:
        out = subprocess.check_output(
            ["vcgencmd", "measure_temp"], text=True
        )
        return float(out.replace("temp=", "").replace("'C\n", ""))

def main():
    fan_on = False
    try:
        set_fan(False)  # 启动时先关闭，接管控制
    except Exception as e:
        print(f"初始化风扇失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"风扇温控已启动：{TEMP_ON}℃ 开，{TEMP_OFF}℃ 关")

    while True:
        try:
            temp = get_cpu_temp()

            if not fan_on and temp >= TEMP_ON:
                set_fan(True)
                fan_on = True
                print(f"{time.ctime()} 温度 {temp:.1f}℃ >= {TEMP_ON}℃，风扇开启")

            elif fan_on and temp <= TEMP_OFF:
                set_fan(False)
                fan_on = False
                print(f"{time.ctime()} 温度 {temp:.1f}℃ <= {TEMP_OFF}℃，风扇关闭")

            else:
                print(f"{time.ctime()} 温度 {temp:.1f}℃，风扇 {'开' if fan_on else '关'}")

        except Exception as e:
            print(f"{time.ctime()} 出错: {e}", file=sys.stderr)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
