# uji_irisan3.py — Bukti Irisan 3: pipe & redirection pysh == bash.
# Skrip yang sama dijalankan pysh dan bash di dua folder kembar;
# keluaran DAN isi berkas hasil redirection harus identik.

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


SKRIP = [
    'echo halo dunia | tr a-z A-Z',
    'printf "b\\na\\nc\\n" | sort | tr a-z A-Z',
    'echo isi-pertama > out.txt',
    'cat out.txt',
    'echo isi-kedua >> out.txt',
    'cat < out.txt',
    'cat < out.txt | tr a-z A-Z > besar.txt',
    'cat besar.txt',
    'echo "a b c" | tr " " "_"',
    'echo operator-di-kutip "|" ">"',
    'exit',
]


def jalan(shell_cmd, skrip, cwd):
    return subprocess.run(shell_cmd, input=('\n'.join(skrip) + '\n').encode(),
                          cwd=cwd, capture_output=True, timeout=30)


base = tempfile.mkdtemp(prefix='pysh-uji3-')
dir_p, dir_b = os.path.join(base, 'p'), os.path.join(base, 'b')
os.makedirs(dir_p)
os.makedirs(dir_b)
rp = jalan([PYSH], SKRIP, dir_p)
rb = jalan(['bash', '--norc'], SKRIP, dir_b)
cek('keluaran pysh identik bash', rp.stdout == rb.stdout,
    f'pysh={rp.stdout!r} bash={rb.stdout!r}')
for nama in ('out.txt', 'besar.txt'):
    a = open(os.path.join(dir_p, nama), 'rb').read()
    b = open(os.path.join(dir_b, nama), 'rb').read()
    cek(f'berkas {nama} identik', a == b, repr(a))
cek('besar.txt hasil rantai < | > benar',
    open(os.path.join(dir_p, 'besar.txt')).read() == 'ISI-PERTAMA\nISI-KEDUA\n')

# Kesalahan: sintaks rusak & berkas tak ada — shell tetap hidup.
r = subprocess.run([PYSH], input=b'echo x |\necho selamat1\ncat < tidakada.txt\necho selamat2\nexit\n',
                   capture_output=True, timeout=20)
out = r.stdout.decode()
cek('pipe menggantung -> kesalahan + shell hidup',
    'selamat1' in out and 'segmen kosong' in r.stderr.decode(), r.stderr.decode().strip()[:70])
cek('redirect dari berkas hantu -> kesalahan + shell hidup',
    'selamat2' in out and 'pysh:' in r.stderr.decode())
r = subprocess.run([PYSH], input=b'echo x >\necho selamat3\nexit\n',
                   capture_output=True, timeout=20)
cek('redirect tanpa tujuan -> kesalahan + shell hidup',
    'selamat3' in r.stdout.decode() and 'tanpa berkas tujuan' in r.stderr.decode(),
    r.stderr.decode().strip()[:70])

# Regresi
for n in ('uji_irisan1.py', 'uji_irisan2.py'):
    rr = subprocess.run(['python3', os.path.join(os.path.dirname(PYSH), n)],
                        capture_output=True, timeout=60)
    cek(f'regresi {n}', rr.returncode == 0)

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 3 terbukti: pipe & redirection pysh setara bash pada baterai uji.')
