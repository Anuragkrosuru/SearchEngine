"""Verify submitted files and directories required by the spec."""

from pathlib import Path
import bs4
import markdown


def test_files_exist():
    """Check for files and directories required by the spec."""
    assert Path("bin").exists()
    assert Path("bin/search").exists()
    assert Path("bin/index").exists()
    assert Path("bin/searchdb").exists()
    assert Path("bin/install").exists()
    assert Path("inverted_index/pipeline.sh").exists()
    assert Path("index_server").exists()
    assert Path("index_server/index").exists()
    assert Path("index_server/index/api").exists()
    assert Path("index_server/pyproject.toml").exists()
    assert Path(
        "index_server/index/inverted_index/inverted_index_0.txt"
    ).exists()
    assert Path(
        "index_server/index/inverted_index/inverted_index_1.txt"
    ).exists()
    assert Path(
        "index_server/index/inverted_index/inverted_index_2.txt"
    ).exists()
    assert Path("search_server").exists()
    assert Path("search_server/search").exists()
    assert Path("search_server/search/views").exists()
    assert Path("search_server/pyproject.toml").exists()


def test_check_chatdoc_survey():
    """Check for and validate chatdoc.md."""
    assert Path("chatdoc.md").exists()

    with open("chatdoc.md", encoding="utf-8") as md_file:
        md_text = md_file.read()

    # Parse the HTML content
    html_text = markdown.markdown(md_text, extensions=["attr_list"])
    soup = bs4.BeautifulSoup(html_text, "html.parser")

    # Extract answers
    num_questions = 8
    for i in range(1, num_questions+1):
        qid = f"Q{i}"
        question = soup.find(id=qid)
        assert question, f"Failed to find {qid}"
        answer = question.find_next()
        if answer.name == "ul":
            selection = ""
            for list_item in answer.find_all("li"):
                if list_item.text.lower().startswith("[x]"):
                    assert not selection, f"{qid}: Expected one selection"
                    selection = list_item.text.replace("[x]", "").strip()
            assert selection, f"{qid}: Missing selection"
