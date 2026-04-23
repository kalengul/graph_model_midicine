import os
import subprocess

def get_current_commit_hash():
    try:
        # Задаём абсолютный путь к корню проекта (там, где .git)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        result = subprocess.run(
            ['git', '-C', base_dir, 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None