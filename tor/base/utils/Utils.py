
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def clamp255(n):
    return clamp(n, 0, 255)