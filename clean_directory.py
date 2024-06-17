import os

destination = "data"
file_keyword = "MacLeish.dat"
no_touchy = [".venv", ".vscode", "Py3SQM", "data"]


def clean_up() -> None:
    """Moves sensor readings to a single directory and deletes extraneous directories."""
    make_dest()  # make destination folder
    for item in os.listdir("."):  # look at all items
        if item not in no_touchy:
            if os.path.isdir(item):
                rec(item)  # recurse on directory
            elif file_keyword in item:
                src = f"{item}"
                dst = f"{destination}/{item}"
                try_replace(src, dst)
                # os.replace(src, dst)  # move file to destination


def try_replace(src: str, dst: str) -> None:
    """Replaces file at destination with source file, if the source file is younger.

    Args:
        src (str): source file to move
        dst (str): _description_
    """
    if os.path.isfile(dst):
        print(f"file already exists at {dst}: ", end="")
        birth_dst = os.path.getctime(dst)  # time dst file created
        birth_src = os.path.getctime(src)  # time src file created
        if birth_dst <= birth_src:  # if dst is more recent
            os.remove(src)  # just remove old src file
            print("keeping most recent file")
            return
    # if src is more recent or dst doesn't exist:
    print("")
    os.replace(src, dst)  # move file to destination


def make_dest() -> None:
    """Creates destination directory, if it doesn't already exist."""
    if not os.path.isdir(destination):
        os.makedirs(destination)


def rec(curr_path: str) -> None:
    """Recurses through directories, moving sensor readings and deleting empty directories.

    Args:
        curr_path (str): current location in file tree
    """
    for item in os.listdir(curr_path):
        # if directory, search it
        if os.path.isdir(f"{curr_path}/{item}"):
            rec(f"{curr_path}/{item}")
        # if file matches keyword, move to dest
        elif file_keyword in item:
            src = f"{curr_path}/{item}"
            dst = f"{destination}/{item}"
            try_replace(src, dst)
            # os.replace(src, dst)
    if len(os.listdir(curr_path)) == 0:
        # if this dir is empty, delete it
        os.rmdir(curr_path)


clean_up()
