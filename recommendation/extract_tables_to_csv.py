#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract table data from MySQL dump file to separate CSV files
"""

import re
import csv
import os
from datetime import datetime

def parse_sql_file(sql_file_path):
    """Parse SQL file and extract table data"""
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all CREATE TABLE statements
    create_table_pattern = r'CREATE TABLE `([^`]+)`'
    table_names = re.findall(create_table_pattern, content)
    
    # Find all INSERT INTO statements
    insert_pattern = r'INSERT INTO `([^`]+)`[^V]+VALUES\s+(.+?);'
    insert_statements = re.findall(insert_pattern, content, re.DOTALL)
    
    # Group inserts by table name
    table_data = {}
    for table_name, insert_values in insert_statements:
        if table_name not in table_data:
            table_data[table_name] = []
        table_data[table_name].append(insert_values)
    
    return table_names, table_data

def extract_column_names(create_table_match, table_name):
    """Extract column names from CREATE TABLE statement"""
    columns_pattern = r'`([^`]+)`\s+([^\s]+)'
    columns = re.findall(columns_pattern, create_table_match.group(0))
    return [col[0] for col in columns]

def parse_insert_values(insert_values):
    """Parse INSERT VALUES into list of dictionaries"""
    rows = []
    
    # Find all value tuples
    value_pattern = r'\(([^)]+)\)'
    matches = re.finditer(value_pattern, insert_values)
    
    for match in matches:
        values_str = match.group(1)
        # Split by comma but respect string quotes
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        for char in values_str:
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    in_quotes = False
                    quote_char = None
                current_value += char
            elif char == ',' and not in_quotes:
                # Remove quotes if they exist
                clean_value = current_value.strip()
                if clean_value.startswith("'") and clean_value.endswith("'"):
                    clean_value = clean_value[1:-1]
                elif clean_value.startswith('"') and clean_value.endswith('"'):
                    clean_value = clean_value[1:-1]
                values.append(clean_value)
                current_value = ""
            else:
                current_value += char
        
        # Add last value
        if current_value:
            clean_value = current_value.strip()
            if clean_value.startswith("'") and clean_value.endswith("'"):
                clean_value = clean_value[1:-1]
            elif clean_value.startswith('"') and clean_value.endswith('"'):
                clean_value = clean_value[1:-1]
            values.append(clean_value)
        
        rows.append(values)
    
    return rows

def parse_column_names_from_insert(insert_values):
    """Extract column names from INSERT statement"""
    column_pattern = r'INSERT INTO `[^`]+`\s+\(([^)]+)\)'
    match = re.search(column_pattern, insert_values)
    if match:
        columns_str = match.group(1)
        # Extract column names
        columns = [col.strip().strip('`') for col in columns_str.split(',')]
        return columns
    return None

def write_csv(data, filename, columns=None):
    """Write data to CSV file"""
    if not data:
        print(f"No data for {filename}")
        return
    
    # Ensure columns are available
    if columns and data:
        # Write with column headers
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(data)
    elif data:
        # Write without headers
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    
    print(f"Created: {filename} ({len(data)} rows)")

def main():
    sql_file = 'myhotel.sql'
    output_dir = 'datasets_extracted'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Find all INSERT INTO statements with their data
    insert_pattern = r"INSERT INTO `([^`]+)`\s+\(([^)]+)\)\s+VALUES\s+((?:\([^)]*\)[,\s]*)+);"
    matches = re.finditer(insert_pattern, sql_content, re.DOTALL | re.MULTILINE)
    
    table_data = {}
    table_columns = {}
    
    for match in matches:
        table_name = match.group(1)
        columns_str = match.group(2)
        values_str = match.group(3)
        
        # Extract column names
        columns = [col.strip().strip('`') for col in columns_str.split(',')]
        
        # Parse values
        # Find all value tuples
        value_pattern = r'\(([^)]+)\)'
        value_matches = re.findall(value_pattern, values_str)
        
        rows = []
        for values_str_match in value_matches:
            # Split values more carefully
            values = []
            current_value = ""
            in_quotes = False
            quote_char = None
            
            i = 0
            while i < len(values_str_match):
                char = values_str_match[i]
                
                if char in ["'", '"']:
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                    current_value += char
                elif char == ',' and not in_quotes:
                    # Save current value
                    clean_value = current_value.strip()
                    if clean_value.startswith("'") and clean_value.endswith("'"):
                        clean_value = clean_value[1:-1]
                    elif clean_value.startswith('"') and clean_value.endswith('"'):
                        clean_value = clean_value[1:-1]
                    values.append(clean_value)
                    current_value = ""
                else:
                    current_value += char
                
                i += 1
            
            # Add last value
            if current_value:
                clean_value = current_value.strip()
                if clean_value.startswith("'") and clean_value.endswith("'"):
                    clean_value = clean_value[1:-1]
                elif clean_value.startswith('"') and clean_value.endswith('"'):
                    clean_value = clean_value[1:-1]
                values.append(clean_value)
            
            if values:
                rows.append(values)
        
        # Store table data
        if table_name not in table_data:
            table_data[table_name] = []
        table_data[table_name].extend(rows)
        table_columns[table_name] = columns
    
    # Write each table to CSV
    print(f"Extracting data from {sql_file}...")
    print(f"Output directory: {output_dir}")
    print("=" * 50)
    
    for table_name, rows in table_data.items():
        filename = f"{output_dir}/{table_name}.csv"
        columns = table_columns.get(table_name, [])
        write_csv(rows, filename, columns)
    
    print("=" * 50)
    print(f"Extraction complete! Files saved to '{output_dir}/'")

if __name__ == '__main__':
    main()

