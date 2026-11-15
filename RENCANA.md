# RENCANA — Build 4: Shell dengan Python (pysh)

Sumber: daftar build-your-own-x (fork h0c0de), seksi "Build your own `Shell`".
Seksi itu **tidak punya panduan Python** — pilihannya C/Go/Rust. Sesuai
keputusan Vero (15 Nov 2026), build ini adalah **port ke Python** dari
panduan C klasiknya:

- Stephen Brennan, *Tutorial - Write a Shell in C* (lsh), 16 Jan 2015 —
  https://brennan.io/2015/01/16/write-a-shell-in-c/ (outlink 265 di README fork)

## Bentuk port

Satu berkas eksekutabel `pysh`, Python murni pustaka standar. Struktur
mengikuti panduan persis (loop → baca baris → pecah token → eksekusi;
builtin `cd`/`help`/`exit`; proses luar via `fork`/`execvp`/`waitpid`).
Penyimpangan yang tak terhindarkan oleh bahasa dicatat di CATATAN
(mis. prompt hanya saat stdin terminal, agar mode skrip bersih).

Panduan secara eksplisit TIDAK mencakup: quoting/escaping, pipe &
redirection, globbing, dan builtin selain tiga itu. Dua yang pertama
menjadi irisan ekstensi kita — dilabeli jelas sebagai tambahan di luar
panduan, bukan bagian dari port.

## Irisan

- [x] Irisan 1 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Port setia lsh: loop REPL, parse whitespace, builtin
      cd/help/exit, launch fork+execvp+waitpid. Uji skrip: perintah luar,
      cd berpengaruh ke pwd anak, perintah tak dikenal tak membunuh shell,
      baris kosong diabaikan, exit & EOF menutup shell dengan bersih.
- [x] Irisan 2 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Ekstensi quoting: tokenizer sadar kutip tunggal/ganda dan
      backslash (ditulis sendiri, bukan shlex). Uji banding perilaku bash.
- [x] Irisan 3 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Ekstensi pipe & redirection: `|`, `>`, `>>`, `<` via
      os.pipe/os.dup2 antar anak. Uji banding perilaku bash.
- [x] Irisan 4 — selesai & terverifikasi 15 Nov 2026 (lihat CATATAN.md). Baterai interop final vs bash 5.2: skrip perintah yang
      sama dijalankan pysh dan bash, keluaran dibandingkan; tutup
      (README + CATATAN) dan terbitkan repo.

## Pagar selesai

- [x] Tiap irisan terbukti oleh skrip uji; final: baterai diff vs bash asli.
- [x] `CATATAN.md` satu halaman per irisan: konsep inti + penyimpangan port.
- [ ] Repo GitHub publik `build-your-own-shell-python` terbit & terverifikasi.
