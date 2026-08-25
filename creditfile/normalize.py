# Created 2023-10-16


from .utils import notna
import re


# Normalization utils
def standardize_field(name):
    'Basic standardization of field names.'
    name = name.strip().lower()
    # Standardize splitting chars
    name = re.sub(r'[\/\s]+', '_', name)
    # Standardize characters
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name if name else '_'

def flatten_dict(nested: dict, reduce_fun=lambda k0, k1: f'{k0}__{k1}') -> dict:
    'Flatten a nested dictionary with a reduction function on keys.'
    flattened = {
        reduce_fun(k0, k1): v1
        for k0, v0 in nested.items()
        for k1, v1 in v0.items()
    }
    return flattened
    
    
# Section normalizers
# Personal data
def normalize_personal_data(parsed) -> dict:
    'Normalize personal data fields.'
    if 'personal_data' not in parsed:
        return {}
    data = parsed['personal_data']
    pre_corrections = {
        'Date of Birth': 'spouse__dob',
        'Present Address': 'spouse__present_address',
        'Previous Address': 'spouse__previous_address'
    }
    post_corrections = {
        'amount_applied_for': 'loan_amount',
        'contact_number': 'contact_no',
        'downpayment_terms': 'loan_terms',
        'educational_attainment': 'education',
        'length_of_stay_at_present_address': 'present_address_tenure',
        'length_of_stay_at_previous_address': 'previous_address_tenure',
        'no_of_children': 'n_children',
        'name_of_applicant': 'name',
        'name_of_landlady_number': 'landlord',
        'name_of_spouse': 'spouse__name',
        'parents_address_1': 'spouse__parents_adress',
        'place_of_birth': 'birthplace',
        'spouse__date_of_birth': 'spouse__dob',
        'spouse__educational_attainment': 'spouse__education',
        'type_of_residence': 'housing_status',
        'unit_applied_collateral': 'unit_applied',
        'units_applied': 'unit_applied'
    }
    canonical_fields = {
        'age',
        'birthplace',
        'contact_no',
        'date_applied',
        'dob',
        'education',
        'housing_status',
        'landlord',
        'loan_amount',
        'loan_terms',
        'marital_status',
        'n_children',
        'n_dependents',
        'name',
        'nationality',
        'parents_address',
        'parents_address_2',
        'parents_name',
        'parents_name_2',
        'present_address',
        'present_address_tenure',
        'previous_address',
        'previous_address_tenure',
        'spouse__dob',
        'spouse__education',
        'spouse__name',
        'spouse__parents_address',
        'spouse__parents_adress',
        'spouse__parents_name',
        'spouse__parents_name_2',
        'spouse__present_address',
        'spouse__previous_address',
        'unit_applied'
    }
    normalized = {}
    for k, v in data.items():
        k = pre_corrections.get(k, k)
        k = standardize_field(k)
        k = post_corrections.get(k, k)
        if k in canonical_fields and notna(v):
            normalized[k] = v
    if 'dependents' in parsed:
        dependent_data = parsed['dependents']
        if 'Age' in dependent_data:
            normalized['dependent_ages'] = dependent_data['Age']
    return normalized

# Income source details
def normalize_income_source_details(parsed) -> dict:
    'Normalize income source details fields.'
    if (
        'income_data' not in parsed
        or 'income_sources' not in parsed['income_data']
    ):
        return {}
    data = parsed['income_data']['income_sources']

    # Normalization
    field_corrections = {
        'business__address_of_business': 'business__address',
        'business__business_name': 'business__name',
        'business__business_permit_no': 'business__permit_no',
        'business__monthly_income': 'business__monthly_income',
        'business__remarks': 'business__remarks',
        'business__route_of_vehicle': 'business__vehicle_route',
        'business__years_in_business': 'business__tenure',
        'employment__address_of_employer': 'employment__address',
        'employment__contact_number_of_employer': 'employment__contact_no',
        'employment__length_of_service': 'employment__tenure',
        'employment__monthly_net_pay': 'employment__monthly_income',
        'employment__monthly_pay': 'employment__monthly_income',
        'employment__name_of_employer': 'employment__name',
        'employment__position_employement_status': 'employment__status',
        'employment__position_employment_status': 'employment__status',
        'employment__previous_employer_address': 'employment__previous_employer',
        'employment__remarks': 'employment__remarks',
        'employment__verified_thru_name_contact_no': 'employment__verifier',
        'employment__verified_thru_name_contact_no_verified': 'employment__verifier',
        'employment__years_in_operation_of_employer': 'employment__employer_tenure',
        'other_business_or_remittance__address_of_business': 'remittance__address',
        'other_business_or_remittance__address_of_business_address_of_sender': 'remittance__address',
        'other_business_or_remittance__address_of_sender': 'remittance__address',
        'other_business_or_remittance__business_name': 'remittance__name',
        'other_business_or_remittance__business_name_name_of_sender': 'remittance__name',
        'other_business_or_remittance__name_of_sender': 'remittance__name',
        'other_business_or_remittance__monthly_income': 'remittance__monthly_income',
        'other_business_or_remittance__monthly_net_income_p': 'remittance__monthly_income',
        'other_business_or_remittance__monthly_net_income_remittance': 'remittance__monthly_income',
        'other_business_or_remittance__monthly_net_income_remittance_p': 'remittance__monthly_income',
        'other_business_or_remittance__nature_of_business': 'remittance__industry',
        'other_business_or_remittance__nature_of_business_source_of_income_of_sender': 'remittance__industry',
        'other_business_or_remittance__relationship_of_sender_to_credit_applicant': 'remittance__relationship',
        'other_business_or_remittance__remarks': 'remittance__remarks',
        'other_business_or_remittance__years_in_business': 'remittance__tenure',
        'other_business_or_remittance__years_in_business_years_of_remittance': 'remittance__tenure',
        'other_business_or_remittance__years_of_remittance': 'remittance__tenure',
        'spouse__address_of_employer': 'spouse__employer_address',
        'spouse__address_of_business_address_of_sender': 'spouse__employer_address',
        'spouse__contact_number_of_employer': 'spouse__employer_contact_no',
        'spouse__length_of_service': 'spouse__employment_tenure',
        'spouse__monthly_net_income_remittance_p': 'spouse__income',
        'spouse__monthly_net_pay': 'spouse__income',
        'spouse__monthly_pay': 'spouse__income',
        'spouse__nature_of_business_source_of_income_of_sender': 'spouse__income',
        'spouse__name_of_employer': 'spouse__employer_name',
        'spouse__position_employement_status': 'spouse__employment_status',
        'spouse__position_employment_status': 'spouse__employment_status',
        'spouse__previous_employer_address': 'employment__previous_employer',
        'spouse__remarks': 'spouse__remarks',
        'spouse__verified_thru_name_contact_no': 'spouse__employment_verifier',
        'spouse__years_in_operation_of_employer': 'spouse__employer_tenure'
    }
    normalized = {}
    for k, v in flatten_dict(data).items():
        k = standardize_field(k)
        if k in field_corrections and notna(v):
            normalized[field_corrections[k]] = v
    return normalized

# Income analysis
def match_len(a, b):
    'Get the length of the exact character matches.'
    for i, (a_char, b_char) in enumerate(zip(a, b)):
        if a_char != b_char:
            break
    return i+1

def extract_longest_match(query, references, min_match_len=0):
    'Extract the longest matching reference string.'
    running_max = 0
    for ref in references:
        match_length = match_len(query, ref)
        if match_length > running_max:
            running_max = match_length
            longest_match = ref
    if running_max > min_match_len:
        return longest_match

def normalize_income_analysis(parsed):
    'Normalize income analysis fields.'
    if (
        'income_data' not in parsed
        or 'income_adjudication' not in parsed['income_data']
    ):
        return {}
    data = parsed['income_data']['income_adjudication']

    # Income normalization
    income_fields = {
        'applicant',
        'business',
        'others', # Mainly remittances
        'spouse',
        'total_income'
    }
    income_corrections = {'1': 'primary', '2': 'secondary'}
    income_items = {}
    for k, v in data['income'].items():
        standardized = standardize_field(k)
        if standardized in income_fields:
            k = standardized
        elif standardized in income_corrections:
            k = income_corrections[standardized]
        else:
            k = extract_longest_match(standardized, income_fields, 3)
        if k and notna(v):
            income_items[k] = v

    # Expense normalization
    expense_fields = {
        'living',
        'education',
        'amortization',
        'elementary',
        'high_school',
        'college',
        'misc',
        'others',
        'rental',
        'transportation',
        'maintenance',
        'house',
        'helper',
        'building',
        'electric',
        'water',
        'internet',
        'load',
        'total_expenses',
    }
    expense_corrections = {'cignal': 'internet'}
    expense_items = {}
    for k, v in data['expense'].items():
        standardized = standardize_field(k)
        if standardized in expense_fields:
            k = standardized
        elif standardized in expense_corrections:
            k = expense_corrections[standardized]
        else:
            k = extract_longest_match(standardized, expense_fields, 3)
        if k and notna(v):
            expense_items[k] = v

    # Summary normalization
    summary_corrections = {
        'Gross Disposable Income': 'net_income',
        'LESS MONTHLY EXPENSES': 'total_expenses',
        'Monthly Amortization': 'monthly_amortization',
        'NET DISPOSABLE INCOME': 'net_disposable_income',
        'TOTAL EXPENSES': 'total_expenses',
        'TOTAL MONTHLY INCOME': 'gross_income'
    }
    summary = {}
    for k, v in data['summary'].items():
        if k in summary_corrections and notna(v):
            summary[summary_corrections[k]] = v

    normalized = {
        'income': income_items,
        'expense': expense_items,
        'summary': summary
    }
    return normalized
    
# Assessment normalization
def normalize_officer_assessment(parsed):
    'Normalize the credit officer assessment record.'
    if 'assessment' not in parsed:
        return {}
    data = parsed['assessment']
    field_corrections = {
        'Purpose of loan': 'loan_purpose',
        'Who will use the unit': 'unit_rider',
        'Who will pay the for the unit': 'unit_payor',
        'User with/without license': 'rider_license',
        'Cellular signal on the area': 'cell_signal_status',
        'Previous/ Current account of Zurich/ Venture': 'existing_account',
        'Motorcyle unit/ vehicle that client owned  at the time of CI': 'other_units',
        'Who will pay the for the unit': 'unit_payor'
    }
    canonical_fields = {
        'loan_purpose',
        'unit_payor',
        'existing_account',
        'other_units',
        'cell_signal_status',
        'unit_rider',
        'rider_license',
        'remarks',
        'prepared_by'
    }
    normalized = {}
    for k, v in data.items():
        k = field_corrections.get(k, k)
        if k in canonical_fields and notna(v):
            normalized[k] = v
    return normalized
    
    
# Credit data normalizer
def normalize_credit_data(parsed):
    'Normalize fields for credit report data.'
    normalized = {
        'filename': parsed['filename'],
        'last_modified': parsed['last_modified'],
        'personal_data': normalize_personal_data(parsed),
        'income_source_details': normalize_income_source_details(parsed),
        'income_analysis': normalize_income_analysis(parsed),
        'officer_assessment': normalize_officer_assessment(parsed),
    }
    return normalized