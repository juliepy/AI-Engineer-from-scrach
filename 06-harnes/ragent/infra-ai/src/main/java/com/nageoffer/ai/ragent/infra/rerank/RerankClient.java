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

package com.nageoffer.ai.ragent.infra.rerank;

import com.nageoffer.ai.ragent.framework.convention.RetrievedChunk;
import com.nageoffer.ai.ragent.infra.model.ModelTarget;

import java.util.List;

/**
 * Rerank客户端接口
 * 用于对检索到的文档片段进行重新排序，以提高检索结果的相关性
 */
public interface RerankClient {

    /**
     * 获取Rerank服务提供商名称
     *
     * @return 提供商标识，如 "bailian"、"jina" 等
     */
    String provider();

    /**
     * 对检索到的文档片段进行重新排序
     *
     * @param query      用户查询文本
     * @param candidates 待排序的候选文档片段列表
     * @param topN       返回前N个最相关的结果
     * @param target     目标模型配置信息
     * @return 重新排序后的文档片段列表，按相关性从高到低排序
     */
    List<RetrievedChunk> rerank(String query, List<RetrievedChunk> candidates, int topN, ModelTarget target);
}
