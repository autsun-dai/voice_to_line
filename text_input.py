import subprocess


def type_text(text: str) -> bool:
    """Linux: 使用 xdotool 输入文字"""
    try:
        subprocess.run(
            ["xdotool", "type", "--clearmodifiers", text],
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[错误] 文字输入失败: {e}")
        return False
