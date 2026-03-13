# 风险登记表

## 概述

本文档识别 AgentOS 实现过程中的主要风险，评估其影响和可能性，并提供缓解策略。

---

## 风险评估矩阵

| 风险等级 | 影响 | 可能性 | 优先级 |
|---------|------|--------|--------|
| 🔴 高 | 严重 | 高 | P0 |
| 🟡 中 | 中等 | 中 | P1 |
| 🟢 低 | 轻微 | 低 | P2 |

---

## 1. 技术风险

### R1.1: LLM 不确定性导致行为不可预测 🔴

**描述**:
- LLM 输出不确定，同样输入可能产生不同输出
- 工具调用可能不正确或不完整
- 难以保证质量和一致性

**影响**: 严重
- 用户体验差
- 难以调试
- 生产环境不可靠

**可能性**: 高

**缓解策略**:
1. **Prompt 工程**
   - 精心设计 system prompt
   - 提供清晰的工具描述和示例
   - 使用 few-shot learning

2. **输出验证**
   ```python
   class OutputValidator:
       def validate_tool_call(self, call: ToolCall) -> bool:
           # 验证工具名称
           if call.name not in self.available_tools:
               return False
           # 验证参数
           schema = self.tools[call.name].parameters
           try:
               jsonschema.validate(call.arguments, schema)
               return True
           except ValidationError:
               return False
   ```

3. **重试机制**
   - 输出无效时，提供错误信息并重试
   - 最多重试 3 次

4. **降级策略**
   - 关键操作需要用户确认
   - 提供"安全模式"（只读操作）

**监控指标**:
- 工具调用成功率
- 重试次数
- 用户中断率

---

### R1.2: 并发控制复杂导致竞态条件 🟡

**描述**:
- 多个请求同时修改会话状态
- 文件系统并发写入冲突
- 死锁风险

**影响**: 中等
- 数据损坏
- 系统挂起
- 难以复现的 bug

**可能性**: 中

**缓解策略**:
1. **简单的全局锁（MVP）**
   ```python
   class AgentOrchestrator:
       def __init__(self):
           self._lock = asyncio.Lock()

       async def process_message(self, message):
           async with self._lock:
               # 串行处理
               await self._handle_message(message)
   ```

2. **会话级锁（优化）**
   ```python
   class SessionLockManager:
       def __init__(self):
           self._locks = {}

       def get_lock(self, session_id: str) -> asyncio.Lock:
           if session_id not in self._locks:
               self._locks[session_id] = asyncio.Lock()
           return self._locks[session_id]
   ```

3. **追加式写入**
   - 避免读-改-写模式
   - 使用 JSONL 追加

4. **充分测试**
   - 并发测试用例
   - 压力测试

**监控指标**:
- 锁等待时间
- 并发请求数
- 文件写入冲突次数

---

### R1.3: 依赖库版本冲突 🟡

**描述**:
- LiteLLM、Pydantic 等库频繁更新
- 破坏性变更
- 依赖地狱

**影响**: 中等
- 功能失效
- 升级困难
- 维护负担

**可能性**: 中

**缓解策略**:
1. **锁定版本**
   ```toml
   [tool.poetry.dependencies]
   python = "^3.10"
   litellm = "1.30.0"  # 精确版本
   pydantic = "^2.5.0"  # 兼容版本
   ```

2. **定期更新**
   - 每月检查依赖更新
   - 测试兼容性
   - 渐进式升级

3. **兼容性测试**
   - CI 中测试多个版本
   - 使用 tox 测试矩阵

4. **抽象层隔离**
   - 不直接暴露第三方库 API
   - 通过适配器模式隔离

**监控指标**:
- 依赖漏洞数量
- 过期依赖数量

---

### R1.4: 内存泄漏导致长时间运行失败 🟡

**描述**:
- 会话历史无限增长
- LLM 响应缓存未清理
- 事件监听器未释放

**影响**: 中等
- 内存占用持续增长
- 最终 OOM
- 需要重启

**可能性**: 中

**缓解策略**:
1. **历史截断**
   ```python
   class ContextManager:
       def truncate_history(
           self,
           messages: List[Message],
           max_tokens: int = 4000
       ) -> List[Message]:
           # 保留最近的消息
           total_tokens = 0
           result = []
           for msg in reversed(messages):
               tokens = self.estimate_tokens(msg)
               if total_tokens + tokens > max_tokens:
                   break
               result.insert(0, msg)
               total_tokens += tokens
           return result
   ```

2. **定期清理**
   ```python
   class CacheManager:
       async def cleanup_old_entries(self):
           # 每小时清理一次
           while True:
               await asyncio.sleep(3600)
               cutoff = datetime.now() - timedelta(hours=24)
               self._cache = {
                   k: v for k, v in self._cache.items()
                   if v.timestamp > cutoff
               }
   ```

3. **内存监控**
   - 使用 memory_profiler
   - 设置内存告警

4. **资源限制**
   - 限制最大会话数
   - 限制单个会话大小

**监控指标**:
- 内存使用量
- 会话数量
- 平均会话大小

---

## 2. 架构风险

### R2.1: 单进程架构无法扩展 🟡

**描述**:
- 单进程限制并发能力
- 无法水平扩展
- 单点故障

**影响**: 中等
- 性能瓶颈
- 可用性问题
- 用户增长受限

**可能性**: 低（MVP 阶段）

**缓解策略**:
1. **接受限制（MVP）**
   - 明确定位为个人/小团队使用
   - 文档说明限制

2. **预留扩展点**
   ```python
   # 使用抽象接口，便于后期替换
   class MessageBus(ABC):
       @abstractmethod
       async def enqueue(self, message): pass

   # MVP: 内存队列
   class InMemoryMessageBus(MessageBus):
       pass

   # 后期: Redis 队列
   class RedisMessageBus(MessageBus):
       pass
   ```

3. **监控瓶颈**
   - 记录响应时间
   - 记录队列长度
   - 识别扩展时机

4. **迁移计划**
   - 文档化多进程架构设计
   - 准备迁移工具

**触发条件**:
- 并发用户 > 10
- 响应时间 > 30s
- 队列积压 > 100

---

### R2.2: 文件系统存储性能不足 🟢

**描述**:
- 大量会话时文件 I/O 慢
- 查询效率低
- 备份困难

**影响**: 轻微
- 响应变慢
- 用户体验下降

**可能性**: 低

**缓解策略**:
1. **优化文件组织**
   - 使用哈希分片
   - 避免单目录过多文件

2. **缓存热数据**
   ```python
   class CachedSessionStore:
       def __init__(self, backend: SessionStore):
           self.backend = backend
           self.cache = LRUCache(maxsize=100)

       async def load_history(self, session_id):
           if session_id in self.cache:
               return self.cache[session_id]
           history = await self.backend.load_history(session_id)
           self.cache[session_id] = history
           return history
   ```

3. **异步 I/O**
   - 使用 aiofiles
   - 批量写入

4. **迁移路径**
   - 提供 SQLite 实现
   - 提供迁移工具

**触发条件**:
- 会话数 > 1000
- 单次查询 > 1s

---

### R2.3: 模块边界不清晰导致耦合 🟡

**描述**:
- 模块间直接依赖
- 循环依赖
- 难以测试和重构

**影响**: 中等
- 维护困难
- 测试困难
- 重构成本高

**可能性**: 中

**缓解策略**:
1. **严格的依赖规则**
   ```
   L3 (apps) → L2 (runtime) → L1 (adapters) → L0 (core)
   禁止反向依赖
   ```

2. **依赖注入**
   ```python
   class AgentLoop:
       def __init__(
           self,
           llm: LLMProvider,  # 注入依赖
           tools: List[Tool],
           storage: SessionStore
       ):
           self.llm = llm
           self.tools = tools
           self.storage = storage
   ```

3. **接口优先**
   - 先定义接口
   - 再实现具体类

4. **定期审查**
   - 使用 pydeps 可视化依赖
   - Code review 检查依赖

**监控指标**:
- 循环依赖数量
- 模块耦合度

---

## 3. 安全风险

### R3.1: 工具执行导致系统被攻击 🔴

**描述**:
- Shell 工具执行任意命令
- 文件工具访问敏感文件
- LLM 被 prompt injection 攻击

**影响**: 严重
- 数据泄露
- 系统被控制
- 法律责任

**可能性**: 高

**缓解策略**:
1. **工具沙箱**
   ```python
   class ShellTool:
       ALLOWED_COMMANDS = ["ls", "cat", "grep", "find"]
       BLOCKED_PATTERNS = [
           r"rm\s+-rf",
           r"sudo",
           r">\s*/dev",
       ]

       async def execute(self, command: str):
           # 检查命令白名单
           cmd_name = command.split()[0]
           if cmd_name not in self.ALLOWED_COMMANDS:
               raise SecurityError(f"Command not allowed: {cmd_name}")

           # 检查危险模式
           for pattern in self.BLOCKED_PATTERNS:
               if re.search(pattern, command):
                   raise SecurityError(f"Dangerous pattern detected")

           # 执行
           ...
   ```

2. **路径限制**
   ```python
   class FileReadTool:
       def __init__(self, workspace_root: Path):
           self.workspace_root = workspace_root.resolve()

       async def execute(self, path: str):
           # 解析路径
           target = (self.workspace_root / path).resolve()

           # 检查是否在工作空间内
           if not target.is_relative_to(self.workspace_root):
               raise SecurityError("Path outside workspace")

           # 读取文件
           ...
   ```

3. **用户确认**
   - 危险操作需要确认
   - 显示将要执行的命令

4. **审计日志**
   - 记录所有工具调用
   - 记录参数和结果

**监控指标**:
- 被阻止的危险操作数
- 工具调用失败率

---

### R3.2: API Key 泄露 🔴

**描述**:
- API Key 硬编码
- 日志中记录 API Key
- 配置文件权限不当

**影响**: 严重
- 财务损失
- 服务被滥用

**可能性**: 中

**缓解策略**:
1. **环境变量**
   ```python
   # 不要硬编码
   # api_key = "sk-xxx"  # ❌

   # 从环境变量读取
   api_key = os.getenv("OPENAI_API_KEY")  # ✅
   if not api_key:
       raise ConfigError("OPENAI_API_KEY not set")
   ```

2. **配置文件权限**
   ```python
   def load_config(path: Path):
       # 检查文件权限
       stat = path.stat()
       if stat.st_mode & 0o077:
           raise SecurityError(
               f"Config file {path} has insecure permissions. "
               f"Run: chmod 600 {path}"
           )
       ...
   ```

3. **日志脱敏**
   ```python
   class SecureLogger:
       SENSITIVE_KEYS = ["api_key", "password", "token"]

       def log(self, data: dict):
           sanitized = self._sanitize(data)
           logger.info(sanitized)

       def _sanitize(self, data: dict) -> dict:
           result = {}
           for k, v in data.items():
               if k in self.SENSITIVE_KEYS:
                   result[k] = "***"
               else:
                   result[k] = v
           return result
   ```

4. **密钥轮换**
   - 文档说明定期轮换
   - 提供轮换工具

**监控指标**:
- 配置文件权限检查
- 日志扫描敏感信息

---

### R3.3: Prompt Injection 攻击 🟡

**描述**:
- 用户输入包含恶意指令
- 绕过安全限制
- 执行未授权操作

**影响**: 中等
- 安全策略被绕过
- 数据泄露

**可能性**: 中

**缓解策略**:
1. **输入清理**
   ```python
   class InputSanitizer:
       SUSPICIOUS_PATTERNS = [
           r"ignore previous instructions",
           r"system:",
           r"<\|im_start\|>",
       ]

       def sanitize(self, user_input: str) -> str:
           for pattern in self.SUSPICIOUS_PATTERNS:
               if re.search(pattern, user_input, re.IGNORECASE):
                   logger.warning(f"Suspicious input detected: {pattern}")
                   # 可以选择拒绝或清理
           return user_input
   ```

2. **角色隔离**
   ```python
   # 明确区分用户输入和系统指令
   messages = [
       {"role": "system", "content": system_prompt},
       {"role": "user", "content": user_input},  # 明确标记为用户输入
   ]
   ```

3. **输出验证**
   - 验证工具调用的合理性
   - 检测异常行为

4. **用户教育**
   - 文档说明风险
   - 提供安全使用指南

**监控指标**:
- 可疑输入检测次数
- 异常工具调用次数

---

## 4. 可运维性风险

### R4.1: 日志不足导致问题难以排查 🟡

**描述**:
- 日志信息不够
- 日志格式不统一
- 关键信息缺失

**影响**: 中等
- 调试困难
- 问题复现困难
- 用户支持困难

**可能性**: 高

**缓解策略**:
1. **结构化日志**
   ```python
   import structlog

   logger = structlog.get_logger()

   logger.info(
       "agent_turn_completed",
       session_id=session_id,
       turn_id=turn_id,
       tool_calls=len(tool_calls),
       duration_ms=duration,
       tokens_used=tokens,
       success=success
   )
   ```

2. **日志级别**
   - DEBUG: 详细执行流程
   - INFO: 关键事件
   - WARNING: 异常但可恢复
   - ERROR: 错误和失败

3. **关键路径日志**
   ```python
   # 每个关键操作都记录
   logger.info("session_created", session_id=session_id)
   logger.info("message_received", session_id=session_id, content_length=len(content))
   logger.info("llm_call_started", model=model)
   logger.info("llm_call_completed", tokens=tokens, duration=duration)
   logger.info("tool_executed", tool=tool_name, success=success)
   ```

4. **日志聚合**
   - 提供日志查询工具
   - 支持按会话查询

**监控指标**:
- 日志覆盖率
- 错误日志数量

---

### R4.2: 配置管理混乱 🟡

**描述**:
- 配置分散在多处
- 默认值不合理
- 配置验证不足

**影响**: 中等
- 用户配置困难
- 运行时错误
- 支持成本高

**可能性**: 中

**缓解策略**:
1. **统一配置**
   ```python
   # config/schema.py
   from pydantic import BaseModel, Field

   class LLMConfig(BaseModel):
       provider: str = "openai"
       model: str = "gpt-4"
       api_key: str
       max_tokens: int = 4000
       temperature: float = Field(0.7, ge=0, le=2)

   class Config(BaseModel):
       llm: LLMConfig
       storage: StorageConfig
       tools: ToolsConfig

       @classmethod
       def load(cls, path: Path) -> "Config":
           data = yaml.safe_load(path.read_text())
           return cls(**data)  # Pydantic 自动验证
   ```

2. **合理默认值**
   - 开箱即用
   - 文档说明每个配置项

3. **配置验证**
   - 启动时验证
   - 提供友好错误信息

4. **配置工具**
   ```bash
   # CLI 配置管理
   agentos config set llm.api_key sk-xxx
   agentos config get llm.model
   agentos config validate
   ```

**监控指标**:
- 配置错误次数
- 用户支持请求数

---

### R4.3: 版本升级破坏兼容性 🟡

**描述**:
- 数据格式变化
- API 变化
- 配置格式变化

**影响**: 中等
- 用户升级困难
- 数据丢失
- 用户流失

**可能性**: 中

**缓解策略**:
1. **语义化版本**
   - 遵循 semver
   - 明确标注破坏性变更

2. **数据迁移**
   ```python
   class DataMigrator:
       def migrate(self, from_version: str, to_version: str):
           migrations = self._get_migrations(from_version, to_version)
           for migration in migrations:
               logger.info(f"Running migration: {migration.name}")
               migration.run()
   ```

3. **向后兼容**
   - 保留旧 API（标记为 deprecated）
   - 提供兼容层

4. **升级指南**
   - 详细的升级文档
   - 自动化升级工具

**监控指标**:
- 升级成功率
- 迁移失败次数

---

## 5. 复杂度失控风险

### R5.1: 功能蔓延导致代码膨胀 🟡

**描述**:
- 不断添加新功能
- 代码库变得庞大
- 维护困难

**影响**: 中等
- 开发速度下降
- Bug 增多
- 新人上手困难

**可能性**: 高

**缓解策略**:
1. **功能审查**
   - 每个新功能都要评审
   - 问：是否真的需要？
   - 问：是否可以用现有功能组合？

2. **代码复杂度限制**
   ```python
   # 使用 radon 检查复杂度
   # .pre-commit-config.yaml
   - repo: local
     hooks:
       - id: complexity-check
         name: Check code complexity
         entry: radon cc --min C
         language: system
   ```

3. **定期重构**
   - 每个 sprint 预留重构时间
   - 清理死代码
   - 简化复杂逻辑

4. **模块化**
   - 功能独立为插件
   - 核心保持精简

**监控指标**:
- 代码行数
- 圈复杂度
- 技术债数量

---

### R5.2: 测试维护成本过高 🟡

**描述**:
- 测试代码比业务代码多
- 测试频繁失败
- 测试运行时间长

**影响**: 中等
- 开发效率下降
- 测试被忽略
- 质量下降

**可能性**: 中

**缓解策略**:
1. **测试分层**
   - 70% 单元测试（快速）
   - 25% 集成测试（中速）
   - 5% E2E 测试（慢速）

2. **测试工具**
   - 使用 pytest fixtures 复用
   - 使用 factory 生成测试数据
   - 使用 mock 隔离依赖

3. **并行测试**
   ```bash
   pytest -n auto  # 并行运行
   ```

4. **选择性测试**
   ```bash
   # 只测试修改的模块
   pytest --testmon
   ```

**监控指标**:
- 测试运行时间
- 测试失败率
- 测试覆盖率

---

## 风险总结

| 风险 ID | 风险名称 | 等级 | 优先级 | 状态 |
|--------|---------|------|--------|------|
| R1.1 | LLM 不确定性 | 🔴 | P0 | 需要持续关注 |
| R1.2 | 并发控制 | 🟡 | P1 | MVP 使用全局锁 |
| R1.3 | 依赖冲突 | 🟡 | P1 | 锁定版本 |
| R1.4 | 内存泄漏 | 🟡 | P1 | 需要监控 |
| R2.1 | 无法扩展 | 🟡 | P2 | 接受限制 |
| R2.2 | 存储性能 | 🟢 | P2 | 后期优化 |
| R2.3 | 模块耦合 | 🟡 | P1 | 严格依赖规则 |
| R3.1 | 工具安全 | 🔴 | P0 | 必须实现沙箱 |
| R3.2 | API Key 泄露 | 🔴 | P0 | 必须实现保护 |
| R3.3 | Prompt Injection | 🟡 | P1 | 输入清理 |
| R4.1 | 日志不足 | 🟡 | P1 | 结构化日志 |
| R4.2 | 配置混乱 | 🟡 | P1 | 统一配置 |
| R4.3 | 版本兼容 | 🟡 | P1 | 迁移工具 |
| R5.1 | 功能蔓延 | 🟡 | P1 | 功能审查 |
| R5.2 | 测试成本 | 🟡 | P1 | 测试分层 |

---

## 风险审查计划

**每周审查**:
- 检查 P0 风险状态
- 更新缓解措施进展

**每月审查**:
- 全面审查所有风险
- 识别新风险
- 调整优先级

**里程碑审查**:
- MVP 发布前
- 每个大版本发布前
