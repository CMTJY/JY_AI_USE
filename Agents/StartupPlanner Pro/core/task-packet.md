# Task Packet v3

```yaml
task_packet:
  schema_version: "3.0"
  task_id:
  objective:
  selected_agent_id:
  selected_agent_file:
  depends_on: []
  required_artifacts: []
  expected_artifact: {id: "", type: ""}
  file_scope: {allowed: [], prohibited: [], shared: []}
  constraints: []
  acceptance_criteria: []
  required_skills: []
  verification_required: []
  reviewer:
  attempt: 1
```

专业 Agent 收到 Task Packet 后进入团队模式，只处理已授权范围；缺少 Task Packet 时进入独立模式，自行澄清必要输入，但不得声称其他 Agent 已参与。

