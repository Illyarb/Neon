import ast
import os
import re

class Command:
    def __init__(self, name, action):
        self.name = name
        self.action = action

class Interpreter:
    def __init__(self):
        self.commands = {
            'clear': Command('clear', lambda: os.system('cls' if os.name == 'nt' else 'clear')),
            'exit': Command('exit', lambda: 'exit'),
            'quit': Command('quit', lambda: 'exit')
        }
        
    def is_valid_python(self, code):
        try:
            ast.parse(code)
            return True
        except:
            return False

    def preprocess_math(self, expr):
        # Handle square/cube notation
        expr = re.sub(r'(\w+)²', r'\1**2', expr)
        expr = re.sub(r'(\w+)³', r'\1**3', expr)
        
        # Handle square root
        expr = expr.replace('√', 'sqrt(')
        if '√' in expr:
            expr += ')'
            
        # Handle other basic operations
        expr = expr.replace('^', '**')
        
        return expr

    def interpret(self, client, user_input):
        # Check for graph command
        if user_input.startswith('graph '):
            return ('graph', user_input[6:].strip())
            
        cmd = user_input.strip().lower()
        if cmd in self.commands:
            return ('command', self.commands[cmd])

        # Preprocess mathematical notation
        processed_input = self.preprocess_math(user_input)
        
        if self.is_valid_python(processed_input):
            return ('python', processed_input)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Convert mathematical expressions to executable Python code. Use sqrt() for square roots.
Key requirements:
- Handle numeric literals directly (e.g., '16²' -> '16**2')
- Convert mathematical notation (^,²,³,∫,√) to Python syntax
- Create symbols for variables only (not numbers)
- Return only executable code without print statements

Examples:
'16²' -> '16**2'
'x²' -> 'x**2'
'solve x² + 2x + 1' -> 'solve(x**2 + 2*x + 1, x)'"""
                },
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            max_tokens=500
        )

        generated_code = response.choices[0].message.content.strip()
        try:
            ast.parse(generated_code)
            return ('python', generated_code)
        except:
            print(f"Error: Generated invalid Python code")
            print(generated_code)
            return None
