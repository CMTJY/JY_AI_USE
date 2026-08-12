from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from route_eval import build_cases, evaluate  # noqa: E402
from routing import route_request  # noqa: E402


class RoutingTests(unittest.TestCase):
    def selected(self, text):
        return [task["selected"] for task in route_request(text)["tasks"]]

    def test_xiaohongshu_zero_to_one_routes_to_operator_not_startup(self):
        result = self.selected("帮我做一个小红书账号从0到1运营方案")
        self.assertIn("marketing-xiaohongshu-operator", result)
        self.assertNotIn("strategy-opc", result)
        self.assertNotIn("core-orchestrator", result)

    def test_xiaohongshu_note_routes_to_content_specialist(self):
        result = self.selected("为这个护肤品写三篇小红书种草笔记")
        self.assertEqual(["marketing-xiaohongshu-specialist"], result)

    def test_specialist_marketing_routes_are_reachable(self):
        cases = {
            "规划抖音账号矩阵和DOU+投放": "marketing-douyin-strategist",
            "教我用剪映完成短视频剪辑和调色": "marketing-video-editing-coach",
            "规划企业微信私域和SCRM复购运营": "marketing-private-domain",
            "分析Amazon美国站和Shopify跨境电商打法": "marketing-cross-border-ecommerce",
            "训练直播带货主播的话术和控场": "marketing-livestream-coach",
            "制定LinkedIn企业号和创始人IP策略": "marketing-social-strategist",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertIn(expected, self.selected(text))

    def test_product_release_readiness_routes_to_product_director(self):
        self.assertEqual(
            ["product-director"],
            self.selected("评审产品是否达到发布就绪并规划规模化治理"),
        )

    def test_compound_architecture_and_backend_request_is_decomposed(self):
        result = self.selected("设计系统架构和数据库，并完成后端API实现")
        self.assertIn("tech-architect", result)
        self.assertIn("tech-backend-dev", result)
        tasks = route_request("设计系统架构和数据库，并完成后端API实现")["tasks"]
        backend = next(task for task in tasks if task["selected"] == "tech-backend-dev")
        self.assertTrue(backend["depends_on"])

    def test_compound_prd_and_mvp_request_is_decomposed(self):
        result = self.selected("编写PRD并定义MVP范围")
        self.assertEqual(["product-pm", "product-mvp-designer"], result)

    def test_code_review_and_qa_are_distinct_tasks(self):
        result = self.selected("执行代码审查和E2E性能测试")
        self.assertEqual(["tech-code-reviewer", "tech-qa"], result)

    def test_bp_requires_direction_gate_before_writer(self):
        result = route_request("写一份完整商业计划书")
        self.assertTrue(result["direction_gate_required"])
        self.assertEqual("core-orchestrator", result["tasks"][0]["selected"])
        self.assertIn("director-bp", [task["selected"] for task in result["tasks"]])
        self.assertTrue(result["tasks"][-1]["depends_on"])

    def test_unmatched_request_requires_clarification(self):
        result = route_request("帮我弄一下这个")
        self.assertTrue(result["clarification_required"])
        self.assertEqual([], result["tasks"])

    def test_eval_corpus_has_at_least_eighty_cases(self):
        cases = build_cases()
        self.assertGreaterEqual(len(cases), 80)
        self.assertGreaterEqual(len([case for case in cases if case["source"] == "curated"]), 12)

    def test_eval_corpus_meets_hard_routing_targets(self):
        report = evaluate()
        self.assertEqual(0, report["bp_direction_gate_misses"])
        self.assertLessEqual(report["direction_false_positive_rate"], 0.02)
        self.assertGreaterEqual(report["atomic_accuracy"], 0.90)
        self.assertLessEqual(report["specialist_miss_rate"], 0.05)
        self.assertLessEqual(report["unnecessary_call_rate"], 0.10)


if __name__ == "__main__":
    unittest.main()
