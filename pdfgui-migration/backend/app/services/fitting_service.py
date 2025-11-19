"""Fitting service - wraps pdfGUI fitting/refinement logic.

This service extracts and wraps the computational logic from:
- diffpy.pdfgui.control.fitting
- diffpy.pdfgui.control.pdfguicontrol

IMPORTANT: All algorithms are kept EXACTLY as in the original pdfGUI.
No modifications, optimizations, or intelligence added.
"""

import threading
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

import numpy as np

from diffpy.pdfgui.control.calculation import Calculation
from diffpy.pdfgui.control.constraint import Constraint
from diffpy.pdfgui.control.fitdataset import FitDataSet
from diffpy.pdfgui.control.fitstructure import FitStructure

# Import original pdfGUI control modules
from diffpy.pdfgui.control.fitting import Fitting as PDFGuiFitting
from diffpy.pdfgui.control.parameter import Parameter
from diffpy.pdfgui.control.pdfguicontrol import PDFGuiControl


class FittingService:
    """Service for PDF fitting operations.

    This is a thin wrapper around the original pdfGUI fitting logic. All
    computational methods call the original implementations directly.
    """

    def __init__(self):
        """Initialize the fitting service."""
        self._control = PDFGuiControl()
        self._active_fittings: Dict[str, PDFGuiFitting] = {}
        self._lock = threading.RLock()

    def create_fitting(self, name: str) -> Dict[str, Any]:
        """Create a new fitting object.

        Wraps: PDFGuiControl.newFitting()
        """
        with self._lock:
            fitting = self._control.newFitting(name)
            fitting_id = str(id(fitting))
            self._active_fittings[fitting_id] = fitting
            return {"id": fitting_id, "name": name, "status": "PENDING"}

    def add_structure(self, fitting_id: str, structure_data: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Add a structure/phase to a fitting.

        Wraps: Fitting.newStructure()
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

            # Create structure using original pdfGUI logic
            structure = fitting.newStructure(name)

            # Load structure data
            if "lattice" in structure_data:
                lat = structure_data["lattice"]
                structure.lattice.setLatPar(
                    lat.get("a", 1.0),
                    lat.get("b", 1.0),
                    lat.get("c", 1.0),
                    lat.get("alpha", 90.0),
                    lat.get("beta", 90.0),
                    lat.get("gamma", 90.0),
                )

            # Add atoms
            if "atoms" in structure_data:
                for atom_data in structure_data["atoms"]:
                    structure.addNewAtom(
                        element=atom_data.get("element", "C"),
                        xyz=[atom_data.get("x", 0.0), atom_data.get("y", 0.0), atom_data.get("z", 0.0)],
                        occupancy=atom_data.get("occupancy", 1.0),
                    )

            return {"id": str(id(structure)), "name": name, "atom_count": len(structure)}

    def add_dataset(self, fitting_id: str, data: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Add experimental PDF data to a fitting.

        Wraps: Fitting.newDataSet()
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

            # Create dataset using original pdfGUI logic
            dataset = fitting.newDataSet(name)

            # Set observed data
            if "robs" in data and "Gobs" in data:
                dataset.robs = np.array(data["robs"])
                dataset.Gobs = np.array(data["Gobs"])
                if "dGobs" in data:
                    dataset.dGobs = np.array(data["dGobs"])

            # Set instrument parameters
            dataset.stype = data.get("stype", "N")
            dataset.qmax = data.get("qmax", 32.0)
            dataset.qdamp = data.get("qdamp", 0.01)
            dataset.qbroad = data.get("qbroad", 0.0)
            dataset.dscale = data.get("dscale", 1.0)

            # Set fit range
            dataset.fitrmin = data.get("fitrmin", 1.0)
            dataset.fitrmax = data.get("fitrmax", 30.0)
            dataset.fitrstep = data.get("fitrstep", 0.01)

            return {
                "id": str(id(dataset)),
                "name": name,
                "point_count": len(dataset.robs) if hasattr(dataset, "robs") else 0,
            }

    def set_constraint(
        self, fitting_id: str, target: str, formula: str, structure_index: int = 0
    ) -> Dict[str, Any]:
        """Set a parameter constraint.

        Wraps: FitStructure.constraints
        Uses original Constraint class for formula parsing.
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

            if structure_index >= len(fitting.strucs):
                raise ValueError(f"Structure index {structure_index} out of range")

            structure = fitting.strucs[structure_index]

            # Create constraint using original pdfGUI Constraint class
            constraint = Constraint(formula)
            structure.constraints[target] = constraint

            return {"target": target, "formula": formula, "parameters_used": constraint.parguess()}

    def run_refinement(self, fitting_id: str, callback: Optional[callable] = None) -> Dict[str, Any]:
        """Run PDF refinement.

        Wraps: Fitting.refine()

        This is the core computational method - uses original pdfGUI
        algorithms with NO modifications.
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

        # Run refinement (this calls the original pdffit2 engine)
        start_time = time.time()

        try:
            # The refine() method is the original pdfGUI implementation
            fitting.refine()

            elapsed = time.time() - start_time

            # Extract results
            results = {
                "status": "COMPLETED",
                "rw": fitting.rw if hasattr(fitting, "rw") else None,
                "chi_squared": fitting.chi2 if hasattr(fitting, "chi2") else None,
                "iterations": fitting.step if hasattr(fitting, "step") else 0,
                "elapsed_time": elapsed,
                "parameters": self._extract_refined_parameters(fitting),
                "residuals": self._extract_residuals(fitting),
            }

            return results

        except Exception as e:
            return {"status": "FAILED", "error": str(e), "elapsed_time": time.time() - start_time}

    def _extract_refined_parameters(self, fitting: PDFGuiFitting) -> List[Dict]:
        """Extract refined parameter values from fitting.

        Uses original pdfGUI parameter extraction.
        """
        parameters = []

        for idx, param in enumerate(fitting.parameters.values()):
            parameters.append(
                {
                    "index": idx,
                    "name": param.name if hasattr(param, "name") else f"@{idx}",
                    "initial_value": param.initialValue() if hasattr(param, "initialValue") else 0,
                    "refined_value": param.refined if hasattr(param, "refined") else param.initialValue(),
                    "uncertainty": param.uncertainty if hasattr(param, "uncertainty") else 0,
                }
            )

        return parameters

    def _extract_residuals(self, fitting: PDFGuiFitting) -> Dict[str, List]:
        """Extract residual data (observed, calculated, difference).

        Uses original pdfGUI data arrays.
        """
        residuals = {}

        for i, dataset in enumerate(fitting.datasets):
            key = f"dataset_{i}"
            residuals[key] = {
                "r": dataset.rcalc.tolist() if hasattr(dataset, "rcalc") else [],
                "Gobs": dataset.Gobs.tolist() if hasattr(dataset, "Gobs") else [],
                "Gcalc": dataset.Gcalc.tolist() if hasattr(dataset, "Gcalc") else [],
                "Gdiff": (
                    (dataset.Gobs - dataset.Gcalc).tolist()
                    if hasattr(dataset, "Gcalc") and hasattr(dataset, "Gobs")
                    else []
                ),
            }

        return residuals

    def calculate_pdf(self, fitting_id: str, structure_index: int = 0) -> Dict[str, Any]:
        """Calculate theoretical PDF.

        Wraps: Calculation.calculate()
        Uses original pdfGUI calculation logic.
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

            if not fitting.strucs:
                raise ValueError("No structures in fitting")

            # Get calculation parameters
            calc = fitting.calculations[0] if fitting.calculations else None
            if not calc:
                calc = fitting.newCalculation("calc")

            # Run calculation using original pdfGUI logic
            calc.calculate()

            return {
                "r": calc.rcalc.tolist() if hasattr(calc, "rcalc") else [],
                "G": calc.Gcalc.tolist() if hasattr(calc, "Gcalc") else [],
                "rmin": calc.rmin,
                "rmax": calc.rmax,
                "rstep": calc.rstep,
            }

    def find_parameters(self, fitting_id: str) -> List[Dict]:
        """Find all refinable parameters in fitting.

        Wraps: FitStructure.findParameters()
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

            parameters = []

            for structure in fitting.strucs:
                # Use original findParameters method
                params = structure.findParameters()
                for idx, value in params.items():
                    parameters.append({"index": idx, "initial_value": value, "is_fixed": False})

            return parameters

    def apply_parameters(self, fitting_id: str, parameter_values: Dict[int, float]) -> None:
        """Apply parameter values to structures.

        Wraps: FitStructure.applyParameters()
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

            for structure in fitting.strucs:
                # Use original applyParameters method
                structure.applyParameters(parameter_values)

    def get_pair_selection_flags(self, fitting_id: str, structure_index: int, selections: List[str]) -> List[int]:
        """Get pair selection flags for PDF calculation.

        Wraps: FitStructure.getPairSelectionFlags()
        """
        with self._lock:
            fitting = self._active_fittings.get(fitting_id)
            if not fitting:
                raise ValueError(f"Fitting {fitting_id} not found")

            if structure_index >= len(fitting.strucs):
                raise ValueError(f"Structure index {structure_index} out of range")

            structure = fitting.strucs[structure_index]

            # Use original getPairSelectionFlags method
            flags = structure.getPairSelectionFlags(selections)
            return flags

    def grid_interpolation(self, x0: List[float], y0: List[float], x1: List[float]) -> List[float]:
        """Perform sinc interpolation for PDF resampling.

        Wraps: FitDataSet.grid_interpolation()
        This is the numerical interpolation used for data resampling.
        """
        # Use original grid_interpolation function
        from diffpy.pdfgui.control.fitdataset import grid_interpolation

        result = grid_interpolation(np.array(x0), np.array(y0), np.array(x1))
        return result.tolist()

    def load_project(self, filepath: str) -> Dict[str, Any]:
        """Load a pdfGUI project file (.ddp).

        Wraps: PDFGuiControl.load()
        """
        with self._lock:
            # Use original load method
            self._control.load(filepath)

            # Extract project structure
            project_data = {"fits": [], "name": filepath}

            for fitting in self._control.fits:
                fit_data = {
                    "name": fitting.name,
                    "phases": [s.name for s in fitting.strucs],
                    "datasets": [d.name for d in fitting.datasets],
                }
                project_data["fits"].append(fit_data)

                # Register fitting
                fitting_id = str(id(fitting))
                self._active_fittings[fitting_id] = fitting

            return project_data

    def save_project(self, filepath: str) -> None:
        """Save project to .ddp file.

        Wraps: PDFGuiControl.save()
        """
        with self._lock:
            self._control.save(filepath)
