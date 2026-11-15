# uji_irisan2.py — Bukti Irisan 2: quoting pysh == quoting bash.
# echo tidak bisa membuktikan batas argumen (ia menggabung dengan
# spasi), jadi dipakai pembantu penampil-argv yang membungkus tiap
# argumen dengan «». Baterai baris yang sama dijalankan pysh dan bash;
# keluarannya harus identik baris per baris.

import os
import subprocess
import sys
import tempfile

PYSH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pysh')
gagal = []


def cek(nama, kondisi, detail=''):
    print(('PASS' if kondisi else 'FAIL'), nama, detail)
    if not kondisi:
        gagal.append(nama)


tmp = tempfile.mkdtemp(prefix='pysh-uji2-')
helper = os.path.join(tmp, 'argv')
with open(helper, 'w') as f:
    f.write('#!/usr/bin/env python3\n'
            'import sys\n'
            'print(" ".join("«" + a + "»" for a in sys.argv[1:]))\n')
os.chmod(helper, 0o755)
H = helper

KASUS = [
    f'{H} "dua kata"',            # kutip ganda menyatukan
    f"{H} 'tiga kata tunggal'",  # kutip tunggal menyatukan
    f'{H} a"b"c',                 # fragmen menyatu
    f'{H} "ada \'kutip\'"',       # kutip tunggal di dalam ganda
    f"{H} 'ada \"kutip\"'",       # kutip ganda di dalam tunggal
    f'{H} spasi\\ kabur',         # backslash meng-escape spasi
    f'{H} "dolar \\$HOME utuh"',  # \$ di kutip ganda -> $
    f"{H} 'backslash \\ utuh'",   # \ di kutip tunggal tetap literal
    f'{H} ""',                    # argumen kosong sungguhan
    f"{H} a''b",                  # kutip kosong menyatu di tengah
    f'{H} "\\\\"',                # \\ di kutip ganda -> satu backslash
    f'{H} tanpa kutip biasa',     # regresi: perilaku Irisan 1
]

skrip = '\n'.join(KASUS) + '\nexit\n'
rp = subprocess.run([PYSH], input=skrip.encode(), capture_output=True, timeout=20)
rb = subprocess.run(['bash', '--norc'], input=skrip.encode(), capture_output=True, timeout=20)
keluar_pysh = rp.stdout.decode().splitlines()
keluar_bash = rb.stdout.decode().splitlines()
cek('jumlah baris keluaran sama', len(keluar_pysh) == len(KASUS),
    f'pysh={len(keluar_pysh)} bash={len(keluar_bash)} kasus={len(KASUS)}')
for i, (a, b) in enumerate(zip(keluar_pysh, keluar_bash)):
    cek(f'kasus {i + 1} identik bash', a == b, f'{a!r} vs {b!r}')

# Kutip tak tertutup: kesalahan, baris dilewati, shell tetap hidup.
r = subprocess.run([PYSH], input=f'{H} "belum tutup\n{H} selamat\nexit\n'.encode(),
                   capture_output=True, timeout=20)
cek('kutip tak tertutup -> pesan pysh', 'tidak tertutup' in r.stderr.decode(),
    r.stderr.decode().strip()[:60])
cek('baris rusak dilewati, shell hidup', r.stdout.decode().strip() == '«selamat»',
    r.stdout.decode().strip())

# Regresi Irisan 1
r1 = subprocess.run(['python3', os.path.join(os.path.dirname(PYSH), 'uji_irisan1.py')],
                    capture_output=True, timeout=30)
cek('regresi Irisan 1', r1.returncode == 0)

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 2 terbukti: quoting pysh identik bash pada baterai uji.')
