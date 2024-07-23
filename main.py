import shutil
import subprocess
import tempfile
from pathlib import Path


def mount_tmpfs_to_target_dir(target_dir_path: Path) -> None:
    try:
        args = ["sudo", "mount_tmpfs", target_dir_path.as_posix()]
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while mounting the tmpfs onto {target_dir_path}: {e} {e.output}")
        raise e


def main() -> None:
    target_dir_path = Path("/Library/Developer/CoreSimulator/Profiles/Runtimes/iOS 15.5.simruntime/Contents/Resources/RuntimeRoot/System/Library/CoreServices/CarPlay.app/")
    if not target_dir_path.exists():
        target_dir_path.mkdir()
        mount_tmpfs_to_target_dir(target_dir_path)
    else:
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent.resolve(), delete=False) as temp_dir:

            temp_dir_path = Path(temp_dir)
            for file_path in target_dir_path.iterdir():
                try:
                    # print(f"Stashing {file_path}")
                    subprocess.check_output(["sudo", "cp", "-r", file_path, temp_dir_path])
                    # if file_path.is_file():
                    #     shutil.copy(file_path, temp_dir_path)
                    # elif file_path.is_dir():
                    #     shutil.copytree(file_path, temp_dir_path / file_path.name)
                except Exception as e:
                    print(f"An error occurred while copying a file to the tmpdir: {e} - {file_path}")

            mount_tmpfs_to_target_dir(target_dir_path)
            print(f"Mounted tmpfs at {target_dir_path}")

            for file_path in temp_dir_path.glob("*"):
                try:
                    to_path =  file_path, target_dir_path / file_path.name
                    print(f"Restoring {file_path} to {to_path}")
                    if file_path.is_file():
                        # shutil.copy(file_path, target_dir_path)
                        subprocess.check_output(["sudo", "mv", file_path, target_dir_path / file_path.name])
                    elif file_path.is_dir():
                        subprocess.check_output(["sudo", "mv", file_path, target_dir_path / file_path.name])
                        # shutil.copytree(file_path, target_dir_path / file_path.name)
                except Exception as e:
                    print(f"An error occurred copying a file into the tmpfs: {e}")

    print(f"Done: {target_dir_path}")


if __name__ == "__main__":
    main()
