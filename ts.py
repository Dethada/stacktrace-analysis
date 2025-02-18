import re
import tree_sitter_java as tsj
from tree_sitter import Language, Parser
from typing import Optional, Tuple

JAVA_LANGUAGE = Language(tsj.language())

# Function to find class and method declarations based on line number
def find_class_declaration_and_method(source_code, line_number) -> Tuple[dict, dict]:
    parser = Parser(JAVA_LANGUAGE)
    tree = parser.parse(source_code.encode())

    root_node = tree.root_node
    class_declaration = None
    method_declaration = None
    class_javadoc = None
    method_javadoc = None
    class_start_line = None
    method_start_line = None
    class_jd_start_line = None
    method_jd_start_line = None
    class_found = False
    method_found = False

    # Walk through the nodes of the syntax tree
    def walk(node, line_number):
        nonlocal class_declaration, method_declaration, class_javadoc, method_javadoc, \
            class_start_line, method_start_line, class_jd_start_line, method_jd_start_line, \
            class_found, method_found
        # Check if the node covers the line number
        if node.start_point[0] <= line_number <= node.end_point[0]:
            if node.type == 'class_declaration' and not class_found:
                # Extract the class declaration (up to the opening brace)
                class_declaration_node = node.child_by_field_name('name')
                if class_declaration_node:
                    class_found = True
                    class_start_line, class_declaration = extract_class_declaration(source_code, node)
                    result = find_javadoc(source_code, node)
                    if result:
                        class_jd_start_line, class_javadoc = result
            elif node.type == 'method_declaration' and not method_found:
                method_found = True
                # Extract the method declaration (up to the opening brace)
                method_start_line, method_declaration = extract_func(source_code, node)
                result = find_javadoc(source_code, node)
                if result:
                    method_jd_start_line, method_javadoc = result
            # Recursively check the children nodes
            for child in node.children:
                walk(child, line_number)

    # Start walking the tree from the root
    walk(root_node, line_number - 1)  # Convert to 0-based index

    class_details = {
        'start_line': class_jd_start_line if class_jd_start_line is not None else class_start_line,
        'content': format_output(class_declaration, class_javadoc),
    }

    method_details = {
        'start_line': method_jd_start_line if method_jd_start_line is not None else method_start_line,
        'content': format_output(method_declaration, method_javadoc),
    }

    return (class_details, method_details)

# Helper function to extract declaration up to the opening brace
def extract_class_declaration(source_code, node) -> Tuple[int, str]:
    start_byte = node.start_byte - 1
    start_line = node.start_point[0] + 1
    opening_brace_index = source_code.find('{', start_byte, node.end_byte) + 1
    if opening_brace_index == -1:
        # If there is no brace, just return the node content
        return (start_line, source_code[start_byte:node.end_byte].strip())
    return (start_line, source_code[start_byte:opening_brace_index].strip())

def extract_func_declaration(source_code, node) -> Tuple[int, str]:
    start_byte = node.start_byte - 1
    start_line = node.start_point[0] + 1
    # Use regex to find the pattern ')\s*{' between the start and end bytes
    pattern = r'\).*\{'
    match = re.search(pattern, source_code[start_byte:node.end_byte])

    if match:
        # If the pattern is found, calculate the index at the end of the match
        opening_brace_index = start_byte + match.end()
        return (start_line, source_code[start_byte:opening_brace_index].strip())
        # closing_parenthesis_index = start_byte + match.start() + 1
        # return source_code[start_byte:closing_parenthesis_index].strip()

    # If no match is found, just return the node content
    return (start_line, source_code[start_byte:node.end_byte].strip())

def extract_func(source_code, node) -> Tuple[int, str]:
    func_str = source_code[node.start_byte-1:node.end_byte].strip()
    start_line = node.start_point[0] + 1
    # Extract the entire function using the node's byte range
    return (start_line, func_str)

# Helper function to find Javadocs before a class or method declaration
def find_javadoc(source_code, node) -> Optional[Tuple[int, str]]:
    # Get the line number right before the node's starting point
    node_start_line = node.start_point[0]
    lines = source_code.splitlines()

    if node_start_line == 0:
        return None  # No lines before the first line

    precending_line = lines[node_start_line - 1]
    if not precending_line.strip().endswith('*/'):
        return None  # No Javadoc comment before the node

    # traverse up to find the start of the javadoc
    javadoc_lines = []
    start_line = -1
    for i in range(node_start_line - 1, -1, -1):
        sline = lines[i].strip()
        if sline.startswith('/**'):
            javadoc_lines.append(lines[i])
            start_line = i + 1
            break
        elif sline.endswith('*/') or sline.endswith('**/') or sline.startswith('*'):
            javadoc_lines.append(lines[i])
        else:
            start_line = i + 1
            break

    java_doc = '\n'.join(reversed(javadoc_lines))
    # print(f"Javadoc_start_line: {start_line}")
    return (start_line, java_doc)

def unindent(string: str) -> str:
    lines = string.split('\n')
    return '\n'.join(line.lstrip() for line in lines)

def match_indent(string: str) -> str:
    lines = string.split('\n')
    if len(lines) < 2:
        return string
    # extract the whitespace characters from the second line
    whitespace = lines[1][:len(lines[1]) - len(lines[1].lstrip())]
    fixed_first_line = whitespace + lines[0].lstrip()
    return fixed_first_line + '\n' + '\n'.join(line for line in lines[1:])

def format_output(body: str, java_doc: Optional[str]) -> str:
    return f"{java_doc}\n{body}\n" if java_doc is not None else f"{body}\n"

def get_code_snippet(java_file_path, line_number) -> Tuple[dict, dict]:
    with open(java_file_path, 'r') as f:
        source_code = f.read()

    return find_class_declaration_and_method(source_code, line_number)

# Example usage:
if __name__ == '__main__':
    java_file_path = 'LocalMessage.java'  # Path to the Java file
    line_number = 96  # Line number to search

    output = get_code_snippet(java_file_path, line_number)
    print(output)

