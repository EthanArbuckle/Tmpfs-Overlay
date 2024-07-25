# This tool needs to be ran with sudo. It may need to be given Full Disk Access or Developer Tools permissions
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def mount_tmpfs_to_target_dir(target_dir_path: Path) -> bool:
    try:
        subprocess.run(["sudo", "mount_tmpfs", target_dir_path.as_posix()], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while mounting the tmpfs onto {target_dir_path}: {e}")
    return False


def tmpfs_mounted_on_directory(target_dir_path: Path) -> bool:
    try:
        mount_output = subprocess.check_output(args=["mount"], text=True)
        mount_output_lines = mount_output.splitlines()
        return any(target_dir_path.as_posix() in line for line in mount_output_lines)
    except subprocess.CalledProcessError as e:
        print(f"Failed to check if dir is already overlayed: {e}")
    return False


def setup_overlay_on_directory(target_dir_path: Path) -> bool:

    if not target_dir_path.exists():
        print(f"Cannot setup overlay on non-existent directory: {target_dir_path}")
        return False

    if tmpfs_mounted_on_directory(target_dir_path):
        print(f"tmpfs already mounted on {target_dir_path}")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Copy the contents of the target directory into a temporary directory
        for file_path in target_dir_path.iterdir():
            if file_path.is_dir():
                shutil.copytree(file_path, temp_dir_path, dirs_exist_ok=True)
            elif file_path.is_file():
                shutil.copy2(file_path, temp_dir_path)

        # Create a tmpfs mount at the target directory.
        # The resulting in-memory directory will be empty (the physical files within the target dir are never modified)
        if not mount_tmpfs_to_target_dir(target_dir_path):
            return False

        # Move the contents of the temporary directory back into the target directory, which is now a tmpfs mount
        did_fail = False
        for file_in_tmp in temp_dir_path.iterdir():
            # Skip fseventsd directory
            if "fsevent" in file_in_tmp.as_posix():
                continue

            # This will fail if the caller isn't privileged
            try:
                shutil.move(file_in_tmp, target_dir_path)
            except Exception as e:
                file_path_relative_to_tmp = file_in_tmp.relative_to(temp_dir_path)
                print(f"Error moving {file_path_relative_to_tmp} to tmpfs: {e}\n")
                # Try to continue moving the rest of the files, but consider this operation a failure
                did_fail = True

    if did_fail:
        print(f"Failed to move all files back to tmpfs {target_dir_path}")

    return did_fail is False


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python main.py <path>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        sys.exit(1)

    if setup_overlay_on_directory(input_path) is False:
        print(f"Failed to setup overlay on directory {input_path}")
        sys.exit(1)

    print(f"Successfully setup overlay on directory {input_path}")
