#!/usr/bin/env python3
import argparse
import os
import sys
import re
from typing import Tuple, List, Optional
from dataclasses import dataclass
from ts import get_code_snippet

@dataclass
class LineData:
    filename: str
    filepath: str
    package: str
    method: str
    line_num: int
    expected_suffix: str
    line_of_code: str

def main(project_root: str, input_file: str, output_file: str, rv_format: bool) -> None:
    """Main function that reads input lines and processes each one"""
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            extract_func = extract_stack_trace_rv if rv_format else extract_stack_trace
            fst_st, snd_st = extract_func(infile.read())
            for raw_line in fst_st.split('\n'):
                # Parse line into components
                line = preprocess_input(raw_line)
                if line == '':
                    continue
                data, error = parse_line(line)
                if error:
                    print(error, file=sys.stderr)
                    output_error(line, error, outfile)
                    continue
                if data.package.startswith('com.runtimeverification.rvpredict.runtime.RVPredictRuntime'):
                    print(f"Skipping line: {line}", file=sys.stderr)
                    continue
                if data.line_num == -1:
                    output_unknown(line, outfile)
                    continue
                processed_data, error = process_line(project_root, data)
                if error:
                    print(error, file=sys.stderr)
                    output_error(line, error, outfile)
                    continue
                code_snippet = get_code_snippet(processed_data.filepath, processed_data.line_num)
                output(processed_data, code_snippet, outfile)
            outfile.write('---\n\n')
            for raw_line in snd_st.split('\n'):
                # Parse line into components
                line = preprocess_input(raw_line)
                if line == '':
                    continue
                data, error = parse_line(line)
                if error:
                    print(error, file=sys.stderr)
                    output_error(line, error, outfile)
                    continue
                if data.package.startswith('com.runtimeverification.rvpredict.runtime.RVPredictRuntime'):
                    print(f"Skipping line: {line}", file=sys.stderr)
                    continue
                if data.line_num == -1:
                    output_unknown(line, outfile)
                    continue
                processed_data, error = process_line(project_root, data)
                if error:
                    print(error, file=sys.stderr)
                    output_error(line, error, outfile)
                    continue
                code_snippet = get_code_snippet(processed_data.filepath, processed_data.line_num)
                output(processed_data, code_snippet, outfile)
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

def process_line(project_root: str, data: LineData) -> Tuple[Optional[LineData], Optional[str]]:
    """Process a parsed LineData object to find and read the source line"""
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
                line_of_code=code_line
            ), None

    except FileNotFoundError:
        return None, f"File not found: {file_path}"
    except Exception as e:
        return None, f"Error reading {file_path}: {str(e)}"

def output(data: LineData, code_snippet: str, outfile) -> None:
    """Format and write the final output to specified file"""
    outfile.write(f"`{data.package}#{data.method}:{data.line_num}`\n")
    outfile.write(f"{code_snippet}\n\n")

def output_unknown(line: str, outfile) -> None:
    """Write unknown line format to file"""
    outfile.write(f"```\n{line.strip()}\n```\n\n")

def output_error(line: str, error: str, outfile) -> None:
    """Write error message to file"""
    outfile.write(f"```\n{line.strip()}\n{error}\n```\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find code lines from stack traces',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'project_root',
        help='Path to the root directory of the project'
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
        '--rv',
        action='store_true',
        help='Flag to indicate input is in RV-Predict format'
    )
    args = parser.parse_args()
    main(args.project_root, args.input_file, args.output_file, args.rv)

