import os
import sys
from config import *
import readline
from io import StringIO
from openai import OpenAI
import numpy as np
import sympy as sp
from interpreter import Interpreter
import ast
from xeon import plot_polynomial

class PythonShell:
    def __init__(self):
        self.globals = {
                "np": np,
                "sp": sp,
                "math": __import__('math'),
                "__builtins__": __builtins__,
                "Symbol": sp.Symbol,
                "symbols": sp.symbols,
                "solve": sp.solve,
                "sqrt": lambda x: x ** 0.5
                }
        self.locals = {}
        self.var_expressions = {}

    def ensure_symbol(self, name):
        if name not in self.globals:
            self.globals[name] = sp.Symbol(name)

    def expand_expression(self, expr):
        if isinstance(expr, str):
            while expr in self.var_expressions:
                expr = self.var_expressions[expr]
            return expr
        return str(expr)

    def plot(self, expr_str):
        # Convert string expression to sympy expression
        expr = sp.sympify(self.expand_expression(expr_str))
        
        # Use xeon to plot
        plt = plot_polynomial(expr)
        plt.savefig('graph.png', transparent=True)
        plt.close()
        
        # Display using kitten
        os.system('kitten icat graph.png')

    def execute(self, code):
        buffer = StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            # Handle simple variable lookup
            if code.strip() in self.globals:
                result = self.expand_expression(code.strip())
                print(result)
                return buffer.getvalue().strip()

            try:
                # Parse the code to handle assignments
                tree = ast.parse(code)
                if isinstance(tree.body[0], ast.Assign):
                    target = tree.body[0].targets[0].id
                    value = ast.unparse(tree.body[0].value)

                    # Ensure all variables in the expression are symbols
                    for name in [n.id for n in ast.walk(tree.body[0].value) if isinstance(n, ast.Name)]:
                        self.ensure_symbol(name)
                        value = value.replace(name, self.expand_expression(name))

                    # Store the expanded expression
                    self.var_expressions[target] = value

                # Execute the code with expanded variables
                result = eval(code, self.globals, self.locals)
                if result is not None:
                    print(result)

            except SyntaxError:
                exec(code, self.globals, self.locals)

        finally:
            sys.stdout = old_stdout

        output = buffer.getvalue().strip()
        return output if output else None

def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not found")
    return api_key

def interactive_shell(client):
    shell = PythonShell()
    interpreter = Interpreter()
    readline.parse_and_bind(r'"\C-l": clear-screen')

    while True:
        try:
            user_input = input(shell_symbol)
            if not user_input.strip():
                continue

            result = interpreter.interpret(client, user_input)
            if result is None:
                continue

            klass, content = result
            if klass == 'command':
                if content.action() == 'exit':
                    break
                continue
            
            if klass == 'graph':
                shell.plot(content)
                continue

            if klass == 'python':
                result = shell.execute(content)
                if result is not None:
                    print(result)

        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)
    interactive_shell(client)
