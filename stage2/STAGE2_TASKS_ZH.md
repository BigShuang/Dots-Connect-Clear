# Stage 2 任务书——用 Class 构建 Dot 与 Companion

## 1. 学习目标与任务顺序

Stage 2 不要求学生修改 GUI、动画、重力、计分或 Factory。学生在小型 class
和方法中实现核心算法，并观察不同对象如何合作产生完整游戏能力。

本阶段先学习一个独立的特殊 Dot，再建立所有 Companion 共用的充能基础。
之后，每个 Companion 都紧挨它所创建的 Dot，作为一组完成：

```text
TODO 1.1  FlowerDot：特殊 Dot 入门

TODO 2.1  统计 CompanionDot
TODO 2.2  AbstractCompanion.add_charge
TODO 2.3  StarDot
TODO 2.4  StarCompanion
            ↓ 完成第一组充能能力并运行

TODO 3.1  SwirlDot
TODO 3.2  EskimoCompanion
            ↓ 完成第二组能力并运行

TODO 4.1  BeamDot
TODO 4.2  CaptainCompanion
            ↓ 完成第三组能力并运行

TODO 5.1  TurtleDot
Extension 5.2  AnchorDot
```

顺序原则：

- Companion 的统计和充能基础位于所有具体 Companion 及其关联 Dot 之前；
- 每组先实现 Dot 自己的效果，再实现创建它的 Companion；
- 后面的 TODO 可以依赖前面的 TODO，前面的 TODO 不依赖后面的 TODO；
- 2.1–2.4 是一个完整教学组，中间任务用独立测试验证，完成 2.4 后再运行 GUI；
- 3.1–3.2 和 4.1–4.2 同样以“完成一组、运行一次”为检查点。

代码标记：

- `TODO X`：学生需要完成；
- `For X`：已经实现、用于支持任务 X；
- 没有标记：游戏原有支持代码。

## 2. 已提供的基础

所有 Dot 都继承 `AbstractDot`，共同拥有 `kind`、`connectable`、
`asset_family` 和 `activate(grid, position)`。

学生可以使用以下棋盘操作：

```python
grid.rows
grid.columns
grid.in_bounds(position)
grid.positions()
grid.dot_at(position)
grid.set_dot(position, dot)
grid.is_blocked(position)
```

Factory 是 `For` 支持代码。学生只需使用统一入口：

```python
grid.factory.create_dot(kind="blue", dot_type=StarDot)
grid.factory.create_dot(kind="blue", dot_type=SwirlDot)
grid.factory.create_dot(kind="blue", dot_type=BeamDot, direction="cross")
```

## 3. 第一阶段——特殊 Dot 入门

### TODO 1.1——FlowerDot

Flower 消除自己以及上、下、左、右四个位置，不影响斜对角。

在 `FlowerDot.activate` 中：

1. 拆分 `row` 和 `column`；
2. 建立四个方向变化量；
3. 用循环计算邻居位置；
4. 用 `grid.in_bounds` 跳过棋盘外位置；
5. 返回包含自身和有效邻居的 set。

不要调用 `grid.neighbours`，因为坐标计算和边界判断就是本任务的核心。
当前默认 config 可以直接观察 Flower：中央位置影响 5 格，角落影响 3 格。

## 4. 第二阶段——Companion 基础与 Star 第一组能力

这一组先建立所有 Companion 共用的工作流程，再完成第一种具体能力：

```text
移除 CompanionDot → 统计数量 → 增加 charge
→ 充满并清零 → StarCompanion 创建 StarDot → StarDot 同色全消
```

### TODO 2.1——统计最终移除的 CompanionDot

`CompanionDot` 的 class 和素材是 `For 2.1`。在
`DotGame.count_companion_dots(positions)` 中：

1. 只遍历最终移除位置；
2. 取得每个位置的 Dot；
3. 使用 `isinstance(dot, CompanionDot)` 判断类型；
4. 累加并返回数量。

被 Flower 等范围效果间接移除的 CompanionDot 也必须计数；最终移除集合以外
的对象不能计数。完成后运行该方法的独立测试。

### TODO 2.2——AbstractCompanion.add_charge

实现所有 Companion 共用的状态逻辑：

1. 根据 `amount` 逐点增加 `self.charge`；
2. 每次达到 `charge_limit` 时清零；
3. 调用子类的 `activate(grid, excluded)`；
4. 统计并返回本次激活次数。

事件通知和进度条更新是 `For`。本任务使用测试替身验证累加、触发、清零和
多次触发，不需要调用尚未完成的 StarCompanion。

### TODO 2.3——StarDot

Star 被连接后，消除棋盘上全部与自己同色的 Dot。在 `StarDot.activate` 中：

1. 遍历 `grid.positions()`；
2. 取得每个位置的 Dot；
3. 跳过空格；
4. 比较 `dot.kind` 与 `self.kind`；
5. 收集并返回全部匹配位置。

不要调用 `positions_of_kind`，因为遍历和筛选是本任务的核心。完成后先运行
StarDot 的小测试；Star 在本组中由下一任务的 StarCompanion 创建。

### TODO 2.4——StarCompanion.activate

实现第一种具体 Companion：

1. 遍历棋盘并排除本回合即将删除的位置；
2. 收集存活且可连接的 Dot；
3. 没有候选时安全结束；
4. 随机选择一个候选位置；
5. 保留原 Dot 的颜色；
6. 通过 Factory 创建同色 `StarDot` 并替换原位置。

完成后启用 config 的“TODO 2.1–2.4”配置，观察本组的完整充能链。StarDot
不会随机补充，只会由 StarCompanion 创建，因此来源清楚。

## 5. 第三阶段——Swirl 与 Eskimo 第二组能力

### TODO 3.1——SwirlDot

Swirl 激活后，将周围八格的可连接 Dot 改成自己的颜色，只移除自身：

1. 用两个循环遍历 `-1、0、1` 的行列变化；
2. 跳过 `(0, 0)`、越界位置、空格和不可连接对象；
3. 修改邻居 Dot 的 `kind`；
4. 返回只包含 Swirl 自身的位置集合。

只改变颜色，不替换 class。例如 StarDot 改色后仍然是 StarDot。完成后运行
SwirlDot 的独立测试。

### TODO 3.2——EskimoCompanion.activate

根据 StarCompanion 的经验独立实现第二个子类：

- 收集未被排除的存活、可连接 Dot；
- 随机选择最多 `swirl_count` 个位置；
- 候选不足时只选择已有候选；
- 保留原颜色并通过 Factory 创建 `SwirlDot`。

完成后启用“TODO 3.1–3.2”配置。Swirl 只由 EskimoCompanion 创建。

## 6. 第四阶段——Beam 与 Captain 第三组能力

### TODO 4.1——BeamDot

完成一个完整但简单的 `BeamDot` class：

- 保存 `kind` 和 `direction`；
- 合法方向为 `horizontal`、`vertical`、`cross`；
- 非法方向抛出 `ValueError`；
- `asset_variant` 等于方向；
- horizontal 返回整行，vertical 返回整列，cross 返回两者并集；
- 使用普通循环收集位置。

Beam 内部不随机。Factory 的 `For 4.1` 代码负责在未指定方向时随机选择。
完成后先运行 BeamDot 的方向测试。

### TODO 4.2——CaptainCompanion.activate

Captain 综合使用前面的 Companion 和 Beam 知识：

1. 收集未被排除的候选 Dot；
2. 随机选择最多 `beam_count` 个位置；
3. 为每个位置随机选择一个合法方向；
4. 保留原颜色；
5. 通过 Factory 创建 `BeamDot`。

完成后启用“TODO 4.1–4.2”配置。Beam 只由 CaptainCompanion 创建。

## 7. 第五阶段——状态与生命周期拓展

### TODO 5.1——TurtleDot.take_hit

Turtle 不可直接连接，并拥有两点耐久：

- 创建时显示 `turtle`；
- 第一次范围命中后改为 `shell`，返回 `False`；
- 第二次命中后返回 `True`，通知 Game 删除它。

学生在一个 class 内完成构造和 `take_hit`，不需要 property 或多层耐久父类。
`ShellDot` 是 `For 5.1` 示例。启用对应 config，用已经完成的 Flower 连续命中。

### Extension 5.2——AnchorDot.has_landed

Anchor 不可连接，会随重力下降。它从当前位置下一行开始扫描：下方还存在可玩
位置则返回 `False`，否则返回 `True`。Game 在重力完成后根据结果收集 Anchor。

## 8. For Extension 示例

`WildcardDot` 与 `BuffaloCompanion` 是完整 `For` 示例，不是学生 TODO。
它们展示第四种“关联 Dot + Companion”组合，可用于比较和自主拓展。

## 9. 运行与验收

每完成一个独立任务先运行测试；完成一个能力组后，再启用 config 中对应配置
启动 GUI：

```powershell
python -m unittest discover -s stage2/tests -v
python stage2/a3.py
```

检查：

- 35 个模型测试全部通过；
- 每个能力组能独立运行，不依赖后面的未完成 TODO；
- 特殊 Dot 由对应 Companion 创建，不在该组配置中随机生成；
- 学生能说明每个 class 负责创建对象、改变状态，还是计算移除位置。
