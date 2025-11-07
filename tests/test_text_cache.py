"""
Tests for the TextCache class
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from cacheguard.text_cache import TextCache


class TestTextCache:
    """Test cases for TextCache functionality"""

    @pytest.fixture
    def temp_path(self, tmp_path):
        """Create a temporary file path for testing"""
        return tmp_path / "test_cache.txt"

    @pytest.fixture
    def sample_data(self):
        """Sample text data for testing"""
        return "line1\nline2\nline3"

    @pytest.fixture
    def encrypted_data(self):
        """Sample encrypted data"""
        return "encrypted_content_here"

    def test_init_no_existing_file(self, temp_path):
        """Test initialization when cache file doesn't exist"""
        with patch('cacheguard.base_cache.path.exists', return_value=False):
            cache = TextCache(str(temp_path))
            assert cache.age_pubkeys == []
            assert cache.pgp_fingerprints == []
            assert cache.sops_path == str(temp_path)
            assert cache.newline == "\n"
            assert cache.buffer.getvalue() == ""

    def test_init_with_existing_file(self, temp_path, sample_data):
        """Test initialization when cache file exists"""
        with patch('cacheguard.base_cache.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="dummy")), \
             patch('cacheguard.base_cache.decrypt', return_value=sample_data):
            cache = TextCache(str(temp_path))
            assert cache.age_pubkeys == []
            assert cache.pgp_fingerprints == []
            assert cache.sops_path == str(temp_path)
            assert cache.newline == "\n"
            # Should have appended the lines
            expected = "line1\nline2\nline3\n"
            assert cache.buffer.getvalue() == expected

    def test_init_custom_newline(self, temp_path, sample_data):
        """Test initialization with custom newline"""
        custom_newline = "\r\n"
        sample_data_custom = "line1\r\nline2\r\nline3"
        with patch('cacheguard.base_cache.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="dummy")), \
             patch('cacheguard.base_cache.decrypt', return_value=sample_data_custom):
            cache = TextCache(str(temp_path), newline=custom_newline)
            assert cache.newline == custom_newline
            expected = "line1\r\nline2\r\nline3\r\n"
            assert cache.buffer.getvalue() == expected

    def test_load(self, temp_path, sample_data):
        """Test load method"""
        cache = TextCache(str(temp_path))
        with patch('builtins.open', mock_open(read_data="encrypted")), \
             patch('cacheguard.base_cache.decrypt', return_value=sample_data):
            result = cache.load()
            assert result == sample_data
            # Buffer should be reset to StringIO with data
            assert cache.buffer.getvalue() == sample_data

    def test_save_without_data_string(self, temp_path, encrypted_data):
        """Test save method without providing data_string"""
        cache = TextCache(str(temp_path))
        cache.buffer.write("test content\nmore content\n")

        with patch('cacheguard.base_cache.encrypt', return_value=encrypted_data), \
             patch('cacheguard.base_cache.path.exists', return_value=True), \
             patch('builtins.open', mock_open()) as mock_file:

            cache.save()

            # Should encrypt the buffer content stripped
            expected_data = "test content\nmore content"
            # Verify encrypt was called with stripped buffer content
            # Since we can't easily check the call, check that save was called on super
            # Actually, patch super().save
            with patch('cacheguard.base_cache.BaseCache.save') as mock_super_save:
                cache.save()
                mock_super_save.assert_called_with(expected_data)

    def test_save_with_data_string(self, temp_path, sample_data, encrypted_data):
        """Test save method with provided data_string"""
        cache = TextCache(str(temp_path))

        with patch('cacheguard.base_cache.BaseCache.save') as mock_super_save:
            cache.save(sample_data)
            mock_super_save.assert_called_with(sample_data)

    def test_append(self, temp_path):
        """Test append method"""
        cache = TextCache(str(temp_path))
        cache.append("first line")
        cache.append("second line")
        expected = "first line\nsecond line\n"
        assert cache.buffer.getvalue() == expected

    def test_append_custom_newline(self, temp_path):
        """Test append with custom newline"""
        cache = TextCache(str(temp_path), newline="\r\n")
        cache.append("first line")
        cache.append("second line")
        expected = "first line\r\nsecond line\r\n"
        assert cache.buffer.getvalue() == expected