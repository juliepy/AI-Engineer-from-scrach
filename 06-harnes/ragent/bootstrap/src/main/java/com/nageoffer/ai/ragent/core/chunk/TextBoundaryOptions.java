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

import java.util.Map;

/**
 * 文本边界切分配置
 * 供结构感知切分等基于文本边界的切分策略共用
 *
 * @param targetChars  目标块大小（字符数）
 * @param overlapChars 相邻块重叠大小（字符数）
 * @param maxChars     块的硬上限（字符数）
 * @param minChars     块的最小下限（字符数），小于此值会与后续块合并
 */
public record TextBoundaryOptions(
        int targetChars,
        int overlapChars,
        int maxChars,
        int minChars
) implements ChunkingOptions {

    @Override
    public Map<String, Integer> toConfigMap() {
        return Map.of("targetChars", targetChars, "overlapChars", overlapChars,
                "maxChars", maxChars, "minChars", minChars);
    }
}
