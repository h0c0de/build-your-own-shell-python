# CATATAN — Build 4: Shell dengan Python (pysh)

Port dari *Tutorial - Write a Shell in C* (lsh) oleh Stephen Brennan
(2015): https://brennan.io/2015/01/16/write-a-shell-in-c/
Satu halaman per irisan: konsep inti + penyimpangan port.

## Irisan 1 — Port setia lsh (15 Nov 2026, terverifikasi)

**Yang dibangun:** seluruh isi panduan dalam satu berkas `pysh` — loop baca→parse→eksekusi, `split_line` whitespace murni (padanan `strtok`), builtin `cd`/`help`/`exit` dalam tabel dispatch (padanan array pointer fungsi C), dan `launch` dengan `os.fork()` → `os.execvp()` di anak → `os.waitpid(pid, WUNTRACED)` di induk sampai anak keluar/terbunuh sinyal.

**Bukti jalan:** `uji_irisan1.py` — 13/13 PASS pada jalan pertama: echo/pwd dari proses luar; `cd sub` terbukti mengubah direktori yang diwarisi proses anak (pwd ikut pindah, lalu kembali); help memuat ketiga builtin; perintah tak dikenal menghasilkan pesan `pysh: ...` di stderr tanpa membunuh shell; `cd` tanpa argumen memberi pesan kesalahan persis panduan; baris kosong diabaikan; EOF (tanpa `exit`) menutup shell dengan kode 0; perintah sesudah `exit` tidak dijalankan.

**Konsep inti:**
- Hanya ada satu cara memulai proses baru di Unix: proses yang sudah ada menggandakan diri (`fork`), lalu sang salinan mengganti programnya (`exec`). Shell tidak "menjalankan" program — ia melahirkan anak yang berubah menjadi program itu, lalu menunggu (`waitpid`).
- Builtin ada karena terpaksa: direktori kerja adalah milik proses, jadi `cd` eksternal hanya akan mengubah direktori dirinya sendiri lalu mati sia-sia. `cd`, `exit`, dan kawan-kawannya harus hidup di dalam proses shell.
- Anak yang gagal `exec` harus keluar dengan `os._exit()`, bukan `sys.exit()` — supaya tidak menjalankan cleanup/penyangga milik induk yang ikut terduplikasi oleh fork.

**Penyimpangan port (sadar, tercatat):**
- Prompt `> ` hanya saat stdin terminal. Panduan mencetaknya selalu; dalam mode pipa/skrip itu mengotori keluaran dan membuat uji diff mustahil. Shell asli (bash) berperilaku sama dengan pilihan kami.
- Seluruh tarian `malloc`/`realloc` panduan (buffer baris dan buffer token yang tumbuh manual) lenyap — di Python keduanya operasi bawaan bahasa. Justru di sini nilai port-nya terlihat: yang tersisa adalah syscall-nya saja, dan itu memang inti shell.
- `readline()` Python mengembalikan `''` pada EOF, padanan rapi dari versi `getline()` panduan yang keluar-sukses saat EOF.

## Irisan 2 — Ekstensi quoting (15 Nov 2026, terverifikasi)

**Yang dibangun:** ekstensi pertama di luar panduan (panduan secara eksplisit menghilangkan quoting) — `split_line` ditulis ulang sebagai tokenizer mesin-keadaan tiga modus (di luar kutip / kutip tunggal / kutip ganda), ditulis tangan, bukan `shlex`. Aturannya mengikuti bash untuk subset ini: di luar kutip backslash meng-escape satu karakter apa pun; kutip tunggal literal total tanpa escape; di dalam kutip ganda backslash hanya bekerja di depan `$`, `` ` ``, `"`, `\`, newline.

**Bukti jalan:** `uji_irisan2.py` — 16/16 PASS. echo tidak dipakai sebagai bukti (ia menggabungkan argumen dengan spasi, jadi batas argumen tak terlihat); dipakai pembantu penampil-argv yang membungkus tiap argumen dengan «». 12 kasus — kutip menyatukan kata, fragmen bersebelahan menyatu (`a"b"c` → «abc»), kutip bersarang silang, escape spasi, `\$` di kutip ganda, backslash literal di kutip tunggal, argumen kosong sungguhan (`""` → «»), kutip kosong di tengah kata — **identik baris-per-baris dengan bash asli**. Kutip tak tertutup: pesan kesalahan, baris dilewati, shell tetap hidup. Regresi Irisan 1 hijau.

**Konsep inti:**
- Token bukan sekadar "potongan antar-spasi": satu token bisa tersusun dari banyak fragmen (mentah + terkutip) yang menyatu, dan token kosong pun token yang sah — karena itu tokenizer butuh penanda "token sedang berjalan", bukan sekadar daftar hasil split.
- Tiga modus kutip adalah tiga bahasa mini yang berbeda di dalam satu baris perintah; kesalahan klasik shell (dan sumber bug skrip) lahir dari mengira ketiganya sama.
- Batas jujur irisan ini: ekspansi (`$HOME`, `$(...)`, glob) adalah tahap pemrosesan shell yang *berbeda* dari quoting dan belum dibangun — di pysh, `$HOME` di dalam kutip ganda tetap teks mentah, berbeda dari bash. Tercatat, bukan disembunyikan.

## Irisan 3 — Ekstensi pipe & redirection (15 Nov 2026, terverifikasi)

**Yang dibangun:** ekstensi kedua di luar panduan — operator `|`, `<`, `>`, `>>` dikenali tokenizer (hanya di luar kutip dan di awal token), parser `parse_pipeline` memecah baris menjadi segmen + redirection per segmen, dan `launch_pipeline` menjalankan satu anak per segmen yang dirantai `os.pipe()`/`os.dup2()`; redirection berkas dibuka di dalam anak sebelum `exec`.

**Bukti jalan:** `uji_irisan3.py` — 9/9 PASS sesudah satu perbaikan (lihat temuan), regresi Irisan 1–2 hijau. Skrip yang sama di pysh dan bash dalam folder kembar: keluaran identik byte-per-byte, dan berkas hasil redirection (`out.txt`, `besar.txt` dari rantai `cat < in | tr > out`) identik. Kesalahan sintaks (pipe menggantung, redirect tanpa tujuan, berkas sumber hantu) semuanya dilaporkan tanpa membunuh shell.

**Temuan — token harus membawa tipenya:** jalan pertama GAGAL pada kasus `echo operator-di-kutip "|" ">"`: sesudah tokenisasi, string `"|"` hasil kutip tidak bisa dibedakan dari operator `|` sungguhan, jadi parser membelahnya sebagai pipeline dan barisnya gugur. Perbaikannya bukan tambal-sulam di parser, melainkan mengubah representasi: tokenizer kini mengembalikan token bertipe — `("kata", teks)` vs `("op", simbol)` — dan hanya `op` yang boleh menjadi operator. Ini pelajaran umum shell: informasi "apakah teks ini hasil kutip" hilang tak terpulihkan sesudah tokenisasi datar, jadi ia harus dibawa sejak lahirnya token. (Kasus uji yang menangkapnya kini permanen di baterai.)

**Konsep inti:**
- Pipe bukan fitur program: `tr` tidak tahu ia membaca dari pipa. Shell hanya mengatur ulang *deskriptor berkas* anak sebelum exec — stdin/stdout adalah colokan, dan shell-lah tukang coloknya.
- Induk wajib menutup ujung pipanya sendiri; satu ujung-tulis yang tertinggal terbuka membuat pembaca di hilir tidak pernah melihat EOF dan pipeline menggantung selamanya.
- Batas sadar irisan ini: operator yang menempel di tengah kata (`ls>out`) masih diperlakukan literal (bash memisahkannya); builtin di dalam pipeline tidak berjalan (segmen pipeline selalu program luar; di bash builtin berjalan di subshell).

## Irisan 4 — Baterai interop vs bash + tutup (15 Nov 2026, terverifikasi — build tuntas)

**Yang dibangun:** baterai final gabungan — satu skrip 18 baris yang memakai semua fitur sekaligus (cd antar-direktori, quoting campuran, pipe dua dan tiga segmen, redirect `>`/`>>`/`<`, perintah tak dikenal di tengah jalan, `exit` dengan baris hantu sesudahnya) dijalankan pysh dan bash 5.2 di dua folder kembar yang disiapkan identik.

**Bukti jalan:** `uji_irisan4.py` — 8/8 PASS sesudah satu koreksi *pada ujinya*: stdout identik byte-per-byte (path folder kembar dinormalkan dulu — `pwd` memang mencetak path yang berbeda di kedua folder, itu artefak uji, bukan perbedaan shell), pohon berkas akhir identik (`hasil.txt`, `sub/sub.txt` beserta isinya), kode keluar 0 di keduanya, regresi Irisan 1–3 hijau dalam satu larian.

**Konsep inti penutup:**
- Sesudah empat irisan, anatomi shell terbukti kecil: baca baris, tokenisasi sadar-kutip, pecah pipeline, lahirkan anak per segmen sambil mengatur colokan fd-nya, tunggu. Bash yang sesungguhnya menambahkan di atas fondasi ini: ekspansi, job control, history, pemrograman lengkap — fitur, bukan sihir tambahan.
- Port lintas bahasa menunjukkan hal yang tidak ditunjukkan port sejenis: dari lsh versi C, yang lenyap di Python hanyalah manajemen memori manual; syscall dan struktur datanya utuh kata-per-kata. Inti sebuah shell memang bukan bahasanya.
- Pola lintas-empat-build konsisten: setiap build menjadi "sungguhan" tepat pada titik ia diadu melawan implementasi aslinya — curl untuk web server, redis-py untuk Redis, git asli untuk wyag, dan bash untuk pysh.
