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

package com.nageoffer.ai.ragent.framework.trace;

/**
 * 跨线程 stream 节点的 Trace 支持
 * <p>
 * 解决 @RagTraceNode AOP 在 stream 场景下只测到任务提交（runAsync）的问题：
 * 同步部分（HTTP 提交、首包阻塞）在调用线程执行，真正的 SSE 读循环在线程池
 * worker 线程执行。本接口允许调用线程开启一个跨线程节点，由 SSE 的
 * onComplete / onError 在另一线程上 finish
 */
public interface RagStreamTraceSupport {

    /**
     * 在调用线程开启一个 stream 节点：插入 RUNNING 行，把 nodeId push 进当前
     * 线程的 NODE_STACK 以便嵌套同步子节点（如 first-packet）能识别父节点
     * <p>
     * 注意：返回的 {@link StreamSpan} 必须在调用线程同步部分结束前调用
     * {@link StreamSpan#detach()} 把 nodeId 弹出 stack；finish 在异步线程触发
     */
    StreamSpan beginStreamNode(String name, String type);

    interface StreamSpan {

        /**
         * 调用线程同步部分结束时调用，把 nodeId 从 NODE_STACK 弹出
         * 不会 finish 节点
         */
        void detach();

        /**
         * 异步线程上：onComplete 时调用，CAS 保证幂等
         */
        void finishSuccess();

        /**
         * 异步线程上：onError 时调用，CAS 保证幂等
         */
        void finishError(Throwable error);

        /**
         * cancel 路径：如节点尚未 finish，则按取消语义收尾，避免 RUNNING 悬挂
         */
        void finishCancelledIfRunning();
    }

    /**
     * 不开启 trace 时使用的空实现，所有方法 no-op
     */
    StreamSpan NOOP_SPAN = new StreamSpan() {
        @Override public void detach() {}
        @Override public void finishSuccess() {}
        @Override public void finishError(Throwable error) {}
        @Override public void finishCancelledIfRunning() {}
    };
}
