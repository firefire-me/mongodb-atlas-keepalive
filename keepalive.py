# 保活核心脚本：连接Atlas并执行轻量更新操作
from pymongo import MongoClient
from datetime import datetime
import os

def main():
    # 从GitHub Secrets读取连接字符串（关键：和步骤2的Secret名称一致）
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ 未找到MONGODB_URI环境变量，请检查GitHub Secrets配置")
        exit(1)

    # 初始化MongoDB客户端
    client = None
    try:
        # 连接集群并验证
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # 触发实际连接，验证集群是否可达
        print(f"✅ 成功连接MongoDB Atlas集群 | 时间：{datetime.now()}")

        # 选择数据库（可自定义，不存在会自动创建）
        db = client["keepalive_db"]
        # 选择集合（不存在会自动创建）
        collection = db["activity_log"]

        # 执行轻量更新操作（upsert：不存在则插入，存在则更新）
        result = collection.update_one(
            {"_id": "last_active"},  # 固定ID，便于后续查询
            {"$set": {"timestamp": datetime.now(), "source": "GitHub Actions"}},
            upsert=True
        )

        # 输出执行结果
        if result.modified_count > 0:
            print("✅ 保活操作成功：更新了最后活跃时间")
        elif result.upserted_id:
            print("✅ 保活操作成功：首次创建活跃记录")
        else:
            print("⚠️ 保活操作无变更（数据未更新）")

    except Exception as e:
        print(f"❌ 保活操作失败：{str(e)}")
        exit(1)
    finally:
        # 确保关闭连接
        if client:
            client.close()
            print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    main()
