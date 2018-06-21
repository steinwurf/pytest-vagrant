import os

def walk_up(bottom):
    """
    Mimic os.walk, but walk 'up' instead of down the directory tree.
    """
    while True:
        bottom = os.path.realpath(bottom)
        dirs, nondirs = [], []
        for name in os.listdir(bottom):
            if os.path.isdir(os.path.join(bottom, name)):
                dirs.append(name)
            else:
                nondirs.append(name)

        yield bottom, dirs, nondirs

        new_path = os.path.realpath(os.path.join(bottom, '..'))

        # see if we are at the top
        if new_path == bottom:
            return
        bottom = new_path