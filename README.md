<p align="center">
  <img src="assets/banner.png" alt="Hafiye" width="100%">
</p>

# Hafiye

<p align="center">
  Ubuntu/Linux için yerel öncelikli masaüstü yapay zekâ ajanı
</p>

<p align="center">
  <a href="HAFIYE_MASTER_ROADMAP.md"><img src="https://img.shields.io/badge/Architecture-Master%20Roadmap-7c3aed?style=for-the-badge" alt="Master Roadmap"></a>
  <a href="STATE.md"><img src="https://img.shields.io/badge/Status-P23%20in%20progress-f59e0b?style=for-the-badge" alt="P23 in progress"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge" alt="MIT License"></a>
</p>

Hafiye; [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
üzerinde geliştirilen, masaüstü uygulaması ve kalıcı yerel servisi bulunan bir
kişisel ajandır. Hafiye Desktop, Composer, CLI ve mesajlaşma yüzeyleri aynı
agent çekirdeğini, aynı yapılandırmayı, aynı model yönlendirmesini ve aynı görev
durumunu kullanır.

Hafiye'nin ana hedefi Ubuntu/Linux üzerinde yerel model, Türkçe ses, gerçek
masaüstü kontrolü, kalıcı hafıza ve gerektiğinde denetimli root işlemlerini tek
ürün içinde birleştirmektir. Ana Hafiye prosesi root olarak çalışmaz.

> **Geliştirme durumu:** P0–P22 tamamlanmıştır. P23 gerçek-makine final kabul
> süreci devam etmektedir; henüz final release etiketi yoktur. Güncel ve
> doğrulanmış durum için [STATE.md](STATE.md) ve [ROADMAP.md](ROADMAP.md)
> dosyalarını okuyun.

## Temel özellikler

- Electron + React tabanlı Hafiye Desktop, tray ve `Super+Shift+Space`
  kısayollu Hafiye Composer.
- Kullanıcı oturumunda kalıcı çalışan `hafiye-gateway.service`.
- Hafiye tarafından yönetilen `llama.cpp` ve tek dosyalı GGUF modeller.
- Varsayılan `AUTO` compute politikası: CUDA → Vulkan → CPU.
- GUI üzerinden Hugging Face GGUF indirme, yerel GGUF içe aktarma,
  yükleme/boşaltma ve compute backend seçimi.
- İsteğe bağlı Gemini ve OpenAI-uyumlu uzak model endpoint'leri.
- `NORMAL`, `LOCAL_ONLY` ve `OFFLINE` gizlilik modları.
- `agent-sh/computer-use-linux` ile AT-SPI tabanlı gerçek Linux masaüstü
  kontrolü.
- openWakeWord + `whisper.cpp` + Piper tabanlı yerel Türkçe ses zinciri.
- OpenHands coding delegate, Task Center, scheduler, skills ve MCP desteği.
- Ayrı ve yerel Unix socket kullanan `hafiye-rootd` ayrıcalıklı işlem sınırı.
- Linux Secret Service/keyring içinde provider credential saklama.
- Acil durdurma: `Ctrl+Super+Escape`.

## Desteklenen ana ortam

Mevcut doğrulanmış hedef Ubuntu GNOME/Wayland'dir. X11 ve başka Linux masaüstü
ortamları upstream bileşenler tarafından kısmen desteklenebilir; bunlar mevcut
Hafiye final kabul ortamı değildir.

Kaynak ve paket build'i için:

- Ubuntu/Debian tabanlı Linux,
- Hafiye runtime için Python `>=3.11,<3.14` — proje varsayılanı Python 3.11,
- Node.js `>=22.22.0`,
- proje `package.json` dosyasındaki aralığı sağlayan npm,
- `uv`, Git ve standart C/C++ build araçları,
- Desktop build'i için Electron'un Linux runtime kütüphaneleri,
- yerel CUDA kullanımı için çalışan NVIDIA driver/CUDA ortamı gerekir.

Dağıtımın sistem Python'ı 3.14 olabilir. Birleşik `.deb`, bu interpreter'ı
yalnız stdlib bootstrap için kullanır; `hafiye package install` desteklenen
managed Python 3.11 ortamını `uv` ile ayrıca oluşturur. Sistem Python'ını elle
downgrade etmeyin.

Sürüm kontrolü:

```bash
python3 --version
node --version
npm --version
uv --version
git --version
```

## İlk kurulum

Hafiye henüz final release etiketiyle yayımlanmadığı için desteklenen kurulum
yolu, yetkili Hafiye kaynak kopyasındaki `hafiye/p0` geliştirme dalından birleşik
Ubuntu/Debian paketini üretmektir. Bu repository zaten mevcutsa aşağıdaki
komutları repository kökünde çalıştırın.

### 1. Sistem ve geliştirme bağımlılıkları

```bash
sudo apt update
sudo apt install -y \
  build-essential cmake ninja-build pkg-config \
  git curl ca-certificates python3 python3-venv \
  ripgrep ffmpeg \
  libgtk-3-0t64 libasound2t64 libnss3 libgbm1 \
  libnotify4 libxss1 libxtst6 xdg-utils
```

Modern Ubuntu sürümleri GTK/ALSA paketlerini `libgtk-3-0t64` ve
`libasound2t64` adıyla sunar. Daha eski Ubuntu sürümlerinde bunları sırasıyla
`libgtk-3-0` ve `libasound2` ile değiştirin. Eksik Electron kütüphanelerini
paket yöneticinizin bildirdiği ada göre kurun.

`uv` kurulu değilse:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Node.js için dağıtımın eski `nodejs` paketini kullanmayın; `node --version`
çıktısının en az `22.22.0` olduğundan emin olun.

### 2. Kaynak bağımlılıklarını kurun

```bash
cd /path/to/hafiye
uv sync --locked --python 3.11 --extra all --extra dev
npm ci
```

Python ortamı `.venv/` altında oluşur. `npm ci` repository workspace'lerini ve
Desktop bağımlılıklarını lockfile'dan kurar.

### 3. Desktop ve birleşik `.deb` paketini üretin

```bash
cd apps/desktop
npm run pack
cd ../..

.venv/bin/python scripts/build_deb.py --json
```

`npm run pack`, `apps/desktop/release/linux-unpacked/` ağacını üretir.
`scripts/build_deb.py` bunun üzerine Hafiye backend'ini, launchers, systemd user
unit'ini, root broker aktivasyon yolunu, XDG girişlerini ve paket manifestini
ekler. Son paket `dist/hafiye_<sürüm>_<mimari>.deb` altında oluşur.

### 4. Paketi ve kilitli Python bağımlılıklarını kurun

```bash
HAFIYE_DEB="$(realpath "$(ls -t dist/hafiye_*_"$(dpkg --print-architecture)".deb | head -n 1)")"
test -n "$HAFIYE_DEB"
sudo apt install "$HAFIYE_DEB"

hafiye package install
hafiye package doctor
```

`hafiye package install` root kullanmadan, kilitli Python bağımlılıklarını
`~/.local/share/hafiye/python-venv` içine kurar. `hafiye package doctor` sonucu
`OK` olmalı; required blocker varsa ilk açılıştan önce giderin.
Sistem Python'ı 3.14 ise installer bunun yalnız bootstrap interpreter olduğunu
bildirir ve managed Python 3.11'i otomatik provision eder.

### 5. Root broker'ı etkinleştirin

```bash
hafiye root install
hafiye root status
```

Bu adım normal interaktif `sudo` ile bir kez parola isteyebilir. Komutu gerçek
bir sistem terminalinde çalıştırın. Passwordless sudo veya `NOPASSWD` kuralı
eklemeyin. Normal Hafiye agent/terminal yolu `sudo`, `sudoedit`, `su`, `pkexec`
ve `doas` çalıştırmaz; ayrıcalıklı işler yalnız `hafiye-rootd` sınırından geçer.

### 6. Hafiye Desktop'ı başlatın

Uygulama menüsünden **Hafiye**'yi açın veya:

```bash
systemctl --user enable --now hafiye-gateway.service
hafiye-desktop
```

İlk açılış sihirbazı şu gerçek kurulum sınırlarını yönetir:

1. ortam ve `computer-use-linux` doctor kontrolü;
2. `AUTO`, CUDA, Vulkan veya CPU compute seçimi;
3. Hafiye-managed `llama.cpp` build'i;
4. GGUF model indirme ya da içe aktarma;
5. yerel model server'ı ve varsayılan route;
6. isteğe bağlı uzak endpoint ve Gemini;
7. mikrofon, `whisper.cpp`, Piper ve wake word;
8. execution policy, autostart ve final doctor.

Normal kullanımda Desktop'ı kapatmak kalıcı gateway'i durdurmaz. Tray menüsünü
kullanın; Composer varsayılan olarak `Super+Shift+Space` ile açılır.

### 7. Final kurulum kontrolü

```bash
hafiye status --all
hafiye doctor
hafiye runtime doctor
hafiye voice doctor
hafiye computer doctor --json
hafiye root status
systemctl --user is-enabled hafiye-gateway.service
systemctl --user is-active hafiye-gateway.service
```

`computer doctor` için şu dört readiness alanı `true`, `blockers` ise boş
olmalıdır:

```text
can_register_mcp_tools
can_build_accessibility_tree
can_send_development_input
can_query_windows
```

## computer-use-linux ilk host hazırlığı

Onboarding doctor `computer-use-linux` blocker'ı gösterirse Hafiye'nin pinlediği
kaynak checkout üzerinden upstream'in resmi setup yolunu kullanın:

```bash
mkdir -p "$HOME/.cache/hafiye"
git clone https://github.com/agent-sh/computer-use-linux.git \
  "$HOME/.cache/hafiye/computer-use-linux"
git -C "$HOME/.cache/hafiye/computer-use-linux" checkout --detach \
  94736dc3e0dca56acfc89752c26869fb9ed01202

cd "$HOME/.cache/hafiye/computer-use-linux"
./install.sh
computer-use-linux setup
computer-use-linux setup-window-targeting
computer-use-linux doctor
```

Installer; Rust/Cargo, system dependencies, AT-SPI, `ydotool/ydotoold`, GNOME
Wayland window-targeting extension ve `/dev/uinput` erişimini hazırlar.
Sistem paketi veya grup/cihaz izni için normal `sudo` prompt'u açılabilir.
GNOME extension ya da grup üyeliği değiştiyse oturumu kapatıp yeniden giriş
yapın; sonra `hafiye computer doctor --json` komutunu tekrar çalıştırın.

## GUI'den yerel model ekleme

İlk kurulumdan sonra yeni bir model için terminal kullanmak gerekmez:

1. Hafiye Desktop'ta **Settings → Models** sayfasını açın.
2. **Local GGUF Runtime** bölümünde backend olarak normalde `AUTO` seçin.
3. Runtime kurulu değilse **Install / rebuild runtime** düğmesini kullanın.
4. Hugging Face üzerinden indirmek için repository ve tam `.gguf` dosya adını
   girin. Model ID, revision ve SHA-256 alanları isteğe bağlıdır.
5. Bilgisayardaki bir dosya için `.gguf` yolunu girip **Import GGUF** kullanın.
6. Kayıtlı modeli seçin ve **Load / start** ile llama-server'ı başlatın.
7. Gerekirse aynı Models sayfasının ana model bölümünde `custom` provider ve
   yüklediğiniz model ID'sini seçip uygulayın.

Hafiye'nin yerel engine'i `llama.cpp + GGUF` olarak sabittir. Ollama'nın
manifest/blob model deposu doğrudan içe aktarılmaz ve `ollama pull` Hafiye'ye
model kurmuş sayılmaz. İstenen modelin tek dosyalı GGUF sürümünü GUI'den
Hugging Face üzerinden indirin veya **Import GGUF** ile ekleyin.

Qwen3-14B bu hostta agent-qualified ve seçilebilirdir; ancak KI-046 kaynak
uyarısı nedeniyle varsayılan route değildir. Modelin selectable olması,
otomatik olarak default yapılacağı anlamına gelmez.

## Provider ve gizlilik ayarları

Provider, model, route ve privacy ayarlarını Desktop içinden değiştirmek
önerilen yoldur:

- **Settings → Providers:** Gemini veya OpenAI-uyumlu uzak endpoint.
- **Settings → Models:** ana model, yardımcı modeller ve yerel GGUF runtime.
- **Settings → Routing:** default/fast/strong/vision/coding/long-context route.
- **Settings → Privacy:** `NORMAL`, `LOCAL_ONLY`, `OFFLINE`.

API anahtarları normal ürün akışında plaintext `.env` içine değil Linux Secret
Service/keyring'e yazılır. Anahtarları komut geçmişine, loglara veya repository
dosyalarına koymayın.

## Temel CLI kullanımı

Desktop ve CLI aynı backend/business logic'i kullanır.

```bash
hafiye                              # etkileşimli konuşma
hafiye ask "Firefox'u aç."          # tek seferlik gerçek agent isteği
hafiye start                        # kalıcı backend'i başlat
hafiye stop                         # kalıcı backend'i durdur
hafiye restart                      # backend kodunu yeniden yükle
hafiye models                       # kayıtlı GGUF modeller
hafiye model load MODEL_ID --backend AUTO
hafiye model unload
hafiye providers
hafiye routing
hafiye privacy
hafiye tasks
hafiye computer doctor --json
hafiye voice doctor
hafiye root status
hafiye logs -f
```

Tüm komutlar için:

```bash
hafiye --help
hafiye <komut> --help
```

## Kod değişikliğinden sonra değişiklikleri uygulama

Kaynak checkout'ta dosyayı değiştirmek, kurulu `/usr/lib/hafiye` paketini veya
zaten açık Desktop prosesini kendiliğinden güncellemez. Önce hangi çalışma
modunda olduğunuzu kontrol edin:

```bash
systemctl --user cat hafiye-gateway.service
ps -eo pid,args | grep '[h]afiye-desktop'
```

Unit içindeki `ExecStart` repository `.venv` yolunu gösteriyorsa **kaynak
geliştirme modu**, `/usr/lib/hafiye` gösteriyorsa **kurulu paket modu** aktiftir.

### Kaynak geliştirme modunda hızlı uygulama

Python/backend değişiklikleri için:

```bash
uv sync --locked --python 3.11 --extra all --extra dev
.venv/bin/hafiye restart
curl --fail http://127.0.0.1:9120/api/health
journalctl --user -u hafiye-gateway.service -n 100 --no-pager
```

Kaynak user unit'i henüz kurulmamışsa bir kez:

```bash
.venv/bin/python -m hermes_cli.persistent_gateway install
```

Desktop/React/Electron değişikliklerini geliştirme modunda görmek için açık
Hafiye Desktop'ı tray üzerinden tamamen kapatın ve:

```bash
npm ci
cd apps/desktop
npm run dev
```

Bu yol hızlı geliştirme içindir; final paket davranışının kanıtı değildir.

### Kurulu ürüne güncel kodu uygulama

Backend, Desktop veya packaging değişikliğinden sonra birleşik paketi yeniden
üretip yeniden kurun:

```bash
uv sync --locked --python 3.11 --extra all --extra dev
npm ci

git diff --check
git status --short

cd apps/desktop
npm run typecheck
npm run pack
cd ../..

.venv/bin/python scripts/build_deb.py --json
HAFIYE_DEB="$(realpath "$(ls -t dist/hafiye_*_"$(dpkg --print-architecture)".deb | head -n 1)")"
sudo apt install --reinstall "$HAFIYE_DEB"

hafiye package install
systemctl --user daemon-reload
systemctl --user restart hafiye-gateway.service
hafiye package doctor
```

Dağıtılabilir paket manifestinin doğru source commit'i göstermesi için intended
source değişikliklerini package build'inden önce commit edin. Dirty worktree ile
üretilen bir test paketi dosya değişikliklerini içerebilir, fakat manifestte
yalnız son commit SHA'sı yer alır; bunu final artefact olarak kullanmayın.

Açık Desktop eski bundle'ı bellekte tutar. Tray üzerinden tamamen çıkın ve
uygulama menüsünden Hafiye'yi yeniden açın.

Aynı makinede daha önce kaynak geliştirme unit'i oluşturulduysa
`~/.config/systemd/user/hafiye-gateway.service`, paket içindeki
`/usr/lib/systemd/user/hafiye-gateway.service` dosyasını gölgeler. Paket moduna
geçmeden önce unit'i yedekleyin:

```bash
systemctl --user disable --now hafiye-gateway.service
mv "$HOME/.config/systemd/user/hafiye-gateway.service" \
  "$HOME/.config/systemd/user/hafiye-gateway.service.source-backup"
systemctl --user daemon-reload
systemctl --user enable --now hafiye-gateway.service
systemctl --user cat hafiye-gateway.service
```

Son komutta `ExecStart=/usr/lib/hafiye/bin/hafiye-gateway-run` görülmelidir.

Root broker source'u değiştiyse paket yeniden kurulduktan sonra ayrıca:

```bash
hafiye root install
hafiye root restart
```

`llama.cpp` pin/build flag'i değişmedikçe her source değişikliğinde modeli veya
runtime'ı yeniden indirmeyin. Runtime değiştiyse bilinçli olarak:

```bash
hafiye runtime install --backend AUTO
hafiye runtime doctor
```

### Uygulanan commit'i doğrulama

Birleşik paket, source ve upstream kimliklerini manifestte ayrı tutar:

```bash
python3 -m json.tool /usr/lib/hafiye/package-manifest.json
git rev-parse HEAD
```

Manifestteki `source_commit`, kurmak istediğiniz Hafiye source commit'iyle
eşleşmelidir. Dokümantasyon-only HEAD'in source HEAD yerine yazılmaması
gerektiği için commit kimliklerinin güncel kaydı [UPSTREAM.md](UPSTREAM.md) ve
[STATE.md](STATE.md) içindedir.

## Geliştirme ve test

Değişiklikten sonra en küçük hedefli testi çalıştırın; ardından değişen sınırın
integration/acceptance testine geçin.

```bash
# Python örneği
.venv/bin/python -m pytest -q tests/hermes_cli/test_hafiye_cli.py
.venv/bin/python -m ruff check hermes_cli/hafiye_cli.py

# Desktop örneği
cd apps/desktop
npm run typecheck
npm run test:ui -- src/app/settings/local-runtime-settings.test.tsx
cd ../..

git diff --check
```

Packaging, gateway, root broker, model runtime, voice veya computer-use
değişikliklerinde yalnız unit mock'ları yeterli değildir; gerçek service,
paket, cihaz veya Desktop acceptance testi gerekir. Exact upstream karşılaştırma
komutu ve kabul edilen historical failure seti [TEST_MATRIX.md](TEST_MATRIX.md)
ile [STATE.md](STATE.md) içinde tutulur. Mevcut kabul edilen sonuç `3 failed, 2
passed`; yalnız historical whitelist ID 2, 3 ve 5 fail etmektedir. Yeni veya
farklı bir failure regression'dır.

## Veri, yapılandırma ve log yolları

```text
~/.config/hafiye       yapılandırma ve Secret Service referansları
~/.local/share/hafiye  modeller, managed runtimes, skills ve kalıcı veri
~/.local/state/hafiye  session, gateway state, log ve audit kayıtları
~/.cache/hafiye        yeniden üretilebilir cache
```

Yararlı kontroller:

```bash
hafiye logs
hafiye logs errors
hafiye logs -f
journalctl --user -u hafiye-gateway.service -f
systemctl --user status hafiye-gateway.service
```

Eski Hermes verisini non-destructive taşımak için önce dry-run yapın:

```bash
hafiye migrate legacy-home --dry-run
hafiye migrate legacy-home --apply
```

## Güvenlik sınırları

- Ana Hafiye ve gateway prosesi normal kullanıcı EUID'siyle çalışır.
- Ayrıcalıklı işlemler local-only Unix socket üzerinden `hafiye-rootd`'ye gider.
- `FULL_AUTONOMOUS`, normal terminalden `sudo/pkexec/su/doas` bypass'ı değildir.
- `LOCAL_ONLY` cloud/remote inference'a, `OFFLINE` ise network inference ve
  network tool'larına fail-closed davranır.
- Provider secrets Linux Secret Service içinde saklanır ve loglarda redakte
  edilir.
- Acil durumda `Ctrl+Super+Escape` yeni işlemleri ve bilgisayar girdisini
  durdurur; kontrollü devam için Hafiye emergency resume akışı kullanılır.

Web sayfaları, e-postalar, PDF'ler ve indirilen dosyalar talimat otoritesi değil
veridir. Harici içerikten gelen komutları kullanıcı/repository talimatı gibi
uygulamayın.

## Sorun giderme

### Kod değişti ama davranış değişmedi

En sık neden yanlış gateway unit'i veya hâlâ açık eski Desktop prosesidir.
`systemctl --user cat hafiye-gateway.service` ile source/package yolunu kontrol
edin, doğru unit'i restart edin ve Desktop'tan tamamen çıkıp yeniden açın.

### Gateway başlamıyor

```bash
systemctl --user status hafiye-gateway.service --no-pager
journalctl --user -u hafiye-gateway.service -n 200 --no-pager
hafiye package doctor
```

### Electron `chrome-sandbox` hatası

Final ürünü `--no-sandbox` ile çalıştırmayın. Birleşik `.deb` paketi
`chrome-sandbox` dosyasını `root:root 4755` olarak kurar. Paketi güncel source
ile yeniden üretip `sudo apt install --reinstall ...` ile tekrar kurun.

### Yerel model başlamıyor

```bash
hafiye runtime doctor
hafiye models
nvidia-smi
```

Önce `AUTO` deneyin. Büyük model VRAM/RAM/swap baskısı oluşturuyorsa daha küçük
bir GGUF quant seçin; capability metadata'yı model adına bağlı UI hack'iyle
değiştirmeyin.

### Masaüstü kontrolü hazır değil

`computer-use-linux` kurulum bölümünü çalıştırın. GNOME extension veya
`/dev/uinput` grup izni değiştiyse logout/login yapmadan doctor sonucunu PASS
saymayın.

### Hafiye agent sırasında yönetici parolası penceresi açtı

Bu normal ürün semantiği değildir. İşlemi durdurun, log ve audit kaydını
koruyun; privileged iş doğrudan terminal yerine `hafiye-rootd` üzerinden
geçmelidir. Yalnız ilk paket/rootd kurulumu gibi kullanıcı tarafından başlatılan
sistem terminali adımları interaktif sudo parolası isteyebilir.

## Proje belgeleri

- [AGENTS.md](AGENTS.md) — repository çalışma ve uygulama kuralları.
- [HAFIYE_MASTER_ROADMAP.md](HAFIYE_MASTER_ROADMAP.md) — bağlayıcı ürün ve
  mimari tanımı.
- [STATE.md](STATE.md) — güncel phase, doğrulanmış durum ve sıradaki işler.
- [ROADMAP.md](ROADMAP.md) — phase/task kabul durumu.
- [UPSTREAM.md](UPSTREAM.md) — pinned Hermes commit ve patch grupları.
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — gerçek blocker, warning ve regressions.
- [ENVIRONMENT.md](ENVIRONMENT.md) — doğrulanmış host ortamı.
- [TEST_MATRIX.md](TEST_MATRIX.md) — gerçek test komutları ve sonuçları.
- [DECISIONS.md](DECISIONS.md) — roadmap'i değiştirmeyen uygulama ADR'leri.

## Upstream ve katkı disiplini

Git geçmişi korunur:

```text
origin    Hafiye repository
upstream  https://github.com/NousResearch/hermes-agent.git
```

Upstream kaynaklı kodu değiştirirken en küçük sürdürülebilir patch'i yapın,
test ekleyin ve anlamlı divergence'ı [UPSTREAM.md](UPSTREAM.md) içinde kaydedin.
Hermes iç modüllerini yalnız branding amacıyla topluca yeniden adlandırmayın.

Hermes'in genel CLI/provider/skill dokümantasyonu için
[upstream documentation](https://hermes-agent.nousresearch.com/docs/)
kullanılabilir; upstream installer ve release'ler Hafiye'nin birleşik Linux
paketi değildir.

## Lisans ve atıf

Hafiye, MIT lisanslı Hermes Agent üzerinde sürdürülen bir fork'tur. Lisans
metni için [LICENSE](LICENSE), upstream pin ve attribution ayrıntıları için
[UPSTREAM.md](UPSTREAM.md) dosyasına bakın.

Upstream Hermes Agent, [Nous Research](https://nousresearch.com) tarafından
geliştirilmiştir. Linux desktop-control entegrasyonu
[agent-sh/computer-use-linux](https://github.com/agent-sh/computer-use-linux)
kaynağını kullanır.
