# Open Questions

## 代码库中未明确的问题

### 架构层面

**[OPEN QUESTION]** 1. 多实例部署支持？
- 当前代码是否支持多个 nanobot 实例？
- 如果支持，如何避免 workspace 文件冲突？
- 是否有分布式锁机制？

**[OPEN QUESTION]** 2. Session 并发写入安全性？
- 多个消息同时到达时，JSONL 写入是否安全？
- 是否有文件锁保护？
- 全局锁是否足够？

**[OPEN QUESTION]** 3. Memory 整合的触发精度？
- Token 估算（每条消息 100 tokens）是否准确？
- 是否应该使用 tiktoken 精确计算？
- 不同 provider 的 token 计算差异如何处理？

### 安全层面

**[OPEN QUESTION]** 4. 路径遍历防护？
- 文件工具是否有显式的 `..` 检查？
- `Path.resolve()` 是否足够防止路径遍历？
- 符号链接如何处理？

**[OPEN QUESTION]** 5. 命令注入防护？
- Shell 工具是否有命令白名单？
- 是否有危险命令检测（如 `rm -rf /`）？
- 参数转义是否正确？

**[OPEN QUESTION]** 6. SSRF 防护？
- web_fetch 是否检查内网地址？
- 是否有 URL 白名单机制？
- 重定向如何处理？

**[OPEN QUESTION]** 7. 日志脱敏？
- 工具参数是否会泄露到日志？
- API key 是否会被记录？
- 用户消息是否有敏感信息过滤？

### 功能层面

**[OPEN QUESTION]** 8. MCP 工具冲突？
- 如果 MCP 工具与内置工具同名会怎样？
- 工具优先级如何确定？
- 是否有命名空间隔离？

**[OPEN QUESTION]** 9. Subagent 资源限制？
- 可以同时运行多少个 subagent？
- 是否有内存/CPU 限制？
- 如何防止资源耗尽？

**[OPEN QUESTION]** 10. Cron 任务失败处理？
- Cron 任务失败后是否重试？
- 是否有失败通知？
- 错误如何记录？

**[OPEN QUESTION]** 11. Channel 重连机制？
- Channel 断线后如何重连？
- 是否有指数退避？
- 最大重试次数？

**[OPEN QUESTION]** 12. Session 过期策略？
- Session 是否会过期？
- 旧 session 如何清理？
- 是否有 TTL 机制？

### 性能层面

**[OPEN QUESTION]** 13. 大文件处理？
- read_file 工具对大文件的处理？
- 是否有大小限制？
- 内存占用如何控制？

**[OPEN QUESTION]** 14. 长对话性能？
- 超长 session（1000+ 消息）的性能？
- JSONL 文件读取是否会变慢？
- 是否需要分片存储？

**[OPEN QUESTION]** 15. LLM 调用超时？
- LLM 调用是否有超时设置？
- 超时后如何处理？
- 是否会重试？

### 配置层面

**[OPEN QUESTION]** 16. 配置热更新？
- 修改配置后是否需要重启？
- 是否支持配置热加载？
- 哪些配置可以动态更新？

**[OPEN QUESTION]** 17. Provider 自动切换？
- 主 provider 失败后是否自动切换？
- 切换逻辑是什么？
- 是否有 fallback 链？

**[OPEN QUESTION]** 18. Workspace 迁移？
- 如何迁移到新 workspace？
- 是否有迁移工具？
- 数据兼容性如何保证？

## 需要进一步验证的推断

### 推断 1: 全局锁的范围
**当前推断**: 全局锁保护整个消息处理
**需要验证**:
- 锁的粒度是否真的是全局？
- 是否有其他并发控制机制？
- 子任务是否受锁影响？

### 推断 2: Memory 整合的可靠性
**当前推断**: LLM 总结可能丢失细节
**需要验证**:
- 实际使用中丢失率如何？
- 是否有补偿机制？
- 用户是否可以手动触发？

### 推断 3: Channel 代码重复
**当前推断**: 11 个 channel 有大量重复代码
**需要验证**:
- 重复度具体有多高？
- 是否有共享的辅助函数？
- 重构的收益是否值得？

### 推断 4: 单进程性能瓶颈
**当前推断**: 全局锁限制并发性能
**需要验证**:
- 实际吞吐量是多少？
- 瓶颈是锁还是 LLM 调用？
- 优化空间有多大？

## 建议的深入调查方向

### 如果要继续深入，应优先追查：

1. **安全相关** (高优先级)
   - 文件: `agent/tools/filesystem.py`
   - 文件: `agent/tools/shell.py`
   - 文件: `agent/tools/web.py`
   - 重点: 输入验证和边界检查

2. **并发控制** (高优先级)
   - 文件: `agent/loop.py`
   - 文件: `session/manager.py`
   - 重点: 锁的范围和竞态条件

3. **错误处理** (中优先级)
   - 文件: `providers/base.py`
   - 文件: `channels/*.py`
   - 重点: 重试逻辑和失败恢复

4. **性能优化** (中优先级)
   - 文件: `agent/memory.py`
   - 文件: `session/manager.py`
   - 重点: 大数据量处理

5. **配置系统** (低优先级)
   - 文件: `config/loader.py`
   - 文件: `config/schema.py`
   - 重点: 热更新和验证

## 实验建议

### 验证并发安全性
```bash
# 同时发送多条消息
for i in {1..10}; do
  nanobot agent -m "Test $i" &
done
wait

# 检查 session 文件是否损坏
cat ~/.nanobot/workspace/sessions/*.jsonl | jq .
```

### 验证大文件处理
```bash
# 创建大文件
dd if=/dev/zero of=/tmp/large.txt bs=1M count=100

# 尝试读取
nanobot agent -m "Read /tmp/large.txt"
```

### 验证 Memory 整合
```bash
# 发送大量消息触发整合
for i in {1..100}; do
  nanobot agent -m "Message $i"
done

# 检查 MEMORY.md 和 HISTORY.md
cat ~/.nanobot/workspace/memory/MEMORY.md
cat ~/.nanobot/workspace/memory/HISTORY.md
```

### 验证安全限制
```bash
# 测试路径遍历
nanobot agent -m "Read ../../../../etc/passwd"

# 测试命令注入
nanobot agent -m "Execute: echo test && rm -rf /tmp/test"
```

## 文档缺失

**需要补充的文档**:
1. 安全最佳实践指南
2. 性能调优指南
3. 故障排查手册
4. API 参考文档
5. 贡献者指南
