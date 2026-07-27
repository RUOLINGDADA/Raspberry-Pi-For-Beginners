from gpiozero import LED
from time import sleep

def dot():
    """点 · 亮0.25s"""
    led.on()
    sleep(0.25)
    led.off()
    sleep(0.25)

def dash():
    """划 - 亮0.75s"""
    led.on()
    sleep(0.75)
    led.off()
    sleep(0.25)

led = LED(22)
print("请输入命令:\r\n1 -> on, 0 -> off, -1 -> sos:\r\n", end = "")
try:
    while True:
        sleep(0.01) #减少程序占用
        choice = int(input())
        if choice == 1:
            led.on()
        elif choice == 0:
            led.off()
        elif choice == -1:
            while True:
                sleep(0.01)
                # S: ···
                dot()
                dot()
                dot()
                sleep(0.75) #字母间隔
                # O: ---
                dash()
                dash()
                dash()
                sleep(0.75) #字母间隔
                # S: ···
                dot()
                dot()
                dot()
                sleep(2) #整套SOS结束，停顿2秒再循环
        else:
            print("请输入正确命令!")
except ValueError:
    print("请输入正确命令!")
except KeyboardInterrupt:
    led.off()
