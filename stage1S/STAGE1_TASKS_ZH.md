# Stage 1 任务书——基础 GUI 与游戏流程

## 1. 任务目的

Stage 1 的重点是使用已经提供的支持代码，完成一个可运行的 Tkinter 应用。
学生需要理解鼠标输入如何经过控制器进入游戏模型，再由模型状态的变化驱动界面更新。本阶段不要求学生重新实现棋盘底层算法。

只有以 `# TODO 1.x`、`# TODO 2.x` 或 `# TODO 3.x` 开头的编号注释才是学生需要完成的任务。
其他普通注释和 docstring 都只是对支持代码的解释说明，不要求学生实现。

## 2. 已提供的支持代码

以下功能已经完整实现，不属于 Stage 1 的学生任务：
- 连接合法性检查和闭环检测；
- Dot 激活、消除、下落、补充和棋盘可玩性检查；
- 分数、目标、剩余步数以及胜负规则；
- 非阻塞的消除、下落和补充动画；
- Canvas 绘制、图片加载以及像素坐标到棋盘坐标的转换；
- `DotGrid`、`DotGame`、`DotFactory` 和 Dot 扩展接口。

学生需要调用这些接口并理解其运行流程，而不是复制或重写内部算法。

## 3. 按功能划分的阶段步骤

本阶段划分为`App Class`、`InfoPanel Class`、`File Menu / Popup Dialogs` 三个功能部分。

### 3.1 App Class

#### TODO 1.1 实例化 DotsApp

在 `a3.py` 中使用已经提供的 Tk 根窗口实例化 `DotsApp`，再通过 `pack()`
让主应用自动扩展并占满整个窗口。

**检查标准：** 执行 `python stage1/a3.py` 后能够出现完整应用窗口。

#### TODO 1.2 设置 GridView 布局

在 `DotsApp.__init__` 中创建并布局 `GridView`，使棋盘区域能够随窗口尺寸
变化而扩展。本步骤不创建或更新 `InfoPanel`，也不处理菜单和弹窗。

**检查标准：** 棋盘能够正常显示并随窗口扩展。

当前事件绑定、连接控制器回调和动画流程都没有 TODO 标记。相关普通注释只
用于解释已经提供的实现，不属于学生任务。

### 3.2 InfoPanel Class

#### TODO 2.1 创建剩余步数区域

创建并布局剩余步数的标题和数字标签，使用白色背景、指定文字颜色以及合适的
`Segoe UI Semibold` 字号，并使用 `pack()` 完成区域内部布局。

#### TODO 2.2 创建分数区域

创建并布局 SCORE 标题和分数数字标签，设置文字样式，并使用 `pack()` 将
标签水平排列。

#### TODO 2.3 完成 InfoPanel setters

更新已经提供的分数与剩余步数 Label。紧邻的普通代码负责把 objectives
交给 `ObjectivesView`，该部分没有 TODO 标记。

#### TODO 2.4 将 InfoPanel 加入 DotsApp

在 `DotsApp.__init__` 中创建 `InfoPanel`，并使用 `pack()` 将它放在应用顶部。

#### TODO 2.6 更新游戏状态显示

在 `DotsApp.refresh_status` 中，只读取 `DotGame` 的公开属性，并将分数、
剩余步数和目标传给 `InfoPanel` 对应的 setter。

`app.py` 中编号为 2.5 和 2.7 的注释没有 `TODO`，只解释已经提供的事件绑定
和初始刷新语句，不属于学生任务。

### 3.3 File Menu / Popup Dialogs

#### TODO 3.1 初始化菜单与窗口命令

在 `DotsApp.__init__` 中调用菜单创建方法，并注册窗口关闭协议和 New Game
快捷键。这些初始化语句全部属于第三步。

#### TODO 3.2 创建 File 菜单

在 `DotsApp._create_menu` 中创建包含 New Game 和 Exit 的 File 菜单，
把菜单项连接到已经提供的控制器回调，并将菜单栏设置到根窗口。

**检查标准：** New Game 能够重置当前游戏，`Ctrl+N` 仍然能够开始新游戏，
Exit 能够进入统一的退出确认流程。

#### TODO 3.4 确认退出应用

在 `DotsApp.confirm_exit` 中使用 Tkinter 消息框询问用户是否确认退出。
无论用户通过 File 菜单还是窗口关闭按钮退出，都必须先显示确认弹窗。

**检查标准：** 选择 No 时应用继续运行；选择 Yes 时应用关闭。

#### TODO 3.5 显示游戏结果

一回合的结算与动画完成后，根据模型公开的 `won` 和 `lost` 状态显示胜利或
失败弹窗。弹窗只负责通知结果，不应重新实现胜负判断规则。

**检查标准：** 达成全部目标时显示胜利信息；步数耗尽且目标未完成时显示
失败信息。

`new_game` 旁编号为 3.3 的注释没有 `TODO`，只解释已经提供的重置实现，
不属于学生任务。

## 4. 需要解释的完整流程

完成任务后，学生应能够解释以下调用过程：

```text
GridView 鼠标事件
→ DotsApp 回调
→ DotGame 选择与结算
→ 模型事件
→ DotsApp／GridView 刷新
→ 棋盘和 InfoPanel 更新
```

动画控制器会将一次结算拆分为消除、下落和补充三个阶段。它属于支持代码：
学生需要指出它在哪里被调用，但不需要实现它。

## 5. 完成检查清单

- 应用能够启动，并可以完成一局游戏。
- 无效连接或只选择一个 Dot 时不会消耗步数。
- 合法操作会更新棋盘、分数、剩余步数和目标。
- New Game 会同时重置模型和界面状态。
- 退出确认对话框能够正确处理 Yes 和 No。
- 游戏胜利或失败后会显示相应的结果弹窗。
- Stage 1 不加入 `IntervalBar`、特殊 Dot、Companion 或 ActionBar。
- 不删除或修改已经提供的模型、棋盘和动画实现。

## 6. 建议验证方式

从仓库根目录运行自动测试：

```powershell
python -m pytest stage1/tests
```

然后启动 GUI，逐项完成人工检查：

```powershell
python stage1/a3.py
```
