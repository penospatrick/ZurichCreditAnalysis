# Created 2023-10-23


from .utils import notna, isna, force_numeric, normalize_text
from .loancalc import Loan

from importlib_resources import files, as_file
import joblib
import numpy as np
import pandas as pd
import re


# Constants
NULL_VALUE = float('nan')
MIN_AGE, MAX_AGE = 0, 80
MAX_DEPENDENT_AGE = 21
FEATURE_MAP = {
    'filename': 'info__filename',
    'last_modified': 'info__last_modified',
    'personal_data': [
        ('unit_applied', 'motorcycle_model'),
        ('loan_terms', 'loan_terms'),
        ('loan_amount', 'loan_amount'),
        ('dependent_ages', 'dependent_ages'),
        ('n_dependents', 'n_dependents'),
        ('n_children', 'n_children'),
        ('age', 'age'),
        ('education', 'education'),
        ('housing_status', 'housing_status'),
        ('marital_status', 'marital_status'),
        ('spouse__education', 'spouse_education')
    ],
    'income_analysis': {
        'income': [
            ('applicant', 'employment_income'),
            ('business', 'business_income'),
            ('spouse', 'spouse_income')
        ],
        'summary': [
            ('gross_income', 'gross_income'),
            ('monthly_amortization', 'monthly_amortization')
        ]
    }
}
MODEL_FEATURES = (
    'bow__115',
    'bow__125',
    'bow__125i',
    'bow__150',
    'bow__155',
    'bow__175',
    'bow__barako',
    'bow__black',
    'bow__click',
    'bow__es',
    'bow__fazzio',
    'bow__fi',
    'bow__honda',
    'bow__i',
    'bow__kawasaki',
    'bow__mio',
    'bow__raider',
    'bow__repo',
    'bow__smash',
    'bow__suzuki',
    'bow__tmx',
    'bow__yamaha',
    'cat__housing_status',
    'cat__marital_status',
    'cat__education',
    'cat__spouse_education',
    'num__loan_amount',
    'num__loan_downpayment',
    'num__loan_term',
    'num__monthly_amortization',
    'num__age',
    'num__n_children',
    'num__n_dependents',
    'num__n_dependents_corrected',
    'num__gross_income',
    'num__employment_income',
    'num__business_income',
    'num__spouse_income',
    'num__loan_downpayment_ratio',
    'num__amort_income_ratio'
)


# Artifacts
# bow = joblib.load('artifacts/bow.pickle')
RESOURCE_LOC = files(__package__)
with as_file(RESOURCE_LOC.joinpath('artifacts/bow.pickle')) as eml:
    bow = joblib.load(eml)


# Feature processing
def extract_features(feature_map, data, features=None):
    'Extract nested features using a feature map.'
    if features is None:
        features = {}
    if isinstance(feature_map, dict):
        for parent, child in feature_map.items():
            subset = data.get(parent, {})
            extract_features(child, subset, features)
    elif isinstance(feature_map, list):
        for field_name, feature_name in feature_map:
            features[feature_name] = data.get(field_name, NULL_VALUE)
    elif isinstance(feature_map, str):
        features[feature_map] = data
    return features
    

# Personal data
def clamp_age_val(val):
    'Clamp age values.'
    return val if MIN_AGE <= val <= MAX_AGE else NULL_VALUE

def clean_dependent_ages(ages):
    'Clean an array of ages.'
    if isna(ages):
        return NULL_VALUE
    cleaned = []
    for age in ages:
        age_val = force_numeric(age)
        if isinstance(age, str) and 'mo' in age:
            age_val /= 12
        age_val = clamp_age_val(age_val)
        if notna(age_val):
            cleaned.append(age_val)
    return cleaned

def correct_dependent_counts(features):
    'Correct dependent counts.'
    dependent_ages = clean_dependent_ages(features['dependent_ages'])
    age_count = len(dependent_ages) if notna(dependent_ages) else NULL_VALUE
    dependent_counts = [
        count for count in (age_count, force_numeric(features['n_dependents']))
        if notna(count)
    ]
    n_dependents = (
        max(dependent_counts) if len(dependent_counts) else NULL_VALUE
    )
    dependent_ages_corrected =  (
        [age for age in dependent_ages if age <= MAX_DEPENDENT_AGE]
        if notna(dependent_ages) else NULL_VALUE
    )
    n_dependents_corrected = (
        len(dependent_ages_corrected) if notna(dependent_ages_corrected)
        else NULL_VALUE
    )
    corrected = {
        'n_dependents': min(n_dependents, 10),
        'n_dependents_corrected': min(n_dependents_corrected, 10)
    }
    return corrected

def encode_education(val):
    'Encode education level.'
    if isna(val):
        return -1
    val = normalize_text(val)
    if re.search(r'col|bs|vo|ma?s|tesda', val):
        return 2
    elif re.search(r'hi|h\s*s|k12', val):
        return 1
    elif 'elem' in val:
        return 0
    else:
        return -1

def encode_housing_status(val):
    'Encode housing status.'
    if isna(val):
        return -1
    status_codes = {
        'rented': 0,
        'free_use': 1,
        'owned': 2
    }
    return status_codes.get(val.lower(), -1)

def encode_marital_status(val):
    'Encode marital status.'
    if isna(val):
        return NULL_VALUE
    val = val.lower()
    first_letter = val[0]
    if 'sep' in val:
        return 1
    elif first_letter == 'm':
        return 3
    elif first_letter == 's':
        return 0
    elif first_letter in 'cl':
        return 2
    else:
        return -1

def prepare_demographics(features):
    'Prepare demographic features.'
    demographics = {
        **dict(zip(
            ('bow__' + name for name in bow.get_feature_names_out()),
            bow.transform([
                normalize_text(features['motorcycle_model'])
                if notna(features['motorcycle_model']) else ''
            ]).toarray()[0]
        )),
        'num__age': clamp_age_val(force_numeric(features['age'])),
        'num__n_children': force_numeric(features['n_children']),
        **{'num__' + k: v for k, v in correct_dependent_counts(features).items()},
        'cat__housing_status': encode_housing_status(features['housing_status']),
        'cat__marital_status': encode_marital_status(features['marital_status']),
        'cat__education': encode_education(features['education']),
        'cat__spouse_education': encode_education(features['spouse_education'])
    }
    return demographics
    
    
# Financials
def expand_loan_terms(val):
    'Split loan terms into term and downpayment.'
    if isna(val):
        return {'loan_term': NULL_VALUE, 'loan_downpayment': NULL_VALUE}
    split = val.split('/')
    downpayment = force_numeric(split[0])
    if len(split) > 1:
        term = force_numeric(split[1])
        if 'y' in split[1]:
            term = term * 12
        term = term if 0 < term <= 48 else NULL_VALUE
    else:
        term = NULL_VALUE
    loan_terms = {
        'loan_term': term,
        'loan_downpayment': downpayment
    }
    return loan_terms

def impute_amortization(features, interest=0.039881):
    'Derive missing monthly amortization from loan terms.'
    for_imputation = (
        isna(features['monthly_amortization'])
        and notna(features['loan_amount'])
        and notna(features['loan_term'])
    )
    if for_imputation:
        features['monthly_amortization'] = (
            Loan(
                features['loan_amount'],
                interest,
                features['loan_term']
            )
            .amort
    )
    return features

def add_ratio_features(features):
    'Append financial ratios features.'
    features['amort_income_ratio'] = (
        features['monthly_amortization'] / features['gross_income']
    )
    features['loan_downpayment_ratio'] = (
        features['loan_downpayment'] / features['loan_amount']
    )
    return features

def prepare_financials(features):
    'Pipeline for all financial feature processing.'
    financial_features = (
        'loan_amount', 'monthly_amortization', 'gross_income',
        'employment_income', 'business_income', 'spouse_income'
    )
    financials = {k: force_numeric(features[k]) for k in financial_features}
    if financials['gross_income'] == 0:
        financials['gross_income'] = NULL_VALUE
    financials.update(expand_loan_terms(features['loan_terms']))
    financials = {
        'num__' + k: v for k, v
        in add_ratio_features(impute_amortization(financials)).items()
    }
    return financials
    

# Feature preparation
def prepare_features(normalized):
    'Main function for feature preparation.'
    features = extract_features(FEATURE_MAP, normalized)
    demographics = prepare_demographics(features)
    financials = prepare_financials(features)
    features = demographics | financials
    features = [features[k] for k in MODEL_FEATURES]
    return features