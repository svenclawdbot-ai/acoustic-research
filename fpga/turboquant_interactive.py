#!/usr/bin/env python3
"""
TurboQuant Interactive Control
==============================

Interactive control interfaces for TurboQuant shear wave system:
- Jupyter notebook widgets
- Command-line REPL
- Real-time matplotlib display
- Web dashboard (optional)

Usage:
    # Jupyter notebook
    from turboquant_interactive import TurboQuantInteractive
    tqi = TurboQuantInteractive()
    tqi.show_control_panel()
    
    # Command line
    python3 turboquant_interactive.py --repl
    
    # Real-time display
    python3 turboquant_interactive.py --display

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import threading
import queue
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from pathlib import Path
import json
import cmd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from turboquant_control import TurboQuantFPGA, TurboQuantPipeline
from turboquant_data_logger import TurboQuantDataLogger, AcquisitionConfig

# Optional imports for advanced features
try:
    from IPython.display import display, clear_output
    from ipywidgets import interact, interactive, fixed, interact_manual
    import ipywidgets as widgets
    HAS_IPYWIDGETS = True
except ImportError:
    HAS_IPYWIDGETS = False

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False


@dataclass
class InteractiveState:
    """Current state of the interactive session."""
    connected: bool = False
    acquiring: bool = False
    frequency_hz: int = 100
    burst_cycles: int = 5
    num_frequencies: int = 5
    focus_depth_mm: float = 30.0
    last_G_prime: Optional[float] = None
    last_eta: Optional[float] = None
    acquisition_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'connected': self.connected,
            'acquiring': self.acquiring,
            'frequency_hz': self.frequency_hz,
            'burst_cycles': self.burst_cycles,
            'num_frequencies': self.num_frequencies,
            'focus_depth_mm': self.focus_depth_mm,
            'last_G_prime': self.last_G_prime,
            'last_eta': self.last_eta,
            'acquisition_count': self.acquisition_count
        }


class TurboQuantInteractive:
    """
    Interactive control interface for TurboQuant.
    
    Supports multiple modes:
    - Jupyter notebook widgets
    - Command-line REPL
    - Real-time matplotlib display
    """
    
    def __init__(self, fpga: Optional[TurboQuantFPGA] = None,
                 logger: Optional[TurboQuantDataLogger] = None):
        """
        Initialize interactive controller.
        
        Parameters:
            fpga: Existing TurboQuantFPGA instance or None to create
            logger: Existing TurboQuantDataLogger or None
        """
        self.state = InteractiveState()
        self.fpga = fpga
        self.logger = logger or TurboQuantDataLogger()
        self.pipeline = TurboQuantPipeline(fpga) if fpga else None
        
        # Data buffers for real-time display
        self.data_buffer = queue.Queue(maxsize=100)
        self.dispersion_history = []
        self.G_history = []
        
        # Plotting
        self.fig = None
        self.axes = None
        self.animation = None
        
    def connect(self, local_mmap: bool = True, ip_address: Optional[str] = None) -> bool:
        """Connect to FPGA."""
        try:
            self.fpga = TurboQuantFPGA(local_mmap=local_mmap, ip_address=ip_address)
            self.pipeline = TurboQuantPipeline(self.fpga)
            self.state.connected = True
            print("✓ Connected to TurboQuant FPGA")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            self.state.connected = False
            return False
    
    #====================================================================
    # Jupyter Notebook Interface
    #====================================================================
    
    def show_control_panel(self):
        """
        Display interactive control panel in Jupyter notebook.
        Requires ipywidgets.
        """
        if not HAS_IPYWIDGETS:
            print("ipywidgets not installed. Install with: pip install ipywidgets")
            return
        
        # Connection status
        status_label = widgets.Label(value="Status: Disconnected")
        
        # Frequency slider
        freq_slider = widgets.IntSlider(
            value=100, min=60, max=140, step=10,
            description='Frequency (Hz):',
            style={'description_width': 'initial'}
        )
        
        # Burst cycles
        burst_slider = widgets.IntSlider(
            value=5, min=1, max=15, step=1,
            description='Burst Cycles:',
            style={'description_width': 'initial'}
        )
        
        # Focus depth
        focus_slider = widgets.FloatSlider(
            value=30.0, min=10.0, max=100.0, step=1.0,
            description='Focus Depth (mm):',
            style={'description_width': 'initial'}
        )
        
        # Buttons
        connect_btn = widgets.Button(description="Connect", button_style='primary')
        acquire_btn = widgets.Button(description="Acquire Single", button_style='success')
        sweep_btn = widgets.Button(description="Sequential Sweep", button_style='warning')
        continuous_btn = widgets.Button(description="Start Continuous", button_style='danger')
        
        # Output area
        output = widgets.Output()
        
        # Results display
        results_html = widgets.HTML(value="<b>Results:</b><br>Waiting for acquisition...")
        
        # Event handlers
        def on_connect(b):
            with output:
                clear_output()
                if self.connect():
                    status_label.value = "Status: Connected ✓"
                    connect_btn.description = "Connected"
                    connect_btn.disabled = True
        
        def on_acquire(b):
            with output:
                clear_output()
                if not self.state.connected:
                    print("Not connected! Click Connect first.")
                    return
                
                print(f"Acquiring at {freq_slider.value} Hz...")
                self.state.frequency_hz = freq_slider.value
                self.state.burst_cycles = burst_slider.value
                
                # Configure and acquire
                self.fpga.configure(
                    frequency=freq_slider.value,
                    burst_cycles=burst_slider.value,
                    focus_depth=focus_slider.value
                )
                
                result = self.fpga.acquire_single()
                
                # Process
                processed = self.pipeline.process_frame(result.raw_data, 
                                                        frequency=freq_slider.value)
                
                # Update state
                self.state.last_G_prime = processed.get('G_prime')
                self.state.last_eta = processed.get('eta')
                self.state.acquisition_count += 1
                
                # Update display
                g_val = self.state.last_G_prime or 0
                eta_val = self.state.last_eta or 0
                results_html.value = f"""
                <b>Results:</b><br>
                <span style='color: green;'>✓ Acquisition Complete</span><br>
                Frequency: {freq_slider.value} Hz<br>
                Samples: {len(result.raw_data)}<br>
                <b>G' = {g_val:.0f} Pa</b><br>
                <b>η = {eta_val:.3f} Pa·s</b>
                """
                
                print(f"Complete: G' = {g_val:.0f} Pa, η = {eta_val:.3f} Pa·s")
        
        def on_sweep(b):
            with output:
                clear_output()
                if not self.state.connected:
                    print("Not connected!")
                    return
                
                print("Starting sequential sweep...")
                self.fpga.set_num_frequencies(5)
                
                results = self.fpga.acquire_sequential()
                
                print(f"Sweep complete: {len(results)} frequencies acquired")
                for r in results:
                    print(f"  {r.frequency_hz} Hz: {len(r.raw_data)} samples")
        
        def on_continuous(b):
            with output:
                clear_output()
                if not self.state.connected:
                    print("Not connected!")
                    return
                
                if continuous_btn.description == "Start Continuous":
                    continuous_btn.description = "Stop Continuous"
                    print("Continuous acquisition started...")
                    print("(In real implementation, this would start a background thread)")
                else:
                    continuous_btn.description = "Start Continuous"
                    print("Continuous acquisition stopped.")
        
        # Bind handlers
        connect_btn.on_click(on_connect)
        acquire_btn.on_click(on_acquire)
        sweep_btn.on_click(on_sweep)
        continuous_btn.on_click(on_continuous)
        
        # Layout
        controls = widgets.VBox([
            widgets.HBox([connect_btn, status_label]),
            widgets.HTML("<hr>"),
            freq_slider,
            burst_slider,
            focus_slider,
            widgets.HTML("<hr>"),
            widgets.HBox([acquire_btn, sweep_btn, continuous_btn]),
            widgets.HTML("<hr>"),
            results_html,
            widgets.HTML("<hr>"),
            widgets.Label(value="Console Output:"),
            output
        ])
        
        display(controls)
    
    def show_realtime_plot(self, interval_ms: int = 500):
        """
        Display real-time updating plot in Jupyter.
        Shows G' and η history, last waveform, and dispersion curve.
        """
        if not HAS_IPYWIDGETS:
            print("ipywidgets required")
            return
        
        import matplotlib
        matplotlib.use('module://ipympl.backend_nbagg')  # Interactive backend
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Initialize empty plots
        line_g, = axes[0, 0].plot([], [], 'b-', linewidth=2)
        axes[0, 0].set_xlabel('Acquisition #')
        axes[0, 0].set_ylabel("G' (Pa)")
        axes[0, 0].set_title('G\' History')
        axes[0, 0].grid(True)
        
        line_wave, = axes[0, 1].plot([], [], 'g-', linewidth=0.5)
        axes[0, 1].set_xlabel('Sample')
        axes[0, 1].set_ylabel('Amplitude')
        axes[0, 1].set_title('Last Waveform')
        axes[0, 1].grid(True)
        
        line_disp, = axes[1, 0].plot([], [], 'ro-', markersize=8)
        axes[1, 0].set_xlabel('Frequency (Hz)')
        axes[1, 0].set_ylabel('Velocity (m/s)')
        axes[1, 0].set_title('Dispersion Curve')
        axes[1, 0].grid(True)
        
        text_status = axes[1, 1].text(0.1, 0.5, 'Status: Idle', fontsize=12)
        axes[1, 1].axis('off')
        axes[1, 1].set_title('System Status')
        
        def update(frame):
            # Update G' history
            if len(self.G_history) > 0:
                line_g.set_data(range(len(self.G_history)), self.G_history)
                axes[0, 0].set_xlim(0, max(len(self.G_history), 10))
                axes[0, 0].set_ylim(min(self.G_history)*0.8, max(self.G_history)*1.2)
            
            # Update status text
            status = f"""
            Status: {'Acquiring' if self.state.acquiring else 'Idle'}
            Acquisitions: {self.state.acquisition_count}
            Last G': {self.state.last_G_prime or 'N/A'} Pa
            Last η: {self.state.last_eta or 'N/A'} Pa·s
            """
            text_status.set_text(status)
            
            return line_g, line_wave, line_disp, text_status
        
        ani = FuncAnimation(fig, update, interval=interval_ms, blit=False)
        plt.tight_layout()
        plt.show()
        
        return ani
    
    #====================================================================
    # Command-Line REPL Interface
    #====================================================================
    
    def start_repl(self):
        """Start interactive command-line REPL."""
        repl = TurboQuantREPL(self)
        repl.cmdloop()
    
    #====================================================================
    # Real-time Matplotlib Display
    #====================================================================
    
    def start_realtime_display(self, interval_ms: int = 500):
        """
        Start standalone real-time display window.
        Runs in main thread, acquires in background thread.
        """
        print("Starting real-time display...")
        print("Close window to stop")
        
        # Setup figure
        self.fig, self.axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Waveform plot
        self.axes[0, 0].set_title('Real-time Waveform')
        self.axes[0, 0].set_xlabel('Time (samples)')
        self.axes[0, 0].set_ylabel('Amplitude')
        self.wave_line, = self.axes[0, 0].plot([], [], 'b-', linewidth=0.5)
        self.axes[0, 0].grid(True)
        
        # G' history
        self.axes[0, 1].set_title("G' History")
        self.axes[0, 1].set_xlabel('Frame #')
        self.axes[0, 1].set_ylabel("G' (Pa)")
        self.g_line, = self.axes[0, 1].plot([], [], 'g-o', markersize=4)
        self.axes[0, 1].grid(True)
        
        # Dispersion curve
        self.axes[1, 0].set_title('Dispersion Curve')
        self.axes[1, 0].set_xlabel('Frequency (Hz)')
        self.axes[1, 0].set_ylabel('Velocity (m/s)')
        self.disp_line, = self.axes[1, 0].plot([], [], 'ro-', markersize=8)
        self.axes[1, 0].grid(True)
        
        # Status
        self.axes[1, 1].axis('off')
        self.status_text = self.axes[1, 1].text(0.1, 0.5, '', fontsize=10,
                                                family='monospace',
                                                verticalalignment='center')
        
        plt.tight_layout()
        
        # Start acquisition thread if connected
        if self.state.connected and not self.state.acquiring:
            self._start_acquisition_thread(interval_ms)
        
        # Animation
        self.animation = FuncAnimation(
            self.fig, self._update_display,
            interval=interval_ms,
            blit=False,
            cache_frame_data=False
        )
        
        plt.show()
        
        # Stop on close
        self.stop_acquisition()
    
    def _start_acquisition_thread(self, interval_ms: int):
        """Start background acquisition thread."""
        self.state.acquiring = True
        self.acq_thread = threading.Thread(target=self._acquisition_loop, 
                                           args=(interval_ms,))
        self.acq_thread.daemon = True
        self.acq_thread.start()
    
    def _acquisition_loop(self, interval_ms: int):
        """Background acquisition loop."""
        while self.state.acquiring:
            try:
                if self.fpga and self.pipeline:
                    result = self.pipeline.acquire_and_process(
                        frequency=self.state.frequency_hz
                    )
                    
                    # Update state
                    self.state.last_G_prime = result.get('G_prime')
                    self.state.last_eta = result.get('eta')
                    self.state.acquisition_count += 1
                    
                    # Add to history
                    if self.state.last_G_prime:
                        self.G_history.append(self.state.last_G_prime)
                        if len(self.G_history) > 100:
                            self.G_history.pop(0)
                    
                    # Put in queue for display
                    self.data_buffer.put(result, block=False)
                    
            except Exception as e:
                print(f"Acquisition error: {e}")
            
            time.sleep(interval_ms / 1000)
    
    def _update_display(self, frame):
        """Update display callback."""
        # Get latest data if available
        try:
            while not self.data_buffer.empty():
                data = self.data_buffer.get_nowait()
                
                # Update waveform
                if 'raw_data' in data and len(data['raw_data']) > 0:
                    y = data['raw_data'][0]
                    x = range(len(y))
                    self.wave_line.set_data(x, y)
                    self.axes[0, 0].set_xlim(0, len(y))
                    if len(y) > 0:
                        self.axes[0, 0].set_ylim(np.min(y)*1.1, np.max(y)*1.1)
                
                # Update dispersion
                if 'dispersion' in data and data['dispersion']:
                    disp = data['dispersion']
                    if len(disp.get('frequencies', [])) > 0:
                        self.disp_line.set_data(
                            disp['frequencies'],
                            disp['velocities']
                        )
                        self.axes[1, 0].set_xlim(50, 150)
                        self.axes[1, 0].set_ylim(0, 5)
        except queue.Empty:
            pass
        
        # Update G' history
        if len(self.G_history) > 0:
            self.g_line.set_data(range(len(self.G_history)), self.G_history)
            self.axes[0, 1].set_xlim(0, max(len(self.G_history), 10))
            if len(self.G_history) > 1:
                self.axes[0, 1].set_ylim(
                    min(self.G_history)*0.8,
                    max(self.G_history)*1.2
                )
        
        # Update status text
        status = f"""Status: {'ACQUIRING' if self.state.acquiring else 'IDLE'}
Frequency: {self.state.frequency_hz} Hz
Acquisitions: {self.state.acquisition_count}
Last G': {self.state.last_G_prime or 'N/A':.0f} Pa
Last η: {self.state.last_eta or 'N/A':.3f} Pa·s"""
        self.status_text.set_text(status)
        
        return self.wave_line, self.g_line, self.disp_line, self.status_text
    
    def stop_acquisition(self):
        """Stop background acquisition."""
        self.state.acquiring = False
        if hasattr(self, 'acq_thread'):
            self.acq_thread.join(timeout=1.0)


class TurboQuantREPL(cmd.Cmd):
    """Command-line REPL for TurboQuant."""
    
    intro = """
    ╔══════════════════════════════════════════════════════════╗
    ║     TurboQuant Interactive Control Shell                 ║
    ║     Type 'help' for commands or 'quit' to exit           ║
    ╚══════════════════════════════════════════════════════════╝
    """
    prompt = 'TurboQuant> '
    
    def __init__(self, interactive: TurboQuantInteractive):
        super().__init__()
        self.tqi = interactive
    
    def do_connect(self, arg):
        """Connect to FPGA: connect [local|remote IP]"""
        if arg == 'local' or arg == '':
            self.tqi.connect(local_mmap=True)
        else:
            self.tqi.connect(ip_address=arg)
    
    def do_freq(self, arg):
        """Set frequency: freq 100"""
        try:
            freq = int(arg)
            self.tqi.state.frequency_hz = freq
            if self.tqi.fpga:
                self.tqi.fpga.set_frequency(freq)
            print(f"Frequency set to {freq} Hz")
        except ValueError:
            print("Usage: freq <Hz>")
    
    def do_burst(self, arg):
        """Set burst cycles: burst 5"""
        try:
            cycles = int(arg)
            self.tqi.state.burst_cycles = cycles
            if self.tqi.fpga:
                self.tqi.fpga.set_burst_cycles(cycles)
            print(f"Burst cycles set to {cycles}")
        except ValueError:
            print("Usage: burst <cycles>")
    
    def do_acquire(self, arg):
        """Acquire single frame: acquire"""
        if not self.tqi.state.connected:
            print("Not connected! Use 'connect' first.")
            return
        
        print(f"Acquiring at {self.tqi.state.frequency_hz} Hz...")
        result = self.tqi.pipeline.acquire_and_process(
            frequency=self.tqi.state.frequency_hz
        )
        
        g = result.get('G_prime', 0)
        eta = result.get('eta', 0)
        
        print(f"✓ Complete: G' = {g:.0f} Pa, η = {eta:.3f} Pa·s")
    
    def do_sweep(self, arg):
        """Run frequency sweep: sweep"""
        if not self.tqi.state.connected:
            print("Not connected!")
            return
        
        print("Running sequential sweep...")
        results = self.tqi.fpga.acquire_sequential()
        print(f"Complete: {len(results)} frequencies acquired")
    
    def do_status(self, arg):
        """Show system status: status"""
        print(json.dumps(self.tqi.state.to_dict(), indent=2))
    
    def do_display(self, arg):
        """Start real-time display: display [interval_ms]"""
        interval = int(arg) if arg else 500
        self.tqi.start_realtime_display(interval)
    
    def do_log(self, arg):
        """Start logging session: log <session_name>"""
        if not arg:
            print("Usage: log <session_name>")
            return
        
        print(f"Starting session: {arg}")
        # In real implementation, would start session context
    
    def do_quit(self, arg):
        """Exit the shell: quit"""
        print("Disconnecting...")
        self.tqi.stop_acquisition()
        if self.tqi.fpga:
            self.tqi.fpga.close()
        print("Goodbye!")
        return True
    
    do_exit = do_quit
    do_q = do_quit


def demo_jupyter():
    """Demo: Jupyter notebook interface."""
    print("Jupyter demo - instantiate in notebook:")
    print("  from turboquant_interactive import TurboQuantInteractive")
    print("  tqi = TurboQuantInteractive()")
    print("  tqi.show_control_panel()")


def demo_repl():
    """Demo: Command-line REPL."""
    print("Starting REPL demo (would be interactive with real hardware)")
    print("Commands: connect, freq <Hz>, burst <n>, acquire, sweep, status, quit")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='TurboQuant Interactive Control')
    parser.add_argument('--repl', action='store_true', help='Start REPL')
    parser.add_argument('--display', action='store_true', help='Start real-time display')
    parser.add_argument('--jupyter', action='store_true', help='Show Jupyter demo')
    parser.add_argument('--connect', action='store_true', help='Auto-connect on startup')
    
    args = parser.parse_args()
    
    tqi = TurboQuantInteractive()
    
    if args.connect:
        tqi.connect()
    
    if args.repl:
        tqi.start_repl()
    elif args.display:
        if not tqi.state.connected:
            print("Need to connect first (--connect)")
        else:
            tqi.start_realtime_display()
    elif args.jupyter:
        demo_jupyter()
    else:
        # Default: REPL
        tqi.start_repl()


if __name__ == '__main__':
    main()
