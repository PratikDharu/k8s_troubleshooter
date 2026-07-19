from app.rules.engine import RuleEngine


class Analyzer:
    def __init__(self):
        self.engine = RuleEngine()

    def analyze(self, text: str):
        return self.engine.analyze(text)
