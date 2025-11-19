"""Dataset service - wraps pdfGUI PDF data handling.

Wraps: diffpy.pdfgui.control.fitdataset, diffpy.pdfgui.control.pdfdataset
"""
import numpy as np
from typing import Dict, List, Any, Optional
from diffpy.pdfgui.control.fitdataset import FitDataSet, grid_interpolation
from diffpy.pdfgui.control.pdfdataset import PDFDataSet


class DatasetService:
    """Service for PDF dataset operations."""

    def read_data_file(self, filepath: str) -> Dict[str, Any]:
        """Read PDF data from file.

        Wraps: PDFDataSet.read()
        Supports: .gr, .dat, .chi formats
        """
        dataset = PDFDataSet()
        dataset.read(filepath)

        return self._dataset_to_dict(dataset)

    def read_data_string(self, content: str) -> Dict[str, Any]:
        """Read PDF data from string.

        Wraps: PDFDataSet.readStr()
        """
        dataset = PDFDataSet()
        dataset.readStr(content)

        return self._dataset_to_dict(dataset)

    def _dataset_to_dict(self, dataset: PDFDataSet) -> Dict[str, Any]:
        """Convert PDFDataSet to dictionary."""
        return {
            "stype": dataset.stype,  # 'N' or 'X'
            "qmax": float(dataset.qmax),
            "point_count": len(dataset.robs),
            "r_range": [float(dataset.robs[0]), float(dataset.robs[-1])],
            "observed": {
                "robs": dataset.robs.tolist(),
                "Gobs": dataset.Gobs.tolist(),
                "dGobs": dataset.dGobs.tolist() if hasattr(dataset, 'dGobs') else []
            },
            "metadata": {
                "drobs": dataset.drobs.tolist() if hasattr(dataset, 'drobs') else []
            }
        }

    def create_fit_dataset(self, name: str) -> FitDataSet:
        """Create a new FitDataSet for refinement.

        Wraps: FitDataSet.__init__()
        """
        return FitDataSet(name)

    def set_observed_data(
        self,
        dataset: FitDataSet,
        robs: List[float],
        Gobs: List[float],
        dGobs: Optional[List[float]] = None
    ) -> None:
        """Set observed PDF data.

        Wraps: FitDataSet.robs, Gobs, dGobs
        """
        dataset.robs = np.array(robs)
        dataset.Gobs = np.array(Gobs)
        if dGobs:
            dataset.dGobs = np.array(dGobs)
        else:
            # Default uncertainty
            dataset.dGobs = np.ones_like(dataset.Gobs) * 0.01

    def set_instrument_parameters(
        self,
        dataset: FitDataSet,
        stype: str = "N",
        qmax: float = 32.0,
        qdamp: float = 0.01,
        qbroad: float = 0.0,
        dscale: float = 1.0
    ) -> None:
        """Set instrument parameters.

        Wraps: FitDataSet.stype, qmax, qdamp, qbroad, dscale
        """
        dataset.stype = stype
        dataset.qmax = qmax
        dataset.qdamp = qdamp
        dataset.qbroad = qbroad
        dataset.dscale = dscale

    def set_fit_range(
        self,
        dataset: FitDataSet,
        rmin: float,
        rmax: float,
        rstep: float
    ) -> None:
        """Set fitting range.

        Wraps: FitDataSet.fitrmin, fitrmax, fitrstep
        """
        dataset.fitrmin = rmin
        dataset.fitrmax = rmax
        dataset.fitrstep = rstep

    def resample_data(
        self,
        x0: List[float],
        y0: List[float],
        x1: List[float]
    ) -> List[float]:
        """Resample data using sinc interpolation.

        Wraps: grid_interpolation()

        This is the numerical interpolation function used by pdfGUI
        for resampling calculated PDF to observed r-grid.
        """
        result = grid_interpolation(
            np.array(x0),
            np.array(y0),
            np.array(x1)
        )
        return result.tolist()

    def get_resampled_dataset(self, dataset: FitDataSet) -> Dict[str, Any]:
        """Get resampled PDF data for fitting.

        Wraps: FitDataSet._resampledPDFDataSet()
        """
        # This uses the internal resampling logic
        resampled = dataset._resampledPDFDataSet()

        return {
            "r": resampled.robs.tolist(),
            "G": resampled.Gobs.tolist(),
            "dG": resampled.dGobs.tolist(),
            "point_count": len(resampled.robs)
        }

    def calculate_rw(
        self,
        Gobs: List[float],
        Gcalc: List[float],
        dGobs: Optional[List[float]] = None
    ) -> float:
        """Calculate Rw residual value.

        Standard PDF residual calculation:
        Rw = sqrt(sum(w * (Gobs - Gcalc)^2) / sum(w * Gobs^2))
        """
        Gobs = np.array(Gobs)
        Gcalc = np.array(Gcalc)

        if dGobs:
            w = 1.0 / np.array(dGobs)**2
        else:
            w = np.ones_like(Gobs)

        diff = Gobs - Gcalc
        rw = np.sqrt(np.sum(w * diff**2) / np.sum(w * Gobs**2))

        return float(rw)

    def write_data(
        self,
        dataset: FitDataSet,
        filepath: str,
        include_calc: bool = False
    ) -> None:
        """Write PDF data to file.

        Wraps: FitDataSet.write()
        """
        dataset.write(filepath)

    def get_calculated_data(self, dataset: FitDataSet) -> Dict[str, List[float]]:
        """Get calculated PDF data after refinement.

        Wraps: FitDataSet.rcalc, Gcalc
        """
        if not hasattr(dataset, 'rcalc') or dataset.rcalc is None:
            return {"r": [], "G": []}

        return {
            "r": dataset.rcalc.tolist(),
            "G": dataset.Gcalc.tolist()
        }

    def get_difference(self, dataset: FitDataSet) -> Dict[str, List[float]]:
        """Get difference curve (Gobs - Gcalc).

        Wraps: FitDataSet computed difference
        """
        if not hasattr(dataset, 'Gcalc') or dataset.Gcalc is None:
            return {"r": [], "G": []}

        diff = dataset.Gobs - dataset.Gcalc

        return {
            "r": dataset.robs.tolist(),
            "G": diff.tolist()
        }
