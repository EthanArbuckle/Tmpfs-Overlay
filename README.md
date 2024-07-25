# Tmpfs Overlay

This tool creates a read+write tmpfs overlay of a given directory, which can let you modify files that may normally be protected by OS restrictions. This is useful for injecting tweaks into the iOS simulator without modifying the original binaries.

## Usage

Full Disk Access and/or Developer Tools permissions may be required.

```sh
$ sudo python main.py /Library/Developer/CoreSimulator/..../Applications/MobileSMS.app
Successfully setup overlay on directory /Library/Developer/CoreSimulator/..../Applications/MobileSMS.app
```

After running the script, the directory will be mounted as a tmpfs overlay. The contents of this directory can be modified without affecting the original files.

```sh
$ mount
/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)
devfs on /dev (devfs, local, nobrowse)
tmpfs on /Library/Developer/CoreSimulator/..../Applications/MobileSMS.app (tmpfs, local)
```
