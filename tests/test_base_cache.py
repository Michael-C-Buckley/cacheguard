"""
Tests for the BaseCache class
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from cacheguard.base_cache import BaseCache


class TestBaseCache:
    """Test cases for BaseCache functionality"""

    @pytest.fixture
    def temp_path(self, tmp_path):
        """Create a temporary file path for testing"""
        return tmp_path / "test_cache.json"

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return '{"key": "value"}'

    @pytest.fixture
    def encrypted_data(self):
        """Sample encrypted data"""
        return "encrypted_content_here"

    def test_init_no_existing_file(self, temp_path):
        """Test initialization when cache file doesn't exist"""
        with patch('cacheguard.base_cache.path.exists', return_value=False):
            cache = BaseCache(str(temp_path))
            assert cache.age_pubkeys == []
            assert cache.pgp_fingerprints == []
            assert cache.sops_path == str(temp_path)
            assert cache.data == ""

    def test_init_with_existing_file(self, temp_path, sample_data):
        """Test initialization when cache file exists"""
        with patch('cacheguard.base_cache.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="dummy")), \
             patch('cacheguard.base_cache.decrypt', return_value=sample_data):
            cache = BaseCache(str(temp_path))
            assert cache.age_pubkeys == []
            assert cache.pgp_fingerprints == []
            assert cache.sops_path == str(temp_path)
            assert cache.data == sample_data

    def test_load_success(self, temp_path, sample_data, encrypted_data):
        """Test successful loading of cache data"""
        cache = BaseCache(str(temp_path))
        with patch('builtins.open', mock_open(read_data=encrypted_data)), \
             patch('cacheguard.base_cache.decrypt', return_value=sample_data):
            result = cache.load()
            assert result == sample_data

    def test_load_oserror_archives_file(self, temp_path, sample_data):
        """Test load method handles OSError by archiving corrupt file"""
        cache = BaseCache(str(temp_path))

        # Mock open to raise OSError
        with patch('builtins.open', side_effect=OSError("File error")), \
             patch('builtins.print') as mock_print, \
             patch('cacheguard.base_cache.move') as mock_move, \
             patch('cacheguard.base_cache.datetime') as mock_datetime:

            # Mock datetime.now() to return a fixed timestamp
            mock_datetime.now.return_value.strftime.return_value = "20231106_120000"

            result = cache.load()

            # Should return empty string
            assert result == ""

            # Should have attempted to move the file
            mock_move.assert_called_once()

            # Should have printed the warning
            mock_print.assert_called_once()

    def test_save_creates_file_and_encrypts(self, temp_path, sample_data, encrypted_data):
        """Test save method encrypts data and writes to file"""
        cache = BaseCache(str(temp_path))

        with patch('cacheguard.base_cache.encrypt', return_value=encrypted_data), \
             patch('cacheguard.base_cache.path.exists', return_value=False), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.touch'), \
             patch('builtins.open', mock_open()) as mock_file:

            cache.save(sample_data)

            # Verify encrypt was called with sample data
            # Verify file was written with encrypted data
            mock_file.assert_called_with(str(temp_path), "w")
            mock_file().write.assert_called_with(encrypted_data)

    def test_save_existing_file(self, temp_path, sample_data, encrypted_data):
        """Test save method with existing file"""
        cache = BaseCache(str(temp_path))

        with patch('cacheguard.base_cache.encrypt', return_value=encrypted_data), \
             patch('cacheguard.base_cache.path.exists', return_value=True), \
             patch('builtins.open', mock_open()) as mock_file:

            cache.save(sample_data)

            # Should not create directories or touch file
            mock_file.assert_called_with(str(temp_path), "w")
            mock_file().write.assert_called_with(encrypted_data)

    def test_add_raises_not_implemented(self, temp_path):
        """Test that add method raises NotImplementedError"""
        cache = BaseCache(str(temp_path))
        with pytest.raises(NotImplementedError, match="Incorrect cache type - method for Key Cache"):
            cache.add()

    def test_append_raises_not_implemented(self, temp_path):
        """Test that append method raises NotImplementedError"""
        cache = BaseCache(str(temp_path))
        with pytest.raises(NotImplementedError, match="Incorrect cache type - method for Text Cache"):
            cache.append()
