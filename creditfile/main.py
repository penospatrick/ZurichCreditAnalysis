# Created 2023-10-20


from .utils import isna
from .parse import get_file_details, parse_credit_report
from .normalize import normalize_credit_data
from .featurize import prepare_features
from .score import make_credit_score

from collections.abc import Iterable
import json

# Google Colab specific imports - only load if in Colab environment
try:
    from google.colab import files
    import ipywidgets as widgets
    from IPython.display import display
    IN_COLAB = True
except ImportError:
    IN_COLAB = False


# Constants
ESSENTIAL_FIELDS = {
    'personal_data': [
        'name',
        'present_address',
        'present_address_tenure',
        'contact_no',
        'birthplace',
        'education',
        'parents_name',
        'parents_address',
        'date_applied',
        'unit_applied',
        'loan_amount',
        'loan_terms',
        'housing_status',
        'dob',
        'age',
        'marital_status',
        'n_children',
        'n_dependents',
        'dependent_ages'
    ],
    'income_analysis': {
        'summary': ['gross_income', 'monthly_amortization']
    },
    'officer_assessment': [
        'loan_purpose',
        'unit_payor',
        'unit_rider',
        'rider_license',
        'cell_signal_status',
        'prepared_by',
        'remarks'
    ]
}


# Utils
def is_missing(x):
    return isna(x) or (isinstance(x, Iterable) and all(isna(_) for _ in x))

def validate_fields(data, essential_fields=ESSENTIAL_FIELDS):
    'Check if the data contains all essential fields.'
    missing_fields = {}
    for k, v in essential_fields.items():
        subset = data.get(k, None)
        if isna(subset):
            missing_fields[k] = v
        elif isinstance(v, dict):
            missing = validate_fields(subset, v)
        elif isinstance(v, list):
            missing = [
                field for field in v if isna(subset.get(field, None))
            ]
        if missing:
            missing_fields[k] = missing
    return missing_fields

def pretty_print(data, level=0, null_repr='NULL'):
    'Pretty print a data container.'
    indentation = '    ' * level
    if isna(data):
        print(null_repr)
    elif isinstance(data, dict):
        if level > 0:
            print()
        for k, v in data.items():
            print(f'{indentation}{k}', end='')
            pretty_print(v, level+1)
    elif isinstance(data, list):
        if len(data):
            print()
            for k in data:
                print(f'{indentation}{k}')
        else: print(': []')
    else:
        print(f': {data}')

def print_missing(normalized):
    'Print fields missing from the credit file.'
    print('MISSING DATA', end='')
    missing_fields = validate_fields(normalized)
    if missing_fields:
        pretty_print(missing_fields, level=1)
    else:
        print()
        print('    None')


# Report analysis
def analyze_upload():
    'Upload and analyze a credit file.'
    upload = files.upload()
    fn, report = next(iter(upload.items()))
    parsed = get_file_details(fn) | parse_credit_report(report)
    normalized = normalize_credit_data(parsed)
    features = prepare_features(normalized)
    missing_count = sum(1 for _ in features if isna(_) or _ == -1)
    score = make_credit_score(features)

    # Printing info
    print()
    print_missing(normalized)
    print()
    if missing_count < 5:
        print(f'CREDIT SCORE: {score}')
    else:
        print(f'CREDIT SCORE: Too many missing data fields.')
    print()
    print('DATA VALIDATION')
    pretty_print(normalized)
    print()

    # Exporting normalized data
    def on_button_click(b):
        normalized['credit_score'] = score
        output_fn = fn.rsplit('.', maxsplit=1)[0] + '.json'
        with open(output_fn, mode='w') as file:
            json.dump(normalized, file, indent=4)
        files.download(output_fn)
    button = widgets.Button(
        description='Download validated data'
    )
    button.layout.width = 'auto'
    button.on_click(on_button_click)
    display(button)