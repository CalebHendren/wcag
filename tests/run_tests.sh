#!/usr/bin/env bash
# Smoke tests for the bundled scripts. Runs in CI and before a release.
set -uo pipefail
# contrast.py exits 1 when a pair fails, which is intentional, so pipelines are
# checked by their output rather than by their exit status.
set +e
cd "$(dirname "$0")/.."
fail=0
check() { if [ "$1" = "$2" ]; then echo "  ok   $3"; else echo "FAIL   $3 (got '$1', wanted '$2')"; fail=1; fi; }

echo "contrast.py"
r=$(python3 scripts/contrast.py '#000000' '#ffffff' --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["results"][0]["ratio"])')
check "$r" "21.0" "black on white is 21:1"
r=$(python3 scripts/contrast.py '#767676' '#ffffff' --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["results"][0]["sc_1_4_3_aa_text"]["passes"])')
check "$r" "True" "#767676 on white passes AA at 4.54:1"
r=$(python3 scripts/contrast.py '#777777' '#ffffff' --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["results"][0]["sc_1_4_3_aa_text"]["passes"])')
check "$r" "False" "#777777 on white fails AA"
r=$(python3 scripts/contrast.py '#ffffff' '#ffffff' --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["results"][0]["ratio"])')
check "$r" "1.0" "white on white is 1:1"
r=$(python3 scripts/contrast.py '#949494' '#ffffff' --size 24px --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["results"][0]["large_text"])')
check "$r" "True" "24px counts as large text"

echo "html_audit.py"
r=$(python3 scripts/html_audit.py tests/fixtures/clean-page.html --json | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["findings"]))')
check "$r" "0" "clean page produces no false positives"
r=$(python3 scripts/html_audit.py tests/fixtures/failing-page.html --json | python3 -c 'import json,sys;d=json.load(sys.stdin);print(len(d["findings"])>20)')
check "$r" "True" "failing page produces findings"
r=$(python3 scripts/html_audit.py tests/fixtures/failing-page.html --json | python3 -c '
import json,sys
found={f["sc"] for f in json.load(sys.stdin)["findings"]}
want={"1.1.1","1.3.1","1.4.4","2.1.1","2.4.2","2.4.4","3.1.1","4.1.2"}
print(want.issubset(found))')
check "$r" "True" "failing page covers the expected criteria"

echo "pdf_audit.py"
if python3 -c 'import pypdf' 2>/dev/null; then
  r=$(python3 scripts/pdf_audit.py tests/fixtures/tagged-with-defects.pdf --json | python3 -c '
import json,sys
d=json.load(sys.stdin)
found={f["sc"] for f in d["findings"]}
print(d["stats"]["tagged"] and d["stats"]["figures_without_alt"]==1 and "1.3.1" in found)')
  check "$r" "True" "tagged PDF defects are detected"
  r=$(python3 scripts/pdf_audit.py tests/fixtures/tagged-with-defects.pdf --dump-tags | tr -d ' \n')
  check "$r" "DocumentH1PH3FigureTableTRTDTD" "structure tree is walked in document order"
  r=$(python3 scripts/pdf_audit.py tests/fixtures/tagged-with-defects.pdf --json | python3 -c "
import json,sys
print('untagged_content' in json.load(sys.stdin)['stats'])
")
  check "$r" "True" "untagged content is counted in the stats"

  r=$(python3 scripts/pdf_audit.py tests/fixtures/text-hidden-in-artifacts.pdf --json | python3 -c "
import json,sys
d = json.load(sys.stdin)
print(any('inside artifacts' in f['issue'] for f in d['findings']))
")
  check "$r" "True" "text hidden inside artifacts is reported"
  r=$(python3 scripts/pdf_audit.py tests/fixtures/tagged-with-defects.pdf --json | python3 -c "
import json,sys
d = json.load(sys.stdin)
print(any('inside artifacts' in f['issue'] for f in d['findings']))
")
  check "$r" "False" "a tagged file with nothing artifacted stays quiet"
  r=$(python3 scripts/pdf_audit.py tests/fixtures/table-associated.pdf --json | python3 -c "
import json,sys
print(json.load(sys.stdin)['stats']['artifact_text_share'])
")
  check "$r" "0.0" "text outside all marked content is not counted as artifacted"

  r=$(python3 scripts/pdf_audit.py tests/fixtures/table-unassociated.pdf --json | python3 -c "
import json,sys
d = json.load(sys.stdin)
issues = ' '.join(f['issue'] for f in d['findings'])
print('carry /Scope' in issues and 'fewer cells' in issues)
")
  check "$r" "True" "unassociated table headers and undeclared spans are both reported"
  r=$(python3 scripts/pdf_audit.py tests/fixtures/table-associated.pdf --json | python3 -c "
import json,sys
d = json.load(sys.stdin)
issues = ' '.join(f['issue'] for f in d['findings'])
print('carry /Scope' not in issues and 'fewer cells' not in issues)
")
  check "$r" "True" "a correctly scoped, regular table reports no table findings"
  r=$(python3 scripts/pdf_audit.py tests/fixtures/table-associated.pdf --json | python3 -c "
import json,sys
s = json.load(sys.stdin)['stats']
print(s['header_cells'] == 7 and s['header_cells_with_scope'] == 7)
")
  check "$r" "True" "scope is read from the /A attribute dictionary, not from element keys"
else
  echo "  skip pypdf not installed"
fi

echo "axe_scan.py"
r=$(python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('a', 'scripts/axe_scan.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
cases = [(['wcag111'], '1.1.1'), (['wcag1410'], '1.4.10'), (['wcag258'], '2.5.8'),
         (['wcag2411'], '2.4.11'), (['best-practice'], None)]
print(all(m.criterion_from_tags(t) == w for t, w in cases))
")
check "$r" "True" "axe tags map to criterion numbers, including two-digit ones"

echo "office_audit.py"
for clean in report-clean.docx deck-clean.pptx workbook-clean.xlsx; do
  r=$(python3 scripts/office_audit.py "tests/fixtures/office/$clean" --json |
      python3 -c 'import json,sys;print(len(json.load(sys.stdin)["findings"]))')
  check "$r" "0" "$clean produces no false positives"
done
r=$(python3 scripts/office_audit.py tests/fixtures/office/report-defects.docx --json |
  python3 -c '
import json,sys
found = {f["sc"] for f in json.load(sys.stdin)["findings"]}
print({"1.1.1", "1.3.1", "1.3.2", "2.4.2", "2.4.4", "3.1.1"}.issubset(found))')
check "$r" "True" "the defective Word file covers the expected criteria"
r=$(python3 scripts/office_audit.py tests/fixtures/office/deck-defects.pptx --json |
  python3 -c '
import json,sys
d = json.load(sys.stdin)
issues = " ".join(f["issue"] for f in d["findings"])
print("slide(s) have no title" in issues and "free-floating boxes" in issues)')
check "$r" "True" "an untitled slide and loose text boxes are both reported"
r=$(python3 scripts/office_audit.py tests/fixtures/office/deck-clean.pptx --json |
  python3 -c '
import json,sys
print(json.load(sys.stdin)["stats"]["images_and_shapes"])')
check "$r" "1" "alt text is asked of pictures, not of every text box"
r=$(python3 scripts/office_audit.py tests/fixtures/office/report-defects.docx --json |
  python3 -c '
import json,sys
values = {f["agent_fix"] for f in json.load(sys.stdin)["findings"]}
print(values <= {"direct", "app", "recreate", "owner", "design"} and "direct" in values)')
check "$r" "True" "every finding says who can close it"
printf '\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1padding' > /tmp/wcag-test-encrypted.docx
python3 scripts/office_audit.py /tmp/wcag-test-encrypted.docx --json > /dev/null 2>&1
check "$?" "2" "an encrypted file exits 2 rather than reporting a clean document"
rm -f /tmp/wcag-test-encrypted.docx

echo "office_remediate.py"
rm -rf /tmp/wcag-test-office && mkdir -p /tmp/wcag-test-office
cp tests/fixtures/office/report-defects.docx /tmp/wcag-test-office/in.docx
echo '{"chart1.png": "Column chart. Uptake rose from 40 to 62 percent."}' \
  > /tmp/wcag-test-office/alt.json
python3 scripts/office_remediate.py /tmp/wcag-test-office/in.docx \
  --title auto --language en-GB --table-headers \
  --alt-text /tmp/wcag-test-office/alt.json > /dev/null
check "$?" "0" "a pass whose fixes all apply exits 0"
r=$(python3 -c '
import hashlib
print(hashlib.sha256(open("/tmp/wcag-test-office/in.docx","rb").read()).hexdigest()
      == hashlib.sha256(open("tests/fixtures/office/report-defects.docx","rb").read()
      ).hexdigest())')
check "$r" "True" "the original file is not modified"
r=$(python3 scripts/office_audit.py /tmp/wcag-test-office/in-remediated.docx --json |
  python3 -c '
import json,sys
d = json.load(sys.stdin)
s = d["stats"]
issues = " ".join(f["issue"] for f in d["findings"])
print(s["language"] == "en-GB" and s["title"] == "Quarterly Accessibility Report"
      and s["without_alt_text"] == 0 and "declare no header row" not in issues)')
check "$r" "True" "the four derivable fixes land and survive a re-audit"
r=$(python3 -c '
import zipfile, xml.etree.ElementTree as ET
a = zipfile.ZipFile("tests/fixtures/office/report-defects.docx")
b = zipfile.ZipFile("/tmp/wcag-test-office/in-remediated.docx")
changed = [n for n in a.namelist() if a.read(n) != b.read(n)]
for n in b.namelist():
    ET.fromstring(b.read(n))
print(a.namelist() == b.namelist() and sorted(changed) == [
    "docProps/core.xml", "word/document.xml", "word/styles.xml"])')
check "$r" "True" "only the parts that carry a fix are rewritten, and all stay well formed"
echo '{"no-such-shape": "text"}' > /tmp/wcag-test-office/missing.json
python3 scripts/office_remediate.py /tmp/wcag-test-office/in.docx \
  --alt-text /tmp/wcag-test-office/missing.json --dry-run > /dev/null
check "$?" "1" "a failed fix exits 1, which is the signal to consider recreating"
python3 scripts/office_remediate.py tests/fixtures/office/workbook-defects.xlsx \
  --language en-GB --dry-run > /dev/null
check "$?" "1" "a fix the format cannot carry is reported as failed, not as applied"
rm -rf /tmp/wcag-test-office

echo "build_sc_index.py"
python3 scripts/build_sc_index.py --check > /dev/null
check "$?" "0" "the criteria index matches its generator"

echo "report.py"
python3 scripts/html_audit.py tests/fixtures/failing-page.html --json > /tmp/wcag-test-findings.json
r=$(python3 scripts/report.py /tmp/wcag-test-findings.json --title Test --level AA | grep -c 'Not tested')
check "$([ "$r" -gt 0 ] && echo True || echo False)" "True" "untested criteria are marked, not assumed to pass"
r=$(python3 scripts/report.py /tmp/wcag-test-findings.json --title Test --level AA | grep -c 'does not conform')
check "$([ "$r" -eq 1 ] && echo True || echo False)" "True" "conformance position is stated once"
r=$(python3 scripts/report.py /tmp/wcag-test-findings.json --format vpat --title Test | grep -c 'Not Evaluated')
check "$([ "$r" -gt 0 ] && echo True || echo False)" "True" "VPAT marks unevaluated rows"
python3 scripts/office_audit.py tests/fixtures/office/report-defects.docx --json \
  > /tmp/wcag-test-office-findings.json
r=$(python3 scripts/report.py /tmp/wcag-test-office-findings.json --title Test --level AA |
  grep -c 'What an agent cannot fix')
check "$([ "$r" -eq 1 ] && echo True || echo False)" "True" \
  "the report says which findings an agent cannot close"
rm -f /tmp/wcag-test-office-findings.json

echo "selfcheck.py"
python3 scripts/selfcheck.py --quiet && echo "  ok   repository self-check"

rm -f /tmp/wcag-test-findings.json
if [ "$fail" -ne 0 ]; then echo; echo "Some tests failed."; exit 1; fi
echo; echo "All tests passed."
