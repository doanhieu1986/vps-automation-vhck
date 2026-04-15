#!/usr/bin/env python3
import json
import sys
import pandas as pd
from datetime import datetime
import os

def create_excel_from_json(input_file_path, output_path):
    """
    Create Excel file from JSON file
    """
    try:
        # Read JSON from file
        if not os.path.exists(input_file_path):
            print(json.dumps({
                'status': 'error',
                'message': f'Input file not found: {input_file_path}'
            }))
            sys.exit(1)

        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        records = data.get('records', [])

        if not records:
            print(json.dumps({
                'status': 'error',
                'message': 'No records found in input data'
            }))
            sys.exit(1)

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Create DataFrame from records
        df = pd.DataFrame(records)

        # Write to Excel with formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(
                writer,
                sheet_name='Tin chứng khoán',
                index=False,
                startrow=0
            )

            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Tin chứng khoán']

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        # Return success
        print(json.dumps({
            'status': 'success',
            'message': f'Created Excel file with {len(records)} records',
            'file': output_path,
            'records_count': len(records),
            'timestamp': datetime.now().isoformat()
        }))

    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': str(e),
            'error_type': type(e).__name__
        }))
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({
            'status': 'error',
            'message': 'Missing arguments: input_file_path output_path'
        }))
        sys.exit(1)

    input_file = sys.argv[1]
    output_path = sys.argv[2]

    create_excel_from_json(input_file, output_path)
