#!/bin/bash
# Quick script to view all test results

echo "Opening all test results..."
echo ""

# Open HTML report
echo "1. Opening HTML test report..."
open ui_test_report/test_report.html

sleep 1

# Open mockup comparison screenshots
echo "2. Opening mockup comparison screenshots..."
open mockup_comparison/streamlit_full.png
sleep 0.5
open mockup_comparison/mockup_full.png

sleep 1

# Open Streamlit app
echo "3. Opening Streamlit app in browser..."
open http://localhost:8501

sleep 1

# Open mockup reference
echo "4. Opening mockup reference..."
open https://ma3u.github.io/neo4j-agentframework/

echo ""
echo "✅ All test results opened!"
echo ""
echo "Files opened:"
echo "  - HTML Report: ui_test_report/test_report.html"
echo "  - Streamlit Screenshot: mockup_comparison/streamlit_full.png"
echo "  - Mockup Screenshot: mockup_comparison/mockup_full.png"
echo "  - Live Streamlit: http://localhost:8501"
echo "  - Reference Mockup: https://ma3u.github.io/neo4j-agentframework/"
echo ""
