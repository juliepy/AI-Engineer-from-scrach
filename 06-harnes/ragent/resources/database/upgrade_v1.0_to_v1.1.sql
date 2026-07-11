-- ragent v1.0 -> v1.1 升级脚本
-- 分块日志表：拆分计时字段，修正语义

-- 1. embedding_duration 改名为 embed_duration（原字段实际量的是持久化时间，现改为真正的嵌入 API 耗时）
ALTER TABLE t_knowledge_document_chunk_log RENAME COLUMN embedding_duration TO embed_duration;

-- 2. 新增 persist_duration（DB 持久化耗时，从原 embedding_duration 拆出）
ALTER TABLE t_knowledge_document_chunk_log ADD COLUMN persist_duration BIGINT;
