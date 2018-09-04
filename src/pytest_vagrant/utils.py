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


def path_split(path):
    """ Split a path into a list of directories and a filename.

    :param path: A path as a string.
    :return: 2-tuple where the first element is a list of directories and
        the second element is the filename.
    """
    path_split = []

    while path:
        path, leaf = os.path.split(path)
        if leaf:
            # Adds one element, at the beginning of the list
            path_split = [leaf] + path_split
        else:
            path_split = [path] + path_split
            break

    return path_split[:-1], path_split[-1]
