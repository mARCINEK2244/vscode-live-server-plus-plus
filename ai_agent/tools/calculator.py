import ast
import operator
import math
from typing import Dict, Any, Union
from .base import BaseTool, ToolParameter, ToolResult

class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations."""
    
    name = "calculator"
    description = "Evaluate mathematical expressions and perform calculations"
    parameters = [
        ToolParameter(
            name="expression",
            type="string",
            description="Mathematical expression to evaluate (e.g., '2 + 3 * 4', 'sqrt(16)', 'sin(pi/2)')"
        )
    ]
    
    # Supported operations
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }
    
    # Supported functions
    functions = {
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'ceil': math.ceil,
        'floor': math.floor,
        'abs': abs,
        'round': round,
        'max': max,
        'min': min,
        'sum': sum,
    }
    
    # Supported constants
    constants = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
    }
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            expression = kwargs.get("expression")
            
            if not expression:
                return ToolResult(
                    success=False,
                    error="expression parameter is required"
                )
            
            # Parse and evaluate the expression
            result = self._eval_expr(expression)
            
            return ToolResult(
                success=True,
                data={
                    'expression': expression,
                    'result': result,
                    'type': type(result).__name__
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Calculation failed: {str(e)}"
            )
    
    def _eval_expr(self, expr: str) -> Union[int, float]:
        """Safely evaluate a mathematical expression."""
        # Replace constants
        for name, value in self.constants.items():
            expr = expr.replace(name, str(value))
        
        # Parse the expression
        try:
            node = ast.parse(expr, mode='eval')
        except SyntaxError:
            raise ValueError(f"Invalid expression syntax: {expr}")
        
        return self._eval_node(node.body)
    
    def _eval_node(self, node) -> Union[int, float]:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Constant):  # numbers
            return node.value
        elif isinstance(node, ast.Num):  # fallback for older Python versions
            return node.n
        elif isinstance(node, ast.BinOp):  # binary operations
            return self.operators[type(node.op)](
                self._eval_node(node.left),
                self._eval_node(node.right)
            )
        elif isinstance(node, ast.UnaryOp):  # unary operations
            return self.operators[type(node.op)](self._eval_node(node.operand))
        elif isinstance(node, ast.Call):  # function calls
            func_name = node.func.id
            if func_name not in self.functions:
                raise ValueError(f"Unknown function: {func_name}")
            
            args = [self._eval_node(arg) for arg in node.args]
            return self.functions[func_name](*args)
        elif isinstance(node, ast.Name):  # variables/constants
            if node.id in self.constants:
                return self.constants[node.id]
            else:
                raise ValueError(f"Unknown variable: {node.id}")
        else:
            raise ValueError(f"Unsupported operation: {type(node).__name__}")

class StatsTool(BaseTool):
    """Tool for basic statistical calculations."""
    
    name = "statistics"
    description = "Calculate basic statistics for a list of numbers"
    parameters = [
        ToolParameter(
            name="numbers",
            type="array",
            description="List of numbers to analyze"
        ),
        ToolParameter(
            name="calculations",
            type="array",
            description="List of calculations to perform (mean, median, mode, std, var, min, max, sum, count)",
            required=False,
            default=["mean", "median", "std", "min", "max", "count"]
        )
    ]
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            numbers = kwargs.get("numbers")
            calculations = kwargs.get("calculations", ["mean", "median", "std", "min", "max", "count"])
            
            if not numbers:
                return ToolResult(
                    success=False,
                    error="numbers parameter is required"
                )
            
            if not isinstance(numbers, list):
                return ToolResult(
                    success=False,
                    error="numbers must be a list"
                )
            
            # Convert to floats
            try:
                numbers = [float(x) for x in numbers]
            except (ValueError, TypeError):
                return ToolResult(
                    success=False,
                    error="All numbers must be numeric"
                )
            
            results = {}
            
            if "count" in calculations:
                results["count"] = len(numbers)
            
            if "sum" in calculations:
                results["sum"] = sum(numbers)
            
            if "mean" in calculations and numbers:
                results["mean"] = sum(numbers) / len(numbers)
            
            if "median" in calculations and numbers:
                sorted_nums = sorted(numbers)
                n = len(sorted_nums)
                if n % 2 == 0:
                    results["median"] = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
                else:
                    results["median"] = sorted_nums[n//2]
            
            if "min" in calculations and numbers:
                results["min"] = min(numbers)
            
            if "max" in calculations and numbers:
                results["max"] = max(numbers)
            
            if "std" in calculations and len(numbers) > 1:
                mean = sum(numbers) / len(numbers)
                variance = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
                results["std"] = math.sqrt(variance)
            
            if "var" in calculations and len(numbers) > 1:
                mean = sum(numbers) / len(numbers)
                results["var"] = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
            
            if "mode" in calculations and numbers:
                from collections import Counter
                counts = Counter(numbers)
                max_count = max(counts.values())
                modes = [k for k, v in counts.items() if v == max_count]
                results["mode"] = modes[0] if len(modes) == 1 else modes
            
            return ToolResult(
                success=True,
                data={
                    'input_numbers': numbers,
                    'statistics': results
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Statistics calculation failed: {str(e)}"
            )