"""SocrateAI-Scientific-QuantumFluids: Dual-scale regularization in quantum-fluid physics."""

__version__ = "0.1.0-proposal"
__status__ = "M0 (bootstrap)"

from . import adapters
from . import dispersion_fit
from . import w4_shell_model

__all__ = ["adapters", "dispersion_fit", "w4_shell_model"]
