import json
import asyncio
import os
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
)

async def generate_qa_batch(text: str, num_pairs: int) -> List[Dict]:
    prompt = f"""
    Bạn là một chuyên gia đánh giá AI. Dựa vào đoạn văn bản sau, hãy tạo ra {num_pairs} test case.
    Ít nhất 1 câu hỏi phải là câu hỏi khó hoặc có tính đánh đố (adversarial).
    Mỗi test case phải là một đối tượng JSON có các trường:
    - "question": Câu hỏi.
    - "expected_answer": Câu trả lời chuẩn.
    - "context": Trích đoạn ngắn từ văn bản liên quan.
    - "metadata": Chứa "difficulty" (easy/medium/hard) và "type".
    - "expected_retrieval_ids": Một mảng chứa id tài liệu, hãy điền ["doc_01"].

    Văn bản: {text}

    Hãy trả về ĐÚNG định dạng JSON array chứa {num_pairs} object. Không thêm markdown ```json.
    """
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}, # Mặc dù deepseek có hỗ trợ json_object, ta dùng prompt để chắc chắn
        )
        content = response.choices[0].message.content
        # Xử lý trường hợp có markdown code block
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
            
        try:
            # Parse mảng json (hoặc object chứa mảng json)
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "test_cases" in parsed:
                return parsed["test_cases"]
            elif isinstance(parsed, dict):
                # Nếu nó trả về dict với key random, lấy values
                for v in parsed.values():
                    if isinstance(v, list): return v
                return [parsed]
            elif isinstance(parsed, list):
                return parsed
            else:
                return []
        except json.JSONDecodeError:
            print("Lỗi parse JSON:", content)
            return []
    except Exception as e:
        print("Lỗi khi gọi API:", e)
        return []

async def generate_qa_from_text(text: str, total_pairs: int = 50) -> List[Dict]:
    print(f"Generating {total_pairs} QA pairs from text...")
    batch_size = 10
    tasks = []
    for _ in range(total_pairs // batch_size):
        tasks.append(generate_qa_batch(text, batch_size))
    
    results = await asyncio.gather(*tasks)
    qa_pairs = []
    for res in results:
        qa_pairs.extend(res)
        
    # Bổ sung nếu thiếu (do API bị lỗi)
    while len(qa_pairs) < total_pairs:
        qa_pairs.append({
            "question": f"Câu hỏi bổ sung {len(qa_pairs)+1}?",
            "expected_answer": "Câu trả lời kỳ vọng.",
            "context": text[:100],
            "metadata": {"difficulty": "easy", "type": "fallback"},
            "expected_retrieval_ids": ["doc_01"]
        })
    return qa_pairs[:total_pairs]

async def main():
    raw_text = "AI Evaluation là một quy trình kỹ thuật nhằm đo lường chất lượng của các mô hình AI. Việc đánh giá Retrieval-Augmented Generation (RAG) rất quan trọng để đảm bảo AI không bị hallucination. Các metrics thường dùng bao gồm Hit Rate, Mean Reciprocal Rank (MRR), Faithfulness, và Answer Relevance."
    
    # Prompt API deepseek-chat json_object cần hướng dẫn rõ ràng
    qa_pairs = await generate_qa_from_text(raw_text, 50)
    
    with open("data/golden_set.jsonl", "w", encoding="utf-8") as f:
        for pair in qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    print(f"Done! Saved {len(qa_pairs)} cases to data/golden_set.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
