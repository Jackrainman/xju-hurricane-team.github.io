# FOC学习-硬件版

## 1.引言

从大一下学期开始接触Benjamin的VESC，复刻了七八个版本才成功，硬件懵懵懂懂，软件一窍不通，希望通过写这篇文章彻底弄懂VESC的硬件。

![VESC](Picture/FOC_Hardware4.jpg)

## 2.原理图模块解读

### 单片机控制部分

STM32大致可以分为三个部分：

![VESC](Picture/FOC_Hardware2.png)

**ADC采样**：PA0/1/2对三相电压进行采样，PC0/1/2/3对三相电流和总电压进行采样

**驱动DRV8301**：PA8/9/10、PB13/14/15输出PWM信号驱动DRV8301，SPI3与DRV8301进行通信读取状态，PB5接EN_GATE选择是否启用栅极驱动和采样电流放大器，PB7接收DRV的FALUT数据

**外设**：两个LED显示状态，一个霍尔接口，一个3508的编码器接口，一个6020的编码器接口，一个CAN接口，Benjamin版本还有IMU、无线调试模块，比赛用处较小就删去了

### 驱动芯片

DRV8301大致可以分成四个部分：

![VESC](Picture/FOC_Hardware3.png)

**电源部分**：DRV8301内置一个BUCK降压电路TPS54160，将24V降到5V

**单片机通信部分**：DRV8301通过SPI和单片机通信，用于向上位机报告 DRV8301 状态及故障

**单片机PWM输入部分**：INH_A/B/C、INL_A/B/C。这6个引脚控制GH_A/B/C、GL_A/B/C驱动栅极输出

![VESC](Picture/FOC_Hardware1.png)

**MOS驱动部分**：GH_A/B/C、GL_A/B/C、SH_A/B/C、SL_A/B/C。GH_A/B/C接上管栅极，GL_A/B/C接下管栅极，SH_A/B/C接上管源极，SL_A/B/C接下管源极。

看到一篇华南理工博主自制无刷电机驱动器的博客，他把驱动芯片换成了FD6288Q，确实可以减小不少面积，只需要添加两个降压模块，也很不错，有机会尝试下。

### 电流检测

使用3个AD8418测三相电流，AD8418检测电流的原理是电流通过采样电阻会产生压降，AD8418将这个压降通过内部的运算放大器放大然后输出，输出的这三个电压通过一个RC滤波器输入到单片机的ADC引脚进行采集。

![电流检测](Picture/FOC_Hardware5.png)

### MOS驱动电路







## 3.PCB布局







