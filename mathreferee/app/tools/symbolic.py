"""
Symbolic mathematics tool using SymPy.
Provides equation checking, simplification, and counterexample finding.
"""

from typing import Dict, Any, List, Optional, Union
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols, simplify, solve, diff, integrate, limit, series, Eq


# JSON Schema for Gemini function calling
SYMBOLIC_TOOL_SCHEMA = {
    "verify_equation": {
        "name": "verify_equation",
        "description": "Verify if a mathematical equation is valid by checking both sides",
        "parameters": {
            "type": "object",
            "properties": {
                "left_side": {
                    "type": "string",
                    "description": "Left side of the equation (SymPy expression string)"
                },
                "right_side": {
                    "type": "string",
                    "description": "Right side of the equation (SymPy expression string)"
                },
                "assumptions": {
                    "type": "object",
                    "description": "Assumptions about variables (e.g., {'x': 'real', 'n': 'positive'})"
                }
            },
            "required": ["left_side", "right_side"]
        }
    },
    "find_counterexample": {
        "name": "find_counterexample",
        "description": "Attempt to find a counterexample to a mathematical claim",
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "Mathematical claim as an equation or inequality"
                },
                "variables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Variables to test"
                },
                "domain": {
                    "type": "string",
                    "description": "Domain to search (e.g., 'integers', 'reals', 'positive')"
                }
            },
            "required": ["claim", "variables"]
        }
    },
    "simplify_expression": {
        "name": "simplify_expression",
        "description": "Simplify a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to simplify"
                }
            },
            "required": ["expression"]
        }
    },
    "solve_equation": {
        "name": "solve_equation",
        "description": "Solve an equation for specified variables",
        "parameters": {
            "type": "object",
            "properties": {
                "equation": {
                    "type": "string",
                    "description": "Equation to solve"
                },
                "variables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Variables to solve for"
                }
            },
            "required": ["equation"]
        }
    }
}


class SymbolicMathTool:
    """
    Tool for symbolic mathematical operations using SymPy.
    Returns structured outputs for equation verification and counterexample finding.
    """
    
    def __init__(self):
        """Initialize symbolic math tool."""
        sp.init_printing()
    
    def get_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get JSON schemas for all tool functions."""
        return SYMBOLIC_TOOL_SCHEMA
    
    async def verify_equation(
        self,
        left_side: str,
        right_side: str,
        assumptions: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Verify if a mathematical equation is valid.
        
        Args:
            left_side: Left side of equation
            right_side: Right side of equation
            assumptions: Variable assumptions
            
        Returns:
            Structured verification result
        """
        try:
            # Parse expressions
            left_expr = parse_expr(left_side)
            right_expr = parse_expr(right_side)
            
            # Apply assumptions if provided
            if assumptions:
                for var, assumption in assumptions.items():
                    if assumption == 'real':
                        symbols(var, real=True)
                    elif assumption == 'positive':
                        symbols(var, positive=True)
                    elif assumption == 'integer':
                        symbols(var, integer=True)
            
            # Check if expressions are equal
            difference = simplify(left_expr - right_expr)
            are_equal = difference == 0
            
            # Try to simplify both sides
            left_simplified = simplify(left_expr)
            right_simplified = simplify(right_expr)
            
            return {
                "success": True,
                "are_equal": are_equal,
                "left_side": str(left_expr),
                "right_side": str(right_expr),
                "left_simplified": str(left_simplified),
                "right_simplified": str(right_simplified),
                "difference": str(difference),
                "difference_simplified": str(simplify(difference)),
                "verification": "valid" if are_equal else "invalid",
                "confidence": 1.0 if are_equal else 0.9
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "left_side": left_side,
                "right_side": right_side
            }
    
    async def find_counterexample(
        self,
        claim: str,
        variables: List[str],
        domain: str = "integers"
    ) -> Dict[str, Any]:
        """
        Attempt to find a counterexample to a mathematical claim.
        
        Args:
            claim: Mathematical claim
            variables: Variables to test
            domain: Domain to search in
            
        Returns:
            Structured counterexample result
        """
        try:
            # Parse the claim
            expr = parse_expr(claim)
            
            # Define test ranges based on domain
            if domain == "integers":
                test_values = range(-10, 11)
            elif domain == "positive":
                test_values = range(1, 21)
            elif domain == "natural":
                test_values = range(0, 21)
            else:
                test_values = range(-10, 11)
            
            counterexamples = []
            
            # Test combinations of values
            if len(variables) == 1:
                var = symbols(variables[0])
                for val in test_values:
                    try:
                        result = expr.subs(var, val)
                        # Check if claim is false
                        if result == False or result == 0:
                            counterexamples.append({variables[0]: val})
                            if len(counterexamples) >= 3:
                                break
                    except:
                        continue
            
            elif len(variables) == 2:
                var1, var2 = symbols(variables[0]), symbols(variables[1])
                for val1 in test_values:
                    for val2 in test_values:
                        try:
                            result = expr.subs([(var1, val1), (var2, val2)])
                            if result == False or result == 0:
                                counterexamples.append({
                                    variables[0]: val1,
                                    variables[1]: val2
                                })
                                if len(counterexamples) >= 3:
                                    break
                        except:
                            continue
                    if len(counterexamples) >= 3:
                        break
            
            found_counterexample = len(counterexamples) > 0
            
            return {
                "success": True,
                "claim": claim,
                "variables": variables,
                "domain": domain,
                "counterexample_found": found_counterexample,
                "counterexamples": counterexamples[:3],
                "search_space_size": len(test_values) ** len(variables),
                "conclusion": "claim_refuted" if found_counterexample else "no_counterexample_in_search_space"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "claim": claim
            }
    
    async def simplify_expression(self, expression: str) -> Dict[str, Any]:
        """
        Simplify a mathematical expression.
        
        Args:
            expression: Expression to simplify
            
        Returns:
            Structured simplification result
        """
        try:
            expr = parse_expr(expression)
            simplified = simplify(expr)
            
            # Try different simplification strategies
            expanded = sp.expand(expr)
            factored = sp.factor(expr)
            
            return {
                "success": True,
                "original": str(expr),
                "simplified": str(simplified),
                "expanded": str(expanded),
                "factored": str(factored),
                "is_already_simplified": expr == simplified,
                "latex_simplified": sp.latex(simplified)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    async def solve_equation(
        self,
        equation: str,
        variables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Solve an equation for specified variables.
        
        Args:
            equation: Equation to solve
            variables: Variables to solve for
            
        Returns:
            Structured solution result
        """
        try:
            # Parse equation
            expr = parse_expr(equation)
            
            # Determine variables if not specified
            if variables:
                var_symbols = [symbols(v) for v in variables]
            else:
                var_symbols = list(expr.free_symbols)
                variables = [str(v) for v in var_symbols]
            
            # Solve equation
            if len(var_symbols) == 1:
                solutions = solve(expr, var_symbols[0])
            else:
                solutions = solve(expr, var_symbols)
            
            # Format solutions
            if isinstance(solutions, dict):
                formatted_solutions = {str(k): str(v) for k, v in solutions.items()}
            elif isinstance(solutions, list):
                formatted_solutions = [str(sol) for sol in solutions]
            else:
                formatted_solutions = str(solutions)
            
            return {
                "success": True,
                "equation": str(expr),
                "variables": variables,
                "solutions": formatted_solutions,
                "solution_count": len(solutions) if isinstance(solutions, (list, dict)) else 1,
                "has_solutions": bool(solutions)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "equation": equation
            }
