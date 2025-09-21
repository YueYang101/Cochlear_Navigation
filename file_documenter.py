"""
File Documenter
Generates a comprehensive documentation file containing the project structure
and contents of Python files only in the current directory
"""

import os
from pathlib import Path
from datetime import datetime
import mimetypes


class FileDocumenter:
    """Document all code files in a project directory."""
    
    # File extensions to include in tree structure
    TREE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r',
        '.m', '.html', '.css', '.scss', '.sass', '.less', '.xml', '.json',
        '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.sh', '.bash',
        '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.dockerfile', '.sql',
        '.md', '.rst', '.txt', '.csv', '.gitignore', '.env', '.editorconfig'
    }
    
    # File extensions to include content for (Python only)
    CONTENT_EXTENSIONS = {'.py'}
    
    # Directories to skip
    SKIP_DIRS = {
        '.git', '.svn', '.hg', '__pycache__', 'node_modules', '.idea',
        '.vscode', '.vs', 'venv', 've', 'env', '.env', 'build', 'dist',
        'target', 'out', 'bin', 'obj', '.pytest_cache', '.mypy_cache',
        'coverage', '.coverage', 'htmlcov', '.tox', 'egg-info',
        '.DS_Store', 'Thumbs.db'
    }
    
    # Binary file extensions to skip
    BINARY_EXTENSIONS = {
        '.pyc', '.pyo', '.so', '.dll', '.dylib', '.exe', '.app',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.tar', '.gz', '.rar', '.7z', '.dmg', '.iso',
        '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
        '.ttf', '.otf', '.woff', '.woff2', '.eot'
    }
    
    def __init__(self, root_path=None, output_file='project_documentation.txt'):
        """
        Initialize documenter.
        
        Args:
            root_path: Root directory to document (default: current directory)
            output_file: Output filename
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.output_file = output_file
        self.file_count = 0
        self.total_lines = 0
        self.file_sizes = {}
        self.python_file_count = 0
        
    def should_include_in_tree(self, file_path):
        """Check if file should be included in tree structure."""
        file_path = Path(file_path)
        
        # Skip if in skip directory
        for parent in file_path.parents:
            if parent.name in self.SKIP_DIRS:
                return False
        
        # Skip binary files
        if file_path.suffix.lower() in self.BINARY_EXTENSIONS:
            return False
        
        # Include if has code extension
        if file_path.suffix.lower() in self.TREE_EXTENSIONS:
            return True
        
        # Include if no extension but might be script (Dockerfile, Makefile, etc.)
        if not file_path.suffix and file_path.name in ['Dockerfile', 'Makefile', 'Rakefile']:
            return True
        
        return False
    
    def should_include_content(self, file_path):
        """Check if file content should be included in documentation."""
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.CONTENT_EXTENSIONS
    
    def get_file_tree(self, start_path=None, prefix="", is_last=True):
        """Generate visual file tree structure."""
        if start_path is None:
            start_path = self.root_path
        
        tree_lines = []
        start_path = Path(start_path)
        
        # Add current directory
        if start_path == self.root_path:
            tree_lines.append(f"{start_path.name}/")
        else:
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{start_path.name}/")
        
        # Get all items in directory
        try:
            items = sorted(start_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return tree_lines
        
        # Filter directories
        dirs = [item for item in items if item.is_dir() and item.name not in self.SKIP_DIRS]
        files = [item for item in items if item.is_file() and self.should_include_in_tree(item)]
        
        # Process directories
        for i, dir_path in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and len(files) == 0
            if start_path == self.root_path:
                sub_prefix = ""
            else:
                sub_prefix = prefix + ("    " if is_last else "│   ")
            
            tree_lines.extend(self.get_file_tree(dir_path, sub_prefix, is_last_dir))
        
        # Process files
        for i, file_path in enumerate(files):
            is_last_file = i == len(files) - 1
            connector = "└── " if is_last_file else "├── "
            
            if start_path == self.root_path:
                file_prefix = connector
            else:
                file_prefix = prefix + ("    " if is_last else "│   ") + connector
            
            # Add file size
            size = file_path.stat().st_size
            size_str = self._format_size(size)
            
            # Mark Python files with an indicator
            if self.should_include_content(file_path):
                tree_lines.append(f"{file_prefix}{file_path.name} ({size_str}) *")
            else:
                tree_lines.append(f"{file_prefix}{file_path.name} ({size_str})")
            
            self.file_sizes[str(file_path.relative_to(self.root_path))] = size
        
        return tree_lines
    
    def _format_size(self, size):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_file_content(self, file_path):
        """Get content of a file with error handling."""
        try:
            # Try to detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Try common encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return raw_data.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            return "[Binary or unreadable file]"
            
        except Exception as e:
            return f"[Error reading file: {e}]"
    
    def document_project(self):
        """Generate complete project documentation."""
        output_lines = []
        
        # Header
        output_lines.append("=" * 80)
        output_lines.append("PROJECT DOCUMENTATION")
        output_lines.append("=" * 80)
        output_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"Root Directory: {self.root_path.absolute()}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # File tree
        output_lines.append("FILE STRUCTURE:")
        output_lines.append("-" * 40)
        output_lines.append("(* indicates Python files with content included)")
        output_lines.append("")
        tree_lines = self.get_file_tree()
        output_lines.extend(tree_lines)
        output_lines.append("")
        
        # File contents (Python files only)
        output_lines.append("=" * 80)
        output_lines.append("PYTHON FILE CONTENTS:")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # Walk through all files
        for root, dirs, files in os.walk(self.root_path):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            
            root_path = Path(root)
            
            for file_name in sorted(files):
                file_path = root_path / file_name
                
                # Count all files in tree
                if self.should_include_in_tree(file_path):
                    self.file_count += 1
                
                # Only include content for Python files
                if not self.should_include_content(file_path):
                    continue
                
                self.python_file_count += 1
                rel_path = file_path.relative_to(self.root_path)
                
                # File header
                output_lines.append("-" * 80)
                output_lines.append(f"FILE: {rel_path}")
                output_lines.append(f"SIZE: {self._format_size(self.file_sizes.get(str(rel_path), 0))}")
                output_lines.append("-" * 80)
                
                # File content
                content = self.get_file_content(file_path)
                lines = content.splitlines()
                self.total_lines += len(lines)
                
                # Add line numbers
                for i, line in enumerate(lines, 1):
                    output_lines.append(f"{i:4d} | {line}")
                
                output_lines.append("")
        
        # Summary
        output_lines.append("=" * 80)
        output_lines.append("SUMMARY:")
        output_lines.append("-" * 40)
        output_lines.append(f"Total Files in Tree: {self.file_count}")
        output_lines.append(f"Python Files with Content: {self.python_file_count}")
        output_lines.append(f"Total Python Lines: {self.total_lines:,}")
        total_size = sum(self.file_sizes.values())
        output_lines.append(f"Total Project Size: {self._format_size(total_size)}")
        output_lines.append("=" * 80)
        
        # Write to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print(f"\nDocumentation generated: {self.output_file}")
        print(f"Total files in tree: {self.file_count}")
        print(f"Python files documented: {self.python_file_count}")
        print(f"Total Python lines: {self.total_lines:,}")
        
        return self.output_file
    
    def generate_summary_only(self):
        """Generate a summary without file contents."""
        output_lines = []
        
        # Header
        output_lines.append("=" * 80)
        output_lines.append("PROJECT SUMMARY")
        output_lines.append("=" * 80)
        output_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"Root Directory: {self.root_path.absolute()}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # File tree
        output_lines.append("FILE STRUCTURE:")
        output_lines.append("-" * 40)
        output_lines.append("(* indicates Python files)")
        output_lines.append("")
        tree_lines = self.get_file_tree()
        output_lines.extend(tree_lines)
        output_lines.append("")
        
        # Statistics by file type
        file_stats = {}
        python_stats = {'count': 0, 'size': 0, 'lines': 0}
        
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            root_path = Path(root)
            
            for file_name in files:
                file_path = root_path / file_name
                if self.should_include_in_tree(file_path):
                    ext = file_path.suffix.lower() or 'no extension'
                    if ext not in file_stats:
                        file_stats[ext] = {'count': 0, 'size': 0}
                    file_stats[ext]['count'] += 1
                    file_stats[ext]['size'] += file_path.stat().st_size
                    
                    # Track Python files separately
                    if ext == '.py':
                        python_stats['count'] += 1
                        python_stats['size'] += file_path.stat().st_size
                        # Count lines in Python files
                        content = self.get_file_content(file_path)
                        python_stats['lines'] += len(content.splitlines())
        
        # Summary statistics
        output_lines.append("=" * 80)
        output_lines.append("FILE TYPE STATISTICS:")
        output_lines.append("-" * 40)
        
        for ext, stats in sorted(file_stats.items()):
            output_lines.append(f"{ext:15} {stats['count']:4d} files  {self._format_size(stats['size']):>10}")
        
        output_lines.append("")
        output_lines.append("PYTHON FILE STATISTICS:")
        output_lines.append("-" * 40)
        output_lines.append(f"Python Files: {python_stats['count']}")
        output_lines.append(f"Total Size: {self._format_size(python_stats['size'])}")
        output_lines.append(f"Total Lines: {python_stats['lines']:,}")
        
        output_lines.append("=" * 80)
        
        summary_file = self.output_file.replace('.txt', '_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print(f"\nSummary generated: {summary_file}")
        return summary_file


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Document Python files in a project')
    parser.add_argument('path', nargs='?', default='.',
                      help='Path to document (default: current directory)')
    parser.add_argument('-o', '--output', default='project_documentation.txt',
                      help='Output filename')
    parser.add_argument('-s', '--summary', action='store_true',
                      help='Generate summary only (no file contents)')
    parser.add_argument('--include-content', nargs='+',
                      help='Additional file extensions to include content for (e.g., .js .ts)')
    parser.add_argument('--exclude-tree', nargs='+',
                      help='File extensions to exclude from tree')
    
    args = parser.parse_args()
    
    # Create documenter
    documenter = FileDocumenter(args.path, args.output)
    
    # Add custom content extensions
    if args.include_content:
        for ext in args.include_content:
            if not ext.startswith('.'):
                ext = '.' + ext
            documenter.CONTENT_EXTENSIONS.add(ext.lower())
    
    # Remove extensions from tree
    if args.exclude_tree:
        for ext in args.exclude_tree:
            if not ext.startswith('.'):
                ext = '.' + ext
            documenter.TREE_EXTENSIONS.discard(ext.lower())
    
    # Generate documentation
    if args.summary:
        documenter.generate_summary_only()
    else:
        documenter.document_project()


if __name__ == "__main__":
    main()