import os

def format_output(files_data, format_type, include_path):
    # Prepare the payload according to target AI specs
    if "XML" in format_type:
        output = ["<documents>"]
        for i, (rel_path, content) in enumerate(files_data):
            block = (f'  <document index="{i+1}">\n'
                     f'    <source>{rel_path}</source>\n'
                     f'    <document_content>\n{content}\n    </document_content>\n'
                     f'  </document>')
            output.append(block)
        output.append("</documents>")
        return "\n".join(output)
    
    elif "Markdown" in format_type:
        blocks = []
        for rel_path, content in files_data:
            ext = os.path.splitext(rel_path)[1].replace('.', '')
            lang = "python" if ext == "py" else ext
            header = f"// File: {rel_path}\n" if include_path else ""
            blocks.append(f"```{lang}\n{header}{content}\n```")
        return "\n\n".join(blocks)
    
    else: 
        # Fallback to string list for low-bandwidth scenarios
        blocks = []
        for rel_path, content in files_data:
            text = f"// {rel_path}\n{content}" if include_path else content
            blocks.append(f'"{text.replace(chr(34), chr(92)+chr(34))}"')
        return ", ".join(blocks)