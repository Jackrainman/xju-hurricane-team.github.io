# CAN 通信列表模块 (CAN List)

> 最近修改日期：2026-01-27
> 参与者：Deadline039（作者）, Jackrainman（文档编写）

## 1. 模块概述

本模块提供了一套基于哈希表（Hash Table）和链表（Linked List）的 CAN 消息接收管理机制。

### 核心功能

* **高效分发**：收到 CAN 消息后，根据 ID 快速查找并调用对应的回调函数，避免在中断中进行复杂的 `if-else` 判断。
* **多外设兼容**：同时支持 STM32 的 bxCAN (CAN 2.0) 和 FDCAN 外设，通过宏定义切换。
* **RTOS 支持**：可选集成 FreeRTOS，将消息处理从中断服务函数（ISR）转移到任务线程中，减少中断占用时间。

### 适用场景

* 需要处理大量不同 CAN ID 设备的机器人底盘或云台控制。
* 需要统一管理 CAN 通信回调逻辑的工程项目。

## 2. 集成指南

### 2.1 文件部署

1. 将 `can_list` 文件夹整体复制到工程目录 `/Drivers/bsp/` 下。
2. 在板级支持包头文件（如 `bsp.h`）中包含本模块：
```
#include "can_list/can_list.h"

```



### 2.2 依赖说明

* **必需**：标准库 `<stdlib.h>` (用于内存管理)。
* **可选**：FreeRTOS (若开启 RTOS 模式)。
* **配置**：需依赖项目的 `CSP_Config.h` 或相应的 HAL 库头文件。

## 3. 配置宏说明

在 `can_list.h` 中根据硬件平台和需求修改以下宏定义：

| 宏定义名称 | 默认值 | 说明 |
| --- | --- | --- |
| `CAN_LIST_USE_FDCAN` | `0` | **硬件选择**。<br>

<br>`1`: 启用 FDCAN 支持 (如 STM32G4/H7)。<br>

<br>`0`: 启用 bxCAN 支持 (如 STM32F1/F4)。 |
| `CAN_LIST_MAX_CAN_NUMBER` | `3` | **最大外设数量**。<br>

<br>限制系统支持的 CAN 控制器总数，防止数组越界。 |
| `CAN_LIST_USE_RTOS` | `1` | **系统集成**。<br>

<br>`1`: 创建 FreeRTOS 任务处理消息，需确保 CAN 中断优先级**低于** FreeRTOS 管理的最大优先级。<br>

<br>`0`: 在中断回调中直接处理消息。 |

> **注意**：若启用 RTOS 模式，务必在调用 `vTaskStartScheduler()` 之后再使用 `can_list_add_can` 进行初始化。

## 4. API 参考手册

### 4.1 初始化 CAN 列表

创建一个用于管理特定 CAN 外设的哈希表。

```c
uint8_t can_list_add_can(can_selected_t can_select, uint32_t std_len, uint32_t ext_len);

```

* **参数**：
* `can_select`：目标 CAN 外设（如 `can1_selected`）。
* `std_len`：标准帧 ID 哈希表的桶（Bucket）长度。
* `ext_len`：扩展帧 ID 哈希表的桶（Bucket）长度。


* **性能调优**：
* `len` 值越大，哈希冲突概率越低，查表速度越快，但内存占用增加。
* 若将 `len` 设置为 1，结构将退化为普通单向链表。



### 4.2 注册接收节点

向 CAN 列表中添加一个新的设备节点及其回调函数。

```c
uint8_t can_list_add_new_node(can_selected_t can_select,
                              void *node_data,
                              uint32_t id,
                              uint32_t id_mask,
                              uint32_t id_type,
                              can_callback_t callback);

```

* **参数**：
* `can_select`：使用哪个 CAN 外设接收。
* `node_data`：设备对象指针。触发回调时，该指针将作为参数传入，用于区分不同设备实例。
* `id`：期望匹配的 CAN ID（通常为设备反馈的 ID）。
* `id_mask`：ID 掩码。用于屏蔽 ID 中不相关的位（如包含状态码的高位）。
* 匹配逻辑为：`(RxID & mask) == (id & mask)`。


* `id_type`：ID 类型（标准帧或扩展帧）。
* `callback`：接收到匹配数据后的回调函数。**不能为空**。



### 4.3 管理与维护

* **删除节点**：
```c
uint8_t can_list_del_node_by_id(can_selected_t can_select, uint32_t id_type, uint32_t id);

```


* **更改回调**：
```c
uint8_t can_list_change_callback(can_selected_t can_select, uint32_t id_type, uint32_t id, can_callback_t new_callback);

```



## 5. 使用示例

### 5.1 场景描述

假设我们控制一个电机设备，通信协议定义如下：

* **主机 (Master)**：控制端（我们）。
* **设备 (Device)**：被控端（电机）。
* **反馈帧 (Device -> Master)**：使用扩展帧。
* ID 格式：`[29:22] 错误码 | [21:14] 模式 | [13:11] 数据标识 | [10:8] 保留 | [7:0] Master ID`。
* 我们只关心 `[7:0]` 位是否匹配 Master ID。


* **控制帧 (Master -> Device)**：
* ID 格式：`[15:8] Master ID | [7:0] Dev ID`。



### 5.2 回调函数定义

回调函数必须符合 `can_callback_t` 类型：

```c
/**
 * @brief 电机数据反馈回调
 * @param node_obj      注册时传入的设备对象指针 (dev_demo)
 * @param can_rx_header CAN 接收头部信息
 * @param can_msg       CAN 数据负载 (Payload)
 */
static void motor_callback(void *node_obj, can_rx_header_t *can_rx_header, uint8_t *can_msg) {
    can_dev_t *dev = (can_dev_t *)node_obj;

    /* 提取 ID 中的数据标识位 [13:11] */
    uint32_t data_type = (can_rx_header->id >> 11) & 0x07;

    switch (data_type) {
        case 1:
            /* 处理类型 1 数据：int32, uint16, int16 */
            memcpy(&dev->data1, &can_msg[0], sizeof(int32_t));
            memcpy(&dev->data2, &can_msg[4], sizeof(uint16_t));
            memcpy(&dev->data3, &can_msg[6], sizeof(int16_t));
            break;
        case 2:
            /* 处理类型 2 数据：uint32, float */
            memcpy(&dev->data4, &can_msg[0], sizeof(uint32_t));
            memcpy(&dev->data5, &can_msg[4], sizeof(float));
            break;
        default:
            break;
    }
}

```

### 5.3 业务逻辑实现

```
/* 定义设备结构体 */
typedef struct {
    uint32_t master_id;
    uint32_t dev_id;
    /* 接收数据缓存 */
    int32_t data1;
    uint16_t data2;
    int16_t data3;
    uint32_t data4;
    float data5;
} can_dev_t;

/* 全局设备实例 */
static can_dev_t dev_demo;

void app_demo_init(void) {
    /* 1. 初始化 CAN 底层 (BSP层) */
    // can1_init();

    /* 2. 配置设备 ID */
    dev_demo.master_id = 1;
    dev_demo.dev_id = 2;

    /* 3. 注册接收回调 */
    can_list_add_new_node(
        can1_selected,          /* 使用 CAN1 */
        &dev_demo,              /* 传入设备实例指针 */
        dev_demo.master_id,     /* 期望匹配的 ID (Master ID) */
        0xFF,                   /* 掩码：只匹配 ID 的低 8 位 (0xFF) */
        CAN_ID_EXT,             /* 使用扩展帧 */
        motor_callback          /* 注册回调函数 */
    );
}

void app_demo_loop(void) {
    uint8_t send_data[8] = {0};

    /* 4. 发送控制指令 */
    // can_send_message(can1_selected,
    //                  CAN_ID_EXT,
    //                  (dev_demo.master_id << 8) | dev_demo.dev_id,
    //                  8,
    //                  send_data);
}

```

---
