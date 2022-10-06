# Docker Hub Image Tag Deleter

Schedule and handle the deletion of image tags on the [Docker Hub](https://hub.docker.com).

A GitHub action is also included.

## Getting Started

1. Provide a list of tags in a JSON and/or Markdown file with a deletion date. See [Tag List](#tag-list) below.
2. Run via [cli](#running) or [GitHub Action](#github-action).

## Configuration

### Environment Variables

#### `DOCKERHUB_USERNAME`

__Required__

The username for authenticating with Docker Hub.

#### `DOCKERHUB_PASSWORD`

__Required__

The password or access token for authenticating with Docker Hub.

#### `DOCKERHUB_REPOSITORY`

__Required__

The name of the repository (image) on Docker Hub in the format of `<namespace>/<name>`

#### `DATE_FORMAT`

Format the source date is in using standard the C standard.

See <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>
for more information.

Default: `%B %d, %Y` (October 6, 2022)

#### `DOCKERHUB_API_HOST`

The hostname of the Docker Hub API. Connects over HTTPS.

Default: _hub.docker.com_

#### `JSON_FILE`

The relative path to a JSON file containing a list of tags and dates.

#### `MARKDOWN_FILE`

The relative path to a Markdown file containing a table with tags and dates.

#### `MARKDOWN_BEGIN_STRING`

A string that begins the Markdown table block with tags to parse.

#### `MARKDOWN_END_STRING`

A string that ends the Markdown table block with tags.

### Tag List

A source for tags and their deletion dates must be provided. This may be
provided in a coupld of ways ways - a JSON file and/or a Markdown table.

#### Tag List: JSON File

```json
[
  { "tags": ["1", "1.*"], "date": "October 1, 2022" },
  { "tags": ["2", "2.*"], "date": "November 13, 2023" }
]
```

#### Tag List: Markdown Table

The tag list and deletion dates can be set in a Markdown table using the following format:

```plain
<!-- BEGIN deletion_table -->
| Tag        | Deletion Date
| ---------- | ----------------------
| `1*`       | October 5, 2022
| `2.*`      | October 5, 2022
| `foobar`   | December 25, 2021
<!-- END deletion_table -->
```

* Use a BEGIN and END comment tag surrounding the table block in a Markdown document. These begin/end comment strings are configurable.
* Two-column table with a list of grouped tags in the first column and the deletion date in the second column.
* The table column headers are customizable.
* The list of tags may optionally be formatted (e.g. with single backticks, italics, bold) and can be a comma-separated list of tags with
  wildcards.
* The deletion date format is customizable.

## Running

Ensure the _required_ environment variables are set:

```shell
DOCKERHUB_REPOSITORY=foo/bar
DOCKERHUB_USERNAME=foo
DOCKERHUB_PASSWORD=hunter2
```

```shell
./hub-tag-delete.py
```

## GitHub Action

Basic usage:

```yaml
    - name: Docker Hub Tag Deleter
      uses: joshbeard/hub-tag-delete@v1
      with:
        dockerhub_username: ${{ secrets.DOCKERHUB_USERNAME }}
        dockerhub_password: ${{ secrets.DOCKERHUB_PASSWORD }}
        dockerhub_repository: foo/bar
        markdown_file: README.md
```

__NOTE:__ You __must__ explicitly set one or both of `json_file` and `markdown_file` for
anything to happen.

Setting custom configuration, showing all action inputs:

```yaml
    - name: Docker Hub Tag Deleter
      uses: joshbeard/hub-tag-delete@v1
      with:
        dockerhub_username: ${{ secrets.DOCKERHUB_USERNAME }}
        dockerhub_password: ${{ secrets.DOCKERHUB_PASSWORD }}
        dockerhub_repository: foo/bar
        dockerhub_api_host: hub.docker.com
        date_format: '%B %d, %Y'
        json_file: images.json
        markdown_file: README.md
        markdown_begin_string: '<!-- BEGIN deletion_table -->'
        markdown_end_string: '<!-- END deletion_table -->'
```

Refer to the `inputs` section of the [`action.yml`](action.yml) file for
more information.

## Authors

* Josh Beard, [joshbeard.me](https://joshbeard.me)

## License

[BSD Zero Clause License (0BSD)](LICENSE)

