# Implementation 文档索引

## 概述

本目录包含 AgentOS 的可落地工程实现规划，从仓库结构到具体开发任务，提供完整的实施路线图。

---

## 文档列表

### [01_repo_structure.md](./01_repo_structure.md)

**仓库结构设计**

定义项目的目录组织和模块划分：
- Monorepo vs Polyrepo 选择（推荐 Monorepo）
- 完整的目录结构
- 各 package/app 的职责说明
- 依赖管理策略
- 开发工具配置

**适用于**: 项目初始化阶段

---

### [02_module_breakdown.md](./02_module_breakdown.md)

**模块拆解与依赖**

将系统拆解为可独立开发的模块：
- 9 个核心模块定义
- 模块依赖图
- 每个模块的输入输出
- 优先级排序（P0/P1/P2）
- 并行开发可能性
- 工作量估算

**关键模块**:
- M1: core (核心抽象)
- M2: storage (存储层)
- M3: providers (LLM 提供者)
- M4: channels (渠道适配器)
- M5: tools (工具系统)
- M6: runtime (Agent 运行时)
- M7: cli (命令行应用)
- M8: server (HTTP 服务器)
- M9: orchestrator (编排服务)

**适用于**: 架构设计和任务分配

---

### [03_interfaces_and_contracts.md](./03_interfaces_and_contracts.md)

**接口与契约定义**

详细定义系统中所有关键接口：
- Session Service (会话管理)
- Routing Service (消息路由)
- Tool Registry (工具注册)
- Execution Runtime (执行运行时)
- Policy Engine (策略引擎)
- Skills Loader (技能加载)
- Channel Adapters (渠道适配)
- Event Bus (事件总线)
- State Store (状态存储)
- Artifact Store (产出物存储)

每个接口包含：
- 方法签名
- 参数说明
- 返回值定义
- 异常处理
- 并发安全性
- 实现要点

**适用于**: 详细设计和编码阶段

---

### [04_mvp_build_plan.md](./04_mvp_build_plan.md)

**MVP 构建计划**

6 周迭代计划，每周明确交付：

**Week 1: 基础设施**
- 项目骨架
- core 包
- storage 包基础

**Week 2: LLM 集成**
- providers 包
- tools 包（3 个核心工具）

**Week 3: Agent 运行时**
- runtime 包
- Agent Loop 实现

**Week 4: CLI 应用**
- channels 包（CLI）
- cli 应用

**Week 5: 完善与优化**
- Bug 修复
- 性能优化
- 文档完善

**Week 6: 发布准备**
- 发布工程
- 安全审查
- v0.1.0 发布

每周包含：
- 具体任务
- 交付物
- 验收标准
- 风险点

**适用于**: 项目管理和进度跟踪

---

### [05_test_strategy.md](./05_test_strategy.md)

**测试策略**

完整的测试方法论：

**测试金字塔**:
- 单元测试 (70%)
- 集成测试 (25%)
- E2E 测试 (5%)

**特殊测试**:
- Agent 行为测试（使用 Mock LLM）
- 工具沙箱测试
- 并发安全测试
- 性能测试
- 安全测试

**测试工具**:
- pytest + pytest-asyncio
- pytest-cov (覆盖率)
- pytest-mock (mock)
- locust (压力测试)

**测试数据**:
- Fixtures 设计
- Mock 策略
- 测试数据生成

**适用于**: 质量保证和测试实施

---

### [06_risk_register.md](./06_risk_register.md)

**风险登记表**

识别和管理项目风险：

**技术风险**:
- R1.1: LLM 不确定性 🔴
- R1.2: 并发控制复杂 🟡
- R1.3: 依赖库版本冲突 🟡
- R1.4: 内存泄漏 🟡

**架构风险**:
- R2.1: 单进程无法扩展 🟡
- R2.2: 文件存储性能不足 🟢
- R2.3: 模块耦合 🟡

**安全风险**:
- R3.1: 工具执行攻击 🔴
- R3.2: Prompt injection 🔴
- R3.3: 数据泄露 🟡

**可运维性风险**:
- R4.1: 调试困难 🟡
- R4.2: 配置复杂 🟢
- R4.3: 升级困难 🟡

**复杂度风险**:
- R5.1: 状态管理复杂 🟡
- R5.2: 错误处理不完善 🟡
- R5.3: 文档不足 🟢

每个风险包含：
- 描述
- 影响和可能性
- 缓解策略
- 监控指标
- 触发条件

**适用于**: 风险管理和决策支持

---

### [07_first_tasks.md](./07_first_tasks.md)

**首批开发任务**

可直接执行的任务清单：

**Phase 1: 项目初始化**
- Task 1.1: 创建 Monorepo 结构
- Task 1.2: 配置 CI/CD

**Phase 2: Core 包实现**
- Task 2.1: 定义核心抽象类
- Task 2.2: 定义数据模型
- Task 2.3: 定义异常体系

**Phase 3: Storage 包实现**
- Task 3.1: 实现 FileSessionStore
- Task 3.2: 实现 FileWorkspaceManager
- Task 3.3: 编写存储测试

**Phase 4: Providers 包实现**
- Task 4.1: 实现 LiteLLMProvider
- Task 4.2: 实现配置加载
- Task 4.3: 编写 Provider 测试

**Phase 5: Tools 包实现**
- Task 5.1: 实现 BaseTool
- Task 5.2: 实现文件工具
- Task 5.3: 实现 Shell 工具
- Task 5.4: 实现 ToolRegistry

每个任务包含：
- 背景
- 目标
- 依赖
- 输入输出
- 详细步骤
- 完成标准
- 验收命令

**适用于**: 开发执行阶段

---

## 使用指南

### 场景 1: 启动新项目

**推荐阅读顺序**:
1. `01_repo_structure.md` - 了解项目组织
2. `02_module_breakdown.md` - 理解模块划分
3. `04_mvp_build_plan.md` - 制定开发计划
4. `07_first_tasks.md` - 开始执行

### 场景 2: 详细设计

**推荐阅读顺序**:
1. `02_module_breakdown.md` - 模块职责
2. `03_interfaces_and_contracts.md` - 接口定义
3. `05_test_strategy.md` - 测试设计

### 场景 3: 风险评估

**推荐使用**:
1. `06_risk_register.md` - 识别风险
2. `04_mvp_build_plan.md` - 评估进度风险
3. `05_test_strategy.md` - 评估质量风险

### 场景 4: 开发执行

**推荐使用**:
1. `07_first_tasks.md` - 任务清单
2. `03_interfaces_and_contracts.md` - 接口参考
3. `05_test_strategy.md` - 测试指导

---

## 与其他文档的关系

```
docs/
├── system-design/          # 项目分析（nanobot）
│   └── 理解现有系统
│
├── blueprint/              # 通用蓝图
│   └── 设计原则和模式
│
└── implementation/         # 实施规划（本目录）
    └── 具体执行计划
```

**关系**:
- `system-design` → 分析 nanobot 的实现
- `blueprint` → 提炼通用设计原则
- `implementation` → 应用原则到新项目

**建议**:
- 学习阶段: 先读 `system-design` 和 `blueprint`
- 实施阶段: 重点读 `implementation`
- 决策阶段: 对照三者

---

## 关键决策记录

### 决策 1: Monorepo

**选择**: Monorepo
**原因**:
- 早期快速迭代
- 统一版本管理
- 代码共享容易

**何时重新评估**: 团队 > 10 人

### 决策 2: 文件系统存储

**选择**: 文件系统（JSONL + Markdown）
**原因**:
- 零依赖
- 简单透明
- 适合 MVP

**何时重新评估**: 会话数 > 1000

### 决策 3: 全局锁

**选择**: 单个 asyncio.Lock
**原因**:
- 简单正确
- 避免竞态
- 适合低并发

**何时重新评估**: 并发用户 > 10

### 决策 4: LiteLLM

**选择**: LiteLLM 作为主要 provider
**原因**:
- 支持 20+ providers
- 社区维护
- 快速支持新模型

**何时重新评估**: 性能成为瓶颈

---

## 开发检查清单

### 开始开发前

- [ ] 阅读 `01_repo_structure.md`
- [ ] 阅读 `02_module_breakdown.md`
- [ ] 阅读 `03_interfaces_and_contracts.md`
- [ ] 理解模块依赖关系
- [ ] 确认开发环境（Python 3.10+, Poetry）

### 实现模块时

- [ ] 先定义接口（抽象类）
- [ ] 再实现具体类
- [ ] 编写单元测试
- [ ] 编写文档字符串
- [ ] 通过类型检查（mypy）
- [ ] 通过代码检查（ruff, black）

### 完成模块后

- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 文档完整
- [ ] Code review
- [ ] 更新 CHANGELOG

### 发布前

- [ ] 所有测试通过
- [ ] 文档完整
- [ ] 安全审查
- [ ] 性能测试
- [ ] 用户验收测试

---

## 常见问题

### Q1: 为什么不直接用 LangChain?

**A**:
- LangChain 功能丰富但复杂
- 我们需要更轻量、可控的实现
- 学习和定制成本高
- 但可以参考其设计

### Q2: 为什么不用数据库?

**A**:
- MVP 阶段文件系统足够
- 零依赖，部署简单
- 后期可以迁移
- 已预留抽象接口

### Q3: 如何保证 LLM 输出质量?

**A**:
- 精心设计 prompt
- 输出验证
- 重试机制
- 用户确认关键操作
- 参考 `06_risk_register.md` R1.1

### Q4: 如何处理并发?

**A**:
- MVP: 全局锁（简单正确）
- 后期: 会话级锁（性能优化）
- 参考 `06_risk_register.md` R1.2

### Q5: 如何测试 Agent 行为?

**A**:
- 使用 Mock LLM
- 快照测试
- 属性测试
- 参考 `05_test_strategy.md`

---

## 下一步

1. **如果要开始实施**:
   - 执行 `07_first_tasks.md` 中的任务
   - 按 `04_mvp_build_plan.md` 的周计划推进

2. **如果要深入设计**:
   - 细化 `03_interfaces_and_contracts.md` 中的接口
   - 补充更多实现细节

3. **如果要评估风险**:
   - 审查 `06_risk_register.md`
   - 制定缓解计划

4. **如果要调整计划**:
   - 根据实际情况调整 `04_mvp_build_plan.md`
   - 更新任务优先级

---

## 贡献

如果在实施过程中发现：
- 任务拆解不合理
- 接口设计有问题
- 风险遗漏
- 更好的实现方案

欢迎更新这些文档。

---

## 总结

这套实施文档提供了从零到 MVP 的完整路线图：

1. **结构清晰**: 7 个文档覆盖所有方面
2. **可执行**: 任务粒度适合直接开发
3. **风险可控**: 识别并缓解主要风险
4. **质量保证**: 完整的测试策略
5. **渐进式**: 从简单到复杂，可演进

关键是：**先做出来，再优化**。

祝开发顺利！
