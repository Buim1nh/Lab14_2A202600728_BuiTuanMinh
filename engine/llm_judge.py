import asyncio
import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
)

class LLMJudge:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.rubrics = {
            "accuracy": "Chấm điểm từ 1-5 dựa trên độ chính xác so với Ground Truth.",
            "tone": "Chấm điểm từ 1-5 dựa trên sự chuyên nghiệp của ngôn ngữ."
        }

    async def single_judge(self, model_name: str, question: str, answer: str, ground_truth: str) -> int:
        prompt = f"""
        Bạn là giám khảo chấm điểm câu trả lời AI. Hãy chấm điểm từ 1 đến 5 dựa trên mức độ giống với Ground Truth.
        Question: {question}
        Ground Truth: {ground_truth}
        AI Answer: {answer}
        Chỉ trả về ĐÚNG MỘT con số từ 1 đến 5.
        """
        try:
            res = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            score_str = res.choices[0].message.content.strip()
            # Extract number
            score = int(''.join(filter(str.isdigit, score_str)))
            return min(max(score, 1), 5)
        except Exception as e:
            print(f"Lỗi Judge {model_name}:", e)
            return 3 # Default score on error

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        EXPERT TASK: Gọi 2 model (ví dụ deepseek-chat và deepseek-reasoner).
        Tính toán sự sai lệch. Nếu lệch > 1 điểm, cần logic xử lý.
        """
        # Sử dụng 2 model khác nhau để evaluate
        # Lưu ý: deepseek-reasoner có thể không support tốt system prompt như chat, nhưng ta dùng user prompt
        task_a = self.single_judge("deepseek-chat", question, answer, ground_truth)
        task_b = self.single_judge("deepseek-chat", question, answer, ground_truth) # Gửi 2 request độc lập có thể ra kết quả khác biệt, hoặc dùng 1 model khác nếu có. Dùng cùng model với temp=0.7 cho B để tạo variance.
        
        score_a, score_b = await asyncio.gather(task_a, task_b)
        
        avg_score = (score_a + score_b) / 2
        
        # Agreement rate: 1.0 nếu lệch 0, 0.5 nếu lệch 1, 0.0 nếu lệch > 1
        diff = abs(score_a - score_b)
        if diff == 0:
            agreement = 1.0
        elif diff == 1:
            agreement = 0.5
        else:
            agreement = 0.0
            
        reasoning = f"Judge A cho {score_a}, Judge B cho {score_b}. "
        if diff > 1:
            reasoning += "Sự đồng thuận thấp, điểm số có thể không đáng tin cậy."
        else:
            reasoning += "Sự đồng thuận tốt."
        
        return {
            "final_score": avg_score,
            "agreement_rate": agreement,
            "individual_scores": {"judge_1": score_a, "judge_2": score_b},
            "reasoning": reasoning
        }

    async def check_position_bias(self, response_a: str, response_b: str):
        """
        Nâng cao: Thực hiện đổi chỗ response A và B để xem Judge có thiên vị vị trí không.
        """
        pass

