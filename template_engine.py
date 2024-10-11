import os
import re

class TemplateEngine:
    def __init__(self, template_dir):
        self.template_dir = template_dir

    def render(self, template_name, context=None):
        if context is None:
            context = {}

        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")

        with open(template_path, 'r') as file:
            template_content = file.read()

        # Replace variables
        template_content = re.sub(r'\{\{\s*(\w+)\s*\}\}', lambda m: str(context.get(m.group(1), '')), template_content)

        # Handle simple for loops
        def replace_for_loop(match):
            loop_var = match.group(1)
            inner_content = match.group(2)
            iterable = context.get(loop_var.split()[-1], [])
            result = []
            for item in iterable:
                item_context = context.copy()
                item_context['item'] = item
                result.append(re.sub(r'\{\{\s*item\s*\}\}', str(item), inner_content))
            return ''.join(result)

        template_content = re.sub(r'\{% for (\w+ in \w+) %\}(.*?)\{% endfor %\}', replace_for_loop, template_content, flags=re.DOTALL)

        return template_content