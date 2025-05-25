#!/usr/bin/env python3
"""
Script to process markdown files and extract code blocks into separate files.
"""
import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

def extract_code_blocks(content: str) -> List[Dict[str, Any]]:
    """Extract code blocks from markdown content.
    
    Args:
        content: Markdown content as a string
        
    Returns:
        List of dictionaries with 'filename', 'code', and 'language' keys
    """
    # Pattern to match code blocks with optional language and filename
    pattern = r'```(\w*)(?:\s+file=([^\s]+))?\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    blocks = []
    for lang, filename, code in matches:
        if not filename:
            # If no filename is provided, generate one based on language and block index
            block_count = len([b for b in blocks if b['language'] == lang])
            filename = f"unnamed_{lang}_{block_count}.{lang if lang else 'txt'}"
        
        blocks.append({
            'filename': filename.strip(),
            'code': code.strip(),
            'language': lang.lower() if lang else 'text'
        })
    
    return blocks

def process_markdown_file(md_path: Path, output_dir: Path) -> None:
    """Process a single markdown file and extract code blocks.
    
    Args:
        md_path: Path to the markdown file
        output_dir: Base directory to save extracted files
    """
    print(f"Processing {md_path}...")
    
    # Create a subdirectory based on the markdown filename
    file_output_dir = output_dir / md_path.stem
    file_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read the markdown content
    content = md_path.read_text(encoding='utf-8')
    
    # Extract code blocks
    code_blocks = extract_code_blocks(content)
    
    if not code_blocks:
        print(f"  No code blocks found in {md_path}")
        return
    
    # Process each code block
    for block in code_blocks:
        filename = block['filename']
        code = block['code']
        language = block['language']
        
        # Ensure the file has an appropriate extension
        if not any(filename.endswith(ext) for ext in ['.py', '.js', '.go', '.rs', '.cpp', '.h', '.yaml', '.yml', '.json']):
            if language == 'python':
                filename = f"{filename}.py"
            elif language == 'javascript':
                filename = f"{filename}.js"
            elif language == 'go':
                filename = f"{filename}.go"
            elif language == 'rust':
                filename = f"{filename}.rs"
            elif language == 'cpp':
                filename = f"{filename}.cpp"
            elif language in ['yaml', 'yml']:
                filename = f"{filename}.yaml"
            elif language == 'json':
                filename = f"{filename}.json"
        
        # Create the full output path
        output_path = file_output_dir / filename
        
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        output_path.write_text(code, encoding='utf-8')
        print(f"  Created/Updated: {output_path}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Extract code blocks from markdown files')
    parser.add_argument('--input-dir', type=str, default='todo',
                       help='Directory containing markdown files (default: todo/)')
    parser.add_argument('--output-dir', type=str, default='generated',
                       help='Output directory for extracted files (default: generated/)')
    args = parser.parse_args()
    
    # Convert to Path objects
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir / args.input_dir
    output_dir = base_dir / args.output_dir
    
    # Ensure input directory exists
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Input directory '{input_dir}' does not exist or is not a directory")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all markdown files in the input directory
    md_files = list(input_dir.glob('*.md'))
    
    if not md_files:
        print(f"No markdown files found in {input_dir}")
        return 0
    
    print(f"Found {len(md_files)} markdown file(s) in {input_dir}")
    
    for md_file in md_files:
        process_markdown_file(md_file, output_dir)
    
    print("\nProcessing complete!")
    return 0

if __name__ == '__main__':
    exit(main())
