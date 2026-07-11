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

package com.nageoffer.ai.ragent.rag.core.retrieve.channel;

/**
 * 检索通道类型枚举
 */
public enum SearchChannelType {

    /**
     * 向量全局检索
     * 在所有知识库中进行向量检索
     */
    VECTOR_GLOBAL,

    /**
     * 意图定向检索
     * 基于意图识别结果，在特定知识库中检索
     */
    INTENT_DIRECTED,

    /**
     * ES 关键词检索
     * 基于 Elasticsearch 的关键词分词检索
     */
    KEYWORD_ES,

    /**
     * 混合检索
     * 结合多种检索策略
     */
    HYBRID
}
