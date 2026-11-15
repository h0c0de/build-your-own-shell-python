# uji_irisan1.py — Bukti Irisan 1: port setia lsh berjalan benar.
# pysh digerakkan lewat stdin tertulis (mode skrip); setiap perilaku
# kunci panduan diperiksa: perintah luar, builtin cd/help/exit,
# perintah tak dikenal, baris kosong, EOF.

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


def jalan_pysh(skrip, cwd):
    return subprocess.run([PYSH], input=skrip.encode(), cwd=cwd,
                          capture_output=True, timeout=15)


tmp = tempfile.mkdtemp(prefix='pysh-uji1-')
sub = os.path.join(tmp, 'sub')
os.makedirs(sub)

# 1. Perintah luar sederhana + urutan keluaran
r = jalan_pysh('echo halo dunia\npwd\nexit\n', tmp)
out = r.stdout.decode().splitlines()
cek('echo dari proses luar', out[0] == 'halo dunia', out[0] if out else '(kosong)')
cek('pwd = direktori awal', out[1] == tmp, out[1] if len(out) > 1 else '')
cek('exit code shell 0', r.returncode == 0, str(r.returncode))

# 2. Builtin cd mengubah direktori shell (dan diwarisi anak)
r = jalan_pysh('cd sub\npwd\ncd ..\npwd\nexit\n', tmp)
out = r.stdout.decode().splitlines()
cek('cd sub -> pwd anak ikut berubah', out == [sub, tmp], str(out))

# 3. help memuat ketiga builtin
r = jalan_pysh('help\nexit\n', tmp)
cek('help memuat cd/help/exit',
    all(k in r.stdout.decode() for k in ('cd', 'help', 'exit')))

# 4. Perintah tak dikenal: pesan kesalahan, shell tetap hidup
r = jalan_pysh('perintahngawur123\necho masih-hidup\nexit\n', tmp)
cek('tak dikenal -> stderr menyebut pysh', 'pysh:' in r.stderr.decode(),
    r.stderr.decode().strip()[:60])
cek('shell bertahan sesudah kesalahan', 'masih-hidup' in r.stdout.decode())

# 5. cd tanpa argumen: kesalahan ala panduan, shell tetap hidup
r = jalan_pysh('cd\necho ok\nexit\n', tmp)
cek('cd tanpa argumen -> pesan panduan',
    'expected argument to "cd"' in r.stderr.decode())
cek('shell bertahan sesudah cd gagal', 'ok' in r.stdout.decode())

# 6. Baris kosong & whitespace saja diabaikan
r = jalan_pysh('\n   \n\techo bersih\nexit\n', tmp)
cek('baris kosong diabaikan', r.stdout.decode().strip() == 'bersih')

# 7. EOF tanpa exit: shell menutup bersih dengan kode 0
r = jalan_pysh('echo terakhir\n', tmp)
cek('EOF menutup shell, kode 0',
    r.stdout.decode().strip() == 'terakhir' and r.returncode == 0)

# 8. Perintah sesudah exit tidak dijalankan
r = jalan_pysh('exit\necho hantu\n', tmp)
cek('exit menghentikan loop', 'hantu' not in r.stdout.decode())

# 9. Argumen banyak diteruskan utuh ke proses luar
r = jalan_pysh('echo satu dua tiga empat lima\nexit\n', tmp)
cek('banyak argumen utuh', r.stdout.decode().strip() == 'satu dua tiga empat lima')

print()
if gagal:
    print('GAGAL:', ', '.join(gagal))
    sys.exit(1)
print('SEMUA PASS — Irisan 1 terbukti.')
