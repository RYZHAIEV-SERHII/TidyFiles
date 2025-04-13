from collections import ChainMap
from pathlib import Path

import toml


DEFAULT_CLEANING_PLAN = {
    "documents": {
        "extensions": [
            ".txt",
            ".doc",
            ".docx",
            ".pdf",
            ".rtf",
            ".odt",
            ".tex",
            ".xls",
            ".xlsx",
            ".csv",
            ".ods",
            ".numbers",
            ".tsv",
            ".pages",
        ],
        "ebooks": [".epub", ".mobi", ".azw", ".azw3", ".fb2", ".lit", ".pdb"],
        "presentations": [".ppt", ".pptx", ".odp", ".key", ".pps", ".ppsx"],
    },
    "images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".tif",
        ".webp",
        ".heic",
        ".heif",
        ".raw",
        ".ico",
        ".icns",
        ".svg",
        ".ai",
        ".eps",
        ".psd",
        ".xd",
        ".fig",
        ".sketch",
        ".avif",
        ".jp2",
        ".jxr",
        ".tga",
    ],
    "videos": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".mpeg",
        ".mpg",
        ".vob",
        ".3gp",
        ".ts",
        ".m2ts",
        ".mts",
        ".mxf",
        ".ogv",
    ],
    "music": [
        ".mp3",
        ".flac",
        ".wav",
        ".aac",
        ".ogg",
        ".wma",
        ".opus",
        ".aiff",
        ".alac",
        ".mid",
        ".midi",
        ".m4r",
        ".m4a",
        ".m4b",
        ".amr",
    ],
    "archives": {
        "extensions": [
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".bz2",
            ".xz",
            ".lz",
            ".lzma",
            ".lzh",
            ".arj",
            ".cab",
            ".sit",
            ".sitx",
            ".tgz",
            ".tbz2",
            ".txz",
            ".zst",
            ".cpgz",
            ".pax",
            ".wim",
            ".jar",
            ".xpi",
        ],
        "installers": {
            "windows": [".msi", ".exe", ".msix", ".appx"],
            "unix": [".deb", ".rpm", ".pkg", ".apk", ".run"],
        },
        "disk_images": [".iso", ".img", ".dmg", ".nrg", ".mdf", ".bin"],
    },
    "code": {
        "scripts": [
            ".py",
            ".js",
            ".rb",
            ".php",
            ".sh",
            ".bash",
            ".zsh",
            ".ps1",
            ".ts",
            ".dart",
            ".scala",
            ".groovy",
            ".lua",
            ".pl",
            ".r",
            ".m",
        ],
        "web": [".html", ".css", ".jsx", ".tsx", ".vue", ".svelte"],
        "configs": [".json", ".yaml", ".yml", ".toml", ".ini", ".conf"],
        "compiled": [
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".rs",
            ".swift",
            ".kt",
        ],
        "docs": [".md", ".rst"],
    },
    "fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot", ".ttc", ".dfont"],
    "databases": [
        ".db",
        ".sqlite",
        ".sqlite3",
        ".mdb",
        ".accdb",
        ".dbf",
        ".fdb",
        ".mdf",
        ".ndf",
        ".ldf",
    ],
    "virtual_machines": [
        ".ova",
        ".ovf",
        ".vmdk",
        ".vdi",
        ".vhd",
        ".vhdx",
        ".qcow2",
        ".vbox",
        ".vmx",
    ],
    "cad": {
        "2d": [".dwg", ".dxf", ".iges", ".step"],
        "3d": [
            ".stl",
            ".obj",
            ".3ds",
            ".max",
            ".blend",
            ".skp",
            ".fbx",
            ".dae",
            ".sat",
            ".sldprt",
            ".sldasm",
        ],
    },
    "torrents": [".torrent"],
    "backups": [".bak", ".backup", ".old"],
    "temp": [".tmp", ".temp"],
}

DEFAULT_SETTINGS = {
    "unrecognized_file_name": "other",
    "log_console_output_status": True,
    "log_console_level": "WARNING",
    "log_file_output_status": True,
    "log_file_level": "INFO",
    "log_file_name": "tidyfiles.log",
    "log_folder_name": str(Path.home() / ".tidyfiles"),
    "log_file_mode": "a",
    "settings_file_name": "settings.toml",
    "settings_folder_name": str(Path.home() / ".tidyfiles"),
    "history_file_name": "history.json",
    "history_folder_name": str(Path.home() / ".tidyfiles"),
    "excludes": [],
}

DEFAULT_SETTINGS_PATH = Path.home() / ".tidyfiles" / "settings.toml"


def load_settings(settings_file_path: Path = None) -> dict:
    """
    Load settings from a file.

    If no file path is provided, the function loads the settings from the default
    location (`~/.tidyfiles/settings.toml`). If the file does not exist, it is
    created with default values.

    Args:
        settings_file_path (Path, optional): The path to the settings file. Defaults to None.

    Returns:
        dict: The settings as a dictionary.
    """
    if settings_file_path is None:
        settings_file_path = DEFAULT_SETTINGS_PATH

    try:
        if not settings_file_path.exists():
            settings_file_path.parent.mkdir(parents=True, exist_ok=True)
            save_settings(DEFAULT_SETTINGS, settings_file_path)
        with open(settings_file_path, "r") as f:
            return toml.load(f)
    except (toml.TomlDecodeError, OSError) as e:
        raise RuntimeError(f"Failed to load settings: {e}")


def save_settings(settings: dict, settings_file_path: Path = None) -> None:
    """Save settings to file.

    The settings are saved in TOML format to the file at the specified path (default location is `~/.tidyfiles/settings.toml`).
    If the file does not exist, it is created. If the file exists, it is overwritten.

    Args:
        settings (dict): The settings to save.
        settings_file_path (Path, optional): The path to the settings file. Defaults to None.
    """
    if settings_file_path is None:
        settings_file_path = DEFAULT_SETTINGS_PATH

    settings_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_file_path, "w") as f:
        f.write(toml.dumps(settings))


def get_settings(
    source_dir: str,
    destination_dir: str | None = None,
    cleaning_plan: dict[str, list[str]] | None = None,
    unrecognized_file_name: str = DEFAULT_SETTINGS["unrecognized_file_name"],
    log_console_output_status: bool = DEFAULT_SETTINGS["log_console_output_status"],
    log_file_output_status: bool = DEFAULT_SETTINGS["log_file_output_status"],
    log_console_level: str = DEFAULT_SETTINGS["log_console_level"],
    log_file_level: str = DEFAULT_SETTINGS["log_file_level"],
    log_file_name: str = DEFAULT_SETTINGS["log_file_name"],
    log_folder_name: str = DEFAULT_SETTINGS["log_folder_name"],
    log_file_mode: str = DEFAULT_SETTINGS["log_file_mode"],
    settings_file_name: str = DEFAULT_SETTINGS["settings_file_name"],
    settings_folder_name: str = DEFAULT_SETTINGS["settings_folder_name"],
    excludes: list[str] | None = None,
) -> dict:
    """
    Forms settings for the whole application.

    Settings can be obtained from:
    - CLI (highest priority)
    - settings file
    - default values (lowest priority)

    After combining the primary settings, they are processed and returned as a dictionary.
    """
    if not source_dir:
        raise ValueError("Source directory must be specified")

    # Add source directory validation
    source_path = Path(source_dir)
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    if not source_path.is_dir():
        raise ValueError(f"Source path is not a directory: {source_dir}")

    # Add destination directory validation
    if destination_dir:
        dest_path = Path(destination_dir)
        if dest_path.exists() and not dest_path.is_dir():
            raise ValueError(f"Destination path is not a directory: {destination_dir}")
        try:
            # Try to create the destination directory if it doesn't exist
            dest_path.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise ValueError(
                f"Cannot create destination directory {destination_dir}: {str(e)}"
            )

    default_settings = {
        "source_dir": source_dir,
        "destination_dir": destination_dir,
        "cleaning_plan": cleaning_plan,
        "unrecognized_file_name": unrecognized_file_name,
        "log_console_output_status": log_console_output_status,
        "log_file_output_status": log_file_output_status,
        "log_console_level": log_console_level,
        "log_file_level": log_file_level,
        "log_file_name": log_file_name,
        "log_folder_name": log_folder_name,
        "log_file_mode": log_file_mode,
        "settings_file_name": settings_file_name,
        "settings_folder_name": settings_folder_name,
        "excludes": excludes if excludes else [],
    }

    # Get settings from CLI - collect all non-None values
    cli_settings = {
        key: value for key, value in default_settings.items() if value is not None
    }

    # Get settings from the settings file
    # (a path to the settings file to look for in the settings file - a maven)
    # It is either in the command line or by default
    settings_folder_name = cli_settings.get(
        "settings_folder_name"
    ) or default_settings.get("settings_folder_name")
    settings_file_name = cli_settings.get("settings_file_name") or default_settings.get(
        "settings_file_name"
    )
    if settings_folder_name:
        settings_file_path = (Path(settings_folder_name) / settings_file_name).resolve()
    else:
        settings_file_path = (Path(settings_file_name)).resolve()

    file_settings = load_settings(settings_file_path)

    # Combine settings using ChainMap for priority: CLI > file > defaults
    raw_settings = dict(ChainMap(cli_settings, file_settings, default_settings))

    # --- Process and resolve paths ---

    source_dir = Path(raw_settings["source_dir"]).resolve()
    destination_dir = (
        Path(raw_settings["destination_dir"]).resolve()
        if raw_settings["destination_dir"]
        else source_dir  # Default to source if destination is not provided
    )

    # Resolve cleaning plan paths relative to the destination directory
    if raw_settings["cleaning_plan"]:
        cleaning_plan = {
            (destination_dir / path).resolve(): indexes
            for path, indexes in raw_settings["cleaning_plan"].items()
        }
    else:
        cleaning_plan = {
            (destination_dir / path).resolve(): indexes
            for path, indexes in DEFAULT_CLEANING_PLAN.items()
        }

    # Determine log folder path based on settings or default
    log_folder_setting = raw_settings.get("log_folder_name")
    if log_folder_setting:
        log_folder_path = Path(log_folder_setting).resolve()
    else:
        # Fallback to the default log folder name if not specified
        log_folder_path = Path(DEFAULT_SETTINGS["log_folder_name"]).resolve()
    log_file_path = (log_folder_path / raw_settings["log_file_name"]).resolve()

    # Resolve exclude paths and add settings/log files to the exclude set
    excludes_set = set(Path(path).resolve() for path in raw_settings["excludes"])
    excludes_set.add(settings_file_path)
    excludes_set.add(log_file_path)

    # --- Construct final settings dictionary ---

    settings = {
        "source_dir": source_dir,
        "destination_dir": destination_dir,
        "cleaning_plan": cleaning_plan,
        "unrecognized_file": (destination_dir / unrecognized_file_name).resolve(),
        "log_console_output_status": raw_settings["log_console_output_status"],
        "log_file_path": log_file_path,
        "log_console_level": raw_settings["log_console_level"],
        "log_file_level": raw_settings["log_file_level"],
        "log_level_console": raw_settings["log_console_level"],
        "log_level_file": raw_settings["log_file_level"],
        "log_file_mode": raw_settings["log_file_mode"],
        "settings_file_path": settings_file_path,
        "excludes": excludes_set,
    }

    return settings
