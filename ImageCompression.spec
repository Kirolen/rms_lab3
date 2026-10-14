from pathlib import Path
import PySide6

a = Analysis(
    [str(Path(SPECPATH) / 'main.py')],
    pathex=[], binaries=[], datas=[], hiddenimports=[], hookspath=[],
    hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False,
)

# Qt uses the Windows ICU; avoid unrelated DLLs found on PATH.
a.binaries = [entry for entry in a.binaries if
    Path(entry[0]).name.lower() not in ('icuuc.dll', 'icuin.dll', 'icudt.dll', 'ucrtbase.dll')
    and not Path(entry[0]).name.lower().startswith('api-ms-win-crt-')]
qt_runtime = Path(PySide6.__file__).parent
for name in ('vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll',
             'msvcp140_1.dll', 'msvcp140_2.dll', 'msvcp140_codecvt_ids.dll', 'concrt140.dll'):
    a.binaries = [entry for entry in a.binaries if entry[0].lower() != name]
    a.binaries.append((name, str(qt_runtime / name), 'BINARY'))

pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [],
          name='ImageCompression', console=False, upx=False)
