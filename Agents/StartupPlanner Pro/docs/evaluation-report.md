# StartupPlanner Pro v3 实验与验证报告

日期：2026-08-12

## 路由实验

语料由 15 条人工 curated 高风险案例和 34 个 active 专业角色各 3 条契约正例组成，共 117 条。

| 指标 | 结果 | 目标 |
|---|---:|---:|
| 用例通过 | 117/117 | — |
| 总通过率 | 100.00% | — |
| 原子任务准确率 | 100.00% | ≥90% |
| 专业 Agent 漏调率 | 0.00% | ≤5% |
| 不必要调用率 | 3.12% | ≤10% |
| 方向门误触发率 | 0.00% | ≤2% |
| BP 方向门漏检 | 0 | 0 |

复现：

```powershell
python "Agents/StartupPlanner Pro/tools/route_eval.py"
```

以上是确定性参考路由器的离线规则实验，不等于三平台实机模型表现。Codex、Cursor、TRAE 的实机抽测状态目前为“待各宿主运行”；不得据此声称三个工具已经达到相同准确率。

## 静态验证

```powershell
python "Agents/StartupPlanner Pro/tools/validate.py"
python -m unittest discover -s "Agents/StartupPlanner Pro/tests" -v
```

当前静态配置验证为零错误。最终测试数量和 Token 报告将在发布基线任务完成后更新。

## Token 预算

```powershell
python "Agents/StartupPlanner Pro/tools/token_budget.py"
```

项目以渐进加载为准：单次只加载一个平台入口和命中领域的路由/Agent，不能把角色库和 100 个技能全部作为启动上下文。字符估算是保守范围，不是精确计费。

## 已知限制

- 宿主模型可能不完全遵循纯 Markdown/YAML 协议；
- 平台原生多 Agent、规则发现和权限不同；
- 自动生成的契约正例与真实用户分布不同，需要持续加入生产失败样本；
- 渠道规则和平台政策会变化，事实性建议仍需联网核验；
- 离线规则结果不等于三平台实机结果。

