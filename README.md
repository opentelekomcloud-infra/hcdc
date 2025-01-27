# HCDC - Helpcenter Character Detection Client

HCDC is a client to detect certain characters inside newly changed files from a PR or different git branch. It will look at text files as well as use the OCR service to recognize characters inside new or changed images.

## Usage

```
pip install .
```

```
hcdc --help

options:
  -h, --help            show this help message and exit
  --debug                Option enables Debug output.
  --processes <processes>
                        Number of processes for minification. Default: 4
  --repo-path <repo-path>
                        Path to git repository. Default: .
  --image-file-extensions <file-extensions> [<file-extensions> ...]
                        Image file extensions which should be checked.Default: .jpg .png .jpeg .gif .webp .avif
  --text-file-extensions <file-extensions> [<file-extensions> ...]
                        Text file extensions which should be checked.Default: .txt .md .rst .ini .cfg. json .xml .yml .yaml .py
  --branch <branch>     Branch to compare against main branch. Default: umn
  --main-branch <main-branch>
                        Name of the main branch. Default: main
  --ocr-url <ocr-url>   URL for OCR Service. Default: https://ocr.eu-de.otc.t-systems.com/v2/project-id/ocr/general-text
  --regex-pattern <regex-pattern> [<regex-pattern> ...]
                        Regex pattern to check for unwanted characters.Default: (?![\u4e09\u767d\u76ee\u4e09\u8279\u53e3\u533a\u4e2a\u516b\u4e00\u4eba])[\u4e01-\u9fff]+
  --confidence <processes>
                        Confidence for image recognition. Default 0.95 Default: 0.97

```

You can use a custom regex pattern to check for unwanted characters in the files. The default pattern excludes some chinese characters which can lead to unwanted positive results on results from OCR and checks for all other chinese characters.
To use the tool make sure to specify an `AUTH_TOKEN` which provices access to the OCR service. For more details on how to obtain such a token see: https://docs.otc.t-systems.com/optical-character-recognition/umn/getting_started.html#step-3-using-a-token-for-authentication