"""Structure service - wraps pdfGUI structure/phase logic.

Wraps: diffpy.pdfgui.control.fitstructure, diffpy.pdfgui.control.pdfstructure
"""
import numpy as np
from typing import Dict, List, Any, Optional
from diffpy.pdfgui.control.fitstructure import FitStructure
from diffpy.pdfgui.control.pdfstructure import PDFStructure
from diffpy.structure import Structure, Lattice, Atom


class StructureService:
    """Service for crystal structure operations."""

    def read_structure_file(self, filepath: str, format: str = "auto") -> Dict[str, Any]:
        """Read structure from file.

        Wraps: PDFStructure.read()
        Supports: stru, pdb, cif, xyz formats
        """
        structure = PDFStructure()
        structure.read(filepath, format=format if format != "auto" else None)

        return self._structure_to_dict(structure)

    def read_structure_string(self, content: str, format: str) -> Dict[str, Any]:
        """Read structure from string content.

        Wraps: PDFStructure.readStr()
        """
        structure = PDFStructure()
        structure.readStr(content, format=format)

        return self._structure_to_dict(structure)

    def _structure_to_dict(self, structure: PDFStructure) -> Dict[str, Any]:
        """Convert PDFStructure to dictionary representation."""
        lattice = structure.lattice

        atoms = []
        for i, atom in enumerate(structure):
            atom_dict = {
                "index": i + 1,
                "element": atom.element,
                "x": float(atom.xyz[0]),
                "y": float(atom.xyz[1]),
                "z": float(atom.xyz[2]),
                "occupancy": float(atom.occupancy),
                "uiso": float(atom.Uisoequiv) if hasattr(atom, 'Uisoequiv') else 0.0
            }

            # Add anisotropic parameters if available
            if hasattr(atom, 'U'):
                atom_dict["u11"] = float(atom.U[0, 0])
                atom_dict["u22"] = float(atom.U[1, 1])
                atom_dict["u33"] = float(atom.U[2, 2])
                atom_dict["u12"] = float(atom.U[0, 1])
                atom_dict["u13"] = float(atom.U[0, 2])
                atom_dict["u23"] = float(atom.U[1, 2])

            atoms.append(atom_dict)

        return {
            "lattice": {
                "a": float(lattice.a),
                "b": float(lattice.b),
                "c": float(lattice.c),
                "alpha": float(lattice.alpha),
                "beta": float(lattice.beta),
                "gamma": float(lattice.gamma)
            },
            "space_group": getattr(structure, 'pdffit', {}).get('spacegroup', ''),
            "atoms": atoms,
            "atom_count": len(structure)
        }

    def create_fit_structure(self, name: str) -> FitStructure:
        """Create a new FitStructure for refinement.

        Wraps: FitStructure.__init__()
        """
        return FitStructure(name)

    def set_lattice(
        self,
        structure: FitStructure,
        a: float, b: float, c: float,
        alpha: float, beta: float, gamma: float
    ) -> None:
        """Set lattice parameters.

        Wraps: FitStructure.lattice.setLatPar()
        """
        structure.lattice.setLatPar(a, b, c, alpha, beta, gamma)

    def add_atom(
        self,
        structure: FitStructure,
        element: str,
        x: float, y: float, z: float,
        occupancy: float = 1.0,
        uiso: float = 0.0
    ) -> int:
        """Add atom to structure.

        Wraps: FitStructure.addNewAtom()
        Returns atom index.
        """
        atom = structure.addNewAtom(element, [x, y, z], occupancy)
        if uiso > 0:
            atom.Uiso = uiso
        return len(structure) - 1

    def insert_atoms(
        self,
        structure: FitStructure,
        index: int,
        atoms: List[Dict]
    ) -> None:
        """Insert atoms at specified index.

        Wraps: FitStructure.insertAtoms()
        """
        atom_objects = []
        for atom_data in atoms:
            atom = Atom(
                atype=atom_data["element"],
                xyz=[atom_data["x"], atom_data["y"], atom_data["z"]],
                occupancy=atom_data.get("occupancy", 1.0)
            )
            atom_objects.append(atom)

        structure.insertAtoms(index, atom_objects)

    def delete_atoms(self, structure: FitStructure, indices: List[int]) -> None:
        """Delete atoms by indices.

        Wraps: FitStructure.deleteAtoms()
        """
        structure.deleteAtoms(indices)

    def find_parameters(self, structure: FitStructure) -> Dict[int, float]:
        """Find all refinable parameters.

        Wraps: FitStructure.findParameters()
        """
        return structure.findParameters()

    def apply_parameters(
        self,
        structure: FitStructure,
        parameters: Dict[int, float]
    ) -> None:
        """Apply parameter values.

        Wraps: FitStructure.applyParameters()
        """
        structure.applyParameters(parameters)

    def get_pair_selection_flags(
        self,
        structure: FitStructure,
        selections: List[str]
    ) -> List[int]:
        """Get pair selection flags.

        Wraps: FitStructure.getPairSelectionFlags()
        """
        return structure.getPairSelectionFlags(selections)

    def change_parameter_index(
        self,
        structure: FitStructure,
        old_index: int,
        new_index: int
    ) -> None:
        """Change parameter index in constraints.

        Wraps: FitStructure.changeParameterIndex()
        """
        structure.changeParameterIndex(old_index, new_index)

    def write_structure(
        self,
        structure: FitStructure,
        filepath: str,
        format: str = "pdffit"
    ) -> None:
        """Write structure to file.

        Wraps: FitStructure.write()
        """
        structure.write(filepath, format=format)

    def structure_to_string(
        self,
        structure: FitStructure,
        format: str = "pdffit"
    ) -> str:
        """Convert structure to string.

        Wraps: FitStructure.writeStr()
        """
        return structure.writeStr(format=format)
