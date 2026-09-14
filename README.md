# Raspberry-Pi-For-Beginners
Ubuntu 使用树莓派：GPIO Zero 与 VS Code 远程开发教程

## 核心说明

Windows 端通过 VS Code 远程编辑代码，树莓派 Ubuntu 负责 Python 运行与 GPIO 硬件控制。

- `gpiozero`：面向 LED、按键等设备的高级 Python API
- `lgpio`：底层 Linux GPIO 硬件访问驱动

> 
> 仅树莓派 / 带 GPIO 控制器的设备可用，普通 x86 电脑、WSL 无法控制真实硬件。

---

## 一、安装系统基础依赖

树莓派 Ubuntu 终端执行：

```
sudo apt update
sudo apt install -y openssh-server python3 python3-pip python3-venv python3-dev build-essential swig git
sudo systemctl enable --now ssh
```

- 开启 SSH 服务，供 Windows VS Code 远程连接
- `swig`、`build-essential` 用于编译 lgpio 底层 C 扩展

---

## 二、Python 虚拟环境（.venv）创建与激活教程

### 1. 创建虚拟环境

进入项目目录后执行：

```
cd ~/Raspberry-Pi-For-Beginners
python3 -m venv .venv
```

> 
> 作用：创建独立的 Python 运行环境，与系统全局 Python 包隔离，避免版本冲突。

### 2. 激活虚拟环境

```
source .venv/bin/activate
```

- 激活成功后，终端提示符前会出现 `(.venv)` 标记
- `source` 命令会在**当前终端窗口**加载环境变量，仅对当前窗口生效，新开终端需重新激活

### 3. 验证激活状态

```
which python
```

输出路径包含 `.venv/bin/python` 即为激活成功。

### 4. 退出虚拟环境

```
deactivate
```

执行后 `(.venv)` 标记消失，回到系统全局 Python 环境。

### 可选：进入目录自动激活（direnv）

如果希望进入项目文件夹自动激活、退出目录自动关闭，可通过 direnv 实现：

```
sudo apt install -y direnv
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```

在项目目录下创建 `.envrc` 文件，写入 `source .venv/bin/activate`，执行 `direnv allow` 授权后即可生效。

---

## 三、安装 GPIO 依赖库

**确保虚拟环境已激活（提示符前有 (.venv)）**，依次执行：

```
# 升级 pip
python -m pip install --upgrade pip

# 安装底层 lgpio
python -m pip install lgpio

# 安装上层 gpiozero
python -m pip install gpiozero
```

若安装报错 `cannot find -llgpio`，先安装系统库再重试：

```
sudo apt install -y liblgpio-dev liblgpio1
sudo ldconfig
```

软件源无对应包时，从源码编译安装：

```
git clone https://github.com/joan2937/lgpio.git /tmp/lgpio
cd /tmp/lgpio && make && sudo make install && sudo ldconfig
```

验证安装：

```
python -c "import lgpio, gpiozero; print('安装成功')"
```

---

## 四、LED 测试示例

创建 `gpio_test.py`：

```
from time import sleep
from gpiozero import Device, LED
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory(chip=0)
led = LED(17)  # BCM 编号 GPIO17，对应物理 Pin 11

try:
    while True:
        led.on()
        sleep(0.5)
        led.off()
        sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    led.off()
    led.close()
```

运行：

```
python gpio_test.py
```

> 
> 接线：GPIO17 → 220Ω~1kΩ 限流电阻 → LED 正极；LED 负极 → GND。GPIO 为 3.3V，禁止输入 5V。

---

## 五、常见故障速查

表格

| 报错现象 | 核心原因 | 快速解决 |
| --- | --- | --- |
| `command 'swig' failed` | 缺少 SWIG 编译工具 | `sudo apt install -y swig` |
| `cannot find -llgpio` | 缺少系统底层 lgpio 动态库 | 安装 `liblgpio-dev` 或源码编译 |
| `Permission denied` | 当前用户无 GPIO 设备权限 | 临时用 `sudo python` 运行，长期配置设备权限 |
| LED 无反应 | 引脚编号错误 / 接线异常 | 用 `gpiodetect`、`gpioinfo` 核对引脚状态 |