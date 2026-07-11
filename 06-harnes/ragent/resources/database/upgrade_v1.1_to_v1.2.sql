-- ragent v1.1 -> v1.2 升级脚本
-- t_message 表：新增深度思考内容及耗时字段

ALTER TABLE t_message ADD COLUMN thinking_content TEXT DEFAULT NULL;
ALTER TABLE t_message ADD COLUMN thinking_duration INT DEFAULT NULL;
