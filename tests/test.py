from datetime import datetime
import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

os.environ['MARKDOWN_FILE'] = "tests/test.md"
os.environ['JSON_FILE'] = "tests/test.json"
os.environ['DOCKERHUB_REPOSITORY'] = "foo/bar"

target = __import__("hub-tag-delete")

def test_line_is_ignored():
    assert target.line_is_ignored('| 1.0') is False
    assert target.line_is_ignored('| `1.0`') is False

def test_get_readme_table():
    taglist = [
        {'date': 'October 5, 2022', 'tags': ['1*']},
        {'date': 'October 5, 2022', 'tags': ['2.*']},
        {'date': 'October 5, 2040', 'tags': ['3.*']},
        {'date': 'December 25, 2021', 'tags': ['foobar']}
    ]
    assert target.get_readme_table() == taglist

def test_parse_date():
    date = "October 6, 2022"
    assert target.parse_date(date) == datetime(2022, 10, 6, 0, 0)

def test_parse_md_line():
    mdline = '| `1.*`, `2.0` | October 6, 2022'
    result = {'tags': ['1.*',' 2.0'], 'date': 'October 6, 2022'}
    assert target.parse_md_line(mdline) == result

def test_json_tags():
    result = [
        {'date': 'April 1, 2022', 'tags': ['4', '4.*']},
        {'date': 'June 10, 2023', 'tags': ['5', '5.*']},
        {'date': 'October 31, 2023', 'tags': ['json-foobar']}
    ]
    assert target.json_tags() == result

def test_get_tag_list():
    taglist = [
        {'date': 'April 1, 2022', 'tags': ['4', '4.*']},
        {'date': 'June 10, 2023', 'tags': ['5', '5.*']},
        {'date': 'October 31, 2023', 'tags': ['json-foobar']},
        {'date': 'October 5, 2022', 'tags': ['1*']},
        {'date': 'October 5, 2022', 'tags': ['2.*']},
        {'date': 'October 5, 2040', 'tags': ['3.*']},
        {'date': 'December 25, 2021', 'tags': ['foobar']}
    ]
    assert target.get_tag_list() == taglist

# TODO: The tests that require Docker Hub connectivity are pending
def test_tags_to_delete():
	"""Docker Hub required"""
	pass

def test_delete_expired_tags():
	"""Docker Hub required"""
	pass

def test_docker_hub_token():
	"""Docker Hub required"""
	pass

def test_tags_matching_pattern():
	"""Docker Hub required"""
	pass

