from abc import ABC, abstractmethod

class AIBase(ABC):
    def __init__(self, name: str = "", backend: dict = None):
        self.name = name
        self.backend = backend or {}

    @abstractmethod
    def call(self, prompt: str, **kwargs) -> str:
        pass
