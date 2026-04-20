import tarfile
import os

tar_path = r"L:\Documents\Perso\GPECTview\build\site-packages-snapshot.tar.gz"
temp_path = r"L:\Documents\Perso\GPECTview\build\temp.tar.gz"

with tarfile.open(tar_path, "r:gz") as infile:
    with tarfile.open(temp_path, "w:gz") as outfile:
        for member in infile.getmembers():
            # Support any python version (3.12, 3.13, etc)
            if "/site-packages/js/" not in member.name and not member.name.endswith("/site-packages/js"):
                outfile.addfile(member, infile.extractfile(member))

os.replace(temp_path, tar_path)
print("Removed site-packages/js/ from tarball to prevent Plotly js folder from shadowing Pyodide's js module.")
