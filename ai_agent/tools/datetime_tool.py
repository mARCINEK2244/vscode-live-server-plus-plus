from datetime import datetime, timedelta
import pytz
from typing import List
from .base import BaseTool, ToolParameter, ToolResult

class DateTimeTool(BaseTool):
    """Tool for date and time operations."""
    
    name = "datetime"
    description = "Get current date/time, convert timezones, and perform date calculations"
    parameters = [
        ToolParameter(
            name="operation",
            type="string",
            description="Operation to perform",
            enum_values=["current", "convert_timezone", "add_days", "format", "parse"]
        ),
        ToolParameter(
            name="timezone",
            type="string",
            description="Timezone (e.g., 'UTC', 'US/Eastern', 'Europe/London')",
            required=False,
            default="UTC"
        ),
        ToolParameter(
            name="date_string",
            type="string",
            description="Date string to parse or convert",
            required=False
        ),
        ToolParameter(
            name="days",
            type="integer",
            description="Number of days to add (can be negative)",
            required=False,
            default=0
        ),
        ToolParameter(
            name="format",
            type="string",
            description="Format string for date formatting",
            required=False,
            default="%Y-%m-%d %H:%M:%S"
        )
    ]
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            operation = kwargs.get("operation")
            timezone = kwargs.get("timezone", "UTC")
            date_string = kwargs.get("date_string")
            days = kwargs.get("days", 0)
            date_format = kwargs.get("format", "%Y-%m-%d %H:%M:%S")
            
            if operation == "current":
                return self._get_current_datetime(timezone, date_format)
            
            elif operation == "convert_timezone":
                if not date_string:
                    return ToolResult(
                        success=False,
                        error="date_string is required for timezone conversion"
                    )
                return self._convert_timezone(date_string, timezone, date_format)
            
            elif operation == "add_days":
                if not date_string:
                    # Add days to current time
                    current = datetime.now(pytz.UTC)
                    result_date = current + timedelta(days=days)
                else:
                    # Parse date and add days
                    parsed_date = self._parse_date(date_string)
                    result_date = parsed_date + timedelta(days=days)
                
                return ToolResult(
                    success=True,
                    data={
                        "original_date": date_string or "current",
                        "days_added": days,
                        "result": result_date.strftime(date_format),
                        "iso_format": result_date.isoformat()
                    }
                )
            
            elif operation == "format":
                if not date_string:
                    return ToolResult(
                        success=False,
                        error="date_string is required for formatting"
                    )
                
                parsed_date = self._parse_date(date_string)
                return ToolResult(
                    success=True,
                    data={
                        "original": date_string,
                        "formatted": parsed_date.strftime(date_format),
                        "iso_format": parsed_date.isoformat()
                    }
                )
            
            elif operation == "parse":
                if not date_string:
                    return ToolResult(
                        success=False,
                        error="date_string is required for parsing"
                    )
                
                parsed_date = self._parse_date(date_string)
                return ToolResult(
                    success=True,
                    data={
                        "original": date_string,
                        "parsed": {
                            "year": parsed_date.year,
                            "month": parsed_date.month,
                            "day": parsed_date.day,
                            "hour": parsed_date.hour,
                            "minute": parsed_date.minute,
                            "second": parsed_date.second,
                            "weekday": parsed_date.strftime("%A"),
                            "iso_format": parsed_date.isoformat()
                        }
                    }
                )
            
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"DateTime operation failed: {str(e)}"
            )
    
    def _get_current_datetime(self, timezone: str, date_format: str) -> ToolResult:
        """Get current datetime in specified timezone."""
        try:
            tz = pytz.timezone(timezone)
            current = datetime.now(tz)
            
            return ToolResult(
                success=True,
                data={
                    "timezone": timezone,
                    "current_time": current.strftime(date_format),
                    "iso_format": current.isoformat(),
                    "timestamp": current.timestamp(),
                    "utc_time": current.utctimetuple()
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to get current time: {str(e)}"
            )
    
    def _convert_timezone(self, date_string: str, target_timezone: str, date_format: str) -> ToolResult:
        """Convert datetime to different timezone."""
        try:
            parsed_date = self._parse_date(date_string)
            target_tz = pytz.timezone(target_timezone)
            
            # If the parsed date is naive, assume UTC
            if parsed_date.tzinfo is None:
                parsed_date = pytz.UTC.localize(parsed_date)
            
            converted = parsed_date.astimezone(target_tz)
            
            return ToolResult(
                success=True,
                data={
                    "original": date_string,
                    "original_timezone": str(parsed_date.tzinfo),
                    "target_timezone": target_timezone,
                    "converted": converted.strftime(date_format),
                    "iso_format": converted.isoformat()
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Timezone conversion failed: {str(e)}"
            )
    
    def _parse_date(self, date_string: str) -> datetime:
        """Parse a date string using various formats."""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M",
            "%m-%d-%Y %H:%M",
            "%d-%m-%Y %H:%M"
        ]
        
        # Try ISO format first
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try various formats
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        # Try parsing with dateutil as fallback
        try:
            from dateutil.parser import parse
            return parse(date_string)
        except ImportError:
            pass
        except Exception:
            pass
        
        raise ValueError(f"Unable to parse date string: {date_string}")

class TimezoneInfoTool(BaseTool):
    """Tool for getting timezone information."""
    
    name = "timezone_info"
    description = "Get information about timezones"
    parameters = [
        ToolParameter(
            name="timezone",
            type="string",
            description="Timezone name (e.g., 'US/Eastern') or 'list' to see all",
            required=False,
            default="list"
        )
    ]
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            timezone = kwargs.get("timezone", "list")
            
            if timezone.lower() == "list":
                # Return common timezones
                common_timezones = [
                    "UTC",
                    "US/Eastern",
                    "US/Central", 
                    "US/Mountain",
                    "US/Pacific",
                    "Europe/London",
                    "Europe/Paris",
                    "Europe/Berlin",
                    "Asia/Tokyo",
                    "Asia/Shanghai",
                    "Asia/Kolkata",
                    "Australia/Sydney",
                    "America/New_York",
                    "America/Chicago",
                    "America/Denver",
                    "America/Los_Angeles"
                ]
                
                return ToolResult(
                    success=True,
                    data={
                        "common_timezones": common_timezones,
                        "total_available": len(pytz.all_timezones),
                        "note": "Use timezone names like 'US/Eastern' or 'Europe/London'"
                    }
                )
            
            else:
                # Get specific timezone info
                try:
                    tz = pytz.timezone(timezone)
                    now = datetime.now(tz)
                    
                    return ToolResult(
                        success=True,
                        data={
                            "timezone": timezone,
                            "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                            "utc_offset": str(now.utcoffset()),
                            "dst_active": bool(now.dst()),
                            "zone_name": now.tzname()
                        }
                    )
                except Exception as e:
                    return ToolResult(
                        success=False,
                        error=f"Invalid timezone '{timezone}': {str(e)}"
                    )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Timezone info operation failed: {str(e)}"
            )