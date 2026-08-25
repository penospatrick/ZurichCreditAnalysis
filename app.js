const fileInput = document.querySelector('#file-input');
const dropzone = document.querySelector('#dropzone');
const results = document.querySelector('#results');
const previewBody = document.querySelector('#preview-body');
const resetButton = document.querySelector('#reset-button');

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
  const labels = rows.map(row => row.field.toLowerCase());
  const keywords = ['name', 'income', 'address', 'loan', 'credit', 'employment', 'residence', 'remarks'];
  const detected = keywords.filter(keyword => labels.some(label => label.includes(keyword))).length;
  const score = Math.min(100, Math.max(1, 35 + detected * 8 + Math.min(25, rows.length / 4)));
  const rounded = Math.round(score);
  const rating = rounded >= 75 ? 'Strong profile' : rounded >= 60 ? 'Good profile' : rounded >= 40 ? 'Review recommended' : 'More information needed';
  return { score: rounded, rating, detected, sheets: workbook.SheetNames.length };
}

function render(file, workbook) {
  const rows = allCells(workbook).slice(0, 120);
  const assessment = assess(rows, workbook);
  document.querySelector('#file-name').textContent = file.name;
  document.querySelector('#score').textContent = assessment.score;
  document.querySelector('#rating').textContent = assessment.rating;
  document.querySelector('#fields').textContent = assessment.detected;
  document.querySelector('#sheets').textContent = assessment.sheets;
  document.querySelector('#assessment-title').textContent = assessment.rating;
  document.querySelector('#assessment-copy').textContent = `${rows.length} populated workbook entries were found across ${assessment.sheets} sheet${assessment.sheets === 1 ? '' : 's'}.`;
  document.querySelector('#progress-bar').style.width = `${assessment.score}%`;
  document.querySelector('#assessment-list').innerHTML = [
    `<div><strong>${assessment.detected >= 5 ? '✓' : '!'}</strong> Core report sections detected</div>`,
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
  if (!file || !file.name.toLowerCase().endsWith('.xlsx')) {
    alert('Please choose an Excel .xlsx credit report.');
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

fileInput.addEventListener('change', event => processFile(event.target.files[0]));
dropzone.addEventListener('dragover', event => { event.preventDefault(); dropzone.classList.add('dragging'); });
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragging'));
dropzone.addEventListener('drop', event => { event.preventDefault(); dropzone.classList.remove('dragging'); processFile(event.dataTransfer.files[0]); });
resetButton.addEventListener('click', () => { fileInput.value = ''; results.hidden = true; window.scrollTo({ top: 0, behavior: 'smooth' }); });
