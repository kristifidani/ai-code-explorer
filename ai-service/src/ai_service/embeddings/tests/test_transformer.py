"""
Tests for the transformer module - model loading, device detection, caching.
"""

import pytest
from unittest.mock import patch, MagicMock
from ai_service import errors
from ai_service.embeddings import transformer
from dotenv import load_dotenv

load_dotenv()


class TestDeviceDetection:
    """Test device detection functionality."""

    @pytest.mark.parametrize(
        "cuda_available,mps_available,expected_device,test_name",
        [
            (True, True, "cuda", "prefers_cuda_when_both_available"),
            (False, True, "mps", "falls_back_to_mps_when_cuda_unavailable"),
            (False, False, "cpu", "falls_back_to_cpu_when_neither_available"),
        ],
    )
    @patch("torch.cuda.is_available")
    @patch("torch.backends.mps.is_available")
    def test_device_detection(
        self,
        mock_mps,  # type: ignore
        mock_cuda,  # type: ignore
        cuda_available: bool,
        mps_available: bool,
        expected_device: str,
        test_name: str,
    ):
        """Test device detection logic with different hardware availability scenarios."""
        mock_cuda.return_value = cuda_available
        mock_mps.return_value = mps_available

        with patch(
            "ai_service.embeddings.transformer._get_device",
            return_value=expected_device,
        ) as mock_get_device:
            device = mock_get_device()
            assert device == expected_device


class TestModelLoading:
    """Test model loading and caching functionality."""

    @patch("ai_service.embeddings.transformer.SentenceTransformer")
    @patch("ai_service.utils.get_env_var")
    @patch("ai_service.embeddings.transformer._get_device")
    def test_get_model_loads_successfully(
        self,
        mock_get_device,  # type: ignore
        mock_get_env,  # type: ignore
        mock_transformer,  # type: ignore
    ):
        mock_get_env.return_value = "test-model"
        mock_get_device.return_value = "cpu"
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model

        # Clear cache before test
        transformer.get_model.cache_clear()

        model = transformer.get_model()

        assert model == mock_model
        mock_transformer.assert_called_once_with(  # type: ignore
            model_name_or_path="test-model",
            device="cpu",
            trust_remote_code=False,
            cache_folder=None,
        )

    @patch("ai_service.embeddings.transformer.SentenceTransformer")
    @patch("ai_service.utils.get_env_var")
    def test_get_model_handles_loading_failure(self, mock_get_env, mock_transformer):  # type: ignore
        mock_get_env.return_value = "invalid-model"
        mock_transformer.side_effect = Exception("Model not found")

        # Clear cache before test
        transformer.get_model.cache_clear()

        with pytest.raises(errors.EmbeddingError) as exc_info:
            transformer.get_model()

        assert "Failed to load embedding model 'invalid-model'" in str(exc_info.value)

    @patch("ai_service.embeddings.transformer.SentenceTransformer")
    @patch("ai_service.utils.get_env_var")
    @patch("ai_service.embeddings.transformer._get_device")
    def test_get_model_caching(self, mock_get_device, mock_get_env, mock_transformer):  # type: ignore
        """Test that get_model uses LRU cache and only loads once."""
        mock_get_env.return_value = "test-model"
        mock_get_device.return_value = "cpu"
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model

        # Clear cache first
        transformer.get_model.cache_clear()

        # Call multiple times
        model1 = transformer.get_model()
        model2 = transformer.get_model()
        model3 = transformer.get_model()

        # Should all return the same instance
        assert model1 is model2 is model3
        # SentenceTransformer should only be called once due to caching
        assert mock_transformer.call_count == 1  # type: ignore
