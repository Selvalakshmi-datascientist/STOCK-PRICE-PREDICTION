#!/usr/bin/env python3
"""
Stock Data Graph Viewer
Shows information about generated graphs and how to view them.
"""

import os
from datetime import datetime

def show_graph_info():
    """Display information about the generated graphs"""

    print("🎯 Stock Data Visualization - Complete!")
    print("=" * 50)

    graphs_dir = "graphs"
    if os.path.exists(graphs_dir):
        files = os.listdir(graphs_dir)
        png_files = [f for f in files if f.endswith('.png')]

        print(f"📁 Found {len(png_files)} graph files in '{graphs_dir}' folder:")
        print()

        for i, filename in enumerate(sorted(png_files), 1):
            filepath = os.path.join(graphs_dir, filename)
            size = os.path.getsize(filepath)
            size_kb = size / 1024

            print(f"{i}. 📊 {filename}")
            print(f"   📏 Size: {size_kb:.1f} KB")

        print("🔍 How to view the graphs:")
        print("• Open the PNG files in any image viewer")
        print("• Double-click the files in File Explorer")
        print("• Use any web browser to open the PNG files")
        print()

        print("📈 Graph Descriptions:")
        print("• historical.png - Shows historical stock prices over time")
        print("• predictions.png - Historical data + future price predictions")
        print("• analysis.png - Comprehensive analysis with statistics")
        print()

        print("✅ Generated on:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    else:
        print("❌ Graphs folder not found. Run 'python show_graphs.py' first.")

if __name__ == "__main__":
    show_graph_info()