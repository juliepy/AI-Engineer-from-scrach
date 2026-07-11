class FakeLLM:
    def __init__(self, replies):
        self.replies = iter(replies)

    def chat(self, messages):
        return next(self.replies)
