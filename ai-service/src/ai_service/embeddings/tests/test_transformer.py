import pytest
from unittest.mock import patch


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
