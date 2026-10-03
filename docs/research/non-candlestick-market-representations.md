# 非 K 线市场表示与“市场实体”研究地图

> 研究日期：2026-10-03  
> 目的：系统梳理“不以传统 K 线为核心对象”的市场研究路线，并回答：每一种 representation（表示）已经识别出了哪些市场实体；哪些实体适合进入 Market Entity Discovery 项目；哪些方向仍有较大的自动发现空间。

---

## 0. 结论先行

这次调研后的核心认识是：

> **“分时图研究”并不是一条单独流派，而是一组不同的市场表示。**

传统 K 线把连续交易过程压缩成固定时间窗口中的：

```
Open / High / Low / Close
```

但市场还可以被表示为：

1. **价格轨迹（Price Trajectory）**：只看价格路径怎么走。
2. **Swing / Pivot 结构**：只保留显著高低点与推动/回调。
3. **价格 × 时间（TPO / Market Profile）**：看市场在哪些价格停留、接受或拒绝。
4. **价格 × 成交量（Volume Profile）**：看成交量分布在哪些价格。
5. **Tape / Transaction Sequence**：按逐笔成交序列研究买卖方向、速度、持续性。
6. **Order Flow**：研究主动买卖、订单流不平衡、价格冲击。
7. **LOB / MBO（订单簿 / 逐订单）**：研究挂单深度、队列、撤单、成交和盘口状态。
8. **事件时间 / 信息驱动采样**：不再按固定分钟切市场，而让“市场事件”决定什么时候产生一个观测。

因此项目的统一形式应该从：

```
Market → one representation → entity
```

升级为：

```
Market
  ↓
multiple representations
  ├─ price trajectory
  ├─ swing / directional change
  ├─ price-time profile
  ├─ price-volume profile
  ├─ trade sequence
  ├─ order flow
  └─ order book
  ↓
entities at multiple scales
  ↓
cross-view relations
  ↓
market theory
```

**Representation 决定“什么东西能够被发现”。**

---

# 1. 一张总表

| 表示层 | 基本对象 | 典型时间尺度 | 已经明确存在的实体 | 学术成熟度 | 对本项目价值 |
|---|---|---:|---|---|---|
| Price trajectory | 连续价格路径 | 秒～月 | acceleration、stall、breakout、retest、trajectory motif | 中 | 很高 |
| Swing / Pivot / Directional Change | 显著极值与方向变化事件 | 秒～月 | drawup、drawdown、DC event、overshoot、HH/HL/LH/LL | 高（DC）/中低（传统 swing） | 极高 |
| TPO / Market Profile | price × time distribution | 日内～多日 | POC、Value Area、single prints、balance/imbalance、profile shape | 实务强、严格学术验证有限 | 高 |
| Volume Profile | price × traded volume | 日内～多日 | VPOC、HVN、LVN、volume distribution shape | 实务强、严格学术验证有限 | 高 |
| Tape / trade sequence | 每笔成交 | 毫秒～小时 | signed trade run、trade-intensity burst、persistent order flow | 高 | 极高 |
| Order Flow | 限价/市价/撤单的净压力 | 毫秒～分钟 | OFI、trade imbalance、flow toxicity、price impact state | 很高（OFI 等） | 极高 |
| LOB | 多档 bid/ask 状态 | 微秒～秒 | spread、queue imbalance、depth shape、microprice、depletion/resilience | 很高 | 极高，但数据成本高 |
| MBO | 单个订单事件 | 微秒～秒 | individual-order sequence、queue position、cancel/execute pattern | 中高、较新 | 长期价值极高 |
| Event/information time | 事件而非分钟 | 自适应 | volume/tick/dollar events、imbalance/run bars、DC states | DC 证据较强；部分方法主要来自实务/书籍 | 高 |

这里最重要的不是“哪一种最好”，而是这些表示暴露的是**不同类型的实体**。

---

# 2. Price Trajectory：把市场看成一条路径

## 2.1 它研究什么

最直接的表示：

[
P(t)
]

不关心一根 K 的 OHLC，而关心：

```
价格从哪里来
→ 怎么加速
→ 在哪里停顿
→ 是否继续推进
→ 是否回撤
→ 是否重新恢复
```

这正是我们前面分析 Tyler Durden 那张手绘曲线时看到的东西：

```
Compression
→ Expansion
→ Failure to Progress
→ Breakdown
→ Failed Recovery
→ Continuation
```

这些结构不要求每个阶段持续相同根数，也不要求绝对涨跌幅相同。

## 2.2 已经存在的理论/实体

### Opening Range / Opening Range Breakout

这是典型的“路径 + 位置 + 时间”实体：

```
open
→ initial range
→ escape from range
→ follow-through / failure / retest
```

2013 年 Finance Research Letters 有对 Opening Range Breakout 的机械规则研究；2019 年 IEEE Access 进一步在指数期货的一分钟数据上研究 Timely ORB。

重要的是：ORB 的对象不是某一根 K，而是**一段日内路径相对于 opening range 的关系**。

### Trajectory Motif / Shape Pattern

金融 motif 文献会寻找：

- sharp rise → slow decline
- gradual rise
- recurring shape
- chart-pattern-like subsequences

2021 年的 SLIM 工作结合 SAX、MDL 和 Matrix Profile，明确讨论了金融序列中不同长度 motif 的问题。

## 2.3 对我们的启发

Price trajectory 适合发现：

```
FastRise
SlowRise
Acceleration
Deceleration
Stall
FailedBreakout
Retest
Recovery
Collapse
```

但如果直接用固定窗口 Euclidean distance，常会把：

- 时间长度不同
- 速度不同
- 局部错位

的相同结构判成不同。

因此 trajectory branch 更适合：

- DTW
- multi-scale Matrix Profile
- variable-length motif
- learned embedding
- 或先做 swing / directional-change 压缩

---

# 3. Swing / Pivot / Directional Change：目前最值得优先加入的分支

这是本次调研里，**和 Market Entity Discovery 最契合的一条成熟路线**。

## 3.1 和传统 ZigZag / Swing 的关系

传统 Swing 思路：

```
High → Low → High → Low
```

进一步产生：

```
HH / HL / LH / LL
```

大量市场结构理论都隐含依赖这些 pivot。

但传统“左右各 N 根 K 确认 swing”的方法有两个问题：

1. 参数 N 决定结构粒度；
2. 使用右侧数据确认 pivot，实时使用时天然存在确认延迟，回测若处理不慎会引入 look-ahead。

因此 Swing/Pivot 必须明确区分：

```
historical geometric pivot
vs
causally confirmed pivot
```

## 3.2 Directional Change（DC）更值得关注

Directional Change / Intrinsic Time 不按固定分钟采样。

设阈值：

[
delta
]

只有价格相对最近极值反向移动超过 (delta) 时，才产生新的 Directional Change event。

于是原始价格：

```
tick tick tick tick tick tick...
```

被压成：

```
upturn
→ overshoot
→ downturn
→ overshoot
→ upturn
...
```

这和 ZigZag 很接近，但 Directional Change 已经形成了一套比较完整的 event-time 研究体系。

## 3.3 已经识别出的实体

Directional Change 明确定义了：

- directional-change event
- overshoot
- total move
- drawup / drawdown
- event duration
- event tick count
- event amplitude
- multi-threshold state

Glattfelder、Dupuis、Olsen 在 13 个 FX 汇率上发现 12 个经验 scaling laws，这些结果依赖 event-based representation，而不是固定时间 K 线。

后续 Intrinsic Network 工作又把多个 DC threshold 组合成**多尺度状态网络**，把价格轨迹离散为状态，并研究 state transition 与 liquidity/stress。

## 3.4 为什么它和我们的目标高度一致

我们的长期目标：

```
raw market
→ entity
→ state
→ transition
→ theory
```

Directional Change 已经天然提供：

```
raw price
→ intrinsic event
→ intrinsic state
→ state transition
```

也就是说它已经解决了一部分“从连续市场构造离散实体”的问题。

### 对 Market Entity Discovery 的直接建议

新增：

```
representation/directional_change.py
```

对 BTC 同时跑：

[
delta in
{0.25%, 0.5%, 1%, 2%, 4%, ...}
]

不要只取一个 threshold。

这样自然形成：

[
E^{DC}_{delta}
]

以及跨尺度关系。

**优先级：P0。**

---

# 4. TPO / Market Profile：从“价格怎么走”转为“市场在哪里停留”

## 4.1 Representation

TPO（Time Price Opportunity）不是把 volume 放在时间轴，而是统计：

[
Time at Price
]

一个 session 被切成多个时间块，每个时间块在访问过的 price level 上留下标记。

TradingView 官方文档也将 TPO 描述为一种展示价格在特定价位集中程度、以及 profile 随 session 形成过程的表示。

## 4.2 已形成的实体词汇

Market Profile / Auction Market Theory 中常见实体包括：

### Location entities

- POC（Point of Control）
- VAH / VAL（Value Area High / Low）
- Initial Balance
- single prints / tails

### Distribution entities

- balanced profile
- elongated / trend profile
- double distribution
- P / b 型 profile（实务术语）

### State entities

- acceptance
- rejection
- balance
- imbalance
- value migration
- initiative activity
- responsive activity

从我们的角度看，这些其实已经是非常清晰的“Market Entity ontology”。

## 4.3 学术证据要谨慎区分

这里不能把 practitioner theory 和已严格验证的经验规律混为一谈。

Market Profile 在专业期货交易中使用时间很长，但严格同行评审的系统验证相对有限。

2008 年已有对 futures Market Profile distribution 的统计研究。

2026 年出现两篇很相关、但目前属于 SSRN working paper 的研究：

1. 尝试把 Auction Market Theory 的核心概念形式化为 inventory / Hawkes / price impact 系统；
2. 用 signed futures tape 检验 initiative / responsive / absorption 一类概念。

这些很有启发，但目前不应当视为已经成熟定论。

## 4.4 对 Entity Discovery 的意义

TPO branch 可以让我们寻找的实体从：

```
path shape
```

扩展到：

```
distribution shape
```

即：

[
E = f(	ext{time-at-price distribution})
]

同一段 OHLC 路径可以形成完全不同的 TPO distribution。

**优先级：P1。**

---

# 5. Volume Profile：从时间分布换成成交量分布

## 5.1 Representation

传统 volume bar：

[
Volume(t)
]

Volume Profile：

[
Volume(p)
]

即回答：

> 交易发生在什么价格，而不是发生在什么时间。

## 5.2 已形成的实体

主要包括：

- VPOC / Volume POC
- Value Area
- HVN（High Volume Node）
- LVN（Low Volume Node）
- multi-modal profile
- distribution shape
- value migration

从 Entity Discovery 角度，它们可以数学化成：

### Local maximum

[
HVN = local maxima of V(p)
]

### Local minimum

[
LVN = local minima of V(p)
]

### Main mode

[
VPOC = argmax_p V(p)
]

于是原本大量“凭眼睛找节点”的术语，可以转成 distribution feature extraction。

## 5.3 证据边界

Volume Profile 是非常成熟的实务工具，但把：

```
HVN/LVN/VA
```

直接等价为稳定预测 edge，没有充分的统一学术证据。

2026 年一项 ES value-area breakout working paper 就发现，未过滤的 continuation signal 并没有显著经济效果。

因此我们的系统应该：

```
discover profile entity
→ validate recurrence
→ test conditional outcome
```

而不能：

```
LVN = buy/sell signal
```

**优先级：P1。**

---

# 6. Tape / Transaction Sequence：这是最纯粹的“分时”

K 线出现以前，交易者看到的就是 tape。

## 6.1 Representation

设每笔成交：

[
	au_i =
(t_i,p_i,q_i,s_i)
]

其中：

- (t_i)：时间
- (p_i)：价格
- (q_i)：数量
- (s_i)：主动买/卖方向

于是市场是一条事件序列：

```
buy 2
buy 5
buy 1
sell 8
sell 3
...
```

而不是：

```
5m candle
5m candle
...
```

## 6.2 Wyckoff / Tape Reading 的历史位置

Wyckoff 的早期 Tape Reading 已经非常明确地把：

- price
- time
- volume
- buying/selling wave

联合起来观察。

他的 wave chart 甚至会记录每个 buying/selling wave 的成交量，而不仅是固定小时 volume。

所以 Wyckoff 并不能简单归类为“研究 K 线的理论”；它有很强的 transaction / wave representation 基因。

## 6.3 现代微观结构已经确认的一类重要实体：order-flow persistence

Lillo / Farmer / Bouchaud 等工作发现：

> 买卖订单方向存在 long memory。

一个重要解释是：

```
large parent order
→ split into many smaller child orders
→ same-sign trades persist
```

这意味着 Tape 上本身存在一种非常真实的 latent entity：

[
oxed{Metaorder footprint}
]

虽然你未必能看到 parent order，但能从事件序列看到：

- same-side persistence
- execution bursts
- volume/time footprint

这类 entity 不可能从 OHLC 单独恢复。

## 6.4 对项目的价值

未来可以建立：

```
TradeSequence Entity
├─ sign persistence
├─ trade intensity
├─ size distribution
├─ inter-arrival time
├─ price response
└─ exhaustion / reversal
```

**优先级：P1/P2，取决于数据获取。**

---

# 7. Order Flow：这里已经有很扎实的学术实体

## 7.1 OFI（Order Flow Imbalance）

Cont、Kukanov、Stoikov 对 50 只美股研究限价单、市场单、撤单事件，发现短时间价格变化与 best bid/ask 上供需变化形成的 OFI 有稳定关系，并且 price-impact slope 与 market depth 反向相关。

这里的基本对象不是 K 线，而是：

```
limit order event
market order event
cancellation event
```

形成：

[
OFI_t
]

## 7.2 这意味着哪些实体已经明确存在

可以将以下视为 order-flow representation 下的候选实体：

- positive / negative OFI burst
- persistent OFI regime
- high OFI + low price response
- high OFI + high price response
- trade imbalance
- depth imbalance
- liquidity depletion
- flow reversal

特别值得研究的是：

[
rac{Delta P}{OFI}
]

因为相同的订单流压力，在不同 liquidity/depth 条件下，价格响应完全不同。

这非常接近交易者说的：

```
aggression
vs
absorption
```

但“absorption”作为严格、普适的量化实体仍应自己验证，而不能直接沿用实务标签。

## 7.3 VPIN 要特别谨慎

VPIN 试图度量 order-flow toxicity，并在 volume-time 中更新。

但关于它是否真能作为市场 stress/flash-crash 预警，学术上存在明显争论；后续研究指出其解释力可能大量来自 volatility 本身。

因此：

```
VPIN = candidate representation/feature
```

而不是：

```
VPIN = validated universal trading law
```

**优先级：P1。**

---

# 8. Limit Order Book：市场的“空间结构”

## 8.1 Representation

一个 LOB snapshot：

[
LOB_t =
{
(p^b_1,q^b_1),...,(p^b_L,q^b_L),
(p^a_1,q^a_1),...,(p^a_L,q^a_L)
}
]

这里不再只看成交价格，而是观察：

> 尚未成交的 supply / demand structure。

## 8.2 已经非常成熟的实体

### Spread

[
Spread = Ask_1-Bid_1
]

### Queue / depth imbalance

[
I=
rac{Q_{bid}-Q_{ask}}
{Q_{bid}+Q_{ask}}
]

Gould & Bonart 在 Nasdaq 股票上发现 queue imbalance 对下一次 mid-price movement 方向有显著关系，尤其对 large-tick stocks 更明显。

### Microprice

Stoikov 将：

- spread
- queue imbalance
- book state

结合形成 micro-price，作为条件于 order book 信息的短期 fair-price estimator。

### Book shape

不只 top-of-book，而是：

```
depth at level 1
depth at level 2
...
slope / convexity
asymmetry
```

### Dynamic entities

还可以研究：

- queue depletion
- replenishment
- resilience
- cancellation burst
- liquidity vacuum

## 8.3 Learned entities

DeepLOB 用 CNN 捕获 order book 的空间结构，再用 LSTM 建模时间依赖，说明：

> LOB 本身可以作为高维 representation，让模型学习 latent book states。

更近期的 LOBench 则直接把问题改写为：

```
learn reusable LOB representations
```

而不是只训练一个特定 price-direction classifier。

这和我们的思路非常一致：

```
LOB
→ representation
→ entity discovery
→ multiple downstream tests
```

**优先级：P2，因为数据量、存储和计算成本更高。**

---

# 9. MBO：比 LOB snapshot 更底层

MBO（Market By Order）保留的是单个 order instruction。

它比普通 LOB snapshot 多出了：

- individual order identity
- add
- modify / cancel
- execute
- queue evolution

2021 年 Oxford 的 MBO 深度学习研究指出，MBO 与 LOB representation 可以提供互补信息，二者 ensemble 优于单独使用其中一种。

因此：

[
LOB_t
]

并不是市场的最原始状态，它仍然是对：

[
MBO event stream
]

的聚合。

长期来看，我们的层级应该是：

```
MBO event
↓
LOB state
↓
Order Flow
↓
Trades
↓
Price trajectory
↓
Bars
```

不同层都会丢信息，也会获得新的结构可见性。

---

# 10. Event Time：可能比“分时图”本身更重要

固定时间 K 线隐含一个假设：

> 每一分钟的信息量大致同等重要。

市场显然不满足这一点。

一个晚上安静的 5 分钟和 CPI 发布后的 5 分钟，不应该天然拥有相同的信息权重。

因此另一大研究路线是：

[
physical time
ightarrow
event/intrinsic time
]

## 10.1 Directional Change

事件由：

[
|Delta P| ge delta
]

触发。

## 10.2 Tick / Volume / Dollar Bars

事件由：

[
N_{trades}
]

或：

[
sum volume
]

或：

[
sum price	imes volume
]

达到阈值触发。

## 10.3 Imbalance / Run Bars

让 order-flow imbalance / runs 决定什么时候结束一个 bar。

这里要注意证据层级：

- Directional Change 有比较丰富的同行评审文献与 scaling-law 研究；
- information-driven bars 很多实践主要来自 López de Prado 的书和开源实现，同行评审证据远少于 DC / OFI 等领域。

所以它值得实验，但不能预设“必然优于 time bars”。

---

# 11. 一个重要修正：Representation 和 Segmentation 不是一回事

我们之前容易混在一起。

其实应该分成两个独立维度。

## Representation

回答：

> 一个 observation 里保存什么信息？

例如：

- close price
- swing vector
- TPO distribution
- volume-at-price
- signed trade sequence
- LOB tensor

## Segmentation / Clock

回答：

> 什么时候切一个 observation？

例如：

- every 5 minutes
- every 1000 trades
- every $10M notional
- every directional change
- every regime change

于是可以组合：

[
Entity = Discovery(R(X), S(X))
]

其中：

- (R)：representation
- (S)：segmentation

这给我们的 Agent 一个更大的搜索空间：

```
representation × clock × scale × similarity
```

---

# 12. 把所有已知“市场实体”放到统一层级

## Level A — Trajectory entities

- acceleration
- deceleration
- breakout
- failed breakout
- retest
- recovery
- stall
- collapse

## Level B — Swing / intrinsic entities

- pivot high / low
- HH / HL / LH / LL
- directional change
- overshoot
- drawup / drawdown
- multi-scale intrinsic state

## Level C — Auction / distribution entities

- POC / VPOC
- Value Area
- HVN / LVN
- single prints
- balanced / imbalanced distribution
- value migration

## Level D — Transaction-flow entities

- signed-trade run
- metaorder footprint
- trade-intensity burst
- OFI burst
- order-flow persistence
- flow reversal
- flow toxicity candidate

## Level E — Book entities

- spread regime
- queue imbalance
- depth imbalance
- book-shape state
- microprice deviation
- queue depletion
- replenishment
- resilience state

---

# 13. 对 Market Entity Discovery 的新架构

不应该只有：

```
features/
segmentation/
matrix_profile/
```

更合理的是：

```
representations/
├── bars/
├── trajectory/
├── directional_change/
├── swing/
├── tpo/
├── volume_profile/
├── trades/
├── order_flow/
├── lob/
└── mbo/

clocks/
├── physical_time.py
├── tick_time.py
├── volume_time.py
├── dollar_time.py
├── directional_change.py
└── change_point.py

discovery/
├── matrix_profile/
├── variable_length_motif/
├── clustering/
├── density/
├── state_model/
└── representation_learning/

entities/
├── occurrence
├── prototype
├── dimensions
├── representation
├── scale
└── validation
```

实体身份需要包含：

[
E_k =
(
representation,,
clock,,
scale,,
prototype,,
occurrences
)
]

否则：

```
E001
```

这个名字本身是不完整的。

---

# 14. 建议的实验优先级

## P0 — Directional Change / Swing Path

原因：

1. 只需要现有价格数据；
2. 和 Tyler 手绘 pattern、你刚才的 TradingView line view 直接对应；
3. 天然 variable-length；
4. 已有成熟 event-based research；
5. 可做 multi-scale；
6. 非常适合 Entity → State → Transition。

第一批实体：

```
DC event
overshoot
multi-event sequence
multi-scale state
```

---

## P1 — TPO / Volume Profile

原因：

1. 数据需求仍然可控；
2. representation 与 price path 完全不同；
3. 已经有丰富的 practitioner entity ontology；
4. 很适合检测 balance / imbalance / acceptance / migration。

第一批实体：

```
profile shape
POC migration
HVN/LVN configuration
value-area transition
```

---

## P1 — Order Flow

需要交易方向或盘口事件。

优先：

```
OFI
trade imbalance
price-response / flow-response relation
```

不要一开始堆几十个 footprint pattern。

---

## P2 — LOB / MBO

最后进入，因为它需要：

- 大量数据
- event reconstruction
- exchange-specific rules
- 高存储/计算
- 严格的 timestamp / sequence integrity

但长期来看，这一层可能是自动发现新 microstructure entities 最丰富的地方。

---

# 15. 对当前 V0 的具体修改建议

当前：

```
BTCUSDT 5m
→ six features
→ m=24
→ MSTUMP
→ E001/E002
```

保留。

它成为：

[
Baseline A = Bar Representation
]

新增：

## Baseline B — Close Trajectory

```
close
→ normalize
→ motif discovery
```

## Baseline C — Directional Change

```
tick/1m close
→ DC thresholds
→ event sequence
→ entity discovery
```

## Baseline D — Swing path

```
price
→ causally confirmed pivots
→ normalized swing vector
→ structural similarity
```

之后再比较：

> 同一段真实市场行为，在不同 representation 中会被识别成什么？

这比马上加入更复杂的神经网络更重要。

---

# 16. 最重要的新研究问题

我们原来的问题是：

> 能不能自动发现新的 Market Entity？

现在应升级为：

[
oxed{
	ext{Which representation makes a stable market entity observable?}
}
]

即：

> **哪一种市场表示，能够让稳定、重复、样本外存在的实体变得可见？**

进一步：

[
R^* =
argmax_R
Q(
Discovery(R(X))
)
]

其中 (Q) 可以包含：

- recurrence
- compactness
- temporal stability
- OOS recurrence
- null-model separation
- cross-market transferability

于是 representation 本身也进入可搜索对象。

这是一个比“选哪个 clustering algorithm”更高一层的问题。

---

# 17. 参考文献与可复现资源

## Price trajectory / Opening Range

1. **Assessing the profitability of intraday opening range breakout strategies**  
   Finance Research Letters, 2013.  
   https://doi.org/10.1016/j.frl.2012.09.001

2. **Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets**  
   IEEE Access, 2019.  
   https://doi.org/10.1109/ACCESS.2019.2899177

3. **Side-Length-Independent Motif (SLIM): Motif Discovery and Volatility Analysis in Time Series**  
   https://www.mdpi.com/2571-9394/4/1/13

## Directional Change / Intrinsic Time

4. **Patterns in high-frequency FX data: discovery of 12 empirical scaling laws**  
   Quantitative Finance, 2011.  
   https://doi.org/10.1080/14697688.2010.481632  
   arXiv: https://arxiv.org/abs/0809.1040

5. **Profiling high-frequency equity price movements in directional changes**  
   Quantitative Finance, 2017.  
   https://doi.org/10.1080/14697688.2016.1164887

6. **Multi-scale representation of high frequency market liquidity**  
   Algorithmic Finance, 2016.  
   https://doi.org/10.3233/AF-160054  
   arXiv: https://arxiv.org/abs/1402.2198

7. 开源实现：**VladUZH/VlPetrov**  
   https://github.com/VladUZH/VlPetrov

## TPO / Market Profile / Auction Market Theory

8. TradingView 官方：**Time Price Opportunity charts explained**  
   https://www.tradingview.com/support/solutions/43000725590-time-price-opportunity-charts-explained/

9. TradingView 官方：**TPO indicator**  
   https://www.tradingview.com/support/solutions/43000713306-time-price-opportunity-tpo-indicator/

10. **Market Profile in Futures Markets – a Statistical Review of a Market Practitioner Tool**  
    John A. Anderson, 2008.  
    ResearchGate bibliographic record:  
    https://www.researchgate.net/publication/253235305_Market_Profile_in_Futures_Markets_-_a_Statistical_Review_of_a_Market_Practitioner_Tool

11. **Auction Market Theory as an Emergent Property of Inventory Dynamics**  
    SSRN working paper, 2026 — *尚非成熟共识，作为研究线索使用*。  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6616280

12. **Initiative and Responsive: Auction Market Theory at the Signed Tape**  
    SSRN working paper, 2026 — *尚非成熟共识，作为研究线索使用*。  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7135258

## Tape / Order-flow persistence

13. **The long memory of the efficient market**  
    Lillo & Farmer.  
    https://arxiv.org/abs/cond-mat/0311053

14. **Theory for long memory in supply and demand**  
    Physical Review E, 2005.  
    https://doi.org/10.1103/PhysRevE.71.066122

15. **How markets slowly digest changes in supply and demand**  
    Bouchaud, Farmer, Lillo.  
    https://arxiv.org/abs/0809.0822

16. Richard D. Wyckoff, **Studies in Tape Reading**  
    Google Books bibliographic copy:  
    https://books.google.com/books?id=VmENAAAAYAAJ

## Order Flow

17. **The Price Impact of Order Book Events**  
    Cont, Kukanov, Stoikov. Journal of Financial Econometrics, 2014.  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1712822  
    arXiv: https://arxiv.org/abs/1011.6402

18. **Flow Toxicity and Liquidity in a High Frequency World**  
    Easley, López de Prado, O'Hara. Review of Financial Studies, 2012.  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1695596

19. **Assessing Measures of Order Flow Toxicity and Early Warning Signals for Market Turbulence**  
    Andersen & Bondarenko. Review of Finance, 2015.  
    https://doi.org/10.1093/rof/rfu041

20. 开源：**twowaymind/orderflow-metrics**  
    https://github.com/twowaymind/orderflow-metrics

## Limit Order Book / MBO

21. **Queue Imbalance as a One-Tick-Ahead Price Predictor in a Limit Order Book**  
    Gould & Bonart.  
    https://arxiv.org/abs/1512.03492

22. **The Micro-Price: A High Frequency Estimator of Future Prices**  
    Stoikov.  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2970694  
    Code: https://github.com/sstoikov/microprice

23. **DeepLOB: Deep Convolutional Neural Networks for Limit Order Books**  
    IEEE Transactions on Signal Processing, 2019.  
    https://arxiv.org/abs/1808.03668

24. **Deep Learning for Market by Order Data**  
    Applied Mathematical Finance, 2021.  
    https://arxiv.org/abs/2102.08811

25. **Representation Learning of Limit Order Book: A Comprehensive Study and Benchmarking / LOBench**  
    arXiv, 2025.  
    https://arxiv.org/abs/2505.02139  
    Code: https://github.com/financial-simulation-lab/LOBench

## Event / information-driven sampling

26. **Directional Change**：见上面 4–7。

27. **mlfinpy information-driven bars implementation**  
    https://github.com/baobach/mlfinpy

28. **finmlkit** — tick/volume/dollar/CUSUM/imbalance/run bars 与 footprint/profile features  
    https://github.com/quantscious/finmlkit

---

# 18. 最终判断

对于我们这个项目，“非 K 线研究”不应该单独建立成一个类别。

更准确的顶层结构是：

[
oxed{
Market Entity =
f(
Representation,
Clock,
Scale,
Similarity
)
}
]

而当前最值得立刻验证的不是更复杂的深度学习，而是：

```
Bar / MSTUMP
vs
Raw Trajectory
vs
Directional Change
vs
Swing Path
```

使用完全相同的：

- Train / Validation / Test
- recurrence
- compactness
- temporal stability
- OOS matching
- null model

去比较。

如果同一类结构能在不同 representation 中独立出现，我们得到的就不再只是“某算法的 cluster”，而更接近：

[
oxed{	ext{representation-robust market entity}}
]

这应当成为 Market Entity Discovery 下一阶段最重要的标准之一。
