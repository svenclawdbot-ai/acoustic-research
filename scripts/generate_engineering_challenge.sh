#!/bin/bash
# Engineering Challenge Generator
# Generates daily engineering challenges based on research focus areas

WORKSPACE="/home/james/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
MEMORY_FILE="$WORKSPACE/memory/${DATE}.md"

# Challenge topics rotate based on day
case $DAY_OF_WEEK in
    1)  # Monday - Acoustic NDE / Physics
        TOPIC="Acoustic NDE"
        CHALLENGE="shear_wave_simulation"
        ;;
    2)  # Tuesday - Thermal Management
        TOPIC="Thermal Engineering"
        CHALLENGE="thermal_analysis"
        ;;
    3)  # Wednesday - Mechanical Design
        TOPIC="Mechanical Design"
        CHALLENGE="design_challenge"
        ;;
    4)  # Thursday - Signal Processing
        TOPIC="Signal Processing"
        CHALLENGE="dsp_challenge"
        ;;
    5)  # Friday - System Integration
        TOPIC="System Integration"
        CHALLENGE="integration_challenge"
        ;;
    6|7)  # Weekend - Open Research
        TOPIC="Open Research"
        CHALLENGE="open_ended"
        ;;
esac

echo "📅 ${DATE} - ${TOPIC} Challenge"
echo ""

case $CHALLENGE in
    shear_wave_simulation)
        echo "🎯 Today's Challenge: Extend the 1D Shear Wave Simulator"
        echo ""
        echo "Tasks:"
        echo "1. Run existing 1D simulation with different (G', η) pairs"
        echo "2. Implement 2D FDTD version for realistic wave propagation"
        echo "3. Add absorbing boundary conditions (PML or Mur 2nd order)"
        echo "4. Generate dispersion curves from simulated wave fields"
        echo ""
        echo "Deliverable: Working 2D simulation with visualization"
        ;;
    thermal_analysis)
        echo "🎯 Today's Challenge: Electronics Cooling Analysis"
        echo ""
        echo "Tasks:"
        echo "1. Calculate thermal resistance for a 500W/cm² chip package"
        echo "2. Model heat pipe performance with HFE-7100 working fluid"
        echo "3. Optimize vapor space thickness (5-8mm range)"
        echo "4. Compare CVD diamond vs copper interposer performance"
        echo ""
        echo "Deliverable: Thermal stack analysis with recommendations"
        ;;
    design_challenge)
        echo "🎯 Today's Challenge: Ultrasonic Transducer Design"
        echo ""
        echo "Tasks:"
        echo "1. Design 3.5 MHz focused transducer for phantom imaging"
        echo "2. Calculate focal depth and beam width"
        echo "3. Select backing material and matching layer"
        echo "4. Estimate pulse-echo sensitivity"
        echo ""
        echo "Deliverable: Transducer specification sheet"
        ;;
    dsp_challenge)
        echo "🎯 Today's Challenge: Dispersion Curve Extraction"
        echo ""
        echo "Tasks:"
        echo "1. Implement 2D FFT for space-time wave field data"
        echo "2. Extract phase velocity vs frequency (k-ω analysis)"
        echo "3. Fit Kelvin-Voigt model to extracted dispersion"
        echo "4. Validate against theoretical predictions"
        echo ""
        echo "Deliverable: Python script with dispersion extraction"
        ;;
    integration_challenge)
        echo "🎯 Today's Challenge: End-to-End Phantom System"
        echo ""
        echo "Tasks:"
        echo "1. Design gelatin phantom with known mechanical properties"
        echo "2. Plan echomods kit integration (pulser + ADC + Pi)"
        echo "3. Estimate SNR for pulse-echo acquisition"
        echo "4. Draft experimental validation protocol"
        echo ""
        echo "Deliverable: Experimental setup document"
        ;;
    open_ended)
        echo "🎯 Weekend Research: Literature Deep Dive"
        echo ""
        echo "Tasks:"
        echo "1. Read one key paper from the 50-paper bibliography"
        echo "2. Summarize methodology and key findings"
        echo "3. Identify how it connects to your research"
        echo "4. Update problem statement if needed"
        echo ""
        echo "Deliverable: Paper summary notes"
        ;;
esac

echo ""
echo "⏱️  Time Budget: 2-3 hours focused work"
echo "📝 Log progress in: ${MEMORY_FILE}"
