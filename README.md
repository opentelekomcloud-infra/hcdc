# HCDC - Helpcenter Character Detection Client

HCDC is a client to detect certain characters inside newly changed files from a PR or a different Git branch. It will analyze text files and use an OCR service to recognize characters inside new or changed images.

## Installation

```sh
pip install .
```

## Usage

```sh
hcdc --help
```

### Options

```
  -h, --help            Show this help message and exit.
  --debug               Option enables debug output.
  --processes <processes>
                        Number of processes for minification. Default: 4
  --repo-path <repo-path>
                        Path to the Git repository. Default: .
  --image-file-extensions <file-extensions> [<file-extensions> ...]
                        Image file extensions to be checked. Default: .jpg .png .jpeg .gif .webp .avif
  --text-file-extensions <file-extensions> [<file-extensions> ...]
                        Text file extensions to be checked. Default: .txt .md .rst .ini .cfg .json .xml .yml .yaml .py
  --branch <branch>     Branch to compare against the main branch. Default: main
  --main-branch <main-branch>
                        Name of the main branch. Default: main
  --ocr-url <ocr-url>   URL for the OCR Service. Default: https://ocr.eu-de.otc.t-systems.com/v2/project-id/ocr/general-text
  --regex-pattern <regex-pattern> [<regex-pattern> ...]
                        Regex pattern to check for unwanted characters. Default: (?![\u4e09\u767d\u76ee\u4e09\u8279\u53e3\u533a\u4e2a\u516b\u4e00\u4eba])[\u4e01-\u9fff]+
  --confidence <confidence>
                        Confidence threshold for image recognition. Default: 0.97
```

## Custom Regex Pattern

You can use a custom regex pattern to check for unwanted characters in the files. The default pattern excludes some Chinese characters that may cause false positives in OCR results while checking for all other Chinese characters.

## Authentication

To use this tool, ensure that you specify an `AUTH_TOKEN` to access the OCR service. For details on obtaining a token, refer to the official [T-Systems Documentation](https://docs.otc.t-systems.com/optical-character-recognition/umn/getting_started.html#step-3-using-a-token-for-authentication).
