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

package com.nageoffer.ai.ragent.infra.embedding;

import com.nageoffer.ai.ragent.infra.model.ModelTarget;

import java.util.List;

/**
 * 文本嵌入客户端接口
 * 用于将文本转换为向量表示，支持单个文本和批量文本的嵌入操作
 */
public interface EmbeddingClient {

    /**
     * 获取嵌入服务提供商名称
     *
     * @return 提供商标识字符串
     */
    String provider();

    /**
     * 将单个文本转换为嵌入向量
     *
     * @param text   待嵌入的文本内容
     * @param target 目标模型配置
     * @return 文本的向量表示，以浮点数列表形式返回
     */
    List<Float> embed(String text, ModelTarget target);

    /**
     * 批量将多个文本转换为嵌入向量
     *
     * @param texts  待嵌入的文本列表
     * @param target 目标模型配置
     * @return 文本向量列表，每个文本对应一个向量（浮点数列表）
     */
    List<List<Float>> embedBatch(List<String> texts, ModelTarget target);
}
