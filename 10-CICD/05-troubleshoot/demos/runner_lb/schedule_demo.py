"""教学用：模拟 GitLab Runner 对 Docker Job 的「负载均衡」。

真实 GitLab 调度是 Go 写的协调端逻辑，不是业务仓库里的这段 Python。
这里用「最少连接」思路演示：按 tags 选池 → 选当前负载最低且未满的 Runner → 起容器。

运行：
  python schedule_demo.py
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Runner:
    name: str
    tags: set[str]
    concurrent: int
    running: int = 0
    containers: list[str] = field(default_factory=list)

    @property
    def free_slots(self) -> int:
        return self.concurrent - self.running

    def accept(self, job_tag: str) -> bool:
        return job_tag in self.tags and self.free_slots > 0


@dataclass
class Job:
    name: str
    image: str
    tag: str  # 对应 yml 里 tags: [test] / [build]


def pick_runner(runners: list[Runner], job: Job) -> Runner | None:
    """负载均衡：同 tag 池里选 running 最少（最少连接）的 Runner。"""
    candidates = [r for r in runners if r.accept(job.tag)]
    if not candidates:
        return None
    return min(candidates, key=lambda r: (r.running, r.name))


def schedule(runners: list[Runner], jobs: list[Job]) -> list[str]:
    logs: list[str] = []
    pending = list(jobs)

    while pending:
        progressed = False
        still: list[Job] = []
        for job in pending:
            runner = pick_runner(runners, job)
            if runner is None:
                still.append(job)
                continue
            cid = f"{job.image.replace(':', '-')}#{job.name}@{runner.name}"
            runner.running += 1
            runner.containers.append(cid)
            logs.append(
                f"START  {job.name:20} image={job.image:22} "
                f"-> {runner.name} (load {runner.running}/{runner.concurrent})  container={cid}"
            )
            progressed = True
        pending = still
        if not progressed and pending:
            for job in pending:
                logs.append(f"WAIT   {job.name:20} tag={job.tag} 无空闲 Runner（concurrent 已满）")
            break

        # 模拟一批容器跑完，释放槽位，继续吃队列
        for r in runners:
            if r.running:
                finished = r.containers[:]
                for cid in finished:
                    logs.append(f"DONE   container={cid}")
                r.containers.clear()
                r.running = 0

    return logs


def main() -> None:
    runners = [
        Runner("runner-test-1", tags={"test"}, concurrent=2),
        Runner("runner-test-2", tags={"test"}, concurrent=2),
        Runner("runner-build-1", tags={"build"}, concurrent=1),
    ]
    jobs = [
        Job("lint", "app-test:1.2.3", "test"),
        Job("unit_test", "app-test:1.2.3", "test"),
        Job("unit_test_py311", "app-test:1.2.3", "test"),
        Job("build_fw", "toolchain:3.1", "build"),
    ]

    print("=== Runners ===")
    for r in runners:
        print(f"  {r.name}: tags={sorted(r.tags)} concurrent={r.concurrent}")
    print()
    print("=== Schedule (least-loaded in matching tag pool) ===")
    for line in schedule(runners, jobs):
        print(line)


if __name__ == "__main__":
    main()
