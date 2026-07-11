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

package com.nageoffer.ai.ragent.infra.chat;

import com.nageoffer.ai.ragent.framework.trace.RagStreamTraceSupport.StreamSpan;

/**
 * 把 StreamSpan 的 finish 桥接到 StreamCallback 的终态事件，
 * 让 *-stream-chat trace 节点记录从开始到 onComplete / onError 的真实耗时
 */
public final class StreamSpanCallback extends ForwardingStreamCallback {

    private final StreamSpan span;

    public StreamSpanCallback(StreamCallback delegate, StreamSpan span) {
        super(delegate);
        this.span = span;
    }

    @Override
    protected void onFinish(boolean success, Throwable error) {
        if (success) {
            span.finishSuccess();
        } else {
            span.finishError(error);
        }
    }

    /**
     * 取消时由调用方触发：若 span 仍 RUNNING，按取消语义结束，避免 trace 行悬挂
     */
    public void onCancel() {
        span.finishCancelledIfRunning();
        finishExternally(false, null);
    }
}
