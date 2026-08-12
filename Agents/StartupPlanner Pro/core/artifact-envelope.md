# Artifact Envelope v3

```yaml
artifact:
  schema_version: "3.0"
  artifact_id:
  artifact_type:
  producer_agent_id:
  task_id:
  status: complete | blocked
  changed_files: []
  evidence: []
  assumptions: []
  verification: {commands: [], results: []}
  risks: []
  downstream_inputs: []
  review: {status: pending}
```

事实、推断、假设和建议必须分离。验证只记录实际执行的命令和结果。

