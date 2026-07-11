/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.nageoffer.ai.ragent.rag.core.vector;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.nageoffer.ai.ragent.core.chunk.VectorChunk;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(name = "rag.vector.type", havingValue = "pg")
public class PgVectorStoreService implements VectorStoreService {

    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper;

    @Override
    public void indexDocumentChunks(String collectionName, String docId, List<VectorChunk> chunks) {
        if (chunks == null || chunks.isEmpty()) {
            return;
        }

        // noinspection SqlDialectInspection,SqlNoDataSourceInspection
        jdbcTemplate.batchUpdate(
                "INSERT INTO t_knowledge_vector (id, content, metadata, embedding) VALUES (?, ?, ?::jsonb, ?::vector)",
                chunks, chunks.size(), (ps, chunk) -> {
                    ps.setString(1, chunk.getChunkId());
                    ps.setString(2, chunk.getContent());
                    ps.setString(3, buildMetadataJson(collectionName, docId, chunk));
                    ps.setString(4, toVectorLiteral(chunk.getEmbedding()));
                });

        log.info("批量写入向量到 PostgreSQL，collectionName={}, docId={}, count={}", collectionName, docId, chunks.size());
    }

    @Override
    public void deleteDocumentVectors(String collectionName, String docId) {
        // noinspection SqlDialectInspection,SqlNoDataSourceInspection
        int deleted = jdbcTemplate.update(
                "DELETE FROM t_knowledge_vector WHERE metadata->>'collection_name' = ? AND metadata->>'doc_id' = ?",
                collectionName, docId);
        log.info("删除文档向量，collectionName={}, docId={}, deleted={}", collectionName, docId, deleted);
    }

    @Override
    public void deleteChunkById(String collectionName, String chunkId) {
        // noinspection SqlDialectInspection,SqlNoDataSourceInspection
        jdbcTemplate.update("DELETE FROM t_knowledge_vector WHERE id = ?", chunkId);
    }

    @Override
    public void deleteChunksByIds(String collectionName, List<String> chunkIds) {
        if (chunkIds == null || chunkIds.isEmpty()) {
            return;
        }
        String placeholders = chunkIds.stream().map(id -> "?").collect(java.util.stream.Collectors.joining(", "));
        // noinspection SqlDialectInspection,SqlNoDataSourceInspection
        int deleted = jdbcTemplate.update("DELETE FROM t_knowledge_vector WHERE id IN (" + placeholders + ")", chunkIds.toArray());
        log.info("批量删除 chunk 向量，collectionName={}, count={}, deleted={}", collectionName, chunkIds.size(), deleted);
    }

    @Override
    public void updateChunk(String collectionName, String docId, VectorChunk chunk) {
        // noinspection SqlDialectInspection,SqlNoDataSourceInspection
        jdbcTemplate.update(
                "INSERT INTO t_knowledge_vector (id, content, metadata, embedding) VALUES (?, ?, ?::jsonb, ?::vector) " +
                        "ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding",
                chunk.getChunkId(),
                chunk.getContent(),
                buildMetadataJson(collectionName, docId, chunk),
                toVectorLiteral(chunk.getEmbedding())
        );
    }

    private String buildMetadataJson(String collectionName, String docId, VectorChunk chunk) {
        Map<String, Object> meta = new LinkedHashMap<>();
        if (chunk.getMetadata() != null) {
            meta.putAll(chunk.getMetadata());
        }

        meta.put("collection_name", collectionName);
        meta.put("doc_id", docId);
        meta.put("chunk_index", chunk.getIndex());
        try {
            return objectMapper.writeValueAsString(meta);
        } catch (Exception e) {
            throw new RuntimeException("元数据序列化失败", e);
        }
    }

    private String toVectorLiteral(float[] embedding) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < embedding.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(embedding[i]);
        }
        return sb.append("]").toString();
    }
}
