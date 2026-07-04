import os, re

FILES = [
    'main/tramsac.py',
    'main/lich.py',
    'main/ttoan.py',
    'main/pin.py',
    'main/baotri.py',
    'main/phiensac.py',
]

NEW_IMPORT = (
    "from main.shared_theme import (\n"
    "    GROUP_STYLE, TABLE_STYLE, COMBO_STYLE, INPUT_STYLE,\n"
    "    DIALOG_STYLE, TITLE_STYLE, LBL_STYLE, btn_style, status_color, G1, G2, G_M, G_B, G_L\n"
    ")\n"
)

G1 = '#059669'
G2 = '#22c55e'

for fpath in FILES:
    with open(fpath, encoding='utf-8') as f:
        src = f.read()

    # 1) Inject import after last import line
    lines = src.splitlines()
    last_import = 0
    for i, l in enumerate(lines):
        if l.startswith('import ') or l.startswith('from '):
            last_import = i
    if NEW_IMPORT.strip() not in src:
        lines.insert(last_import + 1, NEW_IMPORT)
        src = '\n'.join(lines)

    # 2) Replace old teal color references
    src = src.replace('color: #00d4aa;', 'color: ' + G1 + ';')
    src = src.replace('"color: #00d4aa"', '"color: ' + G1 + '"')

    # 3) _group_style
    src = re.sub(
        r'def _group_style\(self\):[\s\S]*?"""[\s\S]*?"""',
        'def _group_style(self): return GROUP_STYLE',
        src
    )

    # 4) _table_style
    src = re.sub(
        r'def _table_style\(self\):[\s\S]*?"""[\s\S]*?"""',
        'def _table_style(self): return TABLE_STYLE',
        src
    )

    # 5) _combo_style
    src = re.sub(
        r'def _combo_style\(self\):[\s\S]*?"""[\s\S]*?"""',
        'def _combo_style(self): return COMBO_STYLE',
        src
    )

    # 6) _input_style (single-line return)
    src = re.sub(
        r'def _input_style\(self\):.*',
        'def _input_style(self): return INPUT_STYLE',
        src
    )

    # 7) _btn_style
    src = re.sub(
        r'def _btn_style\(self, color\):.*',
        'def _btn_style(self, color=None): return btn_style(color)',
        src
    )

    # 8) TramDialog stylesheet (dark -> light)
    OLD_D = (
        '        self.setStyleSheet("""\n'
        '            QDialog { background-color: #1e293b; color: #e2e8f0; }\n'
        '            QLabel { color: #94a3b8; }\n'
        '            QLineEdit, QComboBox {\n'
        '                background-color: #334155; color: #e2e8f0;\n'
        '                border: 1px solid #475569; border-radius: 6px;\n'
        '                padding: 6px 10px;\n'
        '            }\n'
        '            QDialogButtonBox QPushButton {\n'
        '                background-color: #00d4aa; color: #0f172a;\n'
        '                border: none; border-radius: 6px;\n'
        '                padding: 6px 18px; font-weight: bold;\n'
        '            }\n'
        '        """)'
    )
    if OLD_D in src:
        src = src.replace(OLD_D, '        self.setStyleSheet(DIALOG_STYLE)')

    # 9) Fix item color references (dark foreground colors in tables)
    src = src.replace('QColor("#ffffff")', 'QColor("#374151")')
    src = src.replace('"#ffffff"', '"#374151"')

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(src)
    print('Updated:', fpath)

print('All done.')
