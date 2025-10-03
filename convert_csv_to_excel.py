#!/usr/bin/env python3
"""
Convert Kalimax seed CSV files to Excel workbook
Creates a single Excel file with each CSV as a separate sheet
"""

import pandas as pd
import os
from pathlib import Path

def convert_csvs_to_excel():
    """Convert all CSV files in data/seed to Excel workbook."""
    
    # Define input and output paths
    seed_dir = Path("data/seed")
    output_file = seed_dir / "kalimax_seed_data.xlsx"
    
    # CSV files to process
    csv_files = [
        "01_glossary.csv",
        "02_corpus.csv", 
        "03_expressions.csv",
        "04_high_risk.csv",
        "05_normalization.csv",
        "06_profanity.csv",
        "07_challenge.csv",
        "08_monolingual.csv",
        "09_haitian_patterns.csv",
        "10_unpolite.csv"
    ]
    
    # Sheet names (Excel sheet names have limitations)
    sheet_names = [
        "Glossary",
        "Corpus", 
        "Expressions",
        "High_Risk",
        "Normalization",
        "Profanity",
        "Challenge",
        "Monolingual",
        "Haitian_Patterns",
        "Unpolite"
    ]
    
    print("Converting CSV files to Excel workbook...")
    print(f"Output file: {output_file}")
    
    # Create Excel writer object
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        for csv_file, sheet_name in zip(csv_files, sheet_names):
            csv_path = seed_dir / csv_file
            
            if not csv_path.exists():
                print(f"⚠️  Warning: {csv_file} not found, skipping...")
                continue
                
            print(f"Processing {csv_file} -> {sheet_name}")
            
            try:
                # Read CSV with error handling for encoding issues
                try:
                    df = pd.read_csv(csv_path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(csv_path, encoding='utf-8-sig')
                except:
                    df = pd.read_csv(csv_path, encoding='latin-1')
                
                # Get basic stats
                rows, cols = df.shape
                print(f"  📊 {rows:,} rows × {cols} columns")
                
                # Write to Excel sheet
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Get the worksheet to apply formatting
                worksheet = writer.sheets[sheet_name]
                
                # Auto-adjust column widths
                for column_cells in worksheet.columns:
                    length = max(len(str(cell.value or "")) for cell in column_cells)
                    # Limit column width to reasonable maximum
                    adjusted_width = min(length + 2, 50)
                    worksheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width
                
                # Freeze the header row
                worksheet.freeze_panes = "A2"
                
                print(f"  ✅ Successfully added to sheet '{sheet_name}'")
                
            except Exception as e:
                print(f"  ❌ Error processing {csv_file}: {e}")
                continue
    
    print(f"\n🎉 Excel workbook created successfully: {output_file}")
    
    # Display summary
    try:
        wb_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
        print(f"📁 File size: {wb_size:.2f} MB")
    except:
        pass
    
    return output_file

if __name__ == "__main__":
    output_path = convert_csvs_to_excel()
    print(f"\n📋 Summary:")
    print(f"   Input: 10 CSV files from data/seed/")
    print(f"   Output: {output_path}")
    print(f"   Format: Excel workbook (.xlsx)")
    print(f"   Sheets: One per CSV file with appropriate formatting")