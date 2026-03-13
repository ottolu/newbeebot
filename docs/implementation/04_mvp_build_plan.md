# MVP 构建计划

## 概述

本文档将 MVP 开发拆解为 6 周的迭代计划，每周有明确的交付目标和验收标准。

---

## MVP 范围定义

### 包含功能

**核心能力**:
- ✅ CLI 交互（单一 channel）
- ✅ 基础 Agent Loop（LLM + 工具调用）
- ✅ 3 个核心工具（文件读写、Shell 执行、Web 搜索）
- ✅ 会话管理（历史持久化）
- ✅ 简单配置系统

**不包含**:
- ❌ 多 channel 支持（Telegram、Slack 等）
- ❌ 记忆整合系统
- ❌ 子任务派发
- ❌ 权限系统
- ❌ Web UI
- ❌ 分布式部署

### 成功标准

**功能性**:
- 用户可以通过 CLI 与 Agent 对话
- Agent 可以调用工具完成任务
- 会话历史可以持久化和恢复
- 支持多轮对话

**非功能性**:
- 单轮响应时间 < 10s（不含 LLM 调用）
- 支持至少 100 轮对话的会话
- 代码测试覆盖率 > 70%
- 核心模块有完整文档

---

## 周计划

### Week 1: 基础设施 (Foundation)

**目标**: 搭建项目骨架，定义核心抽象

**任务**:

**Day 1-2: 项目初始化**
- [ ] 创建 monorepo 结构
- [ ] 配置 Poetry workspace
- [ ] 配置 pre-commit hooks（black, ruff, mypy）
- [ ] 配置 GitHub Actions（lint, test）
- [ ] 编写 README 和贡献指南

**Day 3-4: core 包实现**
- [ ] 定义核心抽象类
  - `Session`, `Agent`, `Tool`, `Channel`, `LLMProvider`
- [ ] 定义数据模型
  - `Message`, `ToolCall`, `ToolResult`, `Config`
- [ ] 定义异常体系
  - `AgentOSError`, `ToolExecutionError`, `SessionNotFoundError`
- [ ] 编写单元测试
- [ ] 生成 API 文档

**Day 5: storage 包基础**
- [ ] 实现 `FileSessionStore`
  - 创建会话
  - 保存消息（JSONL 追加）
  - 加载历史
- [ ] 实现 `FileWorkspaceManager`
  - 读写文件
  - 路径安全检查
- [ ] 编写单元测试

**交付物**:
- ✅ 可运行的项目骨架
- ✅ `packages/core` 完成并通过测试
- ✅ `packages/storage` 基础实现完成

**验收标准**:
```bash
# 所有测试通过
poetry run pytest packages/core packages/storage

# 类型检查通过
poetry run mypy packages/core packages/storage

# 代码格式检查通过
poetry run ruff check .
```

**风险**:
- ⚠️ Poetry workspace 配置可能有坑
- **缓解**: 提前调研，参考成熟项目（如 LangChain）

---

### Week 2: LLM 集成 (LLM Integration)

**目标**: 实现 LLM provider 和基础工具

**任务**:

**Day 1-2: providers 包**
- [ ] 实现 `LiteLLMProvider`
  - 支持 OpenAI、Anthropic、本地模型
  - 消息格式转换
  - 工具调用支持
  - 错误处理和重试
- [ ] 实现配置加载
  - 从环境变量读取 API key
  - 从配置文件读取模型设置
- [ ] 编写单元测试（使用 mock）

**Day 3-5: tools 包**
- [ ] 实现 `BaseTool` 抽象
- [ ] 实现 3 个核心工具:
  - `FileReadTool`: 读取文件
  - `FileWriteTool`: 写入文件
  - `ShellTool`: 执行 shell 命令（带安全限制）
- [ ] 实现 `ToolRegistry`
  - 注册工具
  - 查找工具
  - 生成工具描述（JSON Schema）
- [ ] 编写单元测试

**交付物**:
- ✅ `packages/providers` 完成
- ✅ `packages/tools` 完成
- ✅ 可以调用 LLM 并执行工具

**验收标准**:
```python
# 测试 LLM 调用
from agentos_providers import LiteLLMProvider

provider = LiteLLMProvider(model="gpt-4")
response = await provider.complete([
    {"role": "user", "content": "Hello"}
])
assert response.content

# 测试工具执行
from agentos_tools import FileReadTool

tool = FileReadTool()
result = await tool.execute(path="/tmp/test.txt")
assert result.success
```

**风险**:
- ⚠️ LiteLLM 版本兼容性问题
- **缓解**: 锁定版本，编写兼容性测试

---

### Week 3: Agent 运行时 (Agent Runtime)

**目标**: 实现核心 Agent Loop

**任务**:

**Day 1-3: runtime 包**
- [ ] 实现 `AgentLoop`
  - 主循环逻辑
  - LLM 调用
  - 工具调用执行
  - 结果处理
  - 最大迭代次数控制
- [ ] 实现 `ToolExecutor`
  - 并发执行多个工具调用
  - 超时控制
  - 错误处理
- [ ] 实现 `ContextManager`
  - Token 计数（估算）
  - 历史截断
- [ ] 编写单元测试

**Day 4-5: 集成测试**
- [ ] 端到端测试
  - 多轮对话
  - 工具调用流程
  - 错误恢复
- [ ] 性能测试
  - 单轮响应时间
  - 内存占用
- [ ] 修复发现的问题

**交付物**:
- ✅ `packages/runtime` 完成
- ✅ 完整的 Agent Loop 可运行

**验收标准**:
```python
# 端到端测试
from agentos_runtime import AgentLoop
from agentos_providers import LiteLLMProvider
from agentos_tools import FileReadTool, FileWriteTool

loop = AgentLoop(
    llm=LiteLLMProvider(model="gpt-4"),
    tools=[FileReadTool(), FileWriteTool()],
    max_iterations=10
)

messages = [{"role": "user", "content": "创建文件 test.txt，内容是 hello"}]
response = await loop.run(messages)

assert response.success
assert Path("test.txt").exists()
```

**风险**:
- ⚠️ Agent Loop 逻辑复杂，容易有 bug
- **缓解**: 充分的单元测试和集成测试

---

### Week 4: CLI 应用 (CLI Application)

**目标**: 实现可用的 CLI 工具

**任务**:

**Day 1-2: channels 包（CLI）**
- [ ] 实现 `CLIChannel`
  - 交互式输入输出
  - 消息格式化
  - 历史显示
- [ ] 实现 `ChannelManager`
  - 管理 channel 生命周期
- [ ] 编写单元测试

**Day 3-5: cli 应用**
- [ ] 实现 CLI 命令
  - `agentos chat`: 启动交互式对话
  - `agentos session list`: 列出会话
  - `agentos session show <id>`: 显示会话历史
  - `agentos config`: 配置管理
- [ ] 实现配置系统
  - 从 `~/.agentos/config.yaml` 读取
  - 支持环境变量覆盖
- [ ] 美化输出
  - 使用 Rich 库
  - 语法高亮
  - 进度条
- [ ] 编写用户文档

**交付物**:
- ✅ `packages/channels` 完成（CLI 部分）
- ✅ `apps/cli` 完成
- ✅ 可安装的 CLI 工具

**验收标准**:
```bash
# 安装
poetry install

# 配置
agentos config set llm.provider openai
agentos config set llm.model gpt-4
agentos config set llm.api_key sk-xxx

# 使用
agentos chat
> 你好
< 你好！我是 AgentOS，有什么可以帮你的？
> 创建文件 test.txt
< 好的，我来创建文件...
< [调用工具: file_write]
< 文件创建成功！

# 查看会话
agentos session list
agentos session show cli:default
```

**风险**:
- ⚠️ CLI 交互体验可能不够好
- **缓解**: 参考优秀 CLI 工具（如 gh, docker）

---

### Week 5: 完善与优化 (Polish & Optimization)

**目标**: 修复 bug，优化性能，完善文档

**任务**:

**Day 1-2: Bug 修复**
- [ ] 修复测试中发现的问题
- [ ] 修复用户反馈的问题
- [ ] 边界情况处理
  - 空输入
  - 超长输入
  - 网络错误
  - LLM 超时

**Day 3: 性能优化**
- [ ] 性能分析
  - 使用 cProfile 找瓶颈
- [ ] 优化热点
  - 文件 I/O
  - JSON 序列化
  - Token 计数
- [ ] 内存优化
  - 避免加载完整历史到内存
  - 流式处理大文件

**Day 4-5: 文档完善**
- [ ] 用户文档
  - 快速开始
  - 配置指南
  - 工具使用
  - 常见问题
- [ ] 开发者文档
  - 架构说明
  - API 参考
  - 贡献指南
- [ ] 示例代码
  - 基础对话
  - 文件操作
  - 自定义工具

**交付物**:
- ✅ 稳定的 MVP 版本
- ✅ 完整的文档

**验收标准**:
- 所有已知 bug 修复
- 测试覆盖率 > 70%
- 文档完整可用
- 性能达标（单轮 < 10s）

**风险**:
- ⚠️ 时间可能不够
- **缓解**: 优先修复关键 bug，文档可以后补

---

### Week 6: 发布准备 (Release Preparation)

**目标**: 准备 v0.1.0 发布

**任务**:

**Day 1-2: 发布工程**
- [ ] 配置版本管理
  - 使用 semantic versioning
  - 配置 bump2version
- [ ] 配置 PyPI 发布
  - 编写 pyproject.toml
  - 测试打包
  - 测试安装
- [ ] 编写 CHANGELOG
- [ ] 编写发布说明

**Day 3: 安全审查**
- [ ] 代码安全扫描
  - 使用 bandit
  - 使用 safety
- [ ] 依赖审查
  - 检查已知漏洞
  - 更新依赖
- [ ] 权限检查
  - 文件路径限制
  - Shell 命令限制

**Day 4: 最终测试**
- [ ] 全量回归测试
- [ ] 不同环境测试
  - macOS
  - Linux
  - Windows (WSL)
- [ ] 不同 Python 版本
  - 3.10, 3.11, 3.12
- [ ] 压力测试
  - 长时间运行
  - 大量会话

**Day 5: 发布**
- [ ] 打 tag: v0.1.0
- [ ] 发布到 PyPI
- [ ] 发布 GitHub Release
- [ ] 更新文档网站
- [ ] 社交媒体宣传

**交付物**:
- ✅ v0.1.0 正式发布
- ✅ 可通过 `pip install agentos` 安装

**验收标准**:
```bash
# 用户可以直接安装
pip install agentos

# 运行成功
agentos --version
# agentos 0.1.0

agentos chat
# 正常启动
```

**风险**:
- ⚠️ 发布流程可能有问题
- **缓解**: 提前在 TestPyPI 测试

---

## 里程碑总结

| 周 | 里程碑 | 关键交付 |
|----|--------|---------|
| W1 | 基础设施 | 项目骨架、core、storage |
| W2 | LLM 集成 | providers、tools |
| W3 | Agent 运行时 | runtime、Agent Loop |
| W4 | CLI 应用 | channels、cli 应用 |
| W5 | 完善优化 | Bug 修复、文档 |
| W6 | 发布准备 | v0.1.0 发布 |

---

## 风险管理

### 高风险项

**R1: LLM API 变更**
- **影响**: 可能导致集成失败
- **概率**: 中
- **缓解**: 使用 LiteLLM 抽象层，锁定版本

**R2: Agent Loop 逻辑复杂**
- **影响**: 可能有难以发现的 bug
- **概率**: 高
- **缓解**: 充分测试，简化逻辑，参考 nanobot

**R3: 时间不足**
- **影响**: 功能不完整
- **概率**: 中
- **缓解**: 严格控制范围，优先核心功能

### 中风险项

**R4: 性能不达标**
- **影响**: 用户体验差
- **概率**: 低
- **缓解**: 早期性能测试，及时优化

**R5: 文档不完整**
- **影响**: 用户难以上手
- **概率**: 中
- **缓解**: 边开发边写文档，W5 专门时间

---

## 每周检查点

### 检查清单

**每周五下午**:
- [ ] 本周目标是否完成？
- [ ] 测试是否通过？
- [ ] 文档是否更新？
- [ ] 是否有阻塞问题？
- [ ] 下周计划是否需要调整？

### 调整策略

**如果进度落后**:
1. 砍掉非核心功能
2. 简化实现（先 hardcode）
3. 推迟文档编写
4. 寻求帮助

**如果进度超前**:
1. 增加测试覆盖
2. 完善文档
3. 优化性能
4. 提前开始下周任务

---

## 成功指标

### 功能指标

- [ ] 用户可以通过 CLI 与 Agent 对话
- [ ] Agent 可以调用至少 3 个工具
- [ ] 会话可以持久化和恢复
- [ ] 支持至少 100 轮对话

### 质量指标

- [ ] 测试覆盖率 > 70%
- [ ] 所有核心模块有文档
- [ ] 无 P0/P1 级别 bug
- [ ] 代码通过 lint 和类型检查

### 性能指标

- [ ] 单轮响应 < 10s（不含 LLM）
- [ ] 启动时间 < 2s
- [ ] 内存占用 < 200MB

### 用户指标

- [ ] 安装成功率 > 95%
- [ ] 首次使用成功率 > 80%
- [ ] 文档可理解性 > 4/5

---

## 后续计划（Post-MVP）

### v0.2.0 (Week 7-10)

**新功能**:
- 多 channel 支持（Telegram、Slack）
- 记忆整合系统
- 更多工具（Web 搜索、API 调用）
- Web UI（可选）

### v0.3.0 (Week 11-14)

**企业功能**:
- 权限系统
- 审计日志
- 子任务派发
- 性能优化

### v1.0.0 (Week 15-20)

**生产就绪**:
- 高可用部署
- 监控和告警
- 完整文档
- 社区生态
