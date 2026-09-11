# Raspberry-Pi-For-Beginners
Ubuntu 使用树莓派：GPIO Zero 与 VS Code 远程开发教程

## 一句话结论

Windows 11 只负责通过 VS Code 编辑代码，Ubuntu（运行在树莓派上）负责 Python 环境、编译依赖和 GPIO 硬件控制。`gpiozero` 提供高级 Python 接口，`lgpio` 负责访问 Linux GPIO；二者都不能让普通 x86 Ubuntu 或 WSL 获得真实树莓派 GPIO。

## 适用范围与前置条件

- Ubuntu 必须运行在带 GPIO 控制器的树莓派或兼容开发板上；普通电脑没有可直接控制的树莓派 GPIO。
- 本文以 Raspberry Pi 的 BCM GPIO 编号为例，使用 GPIO17（物理 Pin 11）。实际编号、`gpiochip` 和占用状态需在设备上确认。
- 当前记录中的 `lgpio` 安装尚未完成，故 Properties 中状态保留为“待验证”。

## 开发架构

```text
Windows 11 + VS Code
          │ Remote-SSH
          ▼
树莓派 Ubuntu
  Python 虚拟环境
    gpiozero（高级接口）
      lgpio（底层 Python 扩展）
        liblgpio（系统 C 库）
          /dev/gpiochip* → GPIO 硬件
```

## 1. Ubuntu 安装远程开发与编译依赖

在树莓派 Ubuntu 终端执行：

```bash
sudo apt update
sudo apt install -y openssh-server python3 python3-pip python3-venv python3-dev build-essential swig
sudo systemctl enable --now ssh
hostname -I
```

| 命令或软件包 | 作用 |
| --- | --- |
| `sudo apt update` | 刷新 APT 软件包索引；只更新索引，不升级系统。 |
| `openssh-server` | 让 Ubuntu 接受 Windows 发起的 SSH 连接。 |
| `python3` | Python 3 解释器。 |
| `python3-pip` | 安装 Python 包的工具。 |
| `python3-venv` | 创建项目专用虚拟环境。 |
| `python3-dev` | 编译 `lgpio` 这类 Python C 扩展所需的头文件。 |
| `build-essential` | GCC、Make 等基础编译工具；`lgpio` 从源码构建时需要。 |
| `swig` | 将 `lgpio` 的 C 接口生成 Python 封装；缺少它会出现 `command 'swig' failed`。 |
| `systemctl enable --now ssh` | `enable` 设置开机启动，`--now` 立即启动 SSH 服务。 |
| `hostname -I` | 显示树莓派 IP 地址，供 Windows SSH 使用。 |

## 2. Windows 11 连接 Ubuntu

在 Windows PowerShell 测试连接：

```powershell
ssh 用户名@树莓派IP
```

`ssh` 是远程登录命令；用户名和 IP 必须替换为 Ubuntu 实际值。VS Code 安装 `Remote - SSH` 扩展后，使用同一个 SSH 地址连接，再打开 Ubuntu 上的项目目录。VS Code 的远程终端、Python 解释器和程序运行位置都在 Ubuntu，而不是 Windows。

## 3. 创建 Python 虚拟环境

在 VS Code 的 Ubuntu 远程终端执行：

```bash
cd ~/Raspberry-Pi-For-Beginners
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

| 命令                          | 作用                                     |
| --------------------------- | -------------------------------------- |
| `cd ...`                    | 进入项目目录；后续环境和代码都归属于该项目。                 |
| `python3 -m venv .venv`     | 创建名为 `.venv` 的项目虚拟环境，隔离系统 Python 包。    |
| `source .venv/bin/activate` | 激活虚拟环境；命令行前出现 `(.venv)` 才表示已生效。        |
| `python -m pip ...`         | 让当前 Python 调用自己的 pip，避免多个 Python 版本混用。 |

检查 Python 是否来自虚拟环境：

```bash
which python
```

应指向项目下的 `.venv/bin/python`。

## 4. 安装 `gpiozero` 与 `lgpio`

先安装底层库，再安装上层库：

```bash
python -m pip install lgpio
python -m pip install gpiozero
```

| 包 | 作用 |
| --- | --- |
| `lgpio` | Python 对 `liblgpio` 的封装，负责实际访问 Linux GPIO。它包含 C 扩展，可能需要本机编译。 |
| `gpiozero` | 面向 LED、按键、舵机等设备的高级 Python API。 |
| `colorzero` | `gpiozero` 的依赖，用于颜色和 LED 相关值的处理。 |
| `setuptools` | Python 包构建和安装工具，作为 `colorzero` 的依赖被安装。 |

### 4.1 本次安装错误的原因与处理

第一次安装报错：

```text
error: command 'swig' failed: No such file or directory
```

含义：`lgpio` 开始编译，但系统找不到 SWIG。安装前文的 `swig` 后即可越过这一阶段。

第二次安装报错：

```text
/usr/bin/aarch64-linux-gnu-ld.bfd: cannot find -llgpio
```

含义：SWIG 和 GCC 已经工作，链接器找不到 `liblgpio.so`（`-llgpio` 就是要求链接这个库）。这不是 `gpiozero` 代码错误，而是 Ubuntu 缺少 `liblgpio` 系统库。

先查询当前 Ubuntu 软件源是否提供开发包：

```bash
apt-cache search lgpio
```

如果结果中有 `liblgpio-dev` 和 `liblgpio1`，安装并刷新库缓存：

```bash
sudo apt install -y liblgpio-dev liblgpio1
sudo ldconfig
```

| 软件包或命令 | 作用 |
| --- | --- |
| `liblgpio-dev` | `liblgpio` 的头文件和开发链接文件，编译 Python 扩展时需要。 |
| `liblgpio1` | `liblgpio` 运行时动态库。 |
| `ldconfig` | 刷新动态链接库缓存，使链接器能找到新安装的库。 |

若软件源没有这些包，再从官方源码构建 C 库：

```bash
sudo apt install -y git
git clone https://github.com/joan2937/lgpio.git /tmp/lgpio
cd /tmp/lgpio
make
sudo make install
sudo ldconfig
```

这里 `git` 用于下载源码；`make` 编译库；`sudo make install` 安装到系统目录。安装完成后回到项目目录，在已激活的 `.venv` 中重试：

```bash
cd ~/Raspberry-Pi-For-Beginners
source .venv/bin/activate
python -m pip install --no-cache-dir lgpio gpiozero
```

`--no-cache-dir` 强制 pip 不使用之前失败的缓存构建结果。

验证导入：

```bash
python -c "import lgpio, gpiozero; print('安装成功')"
```

## 5. 检查 GPIO 控制器（可选）

`gpiod` 不是 `gpiozero` 的 Python 依赖，只用于确认 Linux GPIO 设备和 line 状态：

```bash
sudo apt install -y gpiod
gpiodetect
gpioinfo gpiochip0
```

| 命令或包 | 作用 |
| --- | --- |
| `gpiod` | 安装 `gpiodetect`、`gpioinfo` 等 GPIO 诊断命令。 |
| `gpiodetect` | 列出系统中的 GPIO 控制器，例如 `gpiochip0`。 |
| `gpioinfo gpiochip0` | 查看 line 编号、名称和是否被占用。 |

不要把 `gpiod` 命令中的 line 编号、BCM 编号和物理针脚号混为一谈。GPIO Zero 示例中的 `17` 表示 BCM GPIO17；在树莓派上通常对应物理 Pin 11。

## 6. GPIO Zero LED 测试

创建 `gpio_test.py`：

```python
from time import sleep

from gpiozero import Device, LED
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory(chip=0)
led = LED(17)  # BCM GPIO17，物理 Pin 11

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

```bash
python gpio_test.py
```

程序每 0.5 秒翻转一次 GPIO17；按 `Ctrl+C` 停止。`LGPIOFactory(chip=0)` 指定使用 `/dev/gpiochip0`，`LED(17)` 使用 BCM GPIO 编号，`finally` 确保退出时释放 GPIO。

接线：`GPIO17（Pin 11） → 220Ω~1kΩ 电阻 → LED 正极；LED 负极 → GND（如 Pin 6）`。GPIO 是 3.3V，禁止向 GPIO 输入 5V，也不能省略限流电阻。

## 常见故障速查

| 现象 | 直接判断 | 优先处理 |
| --- | --- | --- |
| `command 'swig' failed` | 缺少 SWIG | `sudo apt install -y swig` |
| `cannot find -llgpio` | 缺少 `liblgpio.so` | 查询并安装 `liblgpio-dev`/`liblgpio1`，或按源码方式安装。 |
| `Permission denied` | 当前用户无 GPIO 设备权限 | 先用 `ls -l /dev/gpiochip*` 检查；仅为验证可运行 `sudo .venv/bin/python gpio_test.py`，长期应配置设备权限。 |
| LED 不亮或 GPIO 无变化 | 编号、芯片、占用状态或接线错误 | 用 `gpioinfo gpiochip0` 核对；确认 GPIO17 没有被其他功能占用。 |