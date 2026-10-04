/* Run against the local API: node tests/frontend/test_app.cjs */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const source = fs.readFileSync(path.join(root, 'frontend/app.js'), 'utf8');

// A small DOM adapter exercises our form/event code; Chrome verification is separate.
class Element {
  constructor(tag = 'div') { this.tag = tag; this.children = []; this._value = ''; this.textContent = ''; this.hidden = false; this.disabled = false; }
  set value(v) { this._value = String(v); }
  get value() { return this._value; }
  append(...items) { this.children.push(...items); if (this.tag === 'select' && this.children.length === items.length) this.value = items[0].value; }
  reportValidity() { return true; }
  click() {}
}
function setup(fetcher) {
  const elements = new Map();
  const element = id => { if (!elements.has(id)) elements.set(id, new Element(['threshold','preset','compare-field','status'].includes(id) ? 'select' : 'div')); return elements.get(id); };
  const document = { getElementById: element, createElement: tag => { const e = new Element(tag); Object.defineProperty(e, 'id', {set(id) {elements.set(id, e);}}); return e; } };
  const storage = new Map();
  const context = vm.createContext({document, module: {exports: {}}, fetch: fetcher, structuredClone, Blob, URL, setTimeout, localStorage: {getItem: k => storage.get(k), setItem: (k,v) => storage.set(k,v), removeItem: k => storage.delete(k)}});
  vm.runInContext(source, context);
  return {app: context.module.exports, element, storage};
}
async function run() {
  const results = [];
  async function test(name, fn) { await fn(); results.push({name, status: 'PASS'}); }
  const localFetch = (url, options) => fetch('http://127.0.0.1:8000' + url, options);
  const ui = setup(localFetch), {app, element} = ui;
  const plain = value => JSON.parse(JSON.stringify(value));
  const choose = name => { element('preset').value = name; element('preset').onchange(); };
  const submit = () => element('form').onsubmit({preventDefault(){}});
  const schema = await localFetch('/openapi.json').then(r => r.json());
  await test('Exactly 14 schema fields render', () => assert.deepEqual(plain(app.fields.map(f => f[0])).sort(), Object.keys(schema.components.schemas.HealthProfile.properties).sort()));
  await test('All dropdown codes match API schema', () => { for (const [key,,options] of app.fields) if (options) assert.deepEqual(plain(options.map(x => x[1])).sort(), schema.components.schemas.HealthProfile.properties[key].enum.filter(v => v !== null).sort()); });
  await test('Age categories map 1 through 13', () => assert.deepEqual(plain(app.fields[0][2].map(x => x[1])), Array.from({length:13}, (_,i)=>i+1)));
  await test('Smoking lifetime meaning retained', () => assert.equal(app.fields.find(f=>f[0]==='smoking_status')[2][3][0], 'Fewer than 100 cigarettes lifetime'));
  await test('All four diabetes categories retained', () => assert.deepEqual(plain(app.fields.find(f=>f[0]==='diabetes')[2]), [['Yes',1],['Only during pregnancy',2],['No',3],['Prediabetes / borderline',4]]));
  await test('Missing controls encode null', () => assert.ok(Object.values(app.profile()).every(v=>v===null)));
  await test('Research balanced is default', () => assert.equal(element('threshold').value, 'research_balanced'));
  await test('Eight presets populate every field', () => { for (const name of Object.keys(app.presets)) {choose(name); assert.deepEqual(plain(app.profile()), plain(app.presets[name]));} });
  await test('BMI 28.5 remains unscaled', () => { element('bmi').value='28.5'; assert.equal(app.profile().bmi, 28.5); });
  await test('Low profile displays API score/classification/version', async () => {choose('Young healthy profile'); await submit(); assert.equal(element('score').textContent,'0.3%'); assert.equal(element('classification').textContent,'Lower model association'); assert.equal(JSON.parse(element('raw').textContent).profile_score,0.002504); assert.match(element('version').textContent,/1.0.0/);});
  await test('High profile displays matching raw response', async () => {choose('Older high-association profile'); await submit(); assert.equal(element('score').textContent,'83.1%'); assert.equal(JSON.parse(element('raw').textContent).profile_score,0.831258);});
  await test('Raw response toggle reveals formatted JSON', () => {element('raw-toggle').checked=true;element('raw-toggle').onchange();assert.equal(element('raw').hidden,false);assert.ok(element('raw').textContent.includes('\n  "profile_score"'));});
  await test('All five policies preserve score and change thresholds/classification correctly', async () => {choose('Young healthy profile');element('stroke_history').value='1';const rows=[];for(const t of app.thresholds){element('threshold').value=t;element('threshold').onchange();await submit();rows.push(JSON.parse(element('raw').textContent));}assert.equal(new Set(rows.map(r=>r.profile_score)).size,1);assert.equal(new Set(rows.map(r=>r.threshold)).size,5);assert.equal(new Set(rows.map(r=>r.classification)).size,2);for(const row of rows)assert.equal(row.classification,row.profile_score>=row.threshold?'elevated_model_association':'lower_model_association');});
  await test('Missing-data preset succeeds through rendered form', async () => {choose('Missing-data profile');await submit();assert.ok(JSON.parse(element('raw').textContent).profile_score>=0);});
  await test('API errors render readable sanitized response', async () => {await element('invalid-example').onclick();assert.match(element('error').textContent,/Expected QA validation error/);assert.equal(JSON.parse(element('raw').textContent).error.code,'INVALID_INPUT');});
  await test('Failed prediction cannot be recorded as success', () => {element('record').onclick();assert.match(element('saved').textContent,/Analyze the current profile first/);});
  await test('Baseline duplicates and one-field comparison uses API', async () => {choose('Young healthy profile');await submit();element('baseline').onclick();element('bmi').value='34';element('bmi').oninput();element('compare-field').value='bmi';await element('compare').onclick();assert.match(element('comparison').textContent,/Absolute score difference/);element('restore-baseline').onclick();assert.equal(element('bmi').value,'22');});
  await test('Comparison rejects multiple changed features', async () => {element('bmi').value='34';element('sex').value='1';await element('compare').onclick();assert.match(element('comparison').textContent,/Change exactly/);});
  await test('QA recording saves locally then clears', async () => {choose('Young healthy profile');await submit();element('status').value='REVIEW';element('record').onclick();assert.equal(JSON.parse(ui.storage.get('cardiorisk-qa')).length,1);element('clear-records').onclick();assert.equal(ui.storage.has('cardiorisk-qa'),false);});
  await test('CSV quoting preserves commas and quotes', () => assert.equal(app.csv([['a,b','"note"']]), '"a,b","""note"""'));
  await test('Network failure displays recovery message', async () => {const broken=setup(()=>Promise.reject(new Error('offline')));await broken.element('form').onsubmit({preventDefault(){}});assert.match(broken.element('error').textContent,/Cannot reach the local API/);assert.equal(broken.element('submit').disabled,false);});
  await test('Edited in-flight profile discards stale response', async () => {let finish;const pending=setup(()=>new Promise(resolve=>finish=resolve));const request=pending.element('form').onsubmit({preventDefault(){}});pending.element('bmi').value='34';pending.element('bmi').oninput();finish({ok:true,json:async()=>({profile_score:.8})});await request;assert.equal(pending.element('score').textContent,'—');});
  fs.writeFileSync(path.join(root,'reports/model_qa/frontend_tests.json'),JSON.stringify({passed:results.length,failed:0,tests:results},null,2));
  console.log(`${results.length} frontend JavaScript tests passed`);
  return results;
}
module.exports = {run};
if (require.main === module) run().catch(error => { console.error(error); process.exitCode=1; });
