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

import java.util.List;

/**
 * 文本分块器核心接口
 * 定义统一的文本分块能力
 */
public interface ChunkingStrategy {

    /**
     * 获取分块器类型标识
     *
     * @return 分块器类型名称
     */
    ChunkingMode getType();

    /**
     * 对文本进行分块处理
     *
     * @param text   待分块的原始文本内容
     * @param config 分块配置参数
     * @return 分块后的结果列表
     */
    List<VectorChunk> chunk(String text, ChunkingOptions config);
}
