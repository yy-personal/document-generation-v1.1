from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from semantic_kernel.contents import ChatMessageContent, AuthorRole

class BaseAgent(ABC):
    """
    Base class for all PDF processing agents - Simplified from Phase 1
    """

    agent_description: str = ""
    agent_use_cases: List[str] = []

    def __init__(self):
        self.conversation_history: List[ChatMessageContent] = []

    @abstractmethod
    async def process(self, content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process content and return result - standardized interface
        """
        pass

    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def add_user_message(self, message: str):
        """Add user message to conversation history"""
        self.conversation_history.append(
            ChatMessageContent(role=AuthorRole.USER, content=message)
        )

    def add_assistant_message(self, message: str):
        """Add assistant message to conversation history"""
        self.conversation_history.append(
            ChatMessageContent(role=AuthorRole.ASSISTANT, content=message)
        )

    def get_conversation_history(self) -> List[ChatMessageContent]:
        """Get current conversation history"""
        return self.conversation_history
