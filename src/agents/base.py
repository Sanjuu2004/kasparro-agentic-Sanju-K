# src/agents/base.py

from abc import ABC, abstractmethod
from core.state import PipelineState

class BaseAgent(ABC):
    @abstractmethod
    def run(self, state: PipelineState) -> PipelineState:
        ...
