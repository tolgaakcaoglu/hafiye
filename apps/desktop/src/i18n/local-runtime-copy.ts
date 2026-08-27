import type { Translations } from './types'

type LocalRuntimeCopy = Translations['settings']['localRuntime']

export const EN_LOCAL_RUNTIME_COPY: LocalRuntimeCopy = {
  title: 'Local GGUF Runtime',
  description: 'Managed llama.cpp server, local GGUF models, and the selected compute backend.',
  unknownSize: 'unknown size',
  backend: 'Backend',
  installRuntime: 'Install / rebuild runtime',
  refresh: 'Refresh',
  runtimeInstalled: version => `llama-server ${version}`,
  runtimeNotInstalled: 'llama-server is not installed',
  nvidiaPresent: name => `NVIDIA ${name}`,
  servingModel: model => `serving ${model}`,
  modelFallback: 'model',
  catalogDefault: 'Hafiye catalog default',
  requiresHuggingFaceAuth: 'Requires approved Hugging Face access and an HF_TOKEN credential in Providers.',
  catalogConflict: 'This model ID already exists with different contents. Remove or rename it before downloading.',
  installed: 'Installed',
  downloadVerified: 'Download verified GGUF',
  downloadTitle: 'Download a GGUF model',
  downloadDescription:
    'Downloads one GGUF from Hugging Face, verifies an optional checksum, and registers it for llama.cpp. Hafiye does not use an Ollama model directory as its local runtime.',
  huggingFaceRepository: 'Hugging Face repository',
  ggufFilename: 'GGUF filename',
  downloadedModelId: 'Downloaded model ID',
  huggingFaceRevision: 'Hugging Face revision',
  ggufChecksum: 'GGUF SHA-256 checksum',
  repositoryPlaceholder: 'owner/repository',
  modelIdOptional: 'model id (optional)',
  revisionOptional: 'revision (optional; branch or commit)',
  checksumOptional: 'SHA-256 (optional)',
  downloadGguf: 'Download GGUF',
  modelPathPlaceholder: '/path/to/model.gguf',
  importGguf: 'Import GGUF',
  selectLocalModel: 'Select a local model',
  contextPlaceholder: 'context',
  gpuLayersPlaceholder: 'GPU layers',
  loadStart: 'Load / start',
  unloadStop: 'Unload / stop',
  catalog: {
    'qwen3.8-27b-ud-iq1_s': {
      intendedUse: 'General local-agent qualification candidate',
      resourceWarning:
        "Agent qualification is pending; downloading this catalog model does not make it Hafiye's default route."
    },
    'qwen3.8-27b-uncensored-q4_k_m': {
      intendedUse: 'Uncensored local model evaluation',
      resourceWarning:
        "Uncensored model; Hafiye host, privilege, privacy, and emergency boundaries remain mandatory. The 15.7 GiB GGUF exceeds this host's 10 GiB VRAM and practical qualification envelope, so it is not a default route. Agent qualification is pending. The separate Ollama vision projection is not imported."
    },
    'qwen3.8-flash-next-uncensored-iq2_m': {
      intendedUse: 'Security researchers, red teams, and blue teams',
      resourceWarning:
        "Security-research model for red teams and blue teams. Requires Hugging Face access approval and HF_TOKEN. The 74.6 GiB IQ2_M weights exceed this host's practical qualification envelope and are not a default route."
    }
  }
}

export const TR_LOCAL_RUNTIME_COPY: LocalRuntimeCopy = {
  title: 'Yerel GGUF Çalışma Zamanı',
  description: 'Hafiye tarafından yönetilen llama.cpp sunucusu, yerel GGUF modelleri ve seçili işlem backend’i.',
  unknownSize: 'boyut bilinmiyor',
  backend: 'İşlem backend’i',
  installRuntime: 'Çalışma zamanını kur / yeniden derle',
  refresh: 'Yenile',
  runtimeInstalled: version => `llama-server ${version}`,
  runtimeNotInstalled: 'llama-server kurulu değil',
  nvidiaPresent: name => `NVIDIA ${name}`,
  servingModel: model => `${model} sunuluyor`,
  modelFallback: 'model',
  catalogDefault: 'Hafiye katalog varsayılanı',
  requiresHuggingFaceAuth: 'Onaylı Hugging Face erişimi ve Sağlayıcılar bölümünde HF_TOKEN kimlik bilgisi gerekir.',
  catalogConflict:
    'Bu model kimliği farklı içerikle zaten mevcut. İndirmeden önce modeli kaldırın veya yeniden adlandırın.',
  installed: 'Kurulu',
  downloadVerified: 'Doğrulanmış GGUF’u indir',
  downloadTitle: 'GGUF modeli indir',
  downloadDescription:
    'Hugging Face’ten bir GGUF indirir, isteğe bağlı sağlama toplamını doğrular ve llama.cpp için kaydeder. Hafiye, Ollama model dizinini yerel çalışma zamanı olarak kullanmaz.',
  huggingFaceRepository: 'Hugging Face deposu',
  ggufFilename: 'GGUF dosya adı',
  downloadedModelId: 'İndirilen model kimliği',
  huggingFaceRevision: 'Hugging Face revizyonu',
  ggufChecksum: 'GGUF SHA-256 sağlama toplamı',
  repositoryPlaceholder: 'sahip/depo',
  modelIdOptional: 'model kimliği (isteğe bağlı)',
  revisionOptional: 'revizyon (isteğe bağlı; dal veya commit)',
  checksumOptional: 'SHA-256 (isteğe bağlı)',
  downloadGguf: 'GGUF’u indir',
  modelPathPlaceholder: '/model/dosyası/yolu.gguf',
  importGguf: 'GGUF’u içe aktar',
  selectLocalModel: 'Yerel model seçin',
  contextPlaceholder: 'bağlam',
  gpuLayersPlaceholder: 'GPU katmanları',
  loadStart: 'Yükle / başlat',
  unloadStop: 'Bellekten çıkar / durdur',
  catalog: {
    'qwen3.8-27b-ud-iq1_s': {
      intendedUse: 'Genel yerel-agent yeterlilik adayı',
      resourceWarning:
        'Agent yeterlilik testi bekliyor; bu katalog modelini indirmek modeli Hafiye’nin varsayılan rotası yapmaz.'
    },
    'qwen3.8-27b-uncensored-q4_k_m': {
      intendedUse: 'Sansürsüz yerel model değerlendirmesi',
      resourceWarning:
        'Sansürsüz modeldir; Hafiye’nin ana makine, ayrıcalık, gizlilik ve acil durdurma sınırları zorunlu kalır. 15,7 GiB GGUF bu makinenin 10 GiB VRAM’ini ve pratik yeterlilik sınırını aştığı için varsayılan rota değildir. Agent yeterlilik testi bekliyor. Ayrı Ollama görsel izdüşümü içe aktarılmaz.'
    },
    'qwen3.8-flash-next-uncensored-iq2_m': {
      intendedUse: 'Güvenlik araştırmacıları, kırmızı takımlar ve mavi takımlar',
      resourceWarning:
        'Kırmızı ve mavi takımlara yönelik güvenlik araştırması modelidir. Hugging Face erişim onayı ve HF_TOKEN gerekir. 74,6 GiB IQ2_M ağırlıkları bu makinenin pratik yeterlilik sınırını aşar ve varsayılan rota değildir.'
    }
  }
}
