"""
Base Agent Class for PowerPoint Service
"""
from semantic_kernel.contents import ChatMessageContent, AuthorRole

class BaseAgent:
    """Base class for all PowerPoint generation agents"""
    
    def __init__(self):
        self.conversation_history = []
        self.agent_description = getattr(self.__class__, 'agent_description', 'Base Agent')
        self.agent_use_cases = getattr(self.__class__, 'agent_use_cases', [])

    def add_user_message(self, content: str):
        """Add user message to conversation history"""
        message = ChatMessageContent(role=AuthorRole.USER, content=content)
        self.conversation_history.append(message)

    def add_assistant_message(self, content: str):
        """Add assistant message to conversation history"""
        message = ChatMessageContent(role=AuthorRole.ASSISTANT, content=content)
        self.conversation_history.append(message)

    def get_conversation_history(self):
        """Get current conversation history"""
        return self.conversation_history.copy()

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []

    async def process(self, content: str, context_metadata: dict = None) -> str:
        """Process method to be implemented by child classes"""
        raise NotImplementedError("Child classes must implement the process method")

    def get_agent_info(self) -> dict:
        """Get agent information"""
        return {
            "name": self.__class__.__name__,
            "description": self.agent_description,
            "use_cases": self.agent_use_cases
        }
