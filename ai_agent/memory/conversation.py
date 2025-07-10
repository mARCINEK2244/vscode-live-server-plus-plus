import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import threading

class ConversationManager:
    """Manages conversation history and memory."""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.conversations: Dict[str, List[Dict]] = {}
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for persistent storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    title TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_calls TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            conn.commit()
    
    def create_conversation(self, title: str = None) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        
        with self._lock:
            self.conversations[conversation_id] = []
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO conversations (id, title) VALUES (?, ?)",
                    (conversation_id, title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                )
                conn.commit()
        
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str, tool_calls: List[Dict] = None):
        """Add a message to a conversation."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tool_calls": tool_calls or []
        }
        
        with self._lock:
            self.conversations[conversation_id].append(message)
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO messages (conversation_id, role, content, tool_calls) VALUES (?, ?, ?, ?)",
                    (conversation_id, role, content, json.dumps(tool_calls) if tool_calls else None)
                )
                
                # Update conversation timestamp
                conn.execute(
                    "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (conversation_id,)
                )
                
                conn.commit()
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history."""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id].copy()
        
        # Load from database if not in memory
        return self._load_conversation_from_db(conversation_id)
    
    def _load_conversation_from_db(self, conversation_id: str) -> List[Dict]:
        """Load conversation from database."""
        messages = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content, tool_calls, timestamp FROM messages "
                "WHERE conversation_id = ? ORDER BY timestamp",
                (conversation_id,)
            )
            
            for row in cursor.fetchall():
                role, content, tool_calls_json, timestamp = row
                tool_calls = json.loads(tool_calls_json) if tool_calls_json else []
                
                messages.append({
                    "role": role,
                    "content": content,
                    "tool_calls": tool_calls,
                    "timestamp": timestamp
                })
        
        # Cache in memory
        if messages:
            with self._lock:
                self.conversations[conversation_id] = messages
        
        return messages
    
    def get_conversation_list(self) -> List[Dict]:
        """Get list of all conversations."""
        conversations = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, title, created_at, updated_at FROM conversations "
                "ORDER BY updated_at DESC"
            )
            
            for row in cursor.fetchall():
                conv_id, title, created_at, updated_at = row
                
                # Get message count
                msg_cursor = conn.execute(
                    "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
                    (conv_id,)
                )
                message_count = msg_cursor.fetchone()[0]
                
                conversations.append({
                    "id": conv_id,
                    "title": title,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "message_count": message_count
                })
        
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        with self._lock:
            # Remove from memory
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
            
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                # Delete messages first (foreign key constraint)
                conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                
                # Delete conversation
                cursor = conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
                conn.commit()
                
                return cursor.rowcount > 0
    
    def clear_conversation(self, conversation_id: str):
        """Clear all messages from a conversation."""
        with self._lock:
            if conversation_id in self.conversations:
                self.conversations[conversation_id] = []
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                conn.commit()
    
    def update_conversation_title(self, conversation_id: str, title: str):
        """Update conversation title."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, conversation_id)
            )
            conn.commit()
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary statistics."""
        messages = self.get_conversation(conversation_id)
        
        if not messages:
            return {"error": "Conversation not found"}
        
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
        tool_calls = [msg for msg in messages if msg.get("tool_calls")]
        
        return {
            "conversation_id": conversation_id,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "tool_calls": len(tool_calls),
            "start_time": messages[0]["timestamp"] if messages else None,
            "last_message": messages[-1]["timestamp"] if messages else None
        }
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """Search conversations by content."""
        results = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT c.id, c.title, c.updated_at, m.content
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE m.content LIKE ? OR c.title LIKE ?
                ORDER BY c.updated_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            for row in cursor.fetchall():
                conv_id, title, updated_at, content_snippet = row
                results.append({
                    "conversation_id": conv_id,
                    "title": title,
                    "updated_at": updated_at,
                    "content_snippet": content_snippet[:200] + "..." if len(content_snippet) > 200 else content_snippet
                })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation manager statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Total conversations
            conv_cursor = conn.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = conv_cursor.fetchone()[0]
            
            # Total messages
            msg_cursor = conn.execute("SELECT COUNT(*) FROM messages")
            total_messages = msg_cursor.fetchone()[0]
            
            # Messages by role
            role_cursor = conn.execute("SELECT role, COUNT(*) FROM messages GROUP BY role")
            messages_by_role = dict(role_cursor.fetchall())
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "messages_by_role": messages_by_role,
            "conversations_in_memory": len(self.conversations)
        }