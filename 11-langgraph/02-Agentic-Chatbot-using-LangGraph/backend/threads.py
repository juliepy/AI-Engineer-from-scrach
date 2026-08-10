from backend.graph import checkpoint


def get_all_threads() -> list:
    all_threads = set()

    for ckpt in checkpoint.list(None):
        all_threads.add(ckpt.config["configurable"]["thread_id"])

    return list(all_threads)
