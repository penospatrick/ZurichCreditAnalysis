const fileInput = document.querySelector('#file-input');
const dropzone = document.querySelector('#dropzone');
const results = document.querySelector('#results');
const previewBody = document.querySelector('#preview-body');
const resetButton = document.querySelector('#reset-button');
const analyzeButton = document.querySelector('#analyze-button');
const fileList = document.querySelector('#file-list');
const themeToggle = document.querySelector('.theme-toggle');
const exportButton = document.querySelector('#export-button');
const missingData = document.querySelector('#missing-data');
let selectedFiles = [];
let latestReport = null;

const requiredFields = {
  personal_data: ['name', 'present_address', 'present_address_tenure', 'contact_no', 'birthplace', 'education', 'parents_name', 'parents_address', 'date_applied', 'unit_applied', 'loan_amount', 'loan_terms', 'housing_status', 'dob', 'age', 'marital_status', 'n_children', 'n_dependents', 'dependent_ages'],
  income_analysis: ['gross_income', 'monthly_amortization'],
  officer_assessment: ['loan_purpose', 'unit_payor', 'unit_rider', 'rider_license', 'cell_signal_status', 'prepared_by', 'remarks']
};

const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();
const isValue = value => clean(value) !== '';

function allCells(workbook) {
  const rows = [];
  workbook.SheetNames.forEach(sheetName => {
    const sheet = workbook.Sheets[sheetName];
    XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' }).forEach(row => {
      row.forEach((value, index) => {
        if (isValue(value)) rows.push({ field: clean(value), value: clean(row[index + 1]) || 'Detected', sheet: sheetName });
      });
    });
  });
  return rows;
}

function assess(rows, workbook) {
  const values = new Map(rows.map(row => [row.field.toLowerCase().replace(/[^a-z0-9]+/g, '_'), row.value]));
  const missing = Object.fromEntries(Object.entries(requiredFields).map(([section, fields]) => [section, fields.filter(field => !isValue(values.get(field)))]));
  Object.keys(missing).forEach(section => { if (!missing[section].length) delete missing[section]; });
  const missingCount = Object.values(missing).reduce((total, fields) => total + fields.length, 0);
  return { score: null, rating: 'Backend analysis required', detected: rows.length - missingCount, sheets: workbook.SheetNames.length, missing, missingCount };
}

function render(file, workbook) {
  const rows = allCells(workbook).slice(0, 120);
  const assessment = assess(rows, workbook);
  latestReport = { file: file.name, sheets: workbook.SheetNames, fields: rows, assessment };
  document.querySelector('#file-name').textContent = file.name;
  document.querySelector('#score').textContent = 'N/A';
  document.querySelector('#rating').textContent = assessment.rating;
  document.querySelector('#fields').textContent = assessment.detected;
  document.querySelector('#sheets').textContent = assessment.sheets;
  document.querySelector('#assessment-title').textContent = assessment.rating;
  document.querySelector('#assessment-copy').textContent = `${rows.length} populated workbook entries were found. Run the Streamlit backend for the trained LightGBM score.`;
  document.querySelector('#progress-bar').style.width = '0%';
  missingData.innerHTML = assessment.missingCount ? `<strong>Missing essential data (${assessment.missingCount})</strong><ul>${Object.entries(assessment.missing).flatMap(([section, fields]) => fields.map(field => `<li>${escapeHtml(section)}: ${escapeHtml(field)}</li>`)).join('')}</ul>` : '<strong>All essential fields detected</strong>';
  document.querySelector('#assessment-list').innerHTML = [
    `<div><strong>${assessment.missingCount < 5 ? '✓' : '!'}</strong> ${assessment.missingCount < 5 ? 'Enough data for backend scoring' : 'Too many missing fields for scoring'}</div>`,
    `<div><strong>${rows.length ? '✓' : '!'}</strong> Workbook contains readable data</div>`,
    `<div><strong>i</strong> Review the extracted values before making a lending decision</div>`
  ].join('');
  previewBody.innerHTML = rows.length ? rows.map(row => `<tr><td>${escapeHtml(row.field)}</td><td>${escapeHtml(row.value)}</td></tr>`).join('') : '<tr><td colspan="2">No populated cells found.</td></tr>';
  results.hidden = false;
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, character => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[character]));
}

async function processFile(file) {
  if (!file || !/\.xlsx?$/i.test(file.name)) {
    alert('Please choose an Excel .xlsx or .xls credit report.');
    return;
  }
  try {
    const buffer = await file.arrayBuffer();
    const workbook = XLSX.read(buffer, { type: 'array' });
    render(file, workbook);
  } catch (error) {
    alert('This workbook could not be read. Please verify that it is a valid .xlsx file.');
  }
}

function updateFileList() {
  fileList.textContent = selectedFiles.map(file => file.name).join(', ');
  analyzeButton.disabled = selectedFiles.length === 0;
}

fileInput.addEventListener('change', event => {
  selectedFiles = [...event.target.files];
  updateFileList();
});
analyzeButton.addEventListener('click', () => processFile(selectedFiles[0]));
dropzone.addEventListener('dragover', event => { event.preventDefault(); dropzone.classList.add('dragging'); });
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragging'));
dropzone.addEventListener('drop', event => { event.preventDefault(); dropzone.classList.remove('dragging'); selectedFiles = [...event.dataTransfer.files]; updateFileList(); });
dropzone.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') fileInput.click(); });
resetButton.addEventListener('click', () => { fileInput.value = ''; selectedFiles = []; updateFileList(); results.hidden = true; window.scrollTo({ top: 0, behavior: 'smooth' }); });
exportButton.addEventListener('click', () => {
  if (!latestReport) return;
  const blob = new Blob([JSON.stringify(latestReport, null, 2)], { type: 'application/json' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${latestReport.file.replace(/\.[^.]+$/, '')}_validated.json`;
  link.click();
  URL.revokeObjectURL(link.href);
});
themeToggle.addEventListener('click', () => { document.body.classList.toggle('dark'); themeToggle.textContent = document.body.classList.contains('dark') ? '☀' : '◐'; });
