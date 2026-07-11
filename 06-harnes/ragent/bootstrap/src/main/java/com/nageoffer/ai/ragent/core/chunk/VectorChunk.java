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

package com.nageoffer.ai.ragent.core.chunk;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.HashMap;
import java.util.Map;

/**
 * 分块结果对象
 * 统一的分块输出格式，包含所有必要信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VectorChunk {

    /**
     * 块的唯一标识符
     */
    private String chunkId;

    /**
     * 块在文档中的序号索引，从0开始
     */
    private Integer index;

    /**
     * 块的原始文本内容
     */
    private String content;

    /**
     * 块的元数据信息
     */
    @Builder.Default
    private Map<String, Object> metadata = new HashMap<>();

    /**
     * 块的向量嵌入表示
     * 用于向量相似度检索的浮点数数组
     */
    @JsonIgnore
    private float[] embedding;
}
