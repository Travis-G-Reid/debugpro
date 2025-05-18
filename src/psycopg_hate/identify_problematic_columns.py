import pandas as pd
import numpy as np
from datetime import datetime, date

# Create a DataFrame with a mix of standard and problematic columns
def _create_complex_dataframe(rows=5):
    # Standard column data (these work fine with psycopg2)
    standard_data = {
        'id': range(1, rows+1),
        'name': [f'User {i}' for i in range(1, rows+1)],
        'email': [f'user{i}@example.com' for i in range(1, rows+1)],
        'age': np.random.randint(18, 65, size=rows),
        'signup_date': [date(2023, np.random.randint(1, 13), np.random.randint(1, 28)) for _ in range(rows)],
        'last_login': [datetime.now() for _ in range(rows)],
        'active': [bool(np.random.randint(0, 2)) for _ in range(rows)],
        'score': np.random.uniform(0, 100, size=rows),
        'attempts': np.random.randint(1, 10, size=rows),
        'simple_array': [list(range(np.random.randint(2, 5))) for _ in range(rows)],
        'text_array': [[f'tag{j}' for j in range(np.random.randint(1, 4))] for _ in range(rows)],
        'mixed_array': [[i, f'item{i}', i*1.5] for i in range(rows)],
        'float_array': [np.random.uniform(0, 100, size=3).tolist() for _ in range(rows)],
        'empty_array': [[] for _ in range(rows)],
        'null_column': [None] * rows,
        'json_string': [f'{{"id": {i}, "type": "test"}}' for i in range(rows)],  # This is fine as it's a string
    }
    
    # Problematic column 1: Dictionary
    dict_column = [
        {'user_id': i, 'preferences': {'theme': 'dark' if i % 2 == 0 else 'light', 
                                      'notifications': True}, 
         'stats': {'views': i*10, 'likes': i*5}}
        for i in range(1, rows+1)
    ]
    
    # Problematic column 2: List of dictionaries
    list_of_dicts_column = [
        [{'item_id': i*10+j, 'item_name': f'Item {j}', 'price': j*5.99} 
         for j in range(1, np.random.randint(2, 5))]
        for i in range(1, rows+1)
    ]
    
    # Problematic column 3: Dictionary of lists that may contain dictionaries
    dict_of_lists_column = [
        {
            'recent_purchases': [{'product_id': i*100+j, 'date': f'2023-{j+1}-15'} 
                                for j in range(np.random.randint(1, 4))],
            'viewed_categories': [f'category{j}' for j in range(np.random.randint(1, 5))],
            'recommendations': {'top_picks': [i*10+j for j in range(3)],
                              'similar_users': [{'id': i*10+j, 'similarity': j/10} 
                                              for j in range(2)]}
        }
        for i in range(1, rows+1)
    ]
    
    # Problematic column 4: Deeply nested structure
    deeply_nested_column = [
        {
            'profile': {
                'basic': {'id': i, 'username': f'user{i}'},
                'extended': {'interests': [f'interest{j}' for j in range(np.random.randint(1, 4))],
                           'skills': [{'name': f'skill{j}', 'level': j+1, 
                                      'certifications': [{'id': j*10+k, 'issuer': f'issuer{k}'} 
                                                       for k in range(np.random.randint(1, 3))]} 
                                    for j in range(np.random.randint(1, 3))]}
            },
            'activity': {
                'posts': [{'id': i*100+j, 'content': f'content{j}', 
                          'reactions': [{'user_id': k, 'type': 'like' if k % 2 == 0 else 'share'} 
                                      for k in range(np.random.randint(1, 4))]} 
                        for j in range(np.random.randint(1, 3))],
                'connections': [i+j for j in range(np.random.randint(1, 5))]
            }
        }
        for i in range(1, rows+1)
    ]
    
    # Combine all columns
    data = standard_data.copy()
    data['metadata'] = dict_column  # Problematic column 1
    data['purchases'] = list_of_dicts_column  # Problematic column 2
    data['user_data'] = dict_of_lists_column  # Problematic column 3
    data['complex_profile'] = deeply_nested_column  # Problematic column 4
    
    return pd.DataFrame(data)

# Create the dataframe
df = _create_complex_dataframe(5)

# Display column info
print("DataFrame Info:")
print(f"Total columns: {len(df.columns)}")
print("\nColumn names:")
for col in df.columns:
    print(f"- {col}")

print("\nSample of problematic columns:")
print("\n1. metadata (Dictionary):")
print(df['metadata'].iloc[0])

print("\n2. purchases (List of dictionaries):")
print(df['purchases'].iloc[0])

print("\n3. user_data (Dictionary of lists with nested dictionaries):")
print(df['user_data'].iloc[0])

print("\n4. complex_profile (Deeply nested structure):")
print(df['complex_profile'].iloc[0])

# Function to identify columns that would cause psycopg2 adapter issues
def identify_problematic_columns(df):
    problematic_cols = []
    
    for col in df.columns:
        # Check first non-null value
        sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        
        if sample is not None:
            if isinstance(sample, dict):
                problematic_cols.append((col, "Dictionary"))
            elif isinstance(sample, list) and any(isinstance(item, dict) for item in sample if isinstance(item, dict)):
                problematic_cols.append((col, "List containing dictionaries"))
            elif isinstance(sample, list) and any(isinstance(item, list) for item in sample):
                # Check for nested lists that might contain dictionaries
                has_nested_dict = False
                for item in sample:
                    if isinstance(item, list) and any(isinstance(subitem, dict) for subitem in item if hasattr(subitem, '__iter__')):
                        has_nested_dict = True
                        break
                if has_nested_dict:
                    problematic_cols.append((col, "Nested list potentially containing dictionaries"))
    
    return problematic_cols

# Identify problematic columns
problematic_cols = identify_problematic_columns(df)
print("\nIdentified problematic columns:")
for col, reason in problematic_cols:
    print(f"- {col}: {reason}")