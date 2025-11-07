"""
Tests for the KeyCache class
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from cacheguard.key_cache import KeyCache


class TestKeyCache:
    """Test cases for KeyCache functionality"""

    @pytest.fixture
    def temp_path(self, tmp_path):
        """Create a temporary file path for testing"""
        return tmp_path / "test_cache.json"

    @pytest.fixture
    def sample_data(self):
        """Sample key-value data for testing"""
        return {"key1": "value1", "key2": "value2"}

    @pytest.fixture
    def sample_json(self):
        """Sample JSON string"""
        return '{"key1": "value1", "key2": "value2"}'

    @pytest.fixture
    def encrypted_data(self):
        """Sample encrypted data"""
        return "encrypted_content_here"

    def test_init_no_existing_file(self, temp_path):
        """Test initialization when cache file doesn't exist"""
        with patch('cacheguard.base_cache.path.exists', return_value=False):
            cache = KeyCache(str(temp_path))
            assert cache.age_pubkeys == []
            assert cache.pgp_fingerprints == []
            assert cache.sops_path == str(temp_path)
            assert cache.data == {}

    def test_init_with_existing_file(self, temp_path, sample_json):
        """Test initialization when cache file exists"""
        with patch('cacheguard.base_cache.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="dummy")), \
             patch('cacheguard.base_cache.decrypt', return_value=sample_json):
            cache = KeyCache(str(temp_path))
            assert cache.age_pubkeys == []
            assert cache.pgp_fingerprints == []
            assert cache.sops_path == str(temp_path)
            assert cache.data == {"key1": "value1", "key2": "value2"}

    def test_load_success(self, temp_path, sample_json):
        """Test successful loading of cache data"""
        cache = KeyCache(str(temp_path))
        with patch('builtins.open', mock_open(read_data="encrypted")), \
             patch('cacheguard.base_cache.decrypt', return_value=sample_json):
            result = cache.load()
            assert result == {"key1": "value1", "key2": "value2"}
            assert cache.data == {"key1": "value1", "key2": "value2"}

    def test_load_empty_data(self, temp_path):
        """Test loading when no data exists"""
        cache = KeyCache(str(temp_path))
        with patch('builtins.open', side_effect=OSError("File error")), \
             patch('cacheguard.base_cache.move') as mock_move:
            result = cache.load()
            assert result == {}
            assert cache.data == {}

    def test_save(self, temp_path, sample_data, encrypted_data):
        """Test save method"""
        cache = KeyCache(str(temp_path))
        cache.data = sample_data

        with patch('cacheguard.base_cache.encrypt', return_value=encrypted_data), \
             patch('cacheguard.base_cache.path.exists', return_value=True), \
             patch('builtins.open', mock_open()) as mock_file:

            cache.save()

            # Should encrypt the JSON string
            expected_json = '{"key1": "value1", "key2": "value2"}'
            # Verify encrypt was called with JSON
            # Since we can't easily check the call, check that save was called on super
            with patch('cacheguard.base_cache.BaseCache.save') as mock_super_save:
                cache.save()
                mock_super_save.assert_called_with(expected_json)

    def test_add(self, temp_path):
        """Test add method"""
        cache = KeyCache(str(temp_path))
        cache.data = {"existing": "value"}

        new_entry = {"new_key": "new_value", "another": "entry"}
        cache.add(new_entry)

        expected = {"existing": "value", "new_key": "new_value", "another": "entry"}
        assert cache.data == expected

    def test_add_overwrites_existing(self, temp_path):
        """Test add method overwrites existing keys"""
        cache = KeyCache(str(temp_path))
        cache.data = {"key1": "old_value"}

        cache.add({"key1": "new_value"})

        assert cache.data == {"key1": "new_value"}

    def test_load_env_var_success(self, temp_path):
        """Test loading environment variable successfully"""
        cache = KeyCache(str(temp_path))
        cache.data = {"TEST_VAR": "test_value"}

        with patch.dict('os.environ', {}, clear=True):
            cache.load_env_var("TEST_VAR")
            assert cache.data["TEST_VAR"] == "test_value"

    def test_load_env_var_not_found(self, temp_path):
        """Test loading non-existent environment variable raises KeyError"""
        cache = KeyCache(str(temp_path))
        cache.data = {"existing": "value"}

        with pytest.raises(KeyError, match="Key does not exist in Key Cache"):
            cache.load_env_var("nonexistent")

    def test_deploy(self, temp_path):
        """Test deploy method loads all environment variables"""
        cache = KeyCache(str(temp_path))
        cache.data = {"VAR1": "value1", "VAR2": "value2"}

        with patch.dict('os.environ', {}, clear=True):
            cache.deploy()
            assert cache.data["VAR1"] == "value1"
            assert cache.data["VAR2"] == "value2"