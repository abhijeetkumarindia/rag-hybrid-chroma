from abc import ABC , abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def llm(self):
        pass 