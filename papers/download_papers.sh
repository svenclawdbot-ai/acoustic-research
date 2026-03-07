#!/bin/bash
# Download script for acoustic NDE research papers
# Run this script to fetch papers from various sources

echo "=================================="
echo "Paper Download Script"
echo "=================================="
echo ""

# Create directories
mkdir -p 01_Essential 02_Supporting 03_Experimental

echo "This script will attempt to download papers from open access sources."
echo "Many papers are behind paywalls - manual download may be required."
echo ""

# Essential Papers (5)
echo "📚 ESSENTIAL PAPERS (Download First)"
echo "===================================="
echo ""

echo "1. Sarvazyan 1998 - Shear wave elasticity imaging"
echo "   URL: https://www.researchgate.net/publication/12913173"
echo "   DOI: 10.1016/S0301-5629(98)00110-0"
echo "   Alternative: https://pubmed.ncbi.nlm.nih.gov/10385964/"
echo "   Status: May need ResearchGate account or institutional access"
echo ""

echo "2. Nightingale 2002 - ARFI Imaging"
echo "   DOI: 10.1016/S0301-5629(02)00456-4"
echo "   Search: 'Nightingale ARFI 2002 ultrasound medicine biology'"
echo "   Status: Behind paywall - check institutional access"
echo ""

echo "3. Chen 2009 - SDUV (Shearwave Dispersion Ultrasound Vibrometry)"
echo "   URL: https://www.researchgate.net/publication/24004688"
echo "   DOI: 10.1109/TUFFC.2009.1005"
echo "   Status: Often available on ResearchGate"
echo ""

echo "4. Parker 2014 - Viscoelastic models"
echo "   DOI: 10.1016/j.ultrasmedbio.2014.05.021"
echo "   Search: 'Parker inconvenient nature soft tissue viscosity 2014'"
echo "   Status: Check author website or ResearchGate"
echo ""

echo "5. Barr 2022 - Viscosity in liver disease"
echo "   DOI: 10.1148/radiol.210475"
echo "   Journal: Radiology"
echo "   Status: Recent paper - institutional access likely needed"
echo ""

# Try to download from Sci-Hub alternatives (educational use only)
echo ""
echo "🔍 ALTERNATIVE SOURCES:"
echo "======================"
echo ""
echo "Sci-Hub (if legal in your jurisdiction):"
echo "  https://sci-hub.se/DOI"
echo "  https://sci-hub.st/DOI"
echo ""
echo "Anna's Archive (books/papers):"
echo "  https://annas-archive.org/"
echo ""
echo "Library Genesis:"
echo "  https://libgen.is/"
echo ""

echo ""
echo "📖 SUPPORTING PAPERS (Week 2-3)"
echo "================================"
echo ""
echo "6. Manduca 2001 - Inverse problem in MRE"
echo "   DOI: 10.1118/1.1388012"
echo ""
echo "7. Zhang 2008 - Multi-frequency KV validation"
echo "   DOI: 10.1109/TUFFC.2008.702"
echo ""
echo "8. Raissi 2018 - PINNs for wave problems"
echo "   arXiv: https://arxiv.org/abs/1711.10561 (FREE)"
echo ""
echo "9. Barry 2021 - SWE limitations review"
echo "   DOI: 10.1007/s10396-021-01127-w"
echo ""
echo "10. Bercoff 2004 - Supersonic imaging"
echo "    DOI: 10.1109/TUFFC.2004.1295422"
echo ""

echo ""
echo "💡 DOWNLOAD TIPS:"
echo "================="
echo "1. Use your university library access if available"
echo "2. Check ResearchGate - authors often upload PDFs"
echo "3. Search Google Scholar - click 'All versions' for PDFs"
echo "4. Contact authors directly for recent papers"
echo ""
echo "Press Enter to open URLs in browser (if supported)..."
read

# Open URLs (Linux)
if command -v xdg-open &> /dev/null; then
    xdg-open "https://www.researchgate.net/publication/12913173" 2>/dev/null
    sleep 1
    xdg-open "https://pubmed.ncbi.nlm.nih.gov/10385964/" 2>/dev/null
fi

echo ""
echo "Done! Check the folders for downloaded papers."
