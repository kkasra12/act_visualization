import pytest
import os
import pickle
from unittest.mock import patch, MagicMock
from scrapper import CacheList, Scrapper


@pytest.fixture
def temp_cache_file(tmpdir):
    """Create a temporary cache file for testing."""
    return str(tmpdir.join("test_cache.pkl"))


def test_cachelist_initialization(temp_cache_file):
    cache = CacheList(temp_cache_file)
    assert len(cache) == 0  # Should start empty

    cache.append("test_item")
    assert "test_item" in cache

    # Reload and check persistence
    new_cache = CacheList(temp_cache_file)
    assert "test_item" in new_cache


def test_cachelist_append_and_pop(temp_cache_file):
    cache = CacheList(temp_cache_file)
    cache.append("item1")
    cache.append("item2")

    assert len(cache) == 2
    assert cache[0] == "item1"
    
    cache.pop(0)
    assert len(cache) == 1
    assert cache[0] == "item2"


def test_cachelist_save_and_load(temp_cache_file):
    cache = CacheList(temp_cache_file)
    cache.append("saved_item")

    # Manually load the file
    with open(temp_cache_file, "rb") as f:
        loaded_data = pickle.load(f)

    assert "saved_item" in loaded_data


@pytest.fixture
def mock_scrapper():
    """Create a scrapper instance with a mocked cache to avoid file operations."""
    with patch("scrapper.CacheList") as MockCache:
        mock_cache = MagicMock()
        mock_cache.__len__.return_value = 2
        mock_cache.__getitem__.side_effect = lambda index: [[], []][index]  # Ensure two lists exist
        mock_cache.append.side_effect = lambda x: None  # Simulate append without modifying anything
        MockCache.return_value = mock_cache
        return Scrapper(cache_file="test_cache.pkl")



def test_scrapper_initialization(mock_scrapper):
    assert mock_scrapper.start_url == "https://artificialintelligenceact.com"
    assert isinstance(mock_scrapper.cache, MagicMock)
    assert isinstance(mock_scrapper.unvisited_links, list)
    assert mock_scrapper.unvisited_links[-1] is None  # Stop condition is set


@patch("scrapper.requests.get")
def test_scrapper_request(mock_get, mock_scrapper):
    """Mock an HTML request and test response parsing."""
    mock_response = MagicMock()
    mock_response.content = b"<html><body><p>Test Page</p></body></html>"
    mock_get.return_value = mock_response

    soup = mock_scrapper.request("http://fake-url.com")
    assert soup.find("p").text == "Test Page"


@patch("scrapper.Scrapper.request")
def test_scrap_page(mock_request, mock_scrapper):
    """Mock scraping a page and extracting paragraph content."""
    mock_html = """
    <div class="container main-content">
        <p>First paragraph.</p>
        <p>Second paragraph.</p>
    </div>
    """
    mock_request.return_value = MagicMock(find=MagicMock(return_value=MagicMock(
        find_all=MagicMock(return_value=[MagicMock(text="First paragraph."), MagicMock(text="Second paragraph.")])
    )))

    content = mock_scrapper.scrap_page("http://fake-url.com")
    assert content == ["First paragraph.", "Second paragraph."]


@patch("scrapper.Scrapper.request")
def test_scrap_page_no_content(mock_request, mock_scrapper):
    """Ensure scrapping a page without valid content returns an empty string."""
    mock_request.return_value = MagicMock(find=MagicMock(return_value=None))

    content = mock_scrapper.scrap_page("http://fake-url.com")
    assert content == ""


@patch("scrapper.Scrapper.scrap_page")
def test_scrapper_scrap(mock_scrap_page, mock_scrapper):
    """Simulate the scrapping process with multiple pages."""
    mock_scrap_page.side_effect = [["Page 1 Content"], ["Page 2 Content"]]
    mock_scrapper.unvisited_links = ["http://fake-url1.com", "http://fake-url2.com", None]

    mock_scrapper.scrap()

    assert len(mock_scrapper.content) == 2
    assert mock_scrapper.content[0] == ["Page 1 Content"]
    assert mock_scrapper.content[1] == ["Page 2 Content"]
