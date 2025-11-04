#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract table data from MySQL dump file to separate CSV files
Improved version with better handling of multi-line values
"""

import re
import csv
import os

def parse_insert_statement(text, start_pos=0):
    """
    Parse INSERT INTO statement from SQL text starting at start_pos
    Returns: (table_name, columns, values, end_pos) or None
    """
    # Find the start of INSERT INTO
    insert_match = re.search(r"INSERT INTO `([^`]+)`\s*\(([^)]+)\)\s*VALUES\s*", text[start_pos:], re.IGNORECASE)
    if not insert_match:
        return None
    
    table_name = insert_match.group(1)
    columns_str = insert_match.group(2)
    
    # Extract column names
    columns = [col.strip().strip('`') for col in columns_str.split(',')]
    
    # Find where VALUES starts
    values_start = start_pos + insert_match.end()
    
    # Parse values - need to handle multi-line and nested parentheses
    values_list = []
    current_pos = values_start
    depth = 0
    in_quotes = False
    quote_char = None
    current_tuple = ""
    
    while current_pos < len(text):
        char = text[current_pos]
        
        if char in ["'", '"']:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                if current_pos + 1 < len(text) and text[current_pos + 1] == quote_char:
                    # Escaped quote
                    current_tuple += char
                    current_pos += 1
                else:
                    in_quotes = False
                    quote_char = None
            current_tuple += char
        elif char == '(' and not in_quotes:
            if depth == 0:
                current_tuple = ""
            depth += 1
            current_tuple += char
        elif char == ')' and not in_quotes:
            depth -= 1
            current_tuple += char
            if depth == 0:
                # End of one tuple
                values_list.append(current_tuple)
                current_tuple = ""
        elif char == ';' and not in_quotes and depth == 0:
            # End of INSERT statement
            break
        else:
            current_tuple += char
        
        current_pos += 1
    
    # Parse the tuples into lists of values
    rows = []
    for tuple_str in values_list:
        if not tuple_str.strip():
            continue
        # Remove outer parentheses
        inner = tuple_str.strip()[1:-1].strip() if tuple_str.strip().startswith('(') else tuple_str.strip()
        
        # Parse values
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        escape_next = False
        
        i = 0
        while i < len(inner):
            char = inner[i]
            
            if escape_next:
                current_value += char
                escape_next = False
            elif char == '\\':
                escape_next = True
                current_value += char
            elif char in ["'", '"']:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    if i + 1 < len(inner) and inner[i + 1] == quote_char:
                        # Escaped quote
                        current_value += char
                        current_value += char
                        i += 1
                    else:
                        in_quotes = False
                        quote_char = None
                current_value += char
            elif char == ',' and not in_quotes:
                # End of value
                clean_value = current_value.strip()
                # Remove quotes
                if len(clean_value) > 1 and clean_value[0] in ["'", '"'] and clean_value[0] == clean_value[-1]:
                    clean_value = clean_value[1:-1]
                values.append(clean_value)
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        # Add last value
        if current_value:
            clean_value = current_value.strip()
            if len(clean_value) > 1 and clean_value[0] in ["'", '"'] and clean_value[0] == clean_value[-1]:
                clean_value = clean_value[1:-1]
            values.append(clean_value)
        
        rows.append(values)
    
    return (table_name, columns, rows, current_pos)

def extract_all_tables(sql_content):
    """Extract all tables from SQL content"""
    table_data = {}
    
    current_pos = 0
    while current_pos < len(sql_content):
        result = parse_insert_statement(sql_content, current_pos)
        if result:
            table_name, columns, rows, end_pos = result
            if table_name not in table_data:
                table_data[table_name] = {
                    'columns': columns,
                    'rows': []
                }
            table_data[table_name]['rows'].extend(rows)
            current_pos = end_pos
        else:
            break
    
    return table_data

def write_csv(data, filename, columns):
    """Write data to CSV file"""
    if not data:
        print(f"No data for {filename}")
        return
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)
    
    print(f"Created: {filename} ({len(data)} rows)")

def main():
    sql_file = 'myhotel.sql'
    output_dir = 'datasets_extracted'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {sql_file}...")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("Extracting table data...")
    table_data = extract_all_tables(sql_content)
    
    print("=" * 50)
    for table_name, data in table_data.items():
        filename = f"{output_dir}/{table_name}.csv"
        write_csv(data['rows'], filename, data['columns'])
    
    print("=" * 50)
    print(f"Extraction complete! Files saved to '{output_dir}/'")

if __name__ == '__main__':
    main()

