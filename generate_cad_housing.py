"""
Flexural Beam Housing - CAD Generator
=====================================

Generates 3D printable housing for piezo-actuated flexural beam shear wave probe.

Using CadQuery (Python parametric CAD):
pip install cadquery

Output: STEP file for manufacturing, STL for 3D printing
"""

import cadquery as cq
from dataclasses import dataclass
from typing import Tuple


@dataclass
class HousingDimensions:
    """Configurable dimensions for the housing."""
    # Overall housing
    length: float = 80.0        # mm
    width: float = 35.0         # mm
    height: float = 50.0        # mm
    wall_thickness: float = 3.0 # mm
    
    # Beam cavity
    beam_length: float = 65.0   # mm
    beam_width: float = 20.0    # mm
    beam_height: float = 25.0   # mm
    
    # Piezo stack pocket
    piezo_width: float = 12.0   # mm
    piezo_depth: float = 12.0   # mm
    piezo_height: float = 25.0  # mm
    
    # Spring perch
    spring_diameter: float = 8.0  # mm
    spring_length: float = 15.0   # mm (compressed)
    
    # Mounting
    mount_hole_diameter: float = 4.2  # mm (M4 clearance)
    mount_hole_spacing: float = 60.0  # mm
    
    # Cable management
    cable_diameter: float = 6.0   # mm
    
    # Tolerances for 3D printing
    tolerance: float = 0.3  # mm


def create_beam_housing(dim: HousingDimensions = None) -> cq.Workplane:
    """Create the main housing body."""
    if dim is None:
        dim = HousingDimensions()
    
    # Start with base block
    housing = cq.Workplane("XY").box(
        dim.length, dim.width, dim.height,
        centered=True
    )
    
    # Create beam cavity (front section)
    beam_cavity = cq.Workplane("XY").box(
        dim.beam_length,
        dim.beam_width + dim.tolerance,
        dim.beam_height + dim.tolerance,
        centered=True
    ).translate((
        dim.length/2 - dim.beam_length/2 - dim.wall_thickness,
        0,
        -dim.height/2 + dim.beam_height/2 + dim.wall_thickness
    ))
    
    housing = housing.cut(beam_cavity)
    
    # Create piezo pocket (rear section)
    piezo_pocket = cq.Workplane("XY").box(
        dim.piezo_height,
        dim.piezo_width + dim.tolerance,
        dim.piezo_depth + dim.tolerance,
        centered=True
    ).translate((
        -dim.length/2 + dim.piezo_height/2 + dim.wall_thickness,
        0,
        -dim.height/2 + dim.piezo_depth/2 + dim.wall_thickness
    ))
    
    housing = housing.cut(piezo_pocket)
    
    # Spring perch (above piezo)
    spring_pocket = cq.Workplane("XY").box(
        dim.spring_length,
        dim.spring_diameter + dim.tolerance,
        dim.spring_diameter + dim.tolerance,
        centered=True
    ).translate((
        -dim.length/2 + dim.spring_length/2 + dim.wall_thickness,
        0,
        dim.height/2 - dim.spring_diameter/2 - dim.wall_thickness
    ))
    
    housing = housing.cut(spring_pocket)
    
    # Mounting holes (flanges)
    mount_hole = cq.Workplane("XY").circle(dim.mount_hole_diameter/2).extrude(dim.height)
    
    housing = housing.cut(
        mount_hole.translate((-dim.mount_hole_spacing/2, -dim.width/2 - 5, 0))
    )
    housing = housing.cut(
        mount_hole.translate((dim.mount_hole_spacing/2, -dim.width/2 - 5, 0))
    )
    housing = housing.cut(
        mount_hole.translate((-dim.mount_hole_spacing/2, dim.width/2 + 5, 0))
    )
    housing = housing.cut(
        mount_hole.translate((dim.mount_hole_spacing/2, dim.width/2 + 5, 0))
    )
    
    # Add mounting flanges
    flange = cq.Workplane("XY").box(
        dim.mount_hole_spacing + 15,
        10,
        dim.height,
        centered=True
    ).translate((0, -dim.width/2 - 5, 0))
    
    housing = housing.union(flange)
    
    flange2 = cq.Workplane("XY").box(
        dim.mount_hole_spacing + 15,
        10,
        dim.height,
        centered=True
    ).translate((0, dim.width/2 + 5, 0))
    
    housing = housing.union(flange2)
    
    # Cable exit hole
    cable_hole = cq.Workplane("YZ").circle(dim.cable_diameter/2).extrude(dim.length)
    housing = housing.cut(cable_hole.translate((-dim.length/2, 0, 0)))
    
    # Lightening holes (optional, save material)
    lightening = cq.Workplane("XY").circle(8).extrude(dim.wall_thickness + 1)
    housing = housing.cut(lightening.translate((0, 0, -dim.height/2)))
    
    return housing


def create_beam_clamp(dim: HousingDimensions = None) -> cq.Workplane:
    """Create clamping piece for the aluminum beam."""
    if dim is None:
        dim = HousingDimensions()
    
    # Clamp body
    clamp = cq.Workplane("XY").box(
        20,
        dim.beam_width + 4,
        dim.beam_height + 4,
        centered=True
    )
    
    # Beam clearance
    beam_cutout = cq.Workplane("XY").box(
        22,
        dim.beam_width + dim.tolerance,
        dim.beam_height + dim.tolerance,
        centered=True
    )
    
    clamp = clamp.cut(beam_cutout)
    
    # Mounting holes
    hole = cq.Workplane("XY").circle(1.6).extrude(20)  # M3 thread forming
    clamp = clamp.cut(hole.translate((0, -8, 0)))
    clamp = clamp.cut(hole.translate((0, 8, 0)))
    
    # Piezo contact pad
    pad = cq.Workplane("XY").box(
        5,
        dim.piezo_width - 2,
        3,
        centered=True
    ).translate((-8, 0, -dim.beam_height/2 - 2))
    
    clamp = clamp.union(pad)
    
    return clamp


def create_spring_cap(dim: HousingDimensions = None) -> cq.Workplane:
    """Create cap for spring preload."""
    if dim is None:
        dim = HousingDimensions()
    
    # Cap body
    cap = cq.Workplane("XY").box(
        dim.spring_length + 4,
        dim.spring_diameter + 4,
        8,
        centered=True
    )
    
    # Spring recess
    spring_seat = cq.Workplane("XY").circle(dim.spring_diameter/2 + 0.5).extrude(4)
    cap = cap.cut(spring_seat.translate((0, 0, 4)))
    
    # Adjustment screw hole
    screw_hole = cq.Workplane("XY").circle(1.5).extrude(10)  # M3
    cap = cap.cut(screw_hole.translate((0, 0, 4)))
    
    return cap


def create_tip_cover(dim: HousingDimensions = None) -> cq.Workplane:
    """Create silicone tip cover mold (for casting)."""
    if dim is None:
        dim = HousingDimensions()
    
    # Mold outer
    mold = cq.Workplane("XY").box(
        30,
        dim.beam_width + 4,
        15,
        centered=True
    )
    
    # Cavity for silicone
    cavity = cq.Workplane("XY").box(
        25,
        dim.beam_width - 2,
        12,
        centered=True
    )
    
    mold = mold.cut(cavity)
    
    # Parting line grooves
    groove = cq.Workplane("XY").box(32, 2, 1).translate((0, 0, 0))
    mold = mold.cut(groove)
    
    return mold


def export_models(output_dir: str = "."):
    """Generate and export all CAD files."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    dim = HousingDimensions()
    
    print("Generating CAD models...")
    
    # Main housing
    print("  1. Main housing...")
    housing = create_beam_housing(dim)
    housing.val().exportStep(f"{output_dir}/housing_main.step")
    housing.val().exportStl(f"{output_dir}/housing_main.stl", tolerance=0.1)
    
    # Beam clamp
    print("  2. Beam clamp...")
    clamp = create_beam_clamp(dim)
    clamp.val().exportStep(f"{output_dir}/beam_clamp.step")
    clamp.val().exportStl(f"{output_dir}/beam_clamp.stl", tolerance=0.1)
    
    # Spring cap
    print("  3. Spring cap...")
    cap = create_spring_cap(dim)
    cap.val().exportStep(f"{output_dir}/spring_cap.step")
    cap.val().exportStl(f"{output_dir}/spring_cap.stl", tolerance=0.1)
    
    # Tip cover mold
    print("  4. Silicone mold...")
    mold = create_tip_cover(dim)
    mold.val().exportStep(f"{output_dir}/silicone_mold.step")
    mold.val().exportStl(f"{output_dir}/silicone_mold.stl", tolerance=0.1)
    
    print(f"\nFiles exported to: {output_dir}/")
    print("  - housing_main.step / .stl")
    print("  - beam_clamp.step / .stl")
    print("  - spring_cap.step / .stl")
    print("  - silicone_mold.step / .stl")
    
    # Generate specs
    print("\n" + "=" * 60)
    print("DIMENSIONS SUMMARY")
    print("=" * 60)
    print(f"Housing: {dim.length} × {dim.width} × {dim.height} mm")
    print(f"Beam cavity: {dim.beam_length} × {dim.beam_width} × {dim.beam_height} mm")
    print(f"Piezo pocket: {dim.piezo_height} × {dim.piezo_width} × {dim.piezo_depth} mm")
    print(f"Print volume required: {dim.length + 20} × {dim.width + 30} × {dim.height + 10} mm")
    print(f"Estimated print time: ~4 hours (0.2mm layers, 20% infill)")
    print(f"Estimated filament: ~80g PLA/PETG")


if __name__ == "__main__":
    export_models("./cad_output")
