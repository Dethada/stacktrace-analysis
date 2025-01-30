#!/usr/bin/env python3
import argparse
import os
import sys
import re
import html
import tomllib
import subprocess
from typing import Tuple, List, Optional
from dataclasses import dataclass
from ts import get_code_snippet
from template import HEADER, TABLE_HEADER, FOOTER

ACCESSED_PROJECTS = set()

@dataclass
class LineData:
    filename: str
    filepath: str
    package: str
    method: str
    line_num: int
    expected_suffix: str
    line_of_code: str
    project_dir: str = ""

@dataclass
class Project:
    name: str
    repo_url: str
    tags: str
    commit: str

def get_relative_path(root_path: str, filepath: str) -> str:
    """
    Returns the relative path of filepath with respect to root_path.

    Args:
        root_path (str): The root path.
        filepath (str): The file path.

    Returns:
        str: The relative path of filepath with respect to root_path.
    """
    relative_path = filepath.removeprefix(root_path)
    return relative_path.lstrip(os.sep)

def helper(lines: List[str], project_root: str, mapping: Optional[dict] = None) -> List[str]:
    """Helper function to process each line of the input"""
    result = []
    for raw_line in lines:
        # Parse line into components
        line = preprocess_input(raw_line)
        if line == '':
            continue
        data, error = parse_line(line)
        if error:
            print(error, file=sys.stderr)
            result.append(output_error(line, error))
            continue
        if data.package.startswith('com.runtimeverification.rvpredict.runtime.RVPredictRuntime'):
            print(f"Skipping line: {line}", file=sys.stderr)
            continue
        if data.line_num == -1:
            result.append(output_unknown(line))
            continue
        processed_data, error = process_line(project_root, data, mapping)
        if error:
            print(error, file=sys.stderr)
            result.append(output_error(line, error))
            continue
        relative_path = get_relative_path(project_root, processed_data.filepath)
        ACCESSED_PROJECTS.add(processed_data.project_dir)
        class_details, method_details = get_code_snippet(processed_data.filepath, processed_data.line_num)
        result.append(output(processed_data, class_details, method_details, relative_path))
    return result

def is_rv_format(input_str: str) -> bool:
    return not input_str.lstrip().startswith('=====')

def get_project_details(project_path: str) -> Project:
    """
    Returns the project details from the project path.

    Args:
        project_path (str): The project path.

    Returns:
        Project: The project details.
    """
    project_name = os.path.basename(project_path)

    def run_git_command(command):
        try:
            result = subprocess.run(
                command,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error executing Git command: {e.stderr}")
            return ""

    # Get repository URL
    repo_url = run_git_command(["git", "config", "--get", "remote.origin.url"])

    # Get tags pointing to HEAD
    tags = run_git_command(["git", "describe", "--tags"])

    # Get current commit hash
    commit = run_git_command(["git", "rev-parse", "HEAD"])

    return Project(
        name=project_name,
        repo_url=repo_url,
        tags=tags,
        commit=commit
    )

def main(projects_root: str, input_file: str, output_file: str, mapping_file: Optional[str] = None) -> None:
    """Main function that reads input lines and processes each one"""
    full_projects_root = os.path.abspath(projects_root)

    # Load mapping file if provided
    mapping = None
    if mapping_file:
        try:
            with open(mapping_file, 'rb') as f:
                mapping = tomllib.load(f)
        except Exception as e:
            print(f"Error loading mapping file: {str(e)}", file=sys.stderr)
            sys.exit(1)

    try:
        with open(input_file, 'rb') as infile, open(output_file, 'w') as outfile:
            data = tomllib.load(infile)
            originating_test = html.escape(data['originating_test'])
            field_declaration = html.escape(data['field_declaration'])
            algorithm = html.escape(data['algorithm'])
            raw_stack_trace = data['stack_trace']
            rv_format = is_rv_format(raw_stack_trace)
            extract_func = extract_stack_trace_rv if rv_format else extract_stack_trace
            fst_st, snd_st = extract_func(raw_stack_trace)
            fst = helper(fst_st.split('\n'), full_projects_root, mapping)
            snd = helper(snd_st.split('\n'), full_projects_root, mapping)
            accessed_proj_dirs = sorted(list(
                                    map(lambda x: os.path.join(full_projects_root, x),
                                        ACCESSED_PROJECTS)))
            outfile.write(HEADER)
            outfile.write('<div class="header">\n')
            outfile.write('<h1>Originating Test:</h1>\n')
            outfile.write(f'<h2>{originating_test}</h2>\n')
            outfile.write('<h1>Algorithm:</h1>\n')
            outfile.write(f'<h2>{algorithm}</h2>\n')
            outfile.write('<div class="table-container"><table><thead><tr><th><h2>Project</h2</th><th><h2>Version</h2></th><th><h2>Commit</h2></tr></thead><tbody>\n')
            for proj_dir in accessed_proj_dirs:
                project_details = get_project_details(proj_dir)
                outfile.write(f'<tr>')
                outfile.write(f'<td><a target="_blank" rel="noopener noreferrer" href="{project_details.repo_url}">{project_details.name}</a></td>')
                outfile.write(f'<td>{project_details.tags}</td>')
                outfile.write(f'<td>{project_details.commit}</td>')
                outfile.write('</tr>')
            outfile.write('</tbody></table></div>\n')
            outfile.write('<h1>Field Declaration:</h1>\n')
            outfile.write('<div class="header-code">\n')
            outfile.write(f'<pre><code class="large-code language-java nohljsln">{field_declaration}</code></pre>\n')
            outfile.write('</div>\n')
            outfile.write('</div>\n')
            outfile.write(TABLE_HEADER)
            outfile.write('<tr>\n')
            outfile.write(f'<td><strong>Depth:</strong> {len(fst)}</td>\n')
            outfile.write(f'<td><strong>Depth:</strong> {len(snd)}</td>\n')
            outfile.write('</tr>\n')
            longer_index = max(len(fst), len(snd))
            result = ''
            for i in range(longer_index):
                result += '<tr>\n'
                result += fst[i] if i < len(fst) else '<td></td>'
                result += snd[i] if i < len(snd) else '<td></td>'
                result += '</tr>\n'
            outfile.write(result)
            outfile.write(FOOTER)

    except IOError as e:
        print(f"File error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def extract_stack_trace(input_str: str) -> Tuple[str, str]:
    lines = input_str.split('\n')
    fst_sec = []
    snd_sec = []
    in_snd = False

    for line in lines:
        if line.lstrip().startswith('=================='):
            continue

        if line.startswith('\t'):
            in_snd = True

        if not in_snd:
            fst_sec.append(line)
        else:
            snd_sec.append(line.lstrip())

    fst_out = '\n'.join(fst_sec)
    snd_out = '\n'.join(snd_sec)
    return fst_out, snd_out

def extract_stack_trace_rv(input_str: str) -> Tuple[str, str]:
    lines = input_str.split('\n')
    fst_sec = []
    snd_sec = []
    in_fst = False
    in_sec = False

    for line in lines:
        stripped_line = line.lstrip()  # Remove leading whitespace for checking
        if stripped_line.startswith('Read in thread'):
            if not in_fst and not in_sec:
                in_fst = True
        elif stripped_line.startswith('Write in thread'):
            if not in_fst and not in_sec:
                in_sec = True
        elif stripped_line.startswith('Thread'):
            if in_fst:
                in_fst = False
            elif in_sec:
                in_sec = False
        else:
            if in_fst:
                fst_sec.append(line)
            elif in_sec:
                snd_sec.append(line)

    fst_out = '\n'.join(fst_sec)
    snd_out = '\n'.join(snd_sec)
    return fst_out, snd_out

def preprocess_input(input_str: str) -> str:
    """
    Processes a multi-line string containing stack trace entries and returns cleaned lines.

    Args:
        input_str: A string containing stack trace lines with leading 'at' and possible '>' characters.

    Returns:
        A string with each line cleaned of leading 'at', '>', and whitespace, joined by newlines.
    """
    processed_lines = []
    for line in input_str.strip().split('\n'):
        # Remove leading whitespace, '>', 'at' and any surrounding whitespace
        cleaned_line = re.sub(r'^\s*>*\s*at\s+', '', line.strip())
        processed_lines.append(cleaned_line)
    return '\n'.join(processed_lines)

def parse_line(line: str) -> Tuple[Optional[LineData], Optional[str]]:
    """Parse input line into components with error checking"""
    line = line.strip()
    if not line:
        return None, "Empty line"

    # Split method signature and file info
    try:
        method_part, rest = line.split('(', 1)
    except ValueError:
        return None, f"Invalid line format: {line}"

    # Extract file and line number information
    file_line_part = rest.split(')')[0]
    try:
        filename, line_num_str = file_line_part.split(':')
        if line_num_str != "n/a":
            line_num = int(line_num_str)
        else:
            # Unknown file and line number
            line_num = -1
    except ValueError:
        return None, f"Invalid file:line format in line: {line}"

    # Process method signature to get package structure
    method_parts = method_part.split('.')
    if len(method_parts) < 2:
        return None, f"Invalid method format: {method_part}"

    # Construct expected file suffix
    package_parts = method_parts[:-2]  # Remove class and method names
    dir_path = '/'.join(package_parts)
    expected_suffix = os.path.join(dir_path, filename).replace(os.sep, '/')

    return LineData(
        filename=filename,
        filepath="",
        package='.'.join(method_parts[:-1]),
        method=method_parts[-1],
        line_num=line_num,
        expected_suffix=expected_suffix,
        line_of_code=""
    ), None

def get_directories(projects_root: str) -> List[str]:
    """Get all directories in the project root"""
    return [name for name in os.listdir(projects_root) if os.path.isdir(os.path.join(projects_root, name))]

def find_most_likely_project(package_name: str, project_directories: List[str], mapping: Optional[dict] = None) -> Optional[str]:
    """
    Find the most likely project for a given package name.

    Args:
        package_name (str): The Java package name.
        project_directories (list): A list of project directories.
        mapping (dict, optional): A mapping of package prefixes to directory names.

    Returns:
        str: The most likely project directory.
    """
    # First check the mapping if provided
    if mapping:
        for prefix, directory in mapping.items():
            if package_name.startswith(prefix):
                return directory

    # Fall back to existing logic
    package_parts = package_name.split('.')
    for part in package_parts:
        for project in project_directories:
            if part.lower() == project.lower():
                return project

    return None

def find_file_by_suffix(project_root: str, expected_suffix: str) -> List[str]:
    """Search directory tree for files matching path suffix"""
    matches: List[str] = []
    normalized_suffix = expected_suffix.replace(os.sep, '/')

    for root, _dirs, files in os.walk(project_root):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, os.getcwd()).replace(os.sep, '/')
            if rel_path.endswith(normalized_suffix):
                matches.append(full_path)

    return matches

def process_line(projects_root: str, data: LineData, mapping: Optional[dict] = None) -> Tuple[Optional[LineData], Optional[str]]:
    """Process a parsed LineData object to find and read the source line"""
    project = find_most_likely_project(data.package, get_directories(projects_root), mapping)
    if not project:
        return None, f"No project found for package: {data.package}"
    project_root = os.path.join(projects_root, project)
    # Find matching files
    matches = find_file_by_suffix(project_root, data.expected_suffix)
    if not matches:
        return None, f"No file found ending with '{data.expected_suffix}'"
    if len(matches) > 1:
        print(f"Multiple matches for '{data.expected_suffix}', using first", file=sys.stderr)

    file_path = matches[0]

    # Read and validate the source file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if data.line_num < 1 or data.line_num > len(lines):
                return None, f"Line number {data.line_num} out of range in {file_path}"

            code_line = lines[data.line_num - 1].rstrip('\n')
            return LineData(
                filename=data.filename,
                filepath=file_path,
                package=data.package,
                method=data.method,
                line_num=data.line_num,
                expected_suffix=data.expected_suffix,
                line_of_code=code_line,
                project_dir=project,
            ), None

    except FileNotFoundError:
        return None, f"File not found: {file_path}"
    except Exception as e:
        return None, f"Error reading {file_path}: {str(e)}"

def output(data: LineData, class_details: dict, method_details: dict, relative_path: str) -> str:
    result = "<td>\n"
    result += f'<strong><code class="large-code packagename">{data.package}#{data.method}:{data.line_num}</code></strong><br>\n'
    result += f'<p class="filepath">{relative_path}</p>\n'
    result += '<strong class="seperator">Class</strong>\n'
    result += f'<pre><code class="language-java large-code" data-ln-start-from="{class_details['start_line']}">{html.escape(class_details['content'])}</code></pre>\n'
    result += '<strong class="seperator">Method</strong>\n'
    result += f'<pre><code class="language-java large-code" data-ln-start-from="{method_details['start_line']}">{html.escape(method_details['content'])}</code></pre>\n'
    result += "</td>"
    return result

def output_unknown(line: str) -> str:
    return f'<td><strong><code class="large-code packagename">Unknown line</code></strong><br><div class="wrap">{html.escape(line)}</div></td>'

def output_error(line: str, error: str) -> str:
    return f'<td><strong>Error</strong><br><code class="large-code packagename">{html.escape(line)}</code><br>{error}</td>'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find code lines from stack traces',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'projects_root',
        help='Path to the root directory of the projects'
    )
    parser.add_argument(
        'input_file',
        help='Path to input file containing stack traces'
    )
    parser.add_argument(
        'output_file',
        help='Path to output file for code lines'
    )
    parser.add_argument(
        '--mapping',
        help='Optional TOML file containing package prefix to directory mappings'
    )
    args = parser.parse_args()
    main(args.projects_root, args.input_file, args.output_file, args.mapping)

