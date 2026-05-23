# 水排序谜题 (Water Sort Puzzle)

## 概述

基于 pygame 开发的水排序谜题游戏。8 个瓶子，5 层刻度，7 种颜色，玩家通过点击选择瓶子并将顶层颜色倒入匹配颜色的目标瓶子中，最终使每个瓶子只含一种颜色。

## 环境依赖 / Requirements

| Dependency | Version |
|------------|---------|
| Python | >= 3.10 |
| pygame | >= 2.0 |
| uv | latest |

## 运行方式 / How to Run

```bash
# 安装 uv（如未安装）/ Install uv if needed
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 安装依赖并运行 / Install deps and run
cd dao_rong_ye
uv sync
uv run python water_sort.py
```
```

## 游戏规则

### 基本设定
- 8 个瓶子，每个瓶子被刻度分为 5 部分
- 游戏使用 7 种颜色，每种颜色恰好 4 格
- 开局：2 个空瓶，其余瓶子随机填入颜色
- 共计 7×4 = 28 个有色格子 + 12 个空位

### 操作规则
1. 点击一个瓶子选中它（高亮显示）
2. 点击另一个瓶子作为目标
3. 倒入条件：**目标瓶子有空间 且（目标为空 或 选定瓶子的顶层颜色与目标瓶子顶层颜色相同）**
4. 倒入量：选定瓶子顶层所有连续同色格子

### 胜利条件
- 每个瓶子只包含一种颜色（或为空瓶）

### 操作提示
- 鼠标点击选择/倒入
- `R` 键重新生成谜题
- `ESC` 键退出

## 文件结构

```
dao_rong_ye/
├── water_sort.py    # 主游戏文件
└── README.md        # 本文档
```

## 核心设计

### 数据结构
```python
bottles: List[List[Optional[int]]]
# 8个瓶子，每个瓶子是长度为5的列表
# None 表示空格，0-6 表示7种颜色
# 索引0=瓶底，索引4=瓶口（顶层）
```

### 顶层颜色检测
从瓶口向下扫描，找到第一个非空颜色，并统计连续同色数量。

### 谜题生成
- 7 种颜色 × 4 格 = 28 格
- 随机打散后填入 6 个瓶子（5 瓶满 + 1 瓶 3 格）
- 2 个瓶子保持全空
- 生成后随机打乱瓶子排列顺序

### 倒酒逻辑
```
if src_top is not None and dst_space > 0 and (dst_top is None or dst_top == src_top):
    pour_count = min(src_top_count, dst_space)
    # 从src顶部移除 pour_count 格
    # 加入dst底部空位
```

## 可解性保证

每局生成后经 BFS 验证（50000 状态上限），可解率 100%。落选谜题自动重试，确保所有呈现给玩家的谜题均可解。

## 技术说明

- 分辨率：800×600
- 帧率：60 FPS
- 颜色数：7（红、橙、黄、绿、青、蓝、紫）
- 瓶子布局：2 行 × 4 列
- 每格高度：(260-20)/5 = 48px
