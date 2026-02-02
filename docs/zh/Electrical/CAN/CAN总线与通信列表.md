> **版本**：2.0
>
> **最近修改日期**：2026-02-02
>
> **预计阅读时间**：10-15 分钟
>
> **参与者**：Deadline039（作者），Jackrainman（文档编写）

# CAN List 模块

## 1. 解决什么问题

在机器人电控系统中，一个 CAN 总线可能挂载多个电机和传感器。传统开发中，工程师在中断中使用 `switch-case` 处理不同 CAN ID：

```c
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    if (header.ExtId == 0x201) { /* 处理左前轮 */ }
    else if (header.ExtId == 0x202) { /* 处理右前轮 */ }
    // ... 更多 else if
}
```

**痛点**：
- 中断占用时间长
- 代码维护困难
- 业务逻辑与硬件中断耦合

**本模块解决方案**：哈希表 + 链表 + 回调函数，实现 O(1) 平均查找时间，支持动态设备管理和掩码匹配。

---

## 2. 核心设计

### 2.1 数据结构

```
can_table[can] → hash_table[2] → bucket[0...n] → can_node → can_node → NULL
                                    ↑
                               ID 相同的节点链表
```

**核心结构体**：

```c
typedef struct can_node {
    void *can_data;          // 设备对象指针（如 Motor_t*）
    uint32_t id;             // 期望的 CAN ID
    uint32_t id_mask;        // ID 掩码
    can_callback_t callback; // 回调函数
    struct can_node *next;   // 链表后继
} can_node_t;
```

### 2.2 掩码机制

匹配逻辑：`node->id == (received_id & node->id_mask)`

**应用场景**：电机反馈 ID 高 24 位是动态错误码，低 8 位是设备 ID。

```c
// 只匹配低 8 位（设备 ID）
uint32_t device_id = 0x01;
uint32_t mask = 0x000000FF;

// 0x123401 & 0xFF = 0x01 → 匹配成功
```

**掩码速查**：

| 场景 | 掩码 |
|------|------|
| 全匹配 | `0x1FFFFFFF` (扩展帧) |
| 低 8 位 | `0x000000FF` |
| 低 4 位 | `0x0000000F` |

### 2.3 工作流程

```
硬件 FIFO → 中断 → 哈希查表(ID % len) → 链表遍历 → 执行回调
```

---

## 3. 快速使用

### 3.1 初始化

```c
// 标准帧表 13 桶，扩展帧表 31 桶
can_list_add_can(can1_selected, 13, 31);
```

### 3.2 定义回调

```c
static void motor_callback(void *node_obj, can_rx_header_t *header, uint8_t *data) {
    Motor_t *motor = (Motor_t *)node_obj;
    motor->angle = (data[0] << 8) | data[1];
    motor->speed = (data[2] << 8) | data[3];
}
```

### 3.3 注册设备

```c
can_list_add_new_node(
    can1_selected,           // CAN 外设
    &motor1,                 // 设备对象
    0x201,                   // CAN ID
    0x1FFFFFFF,              // 掩码（全匹配）
    CAN_ID_STD,              // 标准帧
    motor_callback           // 回调函数
);
```

### 3.4 完整示例

```c
typedef struct {
    uint16_t angle;
    int16_t speed;
} Motor_t;

static Motor_t motor1 = {0};

static void motor_callback(void *node_obj, can_rx_header_t *header, uint8_t *data) {
    Motor_t *motor = (Motor_t *)node_obj;
    motor->angle = (data[0] << 8) | data[1];
    motor->speed = (data[2] << 8) | data[3];
}

void app_init(void) {
    can_list_add_can(can1_selected, 13, 31);
    can_list_add_new_node(can1_selected, &motor1, 0x201, 0x1FFFFFFF, CAN_ID_STD, motor_callback);
}
```

---

## 4. API 速查

| 函数 | 说明 |
|------|------|
| `can_list_add_can(can, std_len, ext_len)` | 初始化 CAN 实例 |
| `can_list_add_new_node(...)` | 注册设备节点 |
| `can_list_del_node_by_id(...)` | 删除节点 |
| `can_list_change_callback(...)` | 更改回调 |

---

## 5. 硬件架构

### 5.1 数据流向

![CAN 硬件架构](./Pictures/CAN1.png)

- **发送端**：CPU 写入发送邮箱（Mailbox 0/1/2），优先级由 ID 决定
- **接收端**：报文通过 GPIO 进入过滤器
- **过滤器**：14 个过滤器决定哪些报文进入 FIFO
- **接收 FIFO**：2 个 FIFO，各 3 级邮箱，缓存最多 6 帧

### 5.2 测试模式

![CAN 测试模式](./Pictures/CAN2.png)

| 模式 | 说明 |
|------|------|
| 静默模式 | 只接收不发送，用于监听 |
| 环回模式 | 自发自收，用于自测 |
| 环回静默 | 不影响总线的自测 |

### 5.3 工作模式

![CAN 工作模式](./Pictures/CAN3.png)

- **初始化模式**：配置参数时进入
- **正常模式**：收发报文的正常工作状态
- **睡眠模式**：低功耗状态

### 5.4 中断系统

![CAN 中断系统](./Pictures/CAN4.png)

- **发送中断**：邮箱变空时产生
- **FIFO 中断**：新报文、FIFO 满、溢出
- **错误中断**：处理出错、唤醒、睡眠事件

---

## 6. 配置宏与 API

### 6.1 配置宏

| 宏定义 | 默认值 | 说明 |
|--------|--------|------|
| `CAN_LIST_USE_FDCAN` | 0 | 1=启用 FDCAN，0=启用 bxCAN。STM32 HAL 库的 bxCAN 与 FDCAN 互不兼容，但本模块代码兼容两者 |
| `CAN_LIST_MAX_CAN_NUMBER` | 3 | 最大支持的 CAN 外设数量，防止缓冲区溢出 |
| `CAN_LIST_USE_RTOS` | 1 | 1=使用 FreeRTOS 任务处理 CAN 消息，加快中断退出时间；0=中断内直接处理 |
| `CAN_LIST_QUEUE_LENGTH` | 5 | FreeRTOS 消息队列长度 |
| `CAN_LIST_TASK_PRIORITY` | 2 | FreeRTOS 任务优先级 |
| `CAN_LIST_MALLOC` | `malloc` | 内存分配函数，可自定义 |
| `CAN_LIST_FREE` | `free` | 内存释放函数，可自定义 |

> **注意**：
> - 启用 RTOS 时，CAN 中断优先级**不能高于** FreeRTOS 可管理的优先级
> - 使用 `can_list_add_can` 时，必须在 `vTaskStartScheduler()` 之后调用

### 6.2 API 详解

#### `can_list_add_can`
添加一个 CAN 实例，初始化其哈希表。

```c
uint8_t can_list_add_can(can_selected_t can_select, uint32_t std_len, uint32_t ext_len);
```

| 参数 | 说明 |
|------|------|
| `can_select` | CAN 外设选择（如 `can1_selected`） |
| `std_len` | 标准帧哈希表桶数，根据 ID 分布设置（设为 1 退化为链表） |
| `ext_len` | 扩展帧哈希表桶数，根据 ID 分布设置（设为 1 退化为链表） |

#### `can_list_add_new_node`
注册设备节点，绑定 ID、掩码、设备指针和回调函数。

```c
uint8_t can_list_add_new_node(
    can_selected_t can_select,
    void *node_ptr,           // 设备指针，收到数据后传入回调
    uint32_t id,              // 设备反馈 CAN ID
    uint32_t id_mask,         // ID 掩码
    uint32_t id_type,         // CAN_ID_STD 或 CAN_ID_EXT
    can_callback_t callback   // 回调函数（不能为空！）
);
```

#### `can_list_del_node_by_id`
通过 ID 删除已注册的设备节点。

```c
uint8_t can_list_del_node_by_id(can_selected_t can_select, uint32_t id_type, uint32_t id);
```

#### `can_list_change_callback`
通过 ID 动态更改回调函数。

```c
uint8_t can_list_change_callback(can_selected_t can_select, uint32_t id_type, uint32_t id, can_callback_t new_callback);
```

### 6.3 回调函数类型

```c
typedef void (*can_callback_t)(void *node_obj, can_rx_header_t *header, uint8_t *data);
```

| 参数 | 说明 |
|------|------|
| `node_obj` | 注册时传入的设备指针 |
| `header` | CAN 消息头（包含 ID、ID 类型、数据长度等） |
| `data` | CAN 数据负载（8 字节） |
