from abc import ABC, abstractmethod

class AIBase(ABC):
    @abstractmethod
    def call(self, prompt: str) -> str:
        pass
