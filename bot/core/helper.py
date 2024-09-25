def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours} hours, {minutes} mins, {remaining_seconds} secs"
