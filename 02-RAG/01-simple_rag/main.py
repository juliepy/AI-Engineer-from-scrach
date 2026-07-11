"""
最简单的 RAG 演示入口
运行方式：
    python main.py              # 交互式问答
    python main.py --rebuild    # 强制重建索引后再问答
    python main.py --stream     # 流式输出
"""
import os
import argparse
from dotenv import load_dotenv
from rag import RAGPipeline

# 加载 .env（向上查找 DEEPSEEK_API_KEY）
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))


DEMO_QUESTIONS = [
    "员工工作满3年可以享受多少天年假？",
    "报销金额超过5000元需要谁审批？",
    "智能客服系统的最低内存要求是多少？",
    "绩效考核D级会有什么后果？",
]


def main():
    parser = argparse.ArgumentParser(description="Simple RAG Demo with DeepSeek")
    parser.add_argument("--doc-dir",  default="./docs",  help="知识库文档目录")
    parser.add_argument("--index-dir", default="./index", help="向量索引保存目录")
    parser.add_argument("--rebuild",  action="store_true", help="强制重建索引")
    parser.add_argument("--stream",   action="store_true", help="流式输出答案")
    parser.add_argument("--top-k",    type=int, default=3, help="检索 Top-K 块数")
    parser.add_argument("--demo",     action="store_true", help="运行预设演示问题")
    args = parser.parse_args()

    # ── 初始化 Pipeline ──
    rag = RAGPipeline(
        index_path=args.index_dir,
        top_k=args.top_k,
        use_mmr=True,
        stream=args.stream,
    )

    # ── 离线：构建/加载索引 ──
    rag.build_index(doc_dir=args.doc_dir, force_rebuild=args.rebuild)

    # ── 在线：问答 ──
    if args.demo:
        print("\n" + "=" * 60)
        print("  RAG 演示模式 - 预设问题")
        print("=" * 60)
        for q in DEMO_QUESTIONS:
            answer = rag.ask(q)
            print(f"\n答案：\n{answer}")
            print("-" * 60)
    else:
        print("\n" + "=" * 60)
        print("  RAG 交互问答（输入 'quit' 退出）")
        print("=" * 60)
        while True:
            try:
                question = input("\n请输入问题：").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not question or question.lower() in ("quit", "exit", "q"):
                print("再见！")
                break

            answer = rag.ask(question)
            print(f"\n【答案】\n{answer}")


if __name__ == "__main__":
    main()
