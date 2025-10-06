
from abc import ABC, abstractmethod
from typing import Tuple

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, system: str, user: str, model: str, temperature: float | None, max_tokens: int | None) -> Tuple[str, int, int, int]:
        pass
