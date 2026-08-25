# Created 2023-10-21


from .utils import notna
from contextlib import suppress
import numpy as np
import os
import pandas as pd
import re


# Data loading and sectioning
def wipe_colon(df) -> pd.DataFrame:
    'Remove all colons from a DataFrame.'
    cleaned = (
        df.apply(lambda col: (
            col
            .str.replace(':', '')
            .str.strip()
            .replace('', np.nan)
        ))
    )
    return cleaned

def load_report_sheet(file) -> pd.DataFrame:
    'Load a raw credit report sheet.'
    report_sheet = pd.read_excel(file, header=None, dtype=str)
    if not report_sheet[0].any():
        report_sheet = report_sheet.drop(columns=0)
        report_sheet.columns = range(len(report_sheet.columns))
    return wipe_colon(report_sheet)
    
def locate_sections(report_sheet) -> dict:
    'Locate section bounds.'
    section_tags = iter((
        ('personal_data', 'name'),
        ('dependents', 'name of dependents|rela(?:sh|t)ionship'),
        ('character_references', 'address|contact number'),
        ('income_data', 'sources of income|adjudication'),
        ('client_reputation', '(?:informant|contact).*remarks'),
        ('other_creditors', 'creditor'),
        ('client_assets', 'encumbr'),
        ('credit_assessment', 'remarks'),
    ))
    section, tag = next(section_tags)
    tag_locations = []
    corpus = (
        report_sheet.apply(lambda row: row.str.cat(), axis=1).str.lower()
    )
    for i, row in corpus.items():
        if re.search(tag, row):
            tag_locations.append((section, i))
            try:
                section, tag = next(section_tags)
            except StopIteration:
                break
    tag_locations.append(('end', len(report_sheet)))
    sections, locations = zip(*tag_locations)
    section_bounds = {
        section: (start, end) for section, start, end 
        in zip(sections, locations, locations[1:])
    }
    return section_bounds
    

# Parser utils
def extract_rowwise_key_value_pairs(df) -> dict:
    'Extract rowwise key-value pairs.'
    data = {}
    for row in df.itertuples(index=False, name=None):
        k_v = [x for x in row if notna(x)]
        if k_v:
            k = k_v[0]
            if k in data:
                suffix = 1
                k_new = f'{k}_{suffix}'
                while k_new in data:
                    suffix += 1
                    k_new = f'{k}_{suffix}'
                k = k_new
            data[k] = k_v[1] if len(k_v) > 1 else None
    return data

def join_series_values(ser: pd.Series, sep='|') -> str:
    'Concatenate the values of a Series with a sep.'
    null_mask = ser.isna()
    if null_mask.all():
        return None
    else:
        return ser[~null_mask].str.cat(sep=sep)
        
        
# Section parsers
def parse_personal_data(report_sheet, section_bounds) -> dict:
    'Parse the personal data section.'
    section = (
        report_sheet.iloc[slice(*section_bounds['personal_data'])]
        .reset_index(drop=True)
    )
    if section.iloc[7].any():
        adjusted_index = section.index.values
        adjusted_index[7:] += 1
        section.index = adjusted_index
    left_section, right_section = (
        section.pipe(lambda df: (df.loc[:, :14], df.loc[:, 15:]))
    )
    left_exceptions = {
        5: 'type_of_residence',
        9: 'dob__age__marital_status',
        14: 'parents_name_2',
        16: 'parents_address_2',
        17: 'n_children__n_dependents',
        8: None
    }
    right_exceptions = {
        5: 'type_of_residence',
        16: 'spouse__parents_name_2'
    }
    # Left section
    personal_data = extract_rowwise_key_value_pairs(
        left_section.loc[left_section.index.difference(left_exceptions)]
    )
    # Right section
    personal_data.update({
        k if k not in personal_data else f'spouse__{k}': v 
        for k, v in extract_rowwise_key_value_pairs(
            right_section.loc[right_section.index.difference(right_exceptions)]
        ).items()
    })
    # Exceptions
    personal_data.update({
        'type_of_residence': 
            'owned' if section.loc[5, 8:11].any() 
            else 'rented' if section.loc[5, 13:15].any() 
            else 'free_use' if section.loc[5, 17:21].any() 
            else None,
        'dob': section.loc[9, 2],
        'age': section.loc[9, 9],
        'marital_status': section.loc[9, 13],
        'parents_name_2': section.loc[14, 3],
        'parents_address_2': section.loc[16, 3],
        'spouse__parents_name_2': section.loc[16, 19],
        'n_children': section.loc[17, 2],
        'n_dependents': section.loc[17, 11]
    })
    return personal_data

def parse_income_data(report_sheet, section_bounds) -> dict:
    'Parse the income data section.'
    section = (
        report_sheet
        .iloc[slice(*section_bounds['income_data'])]
        .reset_index(drop=True)
    )
    left_section, right_section = (
        section.pipe(lambda df: (df.loc[:, :14], df.loc[:, 15:]))
    )
    # Left section
    remark_mask = left_section[0].str.lower().str.contains('remark').ffill()
    remark_mask.iloc[0] = False
    remark_start = remark_mask.pipe(lambda x: (x != x.shift() & x))
    remark_groups = remark_start.where(remark_mask).cumsum()
    income_remarks = (
        left_section[4]
        .groupby(remark_groups)
        .agg(join_series_values)
        .rename({v: k for k, v in remark_groups[remark_start].items()})
    )
    left_section_cleaned = left_section.loc[~remark_mask | remark_start, [0, 4]]
    left_section_cleaned[4].update(income_remarks)
    income_source_subsections = {
        'employment': (2, 12),
        'business': (14, 21),
        'other_business_or_remittance': (23, 29),
        'spouse': (31, 40)
    }
    income_sources = {}
    for subsection_name, subsection_bounds in income_source_subsections.items():
        subsection = left_section_cleaned.loc[slice(*subsection_bounds)]
        income_sources[subsection_name] = extract_rowwise_key_value_pairs(
            subsection
        )
    # Right section
    right_section_cleaned = right_section[[15, 24]]
    adjudication_subsections = {
        'income': (2, 9),
        'expense': (11, 31),
        'summary': (32, None)
    }
    income_adjudication = {}
    for subsection_name, subsection_bounds in adjudication_subsections.items():
        subsection = right_section_cleaned.loc[slice(*subsection_bounds)]
        income_adjudication[subsection_name] = extract_rowwise_key_value_pairs(
            subsection
        )
    # Consolidation
    income_data = {
        'income_sources': income_sources,
        'income_adjudication': income_adjudication
    }
    return income_data

def parse_credit_assessment(report_sheet, section_bounds) -> dict:
    'Parse the final remarks section.'
    section = (
        report_sheet.iloc[slice(*section_bounds['credit_assessment'])]
        .reset_index(drop=True)
    )
    assessment_data = extract_rowwise_key_value_pairs(section.loc[:7, [3, 8]])
    assessment_data['remarks'] = section.loc[9, 7]
    assessment_data['prepared_by'] = section[0][lambda x: x.last_valid_index()]
    return assessment_data

def parse_subtable(section) -> dict:
    'Compress a subtable by dropping null rows and columns.'
    value_mask = section.notna()
    subtable = (
        # Drop empty columns - includes headers
        section.loc[value_mask.any(axis=1), value_mask.any(axis=0)]
        .pipe(lambda section: (
            section.iloc[1:]
            .set_axis(section.iloc[0].fillna('').values, axis='columns')
        ))
    )
    if subtable.columns.has_duplicates:
        dupe_mask = subtable.columns.duplicated(keep='first')
        dupes = subtable.columns[dupe_mask].unique()
        colnames = subtable.columns.values
        for dupe in dupes:
            dupe_matches = (colnames == dupe) & dupe_mask
            colnames[dupe_matches] = [
                f'{dupe}_{i}' for i in range(1, dupe_matches.sum()+1)
            ]
        subtable.columns = colnames
    return subtable.to_dict(orient='list')
    
def parse_subtables(report_sheet, section_bounds) -> dict:
    'Parse subtables in the credit report.'
    subtable_offsets = {
        'dependents': (0, -1),
        'character_references': (0, 0),
        'client_reputation': (0, 0),
        'other_creditors': (0, -2),
        'client_assets': (0, 0)
    }
    subtable_data = {}
    for k, offset in subtable_offsets.items():
        indices = (sum(bounds) for bounds in zip(section_bounds[k], offset))
        with suppress(KeyError):
            subtable_data[k] = (
                report_sheet.iloc[slice(*indices)]
                .pipe(parse_subtable)
            )
    return subtable_data
    
def get_file_details(fn):
    'Get basic file details.'
    details = {
        'filename': os.path.basename(fn),
        'last_modified': str(
            pd.to_datetime(os.path.getmtime(fn), unit='s') 
            + pd.Timedelta(hours=8)
        )
    }
    return details
    
    
# Report parser
def parse_credit_report(file, **kwargs):
    'Parse a single credit file.'
    report_sheet = load_report_sheet(file)
    section_bounds = locate_sections(report_sheet)
    parsed = {**kwargs}
    if isinstance(file, str):
        parsed = get_file_details(file) | parsed
    with suppress(KeyError, IndexError):
        parsed['personal_data'] = parse_personal_data(
            report_sheet, section_bounds
        )
    with suppress(KeyError, IndexError):
        parsed['income_data'] = parse_income_data(
            report_sheet, section_bounds
        )
    with suppress(KeyError, IndexError):
        parsed['assessment'] = parse_credit_assessment(
            report_sheet, section_bounds
        )
    with suppress(KeyError, IndexError):
        parsed.update(parse_subtables(report_sheet, section_bounds))
    return parsed