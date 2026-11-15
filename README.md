# Build-Your-Own Shell — Python (pysh)

Build keempat dari seri *build-your-own-x*: sebuah **shell Unix** dalam
satu berkas Python murni pustaka standar. Seksi Shell di
https://github.com/codecrafters-io/build-your-own-x tidak mempunyai
panduan Python, jadi build ini adalah **port ke Python** dari panduan C
klasiknya:

- Stephen Brennan, *Tutorial - Write a Shell in C* (lsh), 2015 —
  https://brennan.io/2015/01/16/write-a-shell-in-c/

Port-nya setia pada struktur panduan (loop baca→parse→eksekusi, builtin
`cd`/`help`/`exit`, proses luar via `fork`/`execvp`/`waitpid`), lalu
menambahkan dua ekstensi yang secara eksplisit dihilangkan panduan:
**quoting** dan **pipe & redirection** — keduanya terbukti setara bash.

## Cara menjalankan

```sh
./pysh            # interaktif: prompt "> "
./pysh < skrip.txt
echo 'echo halo | tr a-z A-Z' | ./pysh
```

## Status verifikasi (15 Nov 2026)

| Irisan | Bukti |
|---|---|
| 1 — port setia lsh | `uji_irisan1.py` — 13/13: fork/exec/wait, builtin, cd diwarisi anak |
| 2 — quoting (ekstensi) | `uji_irisan2.py` — 16/16: 12 kasus identik bash via penampil-argv |
| 3 — pipe & redirection (ekstensi) | `uji_irisan3.py` — 9/9: keluaran + berkas identik bash |
| 4 — baterai gabungan | `uji_irisan4.py` — 8/8: stdout & pohon berkas akhir identik dengan bash 5.2 |

Jalankan: `python3 uji_irisan1.py` … `python3 uji_irisan4.py`.

## Batas yang disadari (tercatat di CATATAN.md)

- Tidak ada ekspansi: `$HOME`, `$(...)`, dan glob belum dibangun
  (tahap pemrosesan shell yang berbeda dari quoting).
- Operator yang menempel di tengah kata (`ls>out`) masih literal;
  bash memisahkannya.
- Builtin tidak berjalan di dalam pipeline (di bash ia berjalan di
  subshell); `cd` tanpa argumen mengikuti panduan (kesalahan), bukan
  bash (ke $HOME).
- Prompt hanya saat stdin terminal — seperti shell asli.

Rencana dan pagar penyelesaian: `RENCANA.md`. Catatan belajar per
irisan, termasuk temuan token bertipe di Irisan 3: `CATATAN.md`.

*Kode ditulis sebagai latihan belajar; struktur mengikuti panduan
Brennan, ekstensinya adalah karya lanjutan dari struktur itu.*
