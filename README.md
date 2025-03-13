# TidyFiles

![TidyFiles Logo](https://i.imgur.com/VkDL4QU.jpeg)

**TidyFiles** is a user-friendly, lightweight CLI tool designed to bring order to your Downloads (or any other) folder! It intelligently organizes files by type and keep logs of all the sorting magic.

## 🌟 Features
- Automatically organizes files by type (e.g., images, documents, videos, etc.).
- Logs all operations to keep track of your file management.
- Simple command-line interface.
- Easy installation via [PyPI](https://pypi.org/).

## 🚀 Getting Started

## Installation
Install TidyFiles via pip:
```bash
pip install tidyfiles
```

## Usage
Run TidyFiles to organize your Downloads folder:

```bash
tidyfiles --path /path/to/your/downloads
```

## Example
### Before running TidyFiles:

```plaintext
Downloads/
├── photo.jpg
├── document.pdf
├── video.mp4
```
### After running TidyFiles:

```plaintext
Downloads/
├── images/
│   └── photo.jpg
├── documents/
│   └── document.pdf
├── videos/
│   └── video.mp4
```

## Logs
TidyFiles generates a log file named ```TidyFiles.log``` to record details of all operations performed.

## 🛠️ Contributing
We welcome contributions! Check out the [CONTRIBUTING](CONTRIBUTING.md) file for guidelines on how to get involved.

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ✨ Future Plans
- Add support for custom file categories.

- Extend functionality to include sorting subdirectories.

- Implement multi-language support.

#### Created with ❤️ by Serhii Ryzhaiev.
