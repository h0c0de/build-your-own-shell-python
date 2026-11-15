# uji_irisan4.py — Bukti final Irisan 4: baterai gabungan vs bash.
# Satu skrip panjang yang memakai SEMUA fitur (builtin cd, quoting,
# pipe, redirect < > >>, perintah tak dikenal, exit) dijalankan pysh
# dan bash di dua folder kembar yang disiapkan identik. Vonis:
# stdout identik byte-per-byte DAN pohon berkas akhir identik.

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


BATERAI = [
    'pwd',
    'cat data.txt',
    'echo "Baris Satu" > hasil.txt',
    "echo 'baris dua' >> hasil.txt",
    'cat hasil.txt',
    'cat < hasil.txt | tr a-z A-Z',
    'printf "c\\na\\nb\\na\\n" | sort | uniq -c',
    'cd sub',
    'pwd',
    'echo "dari sub" > sub.txt',
    'cat sub.txt | tr a-z A-Z',
    'cd ..',
    'pwd',
    'echo selesai "|" ">" bukan-operator',
    'perintahhantu999',
    'echo tetap-hidup | tr a-z A-Z',
    'exit',
    'echo hantu-sesudah-exit',
]


def siapkan(d):
    os.makedirs(os.path.join(d, 'sub'))
    with open(os.path.join(d, 'data.txt'), 'w') as f:
        f.write('data awal\n')


def pohon(d):
    hasil = {}
    for akar, _, berkas in os.walk(d):
        for b in berkas:
            p = os.path.join(akar, b)
            hasil[os.path.relpath(p, d)] = open(p, 'rb').read()
    return hasil


base = tempfile.mkdtemp(prefix='pysh-uji4-')
dir_p, dir_b = os.path.join(base, 'p'), os.path.join(base, 'b')
os.makedirs(dir_p)
os.makedirs(dir_b)
siapkan(dir_p)
siapkan(dir_b)
skrip = ('\n'.join(BATERAI) + '\n').encode()
rp = subprocess.run([PYSH], input=skrip, cwd=dir_p, capture_output=True, timeout=30)
rb = subprocess.run(['bash', '--norc'], input=skrip, cwd=dir_b, capture_output=True, timeout=30)

# pwd mencetak path folder kembar yang memang berbeda (/p vs /b);
# normalkan path folder masing-masing sebelum membandingkan.
out_p = rp.stdout.replace(dir_p.encode(), b'<DIR>')
out_b = rb.stdout.replace(dir_b.encode(), b'<DIR>')
cek('stdout pysh identik bash (byte-per-byte, path dinormalkan)',
    out_p == out_b,
    '' if out_p == out_b else f'pysh={out_p!r}\nbash={out_b!r}')
cek('pohon berkas akhir identik', pohon(dir_p) == pohon(dir_b),
    str(sorted(pohon(dir_p))))
cek('kode keluar keduanya 0', rp.returncode == 0 and rb.returncode == 0,
    f'pysh={rp.returncode} bash={rb.returncode}')
cek('perintah hantu: pysh melapor di stderr & lanjut',
    'pysh:' in rp.stderr.decode() and 'TETAP-HIDUP' in rp.stdout.decode())
cek('baris sesudah exit tidak jalan di keduanya',
    'hantu-sesudah-exit' not in rp.stdout.decode()
    and 'hantu-sesudah-exit' not in rb.stdout.decode())

for n in ('uji_irisan1.py', 'uji_irisan2.py', 'uji_irisan3.py'):
    rr = subprocess.run(['python3', os.path.join(os.path.dirname(PYSH), n)],
                        capture_output=True, timeout=90)
    cek(f'regresi {n}', rr.returncode == 0)

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 4 terbukti: pysh setara bash pada baterai gabungan.')
