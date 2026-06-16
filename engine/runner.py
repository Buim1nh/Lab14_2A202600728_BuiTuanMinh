import asyncio
import time
from typing import List, Dict

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()
        
        # 1. Gọi Agent
        response = await self.agent.query(test_case["question"])
        latency = time.perf_counter() - start_time
        
        # 2. Chạy Multi-Judge
        judge_result = await self.judge.evaluate_multi_judge(
            test_case["question"], 
            response["answer"], 
            test_case.get("expected_answer", "")
        )
        
        return {
            "test_case": test_case.get("question", ""),
            "agent_response": response["answer"],
            "retrieved_ids": response.get("retrieved_ids", []),
            "latency": latency,
            "judge": judge_result,
            "status": "fail" if judge_result["final_score"] < 3 else "pass"
        }

    async def run_all(self, dataset: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Chạy song song bằng asyncio.gather với giới hạn batch_size để không bị Rate Limit.
        """
        results = []
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
        # 3. Chạy Retrieval Eval theo batch sau khi có đủ response từ Agent
        retrieval_eval_scores = await self.evaluator.evaluate_batch(dataset, results)
        
        # Inject retrieval scores into results for summary calculation
        for r in results:
            r["ragas"] = {
                "retrieval": {
                    "hit_rate": retrieval_eval_scores["avg_hit_rate"],
                    "mrr": retrieval_eval_scores["avg_mrr"]
                }
            }
            
        return results

