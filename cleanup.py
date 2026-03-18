#!/usr/bin/env python3
"""
项目清理脚本
清理项目中的无用文件，如缓存文件、日志文件、临时文件等
"""

import os
import shutil
import argparse
from pathlib import Path


def get_cleanup_items():
    """获取需要清理的文件和目录模式"""
    return {
        'directories': [
            '__pycache__',
            '.pytest_cache',
            '.mypy_cache',
            '.ruff_cache',
            'dist',
            'build',
            '*.egg-info',
        ],
        'files': [
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '*.log',
            '.DS_Store',
            '*.swp',
            '*.swo',
            '*~',
            '.coverage',
            'htmlcov/**',
            '.env',
            '*.egg',
        ]
    }


def find_items_to_clean(base_path: Path, pattern_type: str, patterns: list):
    """查找需要清理的文件或目录"""
    items_to_clean = []
    
    if pattern_type == 'directories':
        for pattern in patterns:
            if pattern.endswith('/**') or '**' in pattern:
                items_to_clean.extend(base_path.glob(pattern))
            else:
                items_to_clean.extend(base_path.rglob(pattern))
    else:
        for pattern in patterns:
            if pattern.endswith('/**') or '**' in pattern:
                items_to_clean.extend(base_path.glob(pattern))
            else:
                items_to_clean.extend(base_path.rglob(pattern))
    
    return items_to_clean


def clean_project(base_path: Path, dry_run: bool = False, verbose: bool = False):
    """
    清理项目中的无用文件
    
    Args:
        base_path: 项目根目录路径
        dry_run: 如果为 True，只显示将要删除的内容，不实际删除
        verbose: 如果为 True，显示详细信息
    """
    cleanup_items = get_cleanup_items()
    stats = {
        'directories_removed': 0,
        'files_removed': 0,
        'total_size_freed': 0
    }
    
    print(f"扫描项目目录：{base_path}")
    print("-" * 60)
    
    all_items = []
    
    for pattern_type, patterns in cleanup_items.items():
        items = find_items_to_clean(base_path, pattern_type, patterns)
        all_items.extend([(item, pattern_type) for item in items])
    
    if not all_items:
        print("✓ 没有发现需要清理的文件或目录")
        return stats
    
    print(f"发现 {len(all_items)} 个需要清理的项目:\n")
    
    for item, pattern_type in sorted(all_items):
        if not item.exists():
            continue
            
        try:
            if item.is_dir():
                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            else:
                size = item.stat().st_size
            
            action = "Would delete" if dry_run else "Deleting"
            item_type = "DIR" if item.is_dir() else "FILE"
            
            if verbose:
                print(f"  [{item_type}] {action}: {item} ({size:,} bytes)")
            else:
                print(f"  {action}: {item}")
            
            if not dry_run:
                if item.is_dir():
                    shutil.rmtree(item)
                    stats['directories_removed'] += 1
                else:
                    item.unlink()
                    stats['files_removed'] += 1
                stats['total_size_freed'] += size
                
        except Exception as e:
            print(f"  ✗ 清理失败 {item}: {e}")
    
    if not dry_run:
        print("\n" + "-" * 60)
        print(f"清理完成!")
        print(f"  - 删除的目录数：{stats['directories_removed']}")
        print(f"  - 删除的文件数：{stats['files_removed']}")
        print(f"  - 释放空间：{stats['total_size_freed']:,} bytes ({stats['total_size_freed'] / 1024:.2f} KB)")
    else:
        print("\n" + "-" * 60)
        print(f"干运行模式 - 未删除任何文件")
        print(f"  将要删除的项目数：{len(all_items)}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='清理项目中的无用文件（缓存、日志、临时文件等）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cleanup.py                    # 清理当前目录
  python cleanup.py -p /path/to/project  # 清理指定项目
  python cleanup.py --dry-run          # 预览将要删除的文件
  python cleanup.py -v                 # 显示详细信息
        """
    )
    
    parser.add_argument(
        '-p', '--path',
        type=Path,
        default=Path('.'),
        help='项目根目录路径 (默认：当前目录)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只预览将要删除的文件，不实际删除'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息（包括文件大小）'
    )
    
    args = parser.parse_args()
    
    base_path = args.path.resolve()
    
    if not base_path.exists():
        print(f"错误：目录不存在：{base_path}")
        return 1
    
    if not base_path.is_dir():
        print(f"错误：路径不是目录：{base_path}")
        return 1
    
    try:
        clean_project(base_path, dry_run=args.dry_run, verbose=args.verbose)
        return 0
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 1
    except Exception as e:
        print(f"\n错误：{e}")
        return 1


if __name__ == '__main__':
    exit(main())
