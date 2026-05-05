#!/usr/bin/env python3
"""
Workspace Search Tool for OpenClaw
Quickly find files and content in the organized workspace.

Usage:
    python3 workspace_search.py <query> [options]
    
Examples:
    python3 workspace_search.py turboquant
    python3 workspace_search.py "PCB design" --type md
    python3 workspace_search.py "AD8332" --content
    python3 workspace_search.py "*.kicad*" --files
"""

import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path("/home/james/.openclaw/workspace")

def colorize(text, color):
    """Add ANSI color codes for terminal output."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m', 
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'bold': '\033[1m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def search_files(query, file_type=None, max_results=20):
    """Search for files by name pattern."""
    results = []
    pattern = query.replace('*', '.*').replace('?', '.')
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Skip hidden directories and git
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.git']
        
        for file in files:
            if file.startswith('.'):
                continue
                
            # Check file type filter
            if file_type and not file.endswith(f'.{file_type}'):
                continue
            
            # Check name match
            if re.search(pattern, file, re.IGNORECASE):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(WORKSPACE_ROOT)
                results.append({
                    'path': rel_path,
                    'full_path': full_path,
                    'type': 'file',
                    'size': full_path.stat().st_size,
                    'modified': datetime.fromtimestamp(full_path.stat().st_mtime)
                })
                
            if len(results) >= max_results:
                break
        
        if len(results) >= max_results:
            break
    
    return results

def search_content(query, max_results=10, context_lines=2):
    """Search inside file contents."""
    results = []
    text_extensions = {'.md', '.py', '.txt', '.c', '.cpp', '.h', '.js', '.json', 
                       '.yaml', '.yml', '.sh', '.kicad_sch', '.kicad_pro'}
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.git']
        
        for file in files:
            if file.startswith('.'):
                continue
                
            ext = Path(file).suffix.lower()
            if ext not in text_extensions:
                continue
            
            full_path = Path(root) / file
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                if query.lower() in content.lower():
                    # Find line numbers with matches
                    lines = content.split('\n')
                    matches = []
                    
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            start = max(0, i - context_lines)
                            end = min(len(lines), i + context_lines + 1)
                            context = '\n'.join(lines[start:end])
                            matches.append({
                                'line': i + 1,
                                'context': context,
                                'match_line': line.strip()
                            })
                    
                    if matches:
                        rel_path = full_path.relative_to(WORKSPACE_ROOT)
                        results.append({
                            'path': rel_path,
                            'full_path': full_path,
                            'type': 'content',
                            'matches': matches[:3]  # Limit matches per file
                        })
                        
            except Exception as e:
                continue
            
            if len(results) >= max_results:
                break
        
        if len(results) >= max_results:
            break
    
    return results

def search_projects(query):
    """Search specifically in 01-Projects folder."""
    projects_dir = WORKSPACE_ROOT / "01-Projects"
    if not projects_dir.exists():
        return []
    
    results = []
    for project_dir in sorted(projects_dir.iterdir()):
        if project_dir.is_dir() and query.lower() in project_dir.name.lower():
            # Count files in project
            file_count = sum(1 for _ in project_dir.rglob('*') if _.is_file())
            
            # Look for README
            readme = project_dir / "README.md"
            description = ""
            if readme.exists():
                try:
                    with open(readme) as f:
                        lines = f.readlines()
                        for line in lines[1:10]:  # First few lines after title
                            if line.strip() and not line.startswith('#'):
                                description = line.strip()[:100]
                                break
                except:
                    pass
            
            results.append({
                'path': project_dir.relative_to(WORKSPACE_ROOT),
                'name': project_dir.name,
                'file_count': file_count,
                'description': description,
                'modified': datetime.fromtimestamp(project_dir.stat().st_mtime)
            })
    
    return results

def format_results(results, search_type='files'):
    """Format search results for display."""
    output = []
    
    if not results:
        return colorize("No results found.", 'yellow')
    
    if search_type == 'projects':
        output.append(colorize(f"\n📁 Found {len(results)} project(s):\n", 'bold'))
        for r in results:
            output.append(colorize(f"  📂 {r['name']}", 'cyan'))
            if r['description']:
                output.append(f"     {r['description']}")
            output.append(f"     {colorize(str(r['file_count']), 'green')} files | Modified: {r['modified'].strftime('%Y-%m-%d')}")
            output.append("")
    
    elif search_type == 'content':
        output.append(colorize(f"\n📝 Found {len(results)} file(s) with matches:\n", 'bold'))
        for r in results:
            output.append(colorize(f"  📄 {r['path']}", 'cyan'))
            for match in r['matches']:
                output.append(f"     Line {colorize(str(match['line']), 'yellow')}:")
                # Highlight the matching term
                highlighted = match['context'].replace(
                    match['match_line'],
                    colorize(match['match_line'], 'green')
                )
                for line in highlighted.split('\n'):
                    output.append(f"       {line}")
            output.append("")
    
    else:  # files
        output.append(colorize(f"\n📄 Found {len(results)} file(s):\n", 'bold'))
        for r in results:
            size_kb = r['size'] / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            output.append(f"  {colorize(str(r['path']), 'cyan')}")
            output.append(f"     Size: {colorize(size_str, 'green')} | Modified: {r['modified'].strftime('%Y-%m-%d %H:%M')}")
    
    return '\n'.join(output)

def main():
    parser = argparse.ArgumentParser(
        description='Search workspace files and content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s turboquant                    # Search for files with "turboquant" in name
  %(prog)s "PCB design" --content        # Search inside file contents
  %(prog)s "*.kicad*" --files            # Search by file pattern
  %(prog)s ultrasound --projects         # Search in project folders
  %(prog)s "AD8332" --content --type md  # Search content only in .md files
        """
    )
    parser.add_argument('query', help='Search query')
    parser.add_argument('--content', '-c', action='store_true', 
                        help='Search inside file contents')
    parser.add_argument('--projects', '-p', action='store_true',
                        help='Search in 01-Projects folder')
    parser.add_argument('--files', '-f', action='store_true',
                        help='Search filenames only (default)')
    parser.add_argument('--type', '-t', help='Filter by file extension (e.g., md, py)')
    parser.add_argument('--max', '-m', type=int, default=20,
                        help='Maximum results (default: 20)')
    
    args = parser.parse_args()
    
    print(colorize(f"\n🔍 Searching for: {args.query}", 'bold'))
    print(colorize(f"📂 Workspace: {WORKSPACE_ROOT}\n", 'blue'))
    
    if args.projects:
        results = search_projects(args.query)
        print(format_results(results, 'projects'))
    elif args.content:
        results = search_content(args.query, max_results=args.max)
        print(format_results(results, 'content'))
    else:
        results = search_files(args.query, file_type=args.type, max_results=args.max)
        print(format_results(results, 'files'))
    
    print(colorize("\n💡 Tip: Use --help for more search options\n", 'yellow'))

if __name__ == '__main__':
    main()
