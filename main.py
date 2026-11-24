"""Write the entry image to /output/entry.png (standard library only, no network)."""
import os
import shutil

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "entry.png")
DST_DIR = "/output"


def main():
    os.makedirs(DST_DIR, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(DST_DIR, "entry.png"))


if __name__ == "__main__":
    main()
