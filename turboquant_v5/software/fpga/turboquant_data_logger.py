#!/usr/bin/env python3
"""
TurboQuant Data Logger - HDF5 Persistence
=========================================

HDF5 data logging and management for TurboQuant shear wave acquisitions.
Provides structured storage, metadata tracking, and analysis tools.

Usage:
    from turboquant_data_logger import TurboQuantDataLogger, AcquisitionSession
    
    # Create logger
    logger = TurboQuantDataLogger('experiments.h5')
    
    # Start session
    with logger.new_session('phantom_test_001') as session:
        # Log acquisitions
        for i in range(10):
            data = acquire_frame()
            session.log_acquisition(data, frequency=100, metadata={'temp': 23.5})
    
    # Later analysis
    data = logger.load_session('phantom_test_001')
    logger.list_sessions()

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import h5py
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid


class MeasurementType(Enum):
    """Types of measurements."""
    SINGLE_FREQUENCY = "single_freq"
    SEQUENTIAL_SWEEP = "sequential"
    CONTINUOUS_MONITORING = "continuous"
    CALIBRATION = "calibration"


@dataclass
class SessionMetadata:
    """Metadata for an acquisition session."""
    session_id: str
    name: str
    description: str
    created_at: str
    operator: str
    sample_type: str  # e.g., 'gelatin_phantom', 'ex_vivo_tissue', 'in_vivo'
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    calibration_date: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SessionMetadata':
        return cls(**data)


@dataclass
class AcquisitionConfig:
    """Configuration for a single acquisition."""
    frequency_hz: int
    burst_cycles: int
    focus_depth_mm: float
    num_averages: int = 1
    gain_db: float = 40.0
    sound_speed_ms: float = 1540.0
    element_spacing_mm: float = 0.5


@dataclass
class ProcessedResult:
    """Processed shear wave results."""
    G_prime_pa: Optional[float] = None
    G_prime_err_pa: Optional[float] = None
    eta_pa_s: Optional[float] = None
    eta_err_pa_s: Optional[float] = None
    r_squared: Optional[float] = None
    dispersion_frequencies: Optional[np.ndarray] = None
    dispersion_velocities: Optional[np.ndarray] = None
    dispersion_uncertainties: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict:
        result = {
            'G_prime_pa': self.G_prime_pa,
            'G_prime_err_pa': self.G_prime_err_pa,
            'eta_pa_s': self.eta_pa_s,
            'eta_err_pa_s': self.eta_err_pa_s,
            'r_squared': self.r_squared
        }
        if self.dispersion_frequencies is not None:
            result['dispersion_frequencies'] = self.dispersion_frequencies.tolist()
        if self.dispersion_velocities is not None:
            result['dispersion_velocities'] = self.dispersion_velocities.tolist()
        if self.dispersion_uncertainties is not None:
            result['dispersion_uncertainties'] = self.dispersion_uncertainties.tolist()
        return result


class AcquisitionSession:
    """
    Context manager for a single acquisition session.
    Handles logging of multiple acquisitions with consistent metadata.
    """
    
    def __init__(self, logger: 'TurboQuantDataLogger', 
                 session_id: str, metadata: SessionMetadata):
        self.logger = logger
        self.session_id = session_id
        self.metadata = metadata
        self.acquisition_count = 0
        self.start_time = time.time()
        
    def __enter__(self):
        """Initialize session in HDF5."""
        with h5py.File(self.logger.filename, 'a') as f:
            if self.session_id in f:
                raise ValueError(f"Session {self.session_id} already exists")
            
            grp = f.create_group(self.session_id)
            grp.attrs['metadata'] = json.dumps(self.metadata.to_dict())
            grp.attrs['created_at'] = datetime.now().isoformat()
            grp.attrs['start_time'] = self.start_time
        
        print(f"Session started: {self.session_id}")
        print(f"  Description: {self.metadata.description}")
        print(f"  Sample: {self.metadata.sample_type}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finalize session."""
        elapsed = time.time() - self.start_time
        
        with h5py.File(self.logger.filename, 'a') as f:
            grp = f[self.session_id]
            grp.attrs['end_time'] = time.time()
            grp.attrs['duration_sec'] = elapsed
            grp.attrs['acquisition_count'] = self.acquisition_count
            grp.attrs['completed'] = exc_type is None
        
        print(f"Session complete: {self.session_id}")
        print(f"  Acquisitions: {self.acquisition_count}")
        print(f"  Duration: {elapsed:.1f}s")
        return exc_type is None
    
    def log_acquisition(self, 
                       raw_data: np.ndarray,
                       frequency_hz: int,
                       config: Optional[AcquisitionConfig] = None,
                       processed: Optional[ProcessedResult] = None,
                       metadata: Optional[Dict] = None):
        """
        Log a single acquisition.
        
        Parameters:
            raw_data: Raw ADC data (2 channels x samples)
            frequency_hz: Excitation frequency
            config: Acquisition configuration
            processed: Processed results (G', η, etc.)
            metadata: Additional metadata dict
        """
        timestamp = time.time()
        acq_id = f"acq_{self.acquisition_count:04d}"
        
        with h5py.File(self.logger.filename, 'a') as f:
            grp = f[self.session_id]
            acq_grp = grp.create_group(acq_id)
            
            # Store raw data
            acq_grp.create_dataset('raw_data', data=raw_data, 
                                 compression='gzip', compression_opts=4)
            
            # Store attributes
            acq_grp.attrs['timestamp'] = timestamp
            acq_grp.attrs['frequency_hz'] = frequency_hz
            acq_grp.attrs['acquisition_index'] = self.acquisition_count
            
            if config:
                acq_grp.attrs['config'] = json.dumps(config.__dict__)
            
            if processed:
                acq_grp.attrs['processed'] = json.dumps(processed.to_dict())
            
            if metadata:
                acq_grp.attrs['metadata'] = json.dumps(metadata)
        
        self.acquisition_count += 1
        
        # Print progress every 10 acquisitions
        if self.acquisition_count % 10 == 0:
            print(f"  Logged {self.acquisition_count} acquisitions...")
    
    def log_dispersion_curve(self,
                            frequencies: np.ndarray,
                            velocities: np.ndarray,
                            uncertainties: np.ndarray,
                            fitted_G_prime: float,
                            fitted_eta: float,
                            r_squared: float):
        """Log a complete dispersion curve fit."""
        with h5py.File(self.logger.filename, 'a') as f:
            grp = f[self.session_id]
            
            # Create or update dispersion dataset
            if 'dispersion' in grp:
                del grp['dispersion']
            
            disp_grp = grp.create_group('dispersion')
            disp_grp.create_dataset('frequencies', data=frequencies)
            disp_grp.create_dataset('velocities', data=velocities)
            disp_grp.create_dataset('uncertainties', data=uncertainties)
            
            disp_grp.attrs['G_prime_pa'] = fitted_G_prime
            disp_grp.attrs['eta_pa_s'] = fitted_eta
            disp_grp.attrs['r_squared'] = r_squared
            disp_grp.attrs['timestamp'] = time.time()


class TurboQuantDataLogger:
    """
    Main interface for HDF5 data logging.
    
    Manages multiple sessions with full metadata and analysis results.
    """
    
    def __init__(self, filename: str = 'turboquant_data.h5'):
        """
        Initialize logger.
        
        Parameters:
            filename: HDF5 file path
        """
        self.filename = filename
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create HDF5 file if it doesn't exist."""
        if not os.path.exists(self.filename):
            with h5py.File(self.filename, 'w') as f:
                f.attrs['created'] = datetime.now().isoformat()
                f.attrs['version'] = '1.0'
                f.attrs['description'] = 'TurboQuant Shear Wave Data'
    
    def new_session(self, 
                   name: Optional[str] = None,
                   description: str = "",
                   operator: str = "",
                   sample_type: str = "unknown",
                   **kwargs) -> AcquisitionSession:
        """
        Create a new acquisition session.
        
        Parameters:
            name: Session name (auto-generated if None)
            description: Session description
            operator: Operator name
            sample_type: Type of sample (phantom, tissue, etc.)
            **kwargs: Additional metadata fields
            
        Returns:
            AcquisitionSession context manager
        """
        session_id = name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_id = session_id.replace(' ', '_').replace('-', '_')
        
        metadata = SessionMetadata(
            session_id=session_id,
            name=name or session_id,
            description=description,
            created_at=datetime.now().isoformat(),
            operator=operator,
            sample_type=sample_type,
            **kwargs
        )
        
        return AcquisitionSession(self, session_id, metadata)
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions in the HDF5 file."""
        sessions = []
        
        with h5py.File(self.filename, 'r') as f:
            for session_id in f.keys():
                grp = f[session_id]
                try:
                    metadata = json.loads(grp.attrs.get('metadata', '{}'))
                    sessions.append({
                        'session_id': session_id,
                        'name': metadata.get('name', session_id),
                        'description': metadata.get('description', ''),
                        'created_at': grp.attrs.get('created_at', ''),
                        'operator': metadata.get('operator', ''),
                        'sample_type': metadata.get('sample_type', ''),
                        'acquisition_count': grp.attrs.get('acquisition_count', 0),
                        'completed': grp.attrs.get('completed', False)
                    })
                except Exception as e:
                    sessions.append({
                        'session_id': session_id,
                        'error': str(e)
                    })
        
        return sessions
    
    def load_session(self, session_id: str) -> Dict:
        """
        Load all data from a session.
        
        Returns:
            Dictionary with metadata and all acquisitions
        """
        with h5py.File(self.filename, 'r') as f:
            if session_id not in f:
                raise ValueError(f"Session {session_id} not found")
            
            grp = f[session_id]
            
            # Load metadata
            metadata = json.loads(grp.attrs.get('metadata', '{}'))
            
            # Load all acquisitions
            acquisitions = []
            for acq_id in grp.keys():
                if acq_id == 'dispersion':
                    continue
                    
                acq_grp = grp[acq_id]
                acq_data = {
                    'id': acq_id,
                    'timestamp': acq_grp.attrs.get('timestamp'),
                    'frequency_hz': acq_grp.attrs.get('frequency_hz'),
                    'index': acq_grp.attrs.get('acquisition_index')
                }
                
                # Load config if present
                if 'config' in acq_grp.attrs:
                    acq_data['config'] = json.loads(acq_grp.attrs['config'])
                
                # Load processed results if present
                if 'processed' in acq_grp.attrs:
                    acq_data['processed'] = json.loads(acq_grp.attrs['processed'])
                
                # Optionally load raw data (can be large)
                if 'raw_data' in acq_grp:
                    acq_data['raw_data'] = acq_grp['raw_data'][()]
                
                acquisitions.append(acq_data)
            
            # Load dispersion if present
            dispersion = None
            if 'dispersion' in grp:
                disp_grp = grp['dispersion']
                dispersion = {
                    'frequencies': disp_grp['frequencies'][()],
                    'velocities': disp_grp['velocities'][()],
                    'uncertainties': disp_grp['uncertainties'][()],
                    'G_prime_pa': disp_grp.attrs.get('G_prime_pa'),
                    'eta_pa_s': disp_grp.attrs.get('eta_pa_s'),
                    'r_squared': disp_grp.attrs.get('r_squared')
                }
            
            return {
                'metadata': metadata,
                'acquisitions': acquisitions,
                'dispersion': dispersion
            }
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get quick summary of a session."""
        with h5py.File(self.filename, 'r') as f:
            if session_id not in f:
                raise ValueError(f"Session {session_id} not found")
            
            grp = f[session_id]
            metadata = json.loads(grp.attrs.get('metadata', '{}'))
            
            return {
                'session_id': session_id,
                'name': metadata.get('name'),
                'sample_type': metadata.get('sample_type'),
                'acquisition_count': grp.attrs.get('acquisition_count', 0),
                'duration_sec': grp.attrs.get('duration_sec', 0),
                'completed': grp.attrs.get('completed', False),
                'has_dispersion': 'dispersion' in grp
            }
    
    def export_to_matlab(self, session_id: str, output_file: Optional[str] = None):
        """Export session to MATLAB .mat format."""
        try:
            from scipy.io import savemat
        except ImportError:
            raise ImportError("scipy required. Install: pip install scipy")
        
        data = self.load_session(session_id)
        
        if output_file is None:
            output_file = f"{session_id}.mat"
        
        # Prepare MATLAB-compatible structure
        mat_data = {
            'metadata': data['metadata'],
            'acquisitions': data['acquisitions'],
        }
        
        if data['dispersion']:
            mat_data['dispersion'] = data['dispersion']
        
        savemat(output_file, mat_data)
        print(f"Exported to {output_file}")
    
    def export_to_csv(self, session_id: str, output_file: Optional[str] = None):
        """Export dispersion curve to CSV."""
        import csv
        
        data = self.load_session(session_id)
        
        if data['dispersion'] is None:
            raise ValueError(f"Session {session_id} has no dispersion data")
        
        if output_file is None:
            output_file = f"{session_id}_dispersion.csv"
        
        disp = data['dispersion']
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Frequency_Hz', 'Velocity_m_s', 'Uncertainty_m_s'])
            for freq, vel, unc in zip(disp['frequencies'], 
                                      disp['velocities'], 
                                      disp['uncertainties']):
                writer.writerow([freq, vel, unc])
        
        print(f"Exported dispersion to {output_file}")
    
    def delete_session(self, session_id: str):
        """Delete a session from the HDF5 file."""
        with h5py.File(self.filename, 'a') as f:
            if session_id in f:
                del f[session_id]
                print(f"Deleted session: {session_id}")
            else:
                print(f"Session not found: {session_id}")


#============================================================================
# Integration with TurboQuant Control
#============================================================================

class TurboQuantLogger(TurboQuantDataLogger):
    """
    Extended logger with direct TurboQuantFPGA integration.
    """
    
    def __init__(self, filename: str = 'turboquant_data.h5'):
        super().__init__(filename)
        self.current_session = None
    
    def start_acquisition_session(self, 
                                  tq_fpga,
                                  name: str,
                                  description: str = "",
                                  **metadata) -> AcquisitionSession:
        """
        Start a new session with automatic FPGA integration.
        
        Example:
            with logger.start_acquisition_session(tq, 'phantom_test') as session:
                for i in range(10):
                    data = tq.acquire_single()
                    session.log_acquisition(data, frequency=100)
        """
        self.current_session = self.new_session(
            name=name,
            description=description,
            **metadata
        )
        return self.current_session


#============================================================================
# Demo
#============================================================================

def demo_data_logging():
    """Demo: Data logging workflow."""
    print("="*70)
    print("TurboQuant Data Logger Demo")
    print("="*70)
    
    # Create logger
    logger = TurboQuantDataLogger('demo_data.h5')
    
    # Create new session
    with logger.new_session(
        name='gelatin_phantom_calibration',
        description='Gelatin phantom with known stiffness 2000 Pa',
        operator='Researcher',
        sample_type='gelatin_phantom',
        temperature_c=23.5,
        notes='10% gelatin, 24h set time'
    ) as session:
        
        # Simulate acquisitions
        print("\nLogging acquisitions...")
        for freq in [60, 80, 100, 120, 140]:
            # Simulate data
            data = np.random.randn(2, 8192).astype(np.float32)
            
            config = AcquisitionConfig(
                frequency_hz=freq,
                burst_cycles=5,
                focus_depth_mm=30.0
            )
            
            # Log with processed results
            processed = ProcessedResult(
                G_prime_pa=2000 + np.random.randn() * 100,
                eta_pa_s=0.5 + np.random.randn() * 0.1,
                r_squared=0.95
            )
            
            session.log_acquisition(
                raw_data=data,
                frequency_hz=freq,
                config=config,
                processed=processed,
                metadata={'frame': freq // 20}
            )
        
        # Log dispersion curve
        freqs = np.array([60, 80, 100, 120, 140])
        vels = np.array([1.2, 1.35, 1.5, 1.65, 1.8])
        uncs = np.array([0.05, 0.04, 0.03, 0.04, 0.05])
        
        session.log_dispersion_curve(
            frequencies=freqs,
            velocities=vels,
            uncertainties=uncs,
            fitted_G_prime=2050.0,
            fitted_eta=0.52,
            r_squared=0.98
        )
    
    # List all sessions
    print("\nSessions in file:")
    for s in logger.list_sessions():
        print(f"  {s['session_id']}: {s['name']} ({s['acquisition_count']} acq)")
    
    # Load and inspect
    print("\nLoading session data:")
    data = logger.load_session('gelatin_phantom_calibration')
    print(f"  Metadata: {data['metadata']['description']}")
    print(f"  Acquisitions: {len(data['acquisitions'])}")
    print(f"  Dispersion fitted: G' = {data['dispersion']['G_prime_pa']:.0f} Pa")
    
    # Export
    print("\nExporting...")
    logger.export_to_csv('gelatin_phantom_calibration')
    
    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='TurboQuant Data Logger')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--list', type=str, help='List sessions in HDF5 file')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_data_logging()
    elif args.list:
        logger = TurboQuantDataLogger(args.list)
        sessions = logger.list_sessions()
        print(f"\nSessions in {args.list}:")
        for s in sessions:
            print(f"  {s['session_id']}: {s.get('name', 'N/A')}")
            print(f"    Sample: {s.get('sample_type', 'N/A')}")
            print(f"    Acquisitions: {s.get('acquisition_count', 0)}")
            print()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
