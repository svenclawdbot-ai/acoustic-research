#!/bin/bash
# Daily Learning Challenge Generator
# Varied topics: Engineering, Physics/Mathematics, Language, Humanities

WORKSPACE="/home/james/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
MEMORY_FILE="$WORKSPACE/memory/${DATE}.md"

# New rotation: Varied learning topics
case $DAY_OF_WEEK in
    1)  # Monday - Engineering (Acoustic NDE focus)
        TOPIC="Engineering: Acoustic NDE"
        CHALLENGE="acoustic_engineering"
        ;;
    2)  # Tuesday - Physics/Mathematics
        TOPIC="Physics & Mathematics"
        CHALLENGE="physics_math"
        ;;
    3)  # Wednesday - Engineering (Signal Processing)
        TOPIC="Engineering: Signal Processing"
        CHALLENGE="dsp_engineering"
        ;;
    4)  # Thursday - Language
        TOPIC="Language & Communication"
        CHALLENGE="language"
        ;;
    5)  # Friday - Humanities
        TOPIC="Humanities & Society"
        CHALLENGE="humanities"
        ;;
    6|7)  # Weekend - Open Research
        TOPIC="Open Research"
        CHALLENGE="open_ended"
        ;;
esac

echo "📅 ${DATE} - ${TOPIC} Challenge"
echo ""

case $CHALLENGE in
    acoustic_engineering)
        echo "🎯 Monday Challenge: Acoustic NDE / Medical Imaging"
        echo ""
        echo "Tasks:"
        echo "1. Extend 2D shear wave simulation to 3D or add anisotropic media"
        echo "2. Implement inverse problem solver (Bayesian inference for G', η)"
        echo "3. Design phantom experiment protocol for validation"
        echo "4. Compare Kelvin-Voigt vs Zener model predictions"
        echo ""
        echo "Deliverable: Working code or experimental protocol"
        ;;
    dsp_engineering)
        echo "🎯 Wednesday Challenge: Signal Processing & DSP"
        echo ""
        echo "Tasks:"
        echo "1. Implement k-ω transform for dispersion extraction"
        echo "2. Design optimal receiver array (sparse sampling)"
        echo "3. Apply compressive sensing to wavefield reconstruction"
        echo "4. Build real-time processing pipeline"
        echo ""
        echo "Deliverable: DSP algorithm with validation"
        ;;
    physics_math)
        echo "🎯 Tuesday Challenge: Physics & Mathematics"
        echo ""
        echo "Topics rotate:"
        echo "• Wave mechanics: Derive dispersion relation from first principles"
        echo "• Linear algebra: SVD applications in inverse problems"
        echo "• Probability: Bayesian inference derivations"
        echo "• Complex analysis: Poles and zeros in viscoelastic models"
        echo "• Differential equations: PDE solutions for wave propagation"
        echo ""
        echo "Deliverable: Mathematical derivation or proof"
        ;;
    language)
        echo "🎯 Thursday Challenge: Language & Communication"
        echo ""
        echo "Topics rotate:"
        echo "• Technical writing: Draft IEEE paper abstract/introduction"
        echo "• Presentation skills: Prepare 5-minute research pitch"
        echo "• Scientific vocabulary: Learn 10 new terms with etymology"
        echo "• Peer review: Critique a published paper constructively"
        echo "• Translation: Summarize a foreign-language research abstract"
        echo ""
        echo "Deliverable: Written piece or recorded presentation"
        ;;
    humanities)
        echo "🎯 Friday Challenge: Humanities & Society"
        echo ""
        echo "Topics rotate:"
        echo "• Ethics: AI in medical diagnosis - benefits and risks"
        echo "• History: Evolution of medical imaging (X-ray to ultrasound)"
        echo "• Philosophy: Taleb's Antifragility applied to research"
        echo "• Economics: Cost-effectiveness of early disease detection"
        echo "• Sociology: Healthcare access and technology democratization"
        echo ""
        echo "Deliverable: Reflection essay or discussion notes"
        ;;
    open_ended)
        echo "🎯 Weekend Research: Open Exploration"
        echo ""
        echo "Choose your own adventure:"
        echo "1. Deep dive into a paper from the bibliography"
        echo "2. Explore a tangential topic that sparked curiosity"
        echo "3. Catch up on any missed challenges from the week"
        echo "4. Free creative work (blog post, visualization, tool)"
        echo "5. Rest and reflect on the week's learning"
        echo ""
        echo "Deliverable: Whatever you find valuable"
        ;;
esac

echo ""
echo "⏱️  Time Budget: 2-3 hours focused work"
echo "📝 Log progress in: ${MEMORY_FILE}"
echo "🎯 Focus: Deep work, not shallow completion"
