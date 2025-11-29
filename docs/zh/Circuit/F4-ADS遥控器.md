---
title: F4-ADS遥控器
categories: [板子]

---

# 【F4-ADS】基于STM32F429VET6和ADS8688的遥控器

## 1.引言

​       自我进实验室以来，见过两种遥控器，一种是以STM32F103RCT6为主控，摇杆的四个通道直接接到32的ADC引脚采数据，痛点就是STM32F103RCT6的ADC只有12位，采摇杆数据很鸡肋，遂出现了第二种，我们发现STM32H7的ADC是16位，正点原子阿波罗核心板上还有外接的sdram，可以上ui，用了4.3寸IPS显示屏，痛点是成本高，程序调起来也复杂。

​       总之，第一种遥控器太简陋，第二种遥控器太豪华，遂设计一款折中的遥控器——基于STM32F429VET6和ADS8688的遥控器，简称F4-ADS。


## 2.模块说明

F4-ADS的配置如下：

摇杆：PS5 TMR霍尔摇杆

ADC：ADS8688是16位8通道500kspsADC芯片，我们使用其中4个通道采两个摇杆的xy，1个通道采电池电量

MCU：STM32F429VET6

屏幕：ST7789驱动的2寸屏幕

外设：1个NOR FLASH、4个LED、1个4x4矩阵键盘、2个独立按键、1个蜂鸣器、1个typeC+CH340有线调试、1个NRF

![F4-ADS](Picture/ykq1.png)
![F4-ADS](Picture/ykq2.png)

原理图较简单，只说明ADS8688采集电路

通道引脚串联270R电阻，起限流作用，信号和GND间接100nF电容滤波，外接ADR444电压基准芯片为ADS8688提供4.096V基准电压

![ADS8688](Picture/ykq3.png)

PCB大概是15cm x 10cm，为了节约成本画了2层板，大部分电容电阻是0402封装，节省空间。

## 3.IO说明

![IO](Picture/ykq4.png)

## 4.资料

资料包含工程文件、IO说明、外壳.step文件
链接：https://pan.quark.cn/s/e70b1f419f03

