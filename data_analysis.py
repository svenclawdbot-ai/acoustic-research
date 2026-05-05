#!/usr/bin/env python3
"""
data_analysis.py - HDF5 data analysis tools for TurboQuant

Provides:
- Spectrogram and STFT analysis
- Statistical analysis
- Export to various formats
- Interactive plotting

Usage:
    from data_analysis import analyze_file, generate_spectrogram
    
    # Analyze file
    info = analyze_file('recording.h5')
    print(info)
    
    # Generate spectrogram
    generate_spectrogram('recording.h5', 'spectrogram.png', channel=0)
    
    # Interactive viewer
    python data_analysis.py --interactive recording.h5
"""

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass
from scipy import signal
from scipy.fft import fft, fftfreq
import json

# Optional dependencies
 try:
    from scipy.signal import stft, spectrogram
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False


@dataclass
class AnalysisConfig:
    """Analysis configuration"""
    sample_rate: float = 20_000_000
    nperseg: int = 1024
    noverlap: int = 512
    nfft: int = 2048
    window: str = 'hann'
    scaling: str = 'spectrum'


def load_hdf5(filepath: str) -> Dict:
    """Load data from HDF5 file"""
    if not HAS_H5PY:
        raise ImportError("h5py required. Install: pip install h5py")
    
    with h5py.File(filepath, 'r') as f:
        data = {
            'timestamps': f['timestamps'][:],
            'metadata': dict(f['metadata'].attrs)
        }
        
        # Load channels
        ch_idx = 0
        while f'channel_{ch_idx}' in f:
            data[f'channel_{ch_idx}'] = f[f'channel_{ch_idx}'][:]
            ch_idx += 1
        
        data['num_channels'] = ch_idx
    
    return data


def analyze_file(filepath: str) -> Dict:
    """Analyze HDF5 file and return statistics"""
    data = load_hdf5(filepath)
    
    # Extract metadata
    metadata = data.get('metadata', {})
    sample_rate = metadata.get('sample_rate', 20_000_000)
    
    results = {
        'file': filepath,
        'metadata': metadata,
        'num_channels': data['num_channels'],
        'total_samples': {},
        'duration_seconds': {},
        'statistics': {}
    }
    
    for ch in range(data['num_channels']):
        ch_key = f'channel_{ch}'
        if ch_key in data:
            ch_data = data[ch_key]
            
            results['total_samples'][ch_key] = len(ch_data)
            results['duration_seconds'][ch_key] = len(ch_data) / sample_rate
            
            # Convert to voltage
            voltage = (ch_data.astype(np.float32) / 4095.0) * 3300.0 - 1650.0
            
            results['statistics'][ch_key] = {
                'mean_mv': float(np.mean(voltage)),
                'std_mv': float(np.std(voltage)),
                'min_mv': float(np.min(voltage)),
                'max_mv': float(np.max(voltage)),
                'vpp_mv': float(np.max(voltage) - np.min(voltage)),
                'rms_mv': float(np.sqrt(np.mean(voltage**2)))
            }
    
    return results


def generate_spectrogram(filepath: str,
                        output: str,
                        channel: int = 0,
                        config: Optional[AnalysisConfig] = None) -> None:
    """
    Generate spectrogram from recorded data
    
    Args:
        filepath: Input HDF5 file
        output: Output image file
        channel: Channel to analyze
        config: Analysis configuration
    """
    if not HAS_SCIPY:
        raise ImportError("scipy required. Install: pip install scipy")
    
    if config is None:
        config = AnalysisConfig()
    
    # Load data
    data = load_hdf5(filepath)
    ch_key = f'channel_{channel}'
    
    if ch_key not in data:
        raise ValueError(f"Channel {channel} not found in file")
    
    sample_rate = data['metadata'].get('sample_rate', config.sample_rate)
    
    # Get channel data
    ch_data = data[ch_key].astype(np.float32)
    
    # Convert to voltage
    voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
    
    # Downsample if too large (for performance)
    max_samples = 10_000_000  # 10M samples max
    if len(voltage) > max_samples:
        decimation = len(voltage) // max_samples
        voltage = voltage[::decimation]
        sample_rate = sample_rate / decimation
    
    # Compute spectrogram
    print(f"Computing spectrogram for channel {channel}...")
    print(f"  Samples: {len(voltage)}")
    print(f"  Sample rate: {sample_rate/1e6:.2f} MHz")
    
    frequencies, times, Sxx = spectrogram(
        voltage,
        fs=sample_rate,
        window=config.window,
        nperseg=config.nperseg,
        noverlap=config.noverlap,
        nfft=config.nfft,
        scaling=config.scaling
    )
    
    # Convert to dB
    Sxx_db = 10 * np.log10(Sxx + 1e-10)
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                    gridspec_kw={'height_ratios': [1, 2]})
    
    # Time domain (top)
    time_axis = np.arange(len(voltage)) / sample_rate * 1000  # ms
    ax1.plot(time_axis[:10000], voltage[:10000], 'b-', linewidth=0.5)
    ax1.set_ylabel('Amplitude (mV)')
    ax1.set_title(f'Channel {channel} - Time Domain')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, time_axis[-1] if len(time_axis) < 10000 else time_axis[9999])
    
    # Spectrogram (bottom)
    im = ax2.pcolormesh(times * 1000, frequencies / 1e6, Sxx_db, 
                        shading='gouraud', cmap='viridis')
    ax2.set_ylabel('Frequency (MHz)')
    ax2.set_xlabel('Time (ms)')
    ax2.set_title('Spectrogram')
    ax2.set_ylim(0, sample_rate / 2 / 1e6)  # Nyquist
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax2)
    cbar.set_label('Power/Frequency (dB/Hz)')
    
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Saved to {output}")
    
    plt.close()


def generate_stft_plot(filepath: str,
                       output: str,
                       channel: int = 0,
                       config: Optional[AnalysisConfig] = None) -> None:
    """
    Generate STFT (Short-Time Fourier Transform) plot
    
    Similar to spectrogram but with more control over windowing
    """
    if not HAS_SCIPY:
        raise ImportError("scipy required")
    
    if config is None:
        config = AnalysisConfig()
    
    data = load_hdf5(filepath)
    ch_key = f'channel_{channel}'
    
    if ch_key not in data:
        raise ValueError(f"Channel {channel} not found")
    
    sample_rate = data['metadata'].get('sample_rate', config.sample_rate)
    ch_data = data[ch_key].astype(np.float32)
    voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
    
    # Downsample if needed
    max_samples = 5_000_000
    if len(voltage) > max_samples:
        decimation = len(voltage) // max_samples
        voltage = voltage[::decimation]
        sample_rate = sample_rate / decimation
    
    print(f"Computing STFT for channel {channel}...")
    
    # STFT
    f, t, Zxx = stft(
        voltage,
        fs=sample_rate,
        window=config.window,
        nperseg=config.nperseg,
        noverlap=config.noverlap,
        nfft=config.nfft
    )
    
    # Magnitude in dB
    magnitude = np.abs(Zxx)
    magnitude_db = 20 * np.log10(magnitude + 1e-10)
    
    # Plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Time domain
    ax1 = axes[0]
    time_ms = np.arange(len(voltage)) / sample_rate * 1000
    ax1.plot(time_ms, voltage, 'b-', linewidth=0.3)
    ax1.set_ylabel('Amplitude (mV)')
    ax1.set_title(f'Channel {channel} - Waveform')
    ax1.set_xlim(0, time_ms[-1])
    ax1.grid(True, alpha=0.3)
    
    # STFT magnitude
    ax2 = axes[1]
    im1 = ax2.pcolormesh(t * 1000, f / 1e6, magnitude_db, 
                         shading='gouraud', cmap='jet')
    ax2.set_ylabel('Frequency (MHz)')
    ax2.set_title('STFT Magnitude (dB)')
    ax2.set_ylim(0, sample_rate / 4 / 1e6)  # Show up to quarter sample rate
    plt.colorbar(im1, ax=ax2)
    
    # Phase
    ax3 = axes[2]
    phase = np.angle(Zxx)
    im2 = ax3.pcolormesh(t * 1000, f / 1e6, phase, 
                         shading='gouraud', cmap='hsv')
    ax3.set_ylabel('Frequency (MHz)')
    ax3.set_xlabel('Time (ms)')
    ax3.set_title('STFT Phase')
    ax3.set_ylim(0, sample_rate / 4 / 1e6)
    plt.colorbar(im2, ax=ax3)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Saved to {output}")
    
    plt.close()


def plot_time_domain(filepath: str,
                    output: str,
                    channels: Optional[List[int]] = None,
                    duration_ms: Optional[float] = None) -> None:
    """Plot time domain waveforms"""
    data = load_hdf5(filepath)
    sample_rate = data['metadata'].get('sample_rate', 20_000_000)
    
    if channels is None:
        channels = list(range(data['num_channels']))
    
    fig, axes = plt.subplots(len(channels), 1, 
                            figsize=(12, 2 * len(channels)),
                            sharex=True)
    
    if len(channels) == 1:
        axes = [axes]
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(channels)))
    
    for idx, ch in enumerate(channels):
        ch_key = f'channel_{ch}'
        if ch_key not in data:
            continue
        
        ch_data = data[ch_key].astype(np.float32)
        voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
        
        # Limit duration if specified
        if duration_ms:
            n_samples = int(duration_ms * sample_rate / 1000)
            voltage = voltage[:n_samples]
        
        time_ms = np.arange(len(voltage)) / sample_rate * 1000
        
        ax = axes[idx]
        ax.plot(time_ms, voltage, color=colors[idx], linewidth=0.5)
        ax.set_ylabel(f'Ch{ch} (mV)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-1000, 1000)
        
        # Add statistics
        stats_text = f"μ={np.mean(voltage):.1f} σ={np.std(voltage):.1f}"
        ax.text(0.02, 0.95, stats_text, transform=ax.transAxes,
               verticalalignment='top', fontsize=8,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    axes[-1].set_xlabel('Time (ms)')
    fig.suptitle(f'Time Domain Waveforms - {Path(filepath).name}')
    
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Saved to {output}")
    
    plt.close()


def plot_fft(filepath: str,
            output: str,
            channels: Optional[List[int]] = None) -> None:
    """Plot FFT spectrum for multiple channels"""
    data = load_hdf5(filepath)
    sample_rate = data['metadata'].get('sample_rate', 20_000_000)
    
    if channels is None:
        channels = list(range(data['num_channels']))
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Individual channel spectra
    ax1 = axes[0]
    colors = plt.cm.tab10(np.linspace(0, 1, len(channels)))
    
    for idx, ch in enumerate(channels):
        ch_key = f'channel_{ch}'
        if ch_key not in data:
            continue
        
        ch_data = data[ch_key].astype(np.float32)
        voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
        
        # FFT
        fft_vals = fft(voltage)
        freqs = fftfreq(len(voltage), 1/sample_rate)
        
        # Magnitude (one-sided)
        n = len(voltage) // 2
        magnitude = np.abs(fft_vals[:n])
        magnitude_db = 20 * np.log10(magnitude + 1e-10)
        
        ax1.plot(freqs[:n] / 1e6, magnitude_db, 
                color=colors[idx], label=f'Ch{ch}', linewidth=0.8)
    
    ax1.set_xlabel('Frequency (MHz)')
    ax1.set_ylabel('Magnitude (dB)')
    ax1.set_title('Individual Channel Spectra')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, sample_rate / 2 / 1e6)
    
    # Averaged spectrum
    ax2 = axes[1]
    
    all_spectra = []
    for ch in channels:
        ch_key = f'channel_{ch}'
        if ch_key not in data:
            continue
        
        ch_data = data[ch_key].astype(np.float32)
        voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
        
        fft_vals = fft(voltage)
        magnitude = np.abs(fft_vals[:len(fft_vals)//2])
        all_spectra.append(magnitude)
    
    if all_spectra:
        avg_spectrum = np.mean(all_spectra, axis=0)
        freqs = fftfreq(len(voltage), 1/sample_rate)[:len(voltage)//2]
        
        ax2.plot(freqs / 1e6, 20 * np.log10(avg_spectrum + 1e-10), 
                'b-', linewidth=1)
        ax2.fill_between(freqs / 1e6, 
                        20 * np.log10(avg_spectrum + 1e-10), -200,
                        alpha=0.3)
    
    ax2.set_xlabel('Frequency (MHz)')
    ax2.set_ylabel('Average Magnitude (dB)')
    ax2.set_title('Averaged Spectrum (All Channels)')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, sample_rate / 2 / 1e6)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Saved to {output}")
    
    plt.close()


def export_data(filepath: str, output: str, format: str) -> None:
    """Export data to various formats"""
    data = load_hdf5(filepath)
    
    if format == 'csv':
        import csv
        
        # Export first channel as CSV
        ch_data = data['channel_0'].astype(np.float32)
        voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
        
        with open(output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sample', 'voltage_mv'])
            for i, v in enumerate(voltage):
                writer.writerow([i, v])
        
        print(f"Exported to {output}")
    
    elif format == 'wav':
        from scipy.io import wavfile
        
        ch_data = data['channel_0'].astype(np.float32)
        voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
        
        # Normalize to 16-bit
        audio = ((voltage / np.max(np.abs(voltage))) * 32767).astype(np.int16)
        
        # Downsample to standard audio rate
        sample_rate = data['metadata'].get('sample_rate', 20_000_000)
        target_rate = 48000
        decimation = int(sample_rate / target_rate)
        audio = audio[::decimation]
        
        wavfile.write(output, target_rate, audio)
        print(f"Exported to {output}")
    
    elif format == 'npz':
        export_dict = {}
        for key, value in data.items():
            if key != 'metadata':
                export_dict[key] = value
        
        np.savez_compressed(output, **export_dict)
        print(f"Exported to {output}")
    
    else:
        raise ValueError(f"Unknown format: {format}")


def interactive_viewer(filepath: str):
    """Launch interactive matplotlib viewer"""
    try:
        from matplotlib.widgets import Slider, Button
    except ImportError:
        print("Interactive viewer requires matplotlib with widgets support")
        return
    
    data = load_hdf5(filepath)
    sample_rate = data['metadata'].get('sample_rate', 20_000_000)
    
    # Load first channel
    ch_data = data['channel_0'].astype(np.float32)
    voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(bottom=0.25)
    
    # Initial view (10 ms window)
    window_samples = int(10e-3 * sample_rate)
    time_ms = np.arange(window_samples) / sample_rate * 1000
    line, = ax.plot(time_ms, voltage[:window_samples], 'b-', linewidth=0.5)
    
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Voltage (mV)')
    ax.set_title(f'Interactive Viewer - {Path(filepath).name}')
    ax.grid(True, alpha=0.3)
    
    # Position slider
    ax_pos = plt.axes([0.2, 0.1, 0.5, 0.03])
    slider_pos = Slider(
        ax_pos, 'Position', 0, len(voltage) - window_samples,
        valinit=0, valstep=window_samples // 10
    )
    
    # Update function
    def update(val):
        pos = int(slider_pos.val)
        line.set_ydata(voltage[pos:pos + window_samples])
        fig.canvas.draw_idle()
    
    slider_pos.on_changed(update)
    
    # Reset button
    ax_reset = plt.axes([0.8, 0.1, 0.1, 0.04])
    button_reset = Button(ax_reset, 'Reset')
    
    def reset(event):
        slider_pos.reset()
    
    button_reset.on_clicked(reset)
    
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='TurboQuant Data Analysis')
    parser.add_argument('input', help='Input HDF5 file')
    parser.add_argument('--spectrogram', action='store_true', 
                       help='Generate spectrogram')
    parser.add_argument('--stft', action='store_true', 
                       help='Generate STFT plot')
    parser.add_argument('--time-domain', action='store_true', 
                       help='Plot time domain')
    parser.add_argument('--fft', action='store_true', 
                       help='Plot FFT')
    parser.add_argument('--interactive', action='store_true', 
                       help='Interactive viewer')
    parser.add_argument('--export', choices=['csv', 'wav', 'npz'], 
                       help='Export format')
    parser.add_argument('--channel', '-ch', type=int, default=0, 
                       help='Channel to analyze')
    parser.add_argument('--channels', '-chs', type=int, nargs='+', 
                       help='Channels for multi-channel plots')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--info', action='store_true', 
                       help='Show file information')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        return 1
    
    if args.info:
        info = analyze_file(args.input)
        print(json.dumps(info, indent=2))
        return 0
    
    if args.spectrogram:
        output = args.output or args.input.replace('.h5', '_spectrogram.png')
        generate_spectrogram(args.input, output, channel=args.channel)
        return 0
    
    if args.stft:
        output = args.output or args.input.replace('.h5', '_stft.png')
        generate_stft_plot(args.input, output, channel=args.channel)
        return 0
    
    if args.time_domain:
        output = args.output or args.input.replace('.h5', '_time.png')
        channels = args.channels if args.channels else None
        plot_time_domain(args.input, output, channels=channels)
        return 0
    
    if args.fft:
        output = args.output or args.input.replace('.h5', '_fft.png')
        channels = args.channels if args.channels else None
        plot_fft(args.input, output, channels=channels)
        return 0
    
    if args.interactive:
        interactive_viewer(args.input)
        return 0
    
    if args.export:
        ext = {'csv': '.csv', 'wav': '.wav', 'npz': '.npz'}[args.export]
        output = args.output or args.input.replace('.h5', ext)
        export_data(args.input, output, args.export)
        return 0
    
    # Default: show info
    info = analyze_file(args.input)
    print(json.dumps(info, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
