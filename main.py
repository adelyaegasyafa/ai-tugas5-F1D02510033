import json

# 1. Membaca file JSON aturan
file_json = open("kb_sampah.json", "r", encoding="utf-8")
data = json.load(file_json)
file_json.close()

judul = data["judul"]
batas = data["batas"]
sumber = data["sumber"]
daftar_aturan = data["aturan"]

# 2. Mencari fakta dasar (fakta yang tidak pernah menjadi hasil "maka" di aturan manapun)
semua_hasil = []
for aturan in daftar_aturan:
  semua_hasil.append(aturan["maka"])

fakta_ditanyakan = []
for aturan in daftar_aturan:
  for syarat in aturan["jika"]:
    if syarat not in semua_hasil and syarat not in fakta_ditanyakan:
      fakta_ditanyakan.append(syarat)

# 3. Bertanya ke user (y/t) dan simpan jawaban "y" ke dalam list memori
print(judul)
print("Jawab y/t.")

memori = []
nomor = 1
for fakta in fakta_ditanyakan:
  jawaban = input(f"{nomor}. Apakah {fakta}? (y/t) > ").strip().lower()
  if jawaban == "y":
    memori.append(fakta)
  nomor = nomor + 1

print("\nFakta awal:", ", ".join(memori))
print()

# 4. Mesin Inferensi Forward Chaining (FC)
asal_aturan = {}  # Menyimpan catatan aturan mana yang menghasilkan suatu fakta
siklus = 1

while True:
  aturan_cocok = []

  # Cek semua aturan satu per satu
  for aturan in daftar_aturan:
    hasil = aturan["maka"]

    # Lewati jika hasil aturan sudah ada di memori
    if hasil in memori:
      continue

    # Cek apakah syarat aturan terpenuhi oleh memori
    syarat_list = aturan["jika"]
    mode = aturan["mode"]

    if mode == "dan":
      terpenuhi = True
      for s in syarat_list:
        if s not in memori:
          terpenuhi = False
          break
    elif mode == "atau":
      terpenuhi = False
      for s in syarat_list:
        if s in memori:
          terpenuhi = True
          break

    if terpenuhi:
      aturan_cocok.append(aturan)

  # Jika tidak ada aturan baru yang cocok, hentikan perulangan
  if len(aturan_cocok) == 0:
    print(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
    break

  # Ambil aturan pertama yang cocok
  r = aturan_cocok[0]
  memori.append(r["maka"])
  asal_aturan[r["maka"]] = r
  print(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
  siklus = siklus + 1

# 5. Memisahkan kesimpulan akhir (hasil "maka" yang bukan syarat aturan lain)
semua_syarat = []
for aturan in daftar_aturan:
  for syarat in aturan["jika"]:
    semua_syarat.append(syarat)

kesimpulan = []
for item in memori:
  if item in semua_hasil and item not in semua_syarat:
    kesimpulan.append(item)

# 6. Menampilkan Kesimpulan, Alasan, dan Catatan Batas Keberlakuan
print()
if len(kesimpulan) > 0:
  print("Kesimpulan:", ", ".join(kesimpulan))
  print("Alasan:")

  for k in kesimpulan:
    r_utama = asal_aturan[k]
    # Ambil syarat dari aturan utama yang ada di memori
    bukti_utama = []
    for s in r_utama["jika"]:
      if s in memori:
        bukti_utama.append(s)

    print(
        f"  {k} <- {r_utama['id']} ({', '.join(bukti_utama)})"
        f" [{r_utama['sumber']}]"
    )

    # Jika salah satu syarat berasal dari aturan sebelumnya (rantai aturan)
    for b in bukti_utama:
      if b in asal_aturan:
        r_sebelum = asal_aturan[b]
        bukti_sebelum = []
        for s2 in r_sebelum["jika"]:
          if s2 in memori:
            bukti_sebelum.append(s2)
        print(
            f"    {b} <- {r_sebelum['id']} ({', '.join(bukti_sebelum)})"
            f" [{r_sebelum['sumber']}]"
        )
else:
  print("Kesimpulan: tidak ada (fakta belum cukup untuk menarik kesimpulan)")

print("\nCatatan:", batas)