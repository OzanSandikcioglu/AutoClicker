# ⚡ AutoClicker

**🇬🇧 English: [README.md](README.md)**

Fareyi senin yerine tıklayan, ücretsiz ve açık kaynak bir Windows uygulaması. Bir tuşa basıyorsun, sen durdurana kadar tıklamaya devam ediyor. Oyunlarda, sürekli aynı yere tıklamak gereken işlerde ve bilgisayar başında olmadığın zamanlarda kullanılır.

> **Sadece Windows.** Tıklama motoru Windows'un `SendInput` sistemini kullanıyor, bu yüzden Mac veya Linux'ta çalışmaz.

---

## 📦 Hiç Bilmeyenler İçin: Adım Adım Kurulum

Bilgisayar konusunda deneyimin yoksa endişelenme, buradan takip et. Her adımda ne göreceğini de yazdım.

### 1. Dosyayı indir

[**Bu sayfayı aç**](https://github.com/OzanSandikcioglu/AutoClicker/releases/latest). Sayfanın altında **Assets** (Dosyalar) yazan bir liste var. Oradaki **`AutoClicker-v1.4.0-win64.zip`** yazısına tıkla.

İndirme başlar. Dosya genelde **İndirilenler** klasörüne iner.

### 2. Zip'ten çıkar — bu adımı sakın atlama

İndirdiğin şey bir **zip dosyası**, yani içine bir sürü dosya konmuş sıkıştırılmış bir kutu. Önce kutuyu açman gerekiyor:

1. `AutoClicker-v1.4.0-win64.zip` dosyasına **sağ tıkla**.
2. **Tümünü ayıkla...** seçeneğine tıkla.
3. Açılan pencerede **Ayıkla** düğmesine bas.
4. Karşına yeni bir pencere açılır, içinde **AutoClicker** adlı bir klasör görürsün.

> ⚠️ **En sık yapılan hata buradadır.** Zip dosyasına çift tıklayıp içindeki `AutoClicker.exe`'yi oradan çalıştırmak. Windows buna izin verir ama **uygulama açılmaz**, çünkü yanındaki `_internal` klasörü olmadan çalışamaz. Önce mutlaka "Tümünü ayıkla" yap.

**İpucu:** Çıkan **AutoClicker** klasörünü masaüstüne sürükleyip bırakırsan her seferinde kolayca bulursun.

### 3. Uygulamayı aç

**AutoClicker** klasörünün içine gir ve **AutoClicker.exe** dosyasına çift tıkla.

Karşına iki pencere çıkabilir. İkisi de normaldir:

**🔵 "Windows bilgisayarınızı korudu" yazan mavi pencere**

Bu, Windows'un uygulamayı daha önce hiç görmediği anlamına gelir — zararlı olduğu anlamına gelmez. Küçük yazıyla duran **Ek bilgi** yazısına tıkla, sonra alta çıkan **Yine de çalıştır** düğmesine bas.

**🛡️ "Bu uygulamanın cihazınızda değişiklik yapmasına izin ver..." diye soran pencere**

**Evet** de. Bu izni vermezsen uygulama açılır ama **bazı oyunlarda tıklamaları çalışmaz**. Windows, izin verilmemiş programların oyunlara tıklama göndermesini engelliyor.

### 4. Ayarlarını yap

Uygulama açıldığında:

- **Tık Aralığı**: Kaç saniyede bir tıklasın? Dört kutu var: Saat / Dakika / Saniye / ms (milisaniye). Sadece sayı yazabilirsin. `100 ms` saniyede 10 tıklama demektir. Yavaş olsun istersen Saniye kutusuna `1` yaz.
- **Tık Türü**: `Tek` normal tıklama, `Çift` çift tıklama, `Basılı` fare tuşunu basılı tutar (madencilik, sürekli ateş gibi işler için).
- **Fare Btn**: Hangi tuş tıklansın — Sol, Sağ veya Orta.
- **Kısayol**: Başlat/durdur tuşu. Başlangıçta **F6**'dır. Değiştirmek istersen butona tıkla, sonra istediğin tuşa bas. Farenin yan tuşlarını da kullanabilirsin. Vazgeçersen **Esc**'e bas.

### 5. Çalıştır

1. Fareyi tıklanmasını istediğin yerin üzerine getir.
2. **F6**'ya bas (veya alttaki mavi **BAŞLAT** düğmesine tıkla).
3. Tıklamalar başlar, sağ altta sayaç artar.
4. Durdurmak için tekrar **F6**'ya bas.

Tıklamalar farenin durduğu yere gider, o yüzden önce fareyi doğru yere koy, sonra başlat.

### Silmek istersen

**AutoClicker** klasörünü çöp kutusuna at, o kadar. Bu uygulama bilgisayara kurulum yapmaz, kayıt defterine dokunmaz, başka hiçbir yere dosya yazmaz.

---

## 🎮 Ekrandaki Her Şey Ne İşe Yarıyor

| Bölüm | Ne yapar |
| :--- | :--- |
| **Tık Aralığı** | Tıklamalar arasındaki süre. Dört kutunun toplamı alınır: `0 / 0 / 1 / 500` = 1,5 saniyede bir tıklama. Sadece rakam kabul eder; hepsini boş bırakırsan 100 ms kullanılır. |
| **Tık Türü** | `Tek` her aralıkta bir tıklama, `Çift` çift tıklama, `Basılı` fare tuşunu sen durdurana kadar basılı tutar. |
| **Fare Btn** | Hangi fare tuşu gönderilsin: Sol, Sağ veya Orta. |
| **Kısayol** | Başlat/durdur tuşu, varsayılanı `F6`. Butona tıkla, sonra istediğin tuşa ya da farenin yan tuşuna bas; `Esc` iptal eder. Başka bir pencere (veya oyun) öndeyken de çalışır. |
| **BAŞLAT / DURDUR** | Kısayolla aynı iş. Çalışırken düğme turkuaza, durum ışığı yeşile döner. |
| **Tıklama** | O anki çalıştırmada kaç tıklama gönderildiği. |
| **Dil / Tema** | Dil düğmeleri ve karanlık/aydınlık anahtarı; ikisi de anında uygulanır. |
| **Tıklayıcı / Desen** | Araç çubuğunun altındaki iki sekme. **Tıklayıcı** imlecin durduğu yere aynı tıklamayı tekrarlar; **Desen** kaydettiğin sırayı oynatır. Bir şey çalışırken sekme değişmez. |
| **Yönetici şeridi** | En alttaki şerit. Yeşilse tıklamalar ekrandaki her şeye ulaşır. Turuncuysa ulaşamaz — **Yönetici olarak çalıştır** düğmesine bas. |

---

## 🔁 Desen Modu

**Desen** sekmesi, tek bir yere üst üste tıklamak yerine senin tıkladığın yerleri kaydeder.

1. **Desen** sekmesine geç ve **Kaydet**'e bas.
2. Tekrarlanmasını istediğin şeyleri sırayla tıkla. Her tıklama; yeri, hangi fare tuşu olduğu ve öncesinde ne kadar beklediğinle birlikte kaydedilir.
3. **Bitir**'e bas. Liste adımlarla dolar.
4. **Durdurana kadar** ya da **Süre** seç, turlar arasındaki **Ara** değerini ayarla, START'a (veya kısayoluna) bas.

| Ayrıntı | Davranış |
| :--- | :--- |
| AutoClicker penceresine tıklamalar | Kaydedilmez, yani **Bitir**'e basman desenin parçası olmaz. |
| Kayıt sırasında yan tuşlar | Yok sayılır - tıklama motoru sadece sol, sağ ve ortayı gönderebiliyor. |
| Kendi zamanlaman | Korunur. Oynatırken tıklamalar arasında senin beklediğin kadar bekler; tek bir bekleme en fazla 10 saniye sayılır. |
| Uzunluk | Desen başına en fazla 200 tıklama. |
| İmleç nerede kalır | Son tıkladığı noktada. Oynatma gerçek imleci hareket ettirir, o yüzden çalışırken fareye dokunma ve kısayolla durdur. |
| Kaydetme | Desenler sadece bellekte tutulur. Uygulamayı kapatınca unutulur. |

---

## ✨ Özellikler

- **Oyunlarda çalışır:** Windows'un düşük seviyeli `SendInput` sistemini, oyun motorlarının kareyi yakalayabilmesi için özel bir basılı tutma gecikmesiyle kullanır (*Trove* ve başka MMO'larda denendi).
- **İstediğin tuşu kısayol yapabilirsin:** Klavyeden herhangi bir tuş ya da farenin yan tuşu. Tuşu basılı tutmak bir kez tetikler, üst üste açıp kapatmaz.
- **Farenin yan tuşları kısayol olabilir:** Oyuncu farelerindeki baş parmak tuşları (`Mouse 4` / `Mouse 5`) ve tekerlek tıklaması (`Mouse 3`). Uygulamanın kendi gönderdiği tıklamalar sayılmaz, ama fare yazılımının ilettiği makro tuşları çalışır.
- **Desen modu:** Tıklamalarını sırasıyla kaydeder - nereye, hangi tuşla ve kaç saniye bekleyerek - sonra aynı sırayı sen durdurana kadar ya da belirlediğin süre boyunca tekrarlar.
- **Üç tıklama türü:** Tek, çift veya basılı tutma — sol, sağ ya da orta tuşla.
- **Basılı tutma modu:** Fare tuşunu basılı tutar ve oyun motorunun algılaması için sinyali 25 ms'de bir tazeler. Durdurduğunda veya uygulamayı kapattığında tuş **her zaman** bırakılır, asla basılı kalmaz.
- **Hassas aralık:** Saat, dakika, saniye ve milisaniye. Zamanlama kaymaz ve çalışırken aralığı değiştirebilirsin.
- **Yalnız bırakmaya uygun:** Uygulamanın gönderdiği tıklamalar kendi penceresinde yok sayılır, yani fare BAŞLAT düğmesinin üstünde kalsa bile tıklayıcı kendini kapatmaz. Tıklama sürdüğü sürece bilgisayarın uykuya geçmesi de engellenir.
- **Yönetici durumunu gösterir:** Windows, yetkisi daha yüksek bir pencereye giden tıklamaları sessizce çöpe atar — hata bile vermez. Uygulama kendi yetkisini kontrol edip durumu söyler ve tek tıkla yönetici olarak yeniden başlayabilir.
- **Altı dil:** İngilizce, **Türkçe**, Almanca, İspanyolca, Fransızca ve Çince.
- **Karanlık/Aydınlık tema:** Tek düğmeyle anında değişir.

---

## 📥 Hangi Dosyayı İndirmeliyim?

GitHub'da iki ayrı indirme var ve bunlar birbirinin yerine geçmez:

| Amacın | Ne yapmalısın | Eline ne geçer |
| :--- | :--- | :--- |
| **Sadece kullanmak** | [**Releases**](https://github.com/OzanSandikcioglu/AutoClicker/releases/latest) sayfasından `AutoClicker-v1.4.0-win64.zip` | Çalışmaya hazır uygulama, ~12 MB. Python gerekmez. |
| **Kodu okumak / değiştirmek** | Yeşil **Code** düğmesi → *Download ZIP* | Sadece kaynak kod, ~70 KB. İçinde **uygulama yok**, kendin derlemen gerekir. |

> Sayfanın üstündeki yeşil **Code** düğmesi herkesin ilk bastığı düğmedir ve sadece uygulamayı kullanmak istiyorsan **yanlış olanıdır**: sana Python dosyaları verir, uygulamayı değil.

---

## 🧩 Sorun Giderme

**Windows Defender veya antivirüsüm dosyayı engelliyor.**
Otomatik tıklayıcılar bilgisayara yapay fare girdisi gönderir; bilgi çalan zararlı yazılımlar da aynı şeyi yapar, bu yüzden tarayıcılar bu tür programları sık sık işaretler. Bu yüzden uygulama sıkıştırılmamış bir klasör olarak ve sürüm bilgisi gömülü şekilde dağıtılıyor, ama yine de işaretlenebilir. Güvenmiyorsan aşağıdaki adımlarla kendin derleyebilirsin.

**Bir kez çalıştırdım, sonra dosya kayboldu — kapatınca ya da bilgisayarı yeniden başlatınca.**
Uygulama kendini silmedi: **Windows Defender karantinaya aldı.** İmzasız ve işi fare girdisi göndermek olan bir program, bulut korumasının ve "istenmeyen uygulama" filtresinin tam hedefindedir; karar çoğu zaman ilk çalıştırmadan *sonra* gelir, o yüzden dosya kendi kendine kaybolmuş gibi görünür. **Windows Güvenliği → Koruma geçmişi** bölümünde kaydı bulabilirsin; güveniyorsan oradan geri yükleyip hariç tutma ekleyebilirsin.

Dosyayı WhatsApp gibi uygulamalarla elden ele göndermek bu ihtimali çok artırır, çünkü karşı tarafa "internetten geldi" damgasıyla ve hiçbir itibar geçmişi olmadan ulaşır. Dosya yerine [Releases](https://github.com/OzanSandikcioglu/AutoClicker/releases/latest) bağlantısını gönder.

**Masaüstünde tıklıyor ama oyunumda tıklamıyor.**
Önce pencerenin altındaki şeride bak. **Turuncuysa** uygulama yönetici olarak çalışmıyordur ve Windows tıklamaları oyuna ulaşmadan siliyordur — **Yönetici olarak çalıştır** düğmesine basıp **Evet** de. En sık sebep budur. Şerit zaten yeşilse oyun sadece ham girdi okuyor olabilir; çekirdek seviyesinde hile korumalı oyunlara hiçbir tıklayıcı ulaşamaz.

**Faremin makro tuşunu kısayol yapamıyorum.**
Bağlanabilen tuşlar tekerlek tıklaması ve iki baş parmak tuşudur (`Mouse 3`, `Mouse 4`, `Mouse 5`); Windows'un normal fare tuşu olarak bildirdiği tuşlar bunlardır. Sol ve sağ tuş bilerek kabul edilmiyor: onlardan birini bağlarsan arayüzdeki her tıklama tıklayıcıyı açıp kapatır.

Bunların dışındaki tuşlar genelde farenin kendi sürücüsü içinde işlenir ve Windows'a fare girdisi olarak hiç ulaşmaz. Çözüm farenin kendi programıdır (Logitech G HUB, Razer Synapse vb.): o tuşu boş bir klavye tuşuna — mesela `F9` — ata, sonra burada o tuşu bağla.

Bağladığın fare tuşu normal işini yapmaya da devam eder; `Mouse 5`'i bağlamak onu tarayıcıda "ileri" olmaktan çıkarmaz.

**Kutulara yazı yazarken kısayol çalışmıyor.**
Kısayolu harf ya da rakama bağladıysan bu bilerek yapılmıştır: kutuya `5` yazarken tıklayıcının başlaması istenmez. `F6` gibi fonksiyon tuşları etkilenmez, ve **durdurma hiçbir zaman engellenmez**.

**`.exe`'ye çift tıklıyorum, hiçbir şey olmuyor.**
`_internal` klasörünün onun yanında olması gerekir — yukarıdaki 2. adıma bak.

---

## 🛠️ Kaynaktan Derleme (Geliştiriciler İçin)

### Gereksinimler
Windows ve Python 3.10 veya üstü.

### 1. Klonla ve bağımlılıkları kur
```bash
git clone https://github.com/OzanSandikcioglu/AutoClicker.git
cd AutoClicker
pip install -r requirements.txt
```
Bu, uygulamayı çalıştırmak için gereken tek şey olan `pynput`'u kurar. PyInstaller sadece EXE derlemek için gerekir ve `build.bat` onu kendisi kurar.

### 2. Çalıştır
```bash
python auto_clicker.py
```
Kaynaktan çalıştırmak yönetici yetkisi vermez, uygulama turuncu şeridi gösterir. Tıklamaların oyuna ulaşması gerektiğinde **Yönetici olarak çalıştır**'a bas veya terminali yönetici olarak aç.

### 3. EXE derle
```bash
build.bat
```
*Veya elle:*
```bash
pyinstaller --onedir --noconsole --uac-admin --version-file version_info.txt --name AutoClicker auto_clicker.py
```
Sonuç `dist/AutoClicker/` klasörüne çıkar. O klasörün tamamını zip olarak dağıt — `--onedir`, Python çalışma ortamını exe'nin yanında tutar; hem daha hızlı açılır hem de antivirüs sezgisellerini çok daha az tetikler.

### Dosya yapısı
```
auto_clicker.py        Giriş noktası; Tk penceresini ve uygulamayı oluşturur
src/app.py             Arayüz, tema, tıklama döngüsü, kısayol yönetimi
src/mouse.py           SendInput tıklama motoru, olay imzalama, zamanlayıcılar
src/hotkey.py          pynput tuşlarını sabit isimlere çevirir
src/pattern.py         Kaydedilen tık dizileri ve zamanlamaları
src/elevation.py       Yönetici yetkisi kontrolü ve UAC ile yeniden başlatma
src/themes.py          Karanlık ve aydınlık renk paletleri
src/translations.py    Altı dilin arayüz metinleri
build.bat              Tek adımda PyInstaller derlemesi
version_info.txt       EXE'ye gömülen Windows sürüm bilgisi
```

---

## 📄 Lisans
Bu proje açık kaynaktır ve [MIT Lisansı](LICENSE) ile dağıtılır.
