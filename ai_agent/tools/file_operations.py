import os
import json
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseTool, ToolParameter, ToolResult

class ReadFileTool(BaseTool):
    """Tool for reading file contents."""
    
    name = "read_file"
    description = "Read the contents of a file"
    parameters = [
        ToolParameter(
            name="file_path",
            type="string",
            description="Path to the file to read"
        ),
        ToolParameter(
            name="encoding",
            type="string",
            description="File encoding (default: utf-8)",
            required=False,
            default="utf-8"
        )
    ]
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            file_path = kwargs.get("file_path")
            encoding = kwargs.get("encoding", "utf-8")
            
            if not file_path:
                return ToolResult(
                    success=False,
                    error="file_path parameter is required"
                )
            
            path = Path(file_path)
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"File does not exist: {file_path}"
                )
            
            if not path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Path is not a file: {file_path}"
                )
            
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                data={
                    'file_path': str(path),
                    'content': content,
                    'size': len(content),
                    'encoding': encoding
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to read file: {str(e)}"
            )

class WriteFileTool(BaseTool):
    """Tool for writing content to a file."""
    
    name = "write_file"
    description = "Write content to a file"
    parameters = [
        ToolParameter(
            name="file_path",
            type="string",
            description="Path to the file to write"
        ),
        ToolParameter(
            name="content",
            type="string",
            description="Content to write to the file"
        ),
        ToolParameter(
            name="encoding",
            type="string",
            description="File encoding (default: utf-8)",
            required=False,
            default="utf-8"
        ),
        ToolParameter(
            name="append",
            type="boolean",
            description="Whether to append to file instead of overwriting",
            required=False,
            default=False
        )
    ]
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            file_path = kwargs.get("file_path")
            content = kwargs.get("content")
            encoding = kwargs.get("encoding", "utf-8")
            append = kwargs.get("append", False)
            
            if not file_path or content is None:
                return ToolResult(
                    success=False,
                    error="file_path and content parameters are required"
                )
            
            path = Path(file_path)
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            
            return ToolResult(
                success=True,
                data={
                    'file_path': str(path),
                    'bytes_written': len(content.encode(encoding)),
                    'mode': 'append' if append else 'write',
                    'encoding': encoding
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to write file: {str(e)}"
            )

class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""
    
    name = "list_directory"
    description = "List the contents of a directory"
    parameters = [
        ToolParameter(
            name="directory_path",
            type="string",
            description="Path to the directory to list"
        ),
        ToolParameter(
            name="include_hidden",
            type="boolean",
            description="Whether to include hidden files",
            required=False,
            default=False
        )
    ]
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            directory_path = kwargs.get("directory_path")
            include_hidden = kwargs.get("include_hidden", False)
            
            if not directory_path:
                return ToolResult(
                    success=False,
                    error="directory_path parameter is required"
                )
            
            path = Path(directory_path)
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"Directory does not exist: {directory_path}"
                )
            
            if not path.is_dir():
                return ToolResult(
                    success=False,
                    error=f"Path is not a directory: {directory_path}"
                )
            
            items = []
            for item in path.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                items.append({
                    'name': item.name,
                    'path': str(item),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else None
                })
            
            # Sort items: directories first, then files
            items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
            
            return ToolResult(
                success=True,
                data={
                    'directory_path': str(path),
                    'items': items,
                    'total_count': len(items)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to list directory: {str(e)}"
            )