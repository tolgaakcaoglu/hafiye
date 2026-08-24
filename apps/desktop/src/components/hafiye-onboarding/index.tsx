import { useStore } from '@nanostores/react'
import { type ReactNode, useEffect, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  completeHafiyeOnboarding,
  downloadLocalRuntimeModel,
  enableHafiyeAutostart,
  getHafiyeAutostartStatus,
  getHafiyeOnboarding,
  getHafiyeOnboardingDoctor,
  getHafiyeOnboardingEnvironment,
  getHermesConfigRecord,
  getLocalRuntime,
  getLocalRuntimeModels,
  getPiperVoicePreview,
  getVoiceRuntime,
  type HafiyeAutostartStatus,
  type HafiyeEnvironmentProbe,
  type HafiyeOnboardingDoctor,
  type HafiyeOnboardingState,
  type HafiyeOnboardingStep,
  importLocalRuntimeModel,
  installLocalRuntime,
  installPiperRuntime,
  installWhisperRuntime,
  type LocalRuntimeBackend,
  type LocalRuntimeDoctor,
  type LocalRuntimeModel,
  saveHermesConfig,
  setModelAssignment,
  startLocalRuntimeServer,
  transcribeAudio,
  updateHafiyeOnboarding,
  type VoiceRuntimeDoctor
} from '@/hermes'
import { requestOneShot } from '@/lib/oneshot'
import {
  getSelectedVoiceInputDeviceId,
  getVoiceInputStream,
  listVoiceInputDevices,
  requestVoiceInputPermission,
  setSelectedVoiceInputDeviceId
} from '@/lib/voice-input-device'
import { $wakeWord, toggleWakeWord } from '@/store/wake-word'

const DEFAULT_PIPER_VOICE = 'tr_TR-dfki-medium'
const DEFAULT_WHISPER_MODEL = 'base'
const PRIVACY_MODES = ['NORMAL', 'LOCAL_ONLY', 'OFFLINE'] as const
const EXECUTION_POLICIES = ['FULL_AUTONOMOUS', 'PRIVILEGED_CONFIRM', 'WRITE_CONFIRM', 'READ_ONLY'] as const

const STEP_TITLES: Record<HafiyeOnboardingStep, string> = {
  welcome: 'Hafiye’ye hoş geldiniz',
  environment: 'Linux ortamını doğrula',
  computer: 'Masaüstü kontrolünü doğrula',
  compute: 'Hesaplama backend’ini seç',
  'llama-runtime': 'Yerel llama.cpp runtime’ını kur',
  'local-model': 'Yerel GGUF modelini ekle',
  'local-server': 'Yerel modeli başlat',
  'remote-provider': 'İsteğe bağlı uzak sağlayıcı',
  gemini: 'İsteğe bağlı Gemini',
  routing: 'Yönlendirme varsayılanlarını seç',
  microphone: 'Mikrofonu seç',
  whisper: 'whisper.cpp’yi kur',
  stt: 'Türkçe konuşmayı test et',
  piper: 'Piper ve Türkçe sesi kur',
  tts: 'Türkçe ses çıkışını test et',
  'wake-word': 'Uyandırma kelimesini ayarla',
  'test-hafiye': 'Hafiye’yi test et',
  'execution-policy': 'Çalıştırma politikasını doğrula',
  autostart: 'Otomatik başlatmayı etkinleştir',
  doctor: 'Son sağlık kontrolü'
}

const STEP_DESCRIPTIONS: Record<HafiyeOnboardingStep, string> = {
  welcome: 'Hafiye, masaüstü ve yerel modellerle çalışan kişisel yardımcıdır.',
  environment: 'Kurulumun çalışacağı gerçek Linux oturumunu ve araçları kontrol ediyoruz.',
  computer: 'Erişilebilirlik ağacı, pencere sorgusu ve geliştirme girdisi hazır olmalıdır.',
  compute: 'AUTO varsayılandır; bu NVIDIA makinede CUDA öncelikli backend’dir.',
  'llama-runtime': 'Hafiye’nin yönettiği llama.cpp, model sunucusunu kullanıcı hesabında çalıştırır.',
  'local-model': 'Bir GGUF dosyası içe aktarın veya Hugging Face üzerinden indirin.',
  'local-server': 'Model loopback üzerindeki OpenAI-uyumlu yerel sunucuda başlatılır.',
  'remote-provider': 'Uzak OpenAI-uyumlu sağlayıcı daha sonra Ayarlar → Providers bölümünden eklenebilir.',
  gemini: 'Gemini isteğe bağlıdır; anahtarlar normal kurulumda düz metin olarak saklanmaz.',
  routing: 'Yerel model, gizlilik modu ve varsayılan görev rotası aynı backend konfigürasyonuna yazılır.',
  microphone: 'Mikrofon iznini alıp Hafiye’nin kullanacağı gerçek giriş aygıtını seçin.',
  whisper: 'whisper.cpp Türkçe STT için CUDA, Vulkan ve CPU fallback’leriyle yönetilir.',
  stt: 'Kısa bir gerçek mikrofon kaydı yerel transkripsiyon yolundan geçirilir.',
  piper: 'Piper ayrı bir yönetilen süreçte Türkçe ses modelini çalıştırır.',
  tts: 'Kurulu Türkçe sesle gerçek bir ses önizlemesi oluşturulur.',
  'wake-word': 'Hafiye wake-word ayarı gerçek gateway wake.start/wake.stop sınırına bağlanır.',
  'test-hafiye': 'Yerel backend üzerinden stateless gerçek bir Hafiye yanıtı alınır.',
  'execution-policy': 'Varsayılan FULL_AUTONOMOUS’tur; politika backend konfigürasyonuna yazılır.',
  autostart: 'hafiye-gateway.service kullanıcı systemd oturumunda etkinleştirilir.',
  doctor: 'Kurulum, sonraki açılışta terminal gerektirmeden kullanılabilir olmalıdır.'
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : {}
}

function cloneConfig(config: Record<string, unknown>): Record<string, unknown> {
  return JSON.parse(JSON.stringify(config)) as Record<string, unknown>
}

function setConfigValue(config: Record<string, unknown>, path: string[], value: unknown): void {
  let cursor = config

  for (const key of path.slice(0, -1)) {
    const next = asRecord(cursor[key])
    cursor[key] = next
    cursor = next
  }

  cursor[path[path.length - 1]] = value
}

function readConfigValue(config: Record<string, unknown> | null, path: string[]): unknown {
  let cursor: unknown = config

  for (const key of path) {
    cursor = asRecord(cursor)[key]
  }

  return cursor
}

function formatBytes(value: unknown): string {
  const bytes = Number(value)

  if (!Number.isFinite(bytes) || bytes <= 0) {
    return '—'
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)

  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`
}

function toDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(reader.error ?? new Error('Audio data could not be read'))
    reader.onload = () => resolve(String(reader.result ?? ''))
    reader.readAsDataURL(blob)
  })
}

async function captureMicrophoneClip(durationMs = 2600): Promise<Blob> {
  if (typeof MediaRecorder === 'undefined') {
    throw new Error('Bu Desktop ortamı MediaRecorder sağlamıyor.')
  }

  const stream = await getVoiceInputStream({ echoCancellation: true, noiseSuppression: true })

  try {
    const recorder = new MediaRecorder(stream)
    const chunks: BlobPart[] = []

    const blob = await new Promise<Blob>((resolve, reject) => {
      let timer: number | undefined

      const cleanup = () => {
        if (timer !== undefined) {
          window.clearTimeout(timer)
        }
      }

      recorder.ondataavailable = event => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }

      recorder.onerror = () => {
        cleanup()
        reject(new Error('Mikrofon kaydı başarısız oldu.'))
      }

      recorder.onstop = () => {
        cleanup()
        resolve(new Blob(chunks, { type: recorder.mimeType || 'audio/webm' }))
      }

      recorder.start()
      timer = window.setTimeout(() => recorder.stop(), durationMs)
    })

    if (!blob.size) {
      throw new Error('Mikrofon boş bir kayıt döndürdü.')
    }

    return blob
  } finally {
    stream.getTracks().forEach(track => track.stop())
  }
}

function StatusRow({ label, value }: { label: string; value: boolean | null | undefined }) {
  const positive = value === true
  const unknown = value === null || value === undefined

  return (
    <div className="flex items-center justify-between gap-3 border-b border-border/50 py-2 last:border-b-0">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span
        className={
          positive ? 'text-xs text-emerald-500' : unknown ? 'text-xs text-muted-foreground' : 'text-xs text-destructive'
        }
      >
        {positive ? 'Hazır' : unknown ? 'Bilinmiyor' : 'Eksik'}
      </span>
    </div>
  )
}

function Panel({ children }: { children: ReactNode }) {
  return <div className="grid gap-3 rounded-lg border border-border/70 bg-background/35 p-3">{children}</div>
}

function ErrorNotice({ children }: { children: ReactNode }) {
  return (
    <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">
      {children}
    </p>
  )
}

function computeAvailability(environment: HafiyeEnvironmentProbe | null, runtime: LocalRuntimeDoctor | null) {
  const source = environment?.compute ?? runtime?.environment ?? {}

  return {
    cuda: Boolean(source.cuda_build_available),
    vulkan: Boolean(source.vulkan_build_available && (source.vulkan_runtime_available ?? true)),
    expected: String(source.expected_auto_backend ?? 'CPU')
  }
}

function hostEnvironmentBlockers(environment: HafiyeEnvironmentProbe | null): string[] {
  if (!environment) {
    return []
  }

  const blockers: string[] = []

  if (environment.platform !== 'Linux') {
    blockers.push('Hafiye Desktop onboarding Linux gerektirir.')
  }

  if (!environment.wayland && !environment.x11) {
    blockers.push('Wayland veya X11 masaüstü oturumu bulunamadı.')
  }

  return blockers
}

export function HafiyeOnboardingWizard() {
  const [state, setState] = useState<HafiyeOnboardingState | null>(null)
  const [environment, setEnvironment] = useState<HafiyeEnvironmentProbe | null>(null)
  const [computer, setComputer] = useState<Record<string, unknown> | null>(null)
  const [runtime, setRuntime] = useState<LocalRuntimeDoctor | null>(null)
  const [models, setModels] = useState<LocalRuntimeModel[]>([])
  const [voice, setVoice] = useState<VoiceRuntimeDoctor | null>(null)
  const [autostart, setAutostart] = useState<HafiyeAutostartStatus | null>(null)
  const [doctor, setDoctor] = useState<HafiyeOnboardingDoctor | null>(null)
  const [config, setConfig] = useState<Record<string, unknown> | null>(null)
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const [selectedDevice, setSelectedDevice] = useState(() => getSelectedVoiceInputDeviceId())
  const [computeBackend, setComputeBackend] = useState<LocalRuntimeBackend>('AUTO')
  const [privacyMode, setPrivacyMode] = useState<(typeof PRIVACY_MODES)[number]>('NORMAL')
  const [executionPolicy, setExecutionPolicy] = useState<(typeof EXECUTION_POLICIES)[number]>('FULL_AUTONOMOUS')
  const [piperVoice, setPiperVoice] = useState(DEFAULT_PIPER_VOICE)
  const [downloadRepo, setDownloadRepo] = useState('')
  const [downloadFilename, setDownloadFilename] = useState('')
  const [transcript, setTranscript] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [hafiyeResponse, setHafiyeResponse] = useState('')
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const wake = useStore($wakeWord)

  useEffect(() => {
    let cancelled = false

    void getHafiyeOnboarding()
      .then(next => {
        if (!cancelled) {
          setState(next)
          setComputeBackend((next.choices.compute_backend as LocalRuntimeBackend) || 'AUTO')
          setPiperVoice(String(next.choices.piper_voice || DEFAULT_PIPER_VOICE))
        }
      })
      .catch(() => {
        // Development checkouts do not need the packaged-only wizard. If the
        // backend is too old to expose this optional boundary, keep the normal
        // Hermes surface usable instead of rendering a dead setup screen.
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const currentStep = state?.current_step ?? 'welcome'
  const stepIndex = Math.max(0, state ? HAFIYE_STEP_ORDER.indexOf(currentStep) : 0)
  const availability = computeAvailability(environment, runtime)
  const selectedModel = String(state?.choices.model_id || runtime?.server.model_id || models[0]?.id || '')
  const computerReadiness = asRecord(computer?.readiness)

  const environmentBlockers = useMemo(() => {
    return hostEnvironmentBlockers(environment)
  }, [environment])

  useEffect(() => {
    if (!state?.required || currentStep !== 'environment' || environment) {
      return
    }

    void getHafiyeOnboardingEnvironment()
      .then(setEnvironment)
      .catch(errorValue => setError(String(errorValue)))
  }, [currentStep, environment, state?.required])

  useEffect(() => {
    if (!state?.required || currentStep !== 'computer' || computer) {
      return
    }

    void getHafiyeOnboardingDoctor()
      .then(next => setComputer(next.computer))
      .catch(errorValue => setError(String(errorValue)))
  }, [computer, currentStep, state?.required])

  useEffect(() => {
    if (
      !state?.required ||
      !['compute', 'llama-runtime', 'local-model', 'local-server'].includes(currentStep) ||
      runtime
    ) {
      return
    }

    void getLocalRuntime()
      .then(setRuntime)
      .catch(errorValue => setError(String(errorValue)))
  }, [currentStep, runtime, state?.required])

  useEffect(() => {
    if (!state?.required || currentStep !== 'local-model') {
      return
    }

    void getLocalRuntimeModels()
      .then(result => setModels(result.models))
      .catch(errorValue => setError(String(errorValue)))
  }, [currentStep, state?.required])

  useEffect(() => {
    if (!state?.required || !['whisper', 'piper', 'doctor'].includes(currentStep) || voice) {
      return
    }

    void getVoiceRuntime()
      .then(setVoice)
      .catch(errorValue => setError(String(errorValue)))
  }, [currentStep, state?.required, voice])

  useEffect(() => {
    if (!state?.required || currentStep !== 'autostart' || autostart) {
      return
    }

    void getHafiyeAutostartStatus()
      .then(setAutostart)
      .catch(errorValue => setError(String(errorValue)))
  }, [autostart, currentStep, state?.required])

  useEffect(() => {
    if (!state?.required || !['routing', 'execution-policy'].includes(currentStep) || config) {
      return
    }

    void getHermesConfigRecord()
      .then(next => {
        setConfig(next)
        const mode = String(readConfigValue(next, ['hafiye', 'privacy_mode']) || 'NORMAL').toUpperCase()
        const policy = String(readConfigValue(next, ['hafiye', 'execution_policy']) || 'FULL_AUTONOMOUS').toUpperCase()

        if ((PRIVACY_MODES as readonly string[]).includes(mode)) {
          setPrivacyMode(mode as (typeof PRIVACY_MODES)[number])
        }

        if ((EXECUTION_POLICIES as readonly string[]).includes(policy)) {
          setExecutionPolicy(policy as (typeof EXECUTION_POLICIES)[number])
        }
      })
      .catch(errorValue => setError(String(errorValue)))
  }, [config, currentStep, state?.required])

  const run = async (label: string, operation: () => Promise<void>) => {
    setBusy(label)
    setError('')

    try {
      await operation()
    } catch (errorValue) {
      setError(errorValue instanceof Error ? errorValue.message : String(errorValue))
    } finally {
      setBusy('')
    }
  }

  const advance = async (choices: Record<string, boolean | number | string> = {}) => {
    if (!state) {
      return
    }

    const nextIndex = Math.min(stepIndex + 1, HAFIYE_STEP_ORDER.length - 1)
    const completedSteps = Array.from(new Set([...state.completed_steps, currentStep]))

    const next = await updateHafiyeOnboarding({
      choices: { ...state.choices, ...choices },
      completed_steps: completedSteps,
      current_step: HAFIYE_STEP_ORDER[nextIndex]
    })

    setState(next)
  }

  const saveConfig = async (mutate: (next: Record<string, unknown>) => void) => {
    const current = await getHermesConfigRecord()
    const next = cloneConfig(current)
    mutate(next)
    await saveHermesConfig(next)
    setConfig(next)
  }

  const refreshRuntime = async () => {
    const [nextRuntime, nextModels] = await Promise.all([getLocalRuntime(), getLocalRuntimeModels()])
    setRuntime(nextRuntime)
    setModels(nextModels.models)

    return nextRuntime
  }

  const refreshVoice = async () => {
    const next = await getVoiceRuntime()
    setVoice(next)

    return next
  }

  const continueEnvironment = () =>
    void run('Ortam doğrulanıyor…', async () => {
      const next = environment || (await getHafiyeOnboardingEnvironment())
      setEnvironment(next)
      const blockers = hostEnvironmentBlockers(next)

      if (blockers.length) {
        throw new Error(blockers.join(' '))
      }

      await advance()
    })

  const continueComputer = () =>
    void run('Masaüstü kontrolü doğrulanıyor…', async () => {
      const next = computer || (await getHafiyeOnboardingDoctor()).computer
      setComputer(next)

      if (next['ready'] !== true) {
        throw new Error(
          (asRecord(next).blockers as string[] | undefined)?.join(' ') || 'computer-use-linux hazır değil.'
        )
      }

      await advance()
    })

  const continueCompute = () =>
    void run('Backend seçimi kaydediliyor…', async () => {
      if (computeBackend === 'CUDA' && !availability.cuda) {
        throw new Error('CUDA bu makinede kullanılabilir değil.')
      }

      if (computeBackend === 'VULKAN' && !availability.vulkan) {
        throw new Error('Vulkan bu makinede kullanılabilir değil.')
      }

      await advance({ compute_backend: computeBackend })
    })

  const installLlama = () =>
    void run('llama.cpp kuruluyor…', async () => {
      const current = runtime || (await getLocalRuntime())

      if (!current.runtime.installed) {
        await installLocalRuntime(computeBackend)
      }

      const next = await refreshRuntime()

      if (!next.runtime.installed) {
        throw new Error('llama.cpp kurulumu tamamlandı görünmüyor.')
      }

      await advance({ compute_backend: computeBackend })
    })

  const importModel = () =>
    void run('GGUF seçiliyor…', async () => {
      const paths = await window.hermesDesktop.selectPaths({
        filters: [{ extensions: ['gguf'], name: 'GGUF models' }],
        multiple: false,
        title: 'Hafiye GGUF modelini seçin'
      })

      const path = paths[0]

      if (!path) {
        return
      }

      const model = await importLocalRuntimeModel({ path })
      const nextModels = await getLocalRuntimeModels()
      setModels(nextModels.models)
      await advance({ model_id: model.id })
    })

  const downloadModel = () =>
    void run('GGUF indiriliyor…', async () => {
      if (!downloadRepo.trim() || !downloadFilename.trim()) {
        throw new Error('Hugging Face repo ve GGUF dosya adı gereklidir.')
      }

      const model = await downloadLocalRuntimeModel({ repo_id: downloadRepo.trim(), filename: downloadFilename.trim() })
      const nextModels = await getLocalRuntimeModels()
      setModels(nextModels.models)
      await advance({ model_id: model.id })
    })

  const startModel = () =>
    void run('Yerel model başlatılıyor…', async () => {
      const model = selectedModel.trim()

      if (!model) {
        throw new Error('Önce bir GGUF model ekleyin.')
      }

      const health = await startLocalRuntimeServer({ backend: computeBackend, model_id: model })

      if (!health.ready) {
        throw new Error('llama-server başladı ancak hazır duruma geçmedi.')
      }

      await setModelAssignment({
        base_url: health.endpoint || 'http://127.0.0.1:11435/v1',
        model,
        provider: 'custom',
        scope: 'main'
      })
      const next = await refreshRuntime()

      if (!next.server.ready) {
        throw new Error('Yerel model sağlık kontrolü başarısız.')
      }

      await advance({ model_id: model })
    })

  const saveRouting = () =>
    void run('Yönlendirme kaydediliyor…', async () => {
      const model = selectedModel.trim()

      if (!model) {
        throw new Error('Varsayılan rota için yerel GGUF modeli gereklidir.')
      }

      await saveConfig(next => {
        setConfigValue(next, ['hafiye', 'privacy_mode'], privacyMode)
        setConfigValue(next, ['hafiye', 'route_slots', 'default', 'provider'], 'custom')
        setConfigValue(next, ['hafiye', 'route_slots', 'default', 'model'], model)
        setConfigValue(next, ['hafiye', 'route_slots', 'default', 'locality_policy'], privacyMode)
      })
      await advance()
    })

  const refreshMicrophones = () =>
    void run('Mikrofonlar aranıyor…', async () => {
      await requestVoiceInputPermission()
      const next = await listVoiceInputDevices()
      setDevices(next)
      const current = getSelectedVoiceInputDeviceId()

      if (current && !next.some(device => device.deviceId === current)) {
        setSelectedVoiceInputDeviceId('')
        setSelectedDevice('')
      } else {
        setSelectedDevice(current)
      }

      if (!next.length) {
        throw new Error('Hiç mikrofon giriş aygıtı bulunamadı.')
      }

      await advance()
    })

  const installWhisper = () =>
    void run('whisper.cpp kuruluyor…', async () => {
      const current = voice || (await getVoiceRuntime())

      if (!current.whisper?.ready) {
        await installWhisperRuntime(computeBackend, DEFAULT_WHISPER_MODEL)
      }

      const next = await refreshVoice()

      if (!next.whisper?.ready) {
        throw new Error('whisper.cpp runtime/model hazır değil.')
      }

      await saveConfig(configNext => {
        setConfigValue(configNext, ['stt', 'enabled'], true)
        setConfigValue(configNext, ['stt', 'provider'], 'local')
        setConfigValue(configNext, ['stt', 'local', 'model'], DEFAULT_WHISPER_MODEL)
        setConfigValue(configNext, ['stt', 'local', 'language'], 'tr')
      })
      await advance()
    })

  const testStt = () =>
    void run('Mikrofon kaydediliyor…', async () => {
      const clip = await captureMicrophoneClip()
      const dataUrl = await toDataUrl(clip)
      const result = await transcribeAudio(dataUrl, clip.type)

      if (!result.transcript.trim()) {
        throw new Error('STT boş bir transcript döndürdü.')
      }

      setTranscript(result.transcript.trim())
      await advance()
    })

  const installPiper = () =>
    void run('Piper Türkçe sesi kuruluyor…', async () => {
      const current = voice || (await getVoiceRuntime())
      const installedVoice = current.piper?.voices as Array<{ name?: string }> | undefined

      if (!current.piper?.ready || !installedVoice?.some(item => item.name === piperVoice)) {
        await installPiperRuntime(piperVoice)
      }

      const next = await refreshVoice()

      if (!next.piper?.ready) {
        throw new Error('Piper runtime/Türkçe ses hazır değil.')
      }

      await saveConfig(configNext => {
        setConfigValue(configNext, ['tts', 'provider'], 'piper')
        setConfigValue(configNext, ['tts', 'piper', 'voice'], piperVoice)
      })
      await advance({ piper_voice: piperVoice })
    })

  const testTts = () =>
    void run('Türkçe ses oluşturuluyor…', async () => {
      const result = await getPiperVoicePreview('Merhaba, ben Hafiye. Türkçe ses testi.', piperVoice)

      if (!result.data_url) {
        throw new Error('Piper ses önizlemesi boş döndü.')
      }

      setAudioUrl(result.data_url)
      await advance({ piper_voice: piperVoice })
    })

  const configureWakeWord = (enabled: boolean) =>
    void run('Wake-word ayarı kaydediliyor…', async () => {
      if (enabled && !wake.listening) {
        await toggleWakeWord()
      } else if (!enabled && wake.listening) {
        await toggleWakeWord()
      }

      const nextWake = $wakeWord.get()

      if (enabled && !nextWake.listening) {
        throw new Error(nextWake.notice || 'Wake-word başlatılamadı.')
      }

      if (!enabled && nextWake.listening) {
        throw new Error(nextWake.notice || 'Wake-word durdurulamadı.')
      }

      await saveConfig(next => setConfigValue(next, ['wake_word', 'enabled'], enabled))
      await advance({ wake_word_enabled: enabled })
    })

  const testHafiye = () =>
    void run('Hafiye yanıtı bekleniyor…', async () => {
      const response = await requestOneShot({
        input: 'Hafiye hazır mı?',
        instructions: 'Reply with exactly: Hafiye hazır.',
        maxTokens: 16,
        sessionId: null
      })

      if (!response.trim()) {
        throw new Error('Yerel model boş yanıt döndürdü.')
      }

      setHafiyeResponse(response.trim())
      await advance()
    })

  const saveExecutionPolicy = () =>
    void run('Çalıştırma politikası kaydediliyor…', async () => {
      await saveConfig(next => setConfigValue(next, ['hafiye', 'execution_policy'], executionPolicy))
      await advance({ execution_policy: executionPolicy })
    })

  const enableAutostart = () =>
    void run('Kullanıcı autostart etkinleştiriliyor…', async () => {
      const next = await enableHafiyeAutostart()
      setAutostart(next)

      if (!next.enabled) {
        throw new Error(next.message || 'hafiye-gateway.service etkinleştirilemedi.')
      }

      await advance()
    })

  const runDoctor = () =>
    void run('Son doctor çalışıyor…', async () => {
      const next = await getHafiyeOnboardingDoctor()
      setDoctor(next)

      if (!next.ok || next.blockers.length) {
        throw new Error(next.blockers.join(' ') || 'Doctor blocker bildirdi.')
      }

      const completed = await completeHafiyeOnboarding()
      setState(completed)
    })

  const beginSetup = () => void run('Kurulum başlıyor…', () => advance())

  const skipRemoteProvider = () =>
    void run('Uzak sağlayıcı daha sonraya bırakılıyor…', () => advance({ remote_provider_skipped: true }))

  const skipGemini = () => void run('Gemini daha sonraya bırakılıyor…', () => advance({ gemini_skipped: true }))

  if (loading || !state?.required || state.completed) {
    return null
  }

  const currentTitle = STEP_TITLES[currentStep]
  const currentDescription = STEP_DESCRIPTIONS[currentStep]
  const progress = Math.round((stepIndex / (HAFIYE_STEP_ORDER.length - 1)) * 100)

  return (
    <div
      aria-labelledby="hafiye-onboarding-title"
      aria-modal="true"
      className="fixed inset-0 z-[100] flex items-center justify-center bg-(--ui-chat-surface-background) p-5"
      data-glass-opaque
      role="dialog"
    >
      <div className="w-full max-w-3xl overflow-hidden rounded-xl border border-(--stroke-nous) bg-(--ui-chat-bubble-background) shadow-nous">
        <header className="border-b border-border/60 px-5 py-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-primary">HAFİYE KURULUMU</p>
              <h1 className="mt-1 text-lg font-semibold" id="hafiye-onboarding-title">
                {currentTitle}
              </h1>
              <p className="mt-1 max-w-2xl text-xs leading-5 text-muted-foreground">{currentDescription}</p>
            </div>
            <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
              {stepIndex + 1} / {HAFIYE_STEP_ORDER.length}
            </span>
          </div>
          <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${Math.max(3, progress)}%` }}
            />
          </div>
        </header>

        <main className="max-h-[70dvh] overflow-y-auto p-5">
          {error ? <ErrorNotice>{error}</ErrorNotice> : null}
          <div className={error ? 'mt-3' : ''}>
            {renderStepContent({
              advance,
              autostart,
              availability,
              audioUrl,
              busy,
              computer,
              computerReadiness,
              computeBackend,
              config,
              continueComputer,
              continueCompute,
              continueEnvironment,
              currentStep,
              devices,
              doctor,
              downloadFilename,
              downloadModel,
              downloadRepo,
              enableAutostart,
              environment,
              environmentBlockers,
              executionPolicy,
              beginSetup,
              hafiyeResponse,
              importModel,
              installLlama,
              installPiper,
              installWhisper,
              models,
              piperVoice,
              privacyMode,
              refreshMicrophones,
              runDoctor,
              runtime,
              saveExecutionPolicy,
              saveRouting,
              selectedDevice,
              selectedModel,
              setComputeBackend,
              setDownloadFilename,
              setDownloadRepo,
              setExecutionPolicy,
              setPiperVoice,
              setPrivacyMode,
              setSelectedDevice,
              skipGemini,
              skipRemoteProvider,
              startModel,
              testHafiye,
              testStt,
              testTts,
              transcript,
              voice,
              wake,
              configureWakeWord
            })}
          </div>
        </main>
      </div>
    </div>
  )
}

const HAFIYE_STEP_ORDER = Object.keys(STEP_TITLES) as HafiyeOnboardingStep[]

interface StepContentProps {
  advance: (choices?: Record<string, boolean | number | string>) => Promise<void>
  autostart: HafiyeAutostartStatus | null
  availability: { cuda: boolean; expected: string; vulkan: boolean }
  audioUrl: string
  busy: string
  computer: Record<string, unknown> | null
  computerReadiness: Record<string, unknown>
  computeBackend: LocalRuntimeBackend
  config: Record<string, unknown> | null
  continueComputer: () => void
  continueCompute: () => void
  continueEnvironment: () => void
  currentStep: HafiyeOnboardingStep
  devices: MediaDeviceInfo[]
  doctor: HafiyeOnboardingDoctor | null
  downloadFilename: string
  downloadModel: () => void
  downloadRepo: string
  enableAutostart: () => void
  environment: HafiyeEnvironmentProbe | null
  environmentBlockers: string[]
  executionPolicy: (typeof EXECUTION_POLICIES)[number]
  beginSetup: () => void
  hafiyeResponse: string
  importModel: () => void
  installLlama: () => void
  installPiper: () => void
  installWhisper: () => void
  models: LocalRuntimeModel[]
  piperVoice: string
  privacyMode: (typeof PRIVACY_MODES)[number]
  refreshMicrophones: () => void
  runDoctor: () => void
  runtime: LocalRuntimeDoctor | null
  saveExecutionPolicy: () => void
  saveRouting: () => void
  selectedDevice: string
  selectedModel: string
  setComputeBackend: (value: LocalRuntimeBackend) => void
  setDownloadFilename: (value: string) => void
  setDownloadRepo: (value: string) => void
  setExecutionPolicy: (value: (typeof EXECUTION_POLICIES)[number]) => void
  setPiperVoice: (value: string) => void
  setPrivacyMode: (value: (typeof PRIVACY_MODES)[number]) => void
  setSelectedDevice: (value: string) => void
  skipGemini: () => void
  skipRemoteProvider: () => void
  startModel: () => void
  testHafiye: () => void
  testStt: () => void
  testTts: () => void
  transcript: string
  voice: VoiceRuntimeDoctor | null
  wake: { enabled: boolean; listening: boolean; pending: boolean }
  configureWakeWord: (enabled: boolean) => void
}

function ActionButton({ busy, children, onClick }: { busy: string; children: ReactNode; onClick: () => void }) {
  return (
    <Button disabled={Boolean(busy)} onClick={onClick} type="button">
      {busy || children}
    </Button>
  )
}

function renderStepContent(props: StepContentProps): ReactNode {
  const {
    advance,
    autostart,
    availability,
    audioUrl,
    busy,
    computer,
    computerReadiness,
    computeBackend,
    config,
    continueComputer,
    continueCompute,
    continueEnvironment,
    currentStep,
    devices,
    doctor,
    downloadFilename,
    downloadModel,
    downloadRepo,
    enableAutostart,
    environment,
    environmentBlockers,
    executionPolicy,
    beginSetup,
    hafiyeResponse,
    importModel,
    installLlama,
    installPiper,
    installWhisper,
    models,
    piperVoice,
    privacyMode,
    refreshMicrophones,
    runDoctor,
    runtime,
    saveExecutionPolicy,
    saveRouting,
    selectedDevice,
    selectedModel,
    setComputeBackend,
    setDownloadFilename,
    setDownloadRepo,
    setExecutionPolicy,
    setPiperVoice,
    setPrivacyMode,
    setSelectedDevice,
    skipGemini,
    skipRemoteProvider,
    startModel,
    testHafiye,
    testStt,
    testTts,
    transcript,
    voice,
    wake,
    configureWakeWord
  } = props

  switch (currentStep) {
    case 'welcome':
      return (
        <Panel>
          <p className="text-sm leading-6">
            Bu sihirbaz Hafiye’yi gerçek makinenizde hazırlar. Kurulum tamamlanana kadar hiçbir adım başarılı kabul
            edilmez.
          </p>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={beginSetup}>
              Kuruluma başla
            </ActionButton>
          </div>
        </Panel>
      )

    case 'environment':
      return (
        <Panel>
          {!environment ? (
            <p className="text-xs text-muted-foreground">Linux ortamı okunuyor…</p>
          ) : (
            <div className="grid gap-1 sm:grid-cols-2">
              <StatusRow label="Platform" value={environment.platform === 'Linux'} />
              <StatusRow label="Wayland / X11" value={Boolean(environment.wayland || environment.x11)} />
              <div className="border-b border-border/50 py-2 text-xs">
                <span className="text-muted-foreground">Kernel</span>
                <span className="float-right">{environment.kernel || '—'}</span>
              </div>
              <div className="border-b border-border/50 py-2 text-xs">
                <span className="text-muted-foreground">Desktop / GNOME</span>
                <span className="float-right">
                  {environment.desktop || '—'} {environment.gnome_version || ''}
                </span>
              </div>
              <div className="border-b border-border/50 py-2 text-xs">
                <span className="text-muted-foreground">CPU</span>
                <span className="float-right">
                  {environment.cpu || '—'} ({environment.cpu_count || '—'} thread)
                </span>
              </div>
              <div className="border-b border-border/50 py-2 text-xs">
                <span className="text-muted-foreground">RAM</span>
                <span className="float-right">{formatBytes(environment.memory?.total)}</span>
              </div>
              <div className="border-b border-border/50 py-2 text-xs">
                <span className="text-muted-foreground">Python / Node</span>
                <span className="float-right">
                  {environment.python || '—'} / {environment.node || '—'}
                </span>
              </div>
              <div className="border-b border-border/50 py-2 text-xs">
                <span className="text-muted-foreground">Audio</span>
                <span className="float-right">{environment.audio?.wpctl ? 'PipeWire/WirePlumber' : 'wpctl yok'}</span>
              </div>
            </div>
          )}
          {environmentBlockers.length ? <ErrorNotice>{environmentBlockers.join(' ')}</ErrorNotice> : null}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={continueEnvironment}>
              Ortamı doğrula ve devam et
            </ActionButton>
          </div>
        </Panel>
      )
    case 'computer': {
      const readiness = Object.entries(computerReadiness)

      return (
        <Panel>
          {!computer ? (
            <p className="text-xs text-muted-foreground">computer-use-linux doctor çalışıyor…</p>
          ) : (
            <>
              <div className="grid gap-1">
                {readiness.map(([key, value]) => (
                  <StatusRow key={key} label={key} value={value === true} />
                ))}
              </div>
              {Array.isArray(computer.blockers) && computer.blockers.length ? (
                <ErrorNotice>{computer.blockers.join(' ')}</ErrorNotice>
              ) : null}
            </>
          )}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={continueComputer}>
              Doctor sonucunu doğrula
            </ActionButton>
          </div>
        </Panel>
      )
    }

    case 'compute':
      return (
        <Panel>
          <div className="grid gap-2 sm:grid-cols-2">
            {[
              ['AUTO', 'Auto', true, `Öncelik: ${availability.expected}`],
              ['CUDA', 'CUDA', availability.cuda, 'NVIDIA CUDA'],
              ['VULKAN', 'Vulkan', availability.vulkan, 'Vulkan fallback'],
              ['CPU', 'CPU', true, 'CPU fallback']
            ].map(([value, label, available, detail]) => (
              <label
                className={`flex cursor-pointer items-start gap-2 rounded-md border p-3 ${computeBackend === value ? 'border-primary bg-primary/10' : 'border-border/60'} ${available ? '' : 'cursor-not-allowed opacity-50'}`}
                key={String(value)}
              >
                <input
                  checked={computeBackend === value}
                  disabled={!available}
                  name="hafiye-compute-backend"
                  onChange={() => setComputeBackend(value as LocalRuntimeBackend)}
                  type="radio"
                />
                <span>
                  <span className="block text-xs font-medium">{label}</span>
                  <span className="block text-[0.7rem] text-muted-foreground">{detail}</span>
                </span>
              </label>
            ))}
          </div>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={continueCompute}>
              Backend’i kaydet
            </ActionButton>
          </div>
        </Panel>
      )

    case 'llama-runtime':
      return (
        <Panel>
          <StatusRow label="llama-server kurulu" value={runtime?.runtime.installed} />
          <div className="text-xs text-muted-foreground">
            Seçim: {computeBackend}. İlk kurulum gerçek kaynak checkout/build adımını çalıştırabilir.
          </div>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={installLlama}>
              {runtime?.runtime.installed ? 'Runtime’ı doğrula' : 'llama.cpp kur'}
            </ActionButton>
          </div>
        </Panel>
      )

    case 'local-model':
      return (
        <Panel>
          <div className="grid gap-2">
            <p className="text-xs font-medium">İçe aktarılmış modeller</p>
            {models.length ? (
              <select
                aria-label="Yerel GGUF modeli"
                className="h-9 rounded-md border border-input bg-background px-2 text-xs"
                defaultValue={selectedModel}
                onChange={event => void advance({ model_id: event.target.value })}
              >
                {models.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.id}
                  </option>
                ))}
              </select>
            ) : (
              <p className="text-xs text-muted-foreground">Henüz GGUF model kaydı yok.</p>
            )}
          </div>
          <div className="flex justify-end">
            <Button disabled={Boolean(busy)} onClick={importModel} type="button" variant="outline">
              GGUF seç ve içe aktar
            </Button>
          </div>
          <div className="grid gap-2 border-t border-border/50 pt-3 sm:grid-cols-2">
            <Input
              aria-label="Hugging Face repo"
              onChange={event => setDownloadRepo(event.target.value)}
              placeholder="org/repo"
              value={downloadRepo}
            />
            <Input
              aria-label="GGUF dosya adı"
              onChange={event => setDownloadFilename(event.target.value)}
              placeholder="model.Q4_K_M.gguf"
              value={downloadFilename}
            />
          </div>
          <div className="flex justify-end">
            <Button
              disabled={Boolean(busy) || !downloadRepo.trim() || !downloadFilename.trim()}
              onClick={downloadModel}
              type="button"
              variant="outline"
            >
              GGUF indir
            </Button>
          </div>
          {selectedModel ? <p className="text-xs text-muted-foreground">Seçili model: {selectedModel}</p> : null}
        </Panel>
      )

    case 'local-server':
      return (
        <Panel>
          <StatusRow label="llama-server çalışıyor" value={runtime?.server.running} />
          <StatusRow label="Model endpoint hazır" value={runtime?.server.ready} />
          <div className="text-xs text-muted-foreground">
            Model: {selectedModel || 'seçilmedi'} · Endpoint: {runtime?.server.endpoint || '127.0.0.1:11435/v1'}
          </div>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={startModel}>
              Yerel modeli başlat ve bağla
            </ActionButton>
          </div>
        </Panel>
      )

    case 'remote-provider':
      return (
        <Panel>
          <p className="text-sm">
            Uzak OpenAI-uyumlu sağlayıcı zorunlu değildir. Daha sonra Ayarlar → Providers üzerinden gerçek endpoint ve
            Secret Service credential’ı eklenebilir.
          </p>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={skipRemoteProvider}>
              Şimdilik yerel devam et
            </ActionButton>
          </div>
        </Panel>
      )

    case 'gemini':
      return (
        <Panel>
          <p className="text-sm">
            Gemini isteğe bağlıdır. Bu akışta anahtar istemiyoruz; daha sonra Ayarlar → Providers üzerinden güvenli
            olarak yapılandırılabilir.
          </p>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={skipGemini}>
              Gemini’yi daha sonra ayarla
            </ActionButton>
          </div>
        </Panel>
      )

    case 'routing':
      return (
        <Panel>
          <div className="grid gap-2 sm:grid-cols-2">
            <label className="grid gap-1 text-xs">
              <span className="text-muted-foreground">Gizlilik modu</span>
              <select
                className="h-9 rounded-md border border-input bg-background px-2"
                onChange={event => setPrivacyMode(event.target.value as (typeof PRIVACY_MODES)[number])}
                value={privacyMode}
              >
                {PRIVACY_MODES.map(mode => (
                  <option key={mode}>{mode}</option>
                ))}
              </select>
            </label>
            <div className="grid gap-1 text-xs">
              <span className="text-muted-foreground">Varsayılan yerel model</span>
              <span className="rounded-md border border-border/60 px-2 py-2">{selectedModel || '—'}</span>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Mevcut config: {String(readConfigValue(config, ['hafiye', 'privacy_mode']) || privacyMode)}. AUTO/yerel
            model aynı shared route sınırından kullanılacak.
          </p>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={saveRouting}>
              Yönlendirmeyi kaydet
            </ActionButton>
          </div>
        </Panel>
      )

    case 'microphone':
      return (
        <Panel>
          <p className="text-xs text-muted-foreground">
            İzin verildikten sonra gerçek audio input cihazları listelenir.
          </p>
          <select
            aria-label="Hafiye mikrofonu"
            className="h-9 rounded-md border border-input bg-background px-2 text-xs"
            disabled={!devices.length}
            onChange={event => {
              setSelectedDevice(event.target.value)
              setSelectedVoiceInputDeviceId(event.target.value)
            }}
            value={selectedDevice}
          >
            <option value="">Sistem varsayılanı</option>
            {devices.map((device, index) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Mikrofon ${index + 1}`}
              </option>
            ))}
          </select>
          {devices.length ? <p className="text-xs text-emerald-500">{devices.length} mikrofon bulundu.</p> : null}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={refreshMicrophones}>
              {devices.length ? 'Mikrofonu doğrula' : 'İzin ver ve mikrofonları bul'}
            </ActionButton>
          </div>
        </Panel>
      )

    case 'whisper':
      return (
        <Panel>
          <StatusRow label="whisper.cpp hazır" value={voice?.whisper?.ready as boolean | undefined} />
          <div className="text-xs text-muted-foreground">
            Model: {DEFAULT_WHISPER_MODEL} · Dil: Türkçe (tr) · Backend: {computeBackend}
          </div>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={installWhisper}>
              {voice?.whisper?.ready ? 'STT runtime’ı doğrula' : 'whisper.cpp kur'}
            </ActionButton>
          </div>
        </Panel>
      )

    case 'stt':
      return (
        <Panel>
          <p className="text-xs text-muted-foreground">
            Kayıt yaklaşık 2,6 saniye sürer. Gerçek mikrofona Türkçe bir cümle söyleyin.
          </p>
          {transcript ? (
            <p className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-sm">{transcript}</p>
          ) : null}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={testStt}>
              Kayıt yap ve Türkçe STT test et
            </ActionButton>
          </div>
        </Panel>
      )

    case 'piper':
      return (
        <Panel>
          <label className="grid gap-1 text-xs">
            <span className="text-muted-foreground">Türkçe Piper sesi</span>
            <Input onChange={event => setPiperVoice(event.target.value)} value={piperVoice} />
          </label>
          <StatusRow label="Piper hazır" value={voice?.piper?.ready as boolean | undefined} />
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={installPiper}>
              {voice?.piper?.ready ? 'Piper’ı doğrula ve yapılandır' : 'Piper + Türkçe sesi kur'}
            </ActionButton>
          </div>
        </Panel>
      )

    case 'tts':
      return (
        <Panel>
          <p className="text-xs text-muted-foreground">{piperVoice} ile gerçek yerel ses önizlemesi.</p>
          {audioUrl ? <audio className="w-full" controls src={audioUrl} /> : null}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={testTts}>
              Türkçe TTS testi yap
            </ActionButton>
          </div>
        </Panel>
      )

    case 'wake-word':
      return (
        <Panel>
          <StatusRow label="Wake-word gateway durumu" value={wake.listening} />
          <p className="text-xs text-muted-foreground">
            Mevcut ayar: {wake.enabled ? 'etkin' : 'devre dışı'}. Seçim gerçek gateway config’ine yazılır.
          </p>
          <div className="flex flex-wrap justify-end gap-2">
            <Button disabled={Boolean(busy || wake.pending)} onClick={() => configureWakeWord(true)} type="button">
              Hafiye’yi etkinleştir
            </Button>
            <Button
              disabled={Boolean(busy || wake.pending)}
              onClick={() => configureWakeWord(false)}
              type="button"
              variant="outline"
            >
              Devre dışı bırak ve devam et
            </Button>
          </div>
        </Panel>
      )

    case 'test-hafiye':
      return (
        <Panel>
          <p className="text-xs text-muted-foreground">
            Bu test stateless gerçek gateway isteği gönderir; konuşma geçmişine sahte mesaj eklemez.
          </p>
          {hafiyeResponse ? (
            <p className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-sm">
              {hafiyeResponse}
            </p>
          ) : null}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={testHafiye}>
              “Hafiye” testini çalıştır
            </ActionButton>
          </div>
        </Panel>
      )

    case 'execution-policy':
      return (
        <Panel>
          <label className="grid gap-1 text-xs">
            <span className="text-muted-foreground">Host çalıştırma politikası</span>
            <select
              className="h-9 rounded-md border border-input bg-background px-2"
              onChange={event => setExecutionPolicy(event.target.value as (typeof EXECUTION_POLICIES)[number])}
              value={executionPolicy}
            >
              {EXECUTION_POLICIES.map(policy => (
                <option key={policy}>{policy}</option>
              ))}
            </select>
          </label>
          <p className="text-xs text-muted-foreground">
            Varsayılan politika FULL_AUTONOMOUS’tur. Root işlemleri yine hafiye-rootd üzerinden yürür.
          </p>
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={saveExecutionPolicy}>
              Politikayı kaydet
            </ActionButton>
          </div>
        </Panel>
      )

    case 'autostart':
      return (
        <Panel>
          <StatusRow label="hafiye-gateway.service etkin" value={autostart?.enabled} />
          <StatusRow label="hafiye-gateway.service aktif" value={autostart?.active} />
          {autostart?.message ? <p className="text-xs text-muted-foreground">{autostart.message}</p> : null}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={enableAutostart}>
              {autostart?.enabled ? 'Autostart’ı doğrula' : 'Autostart’ı etkinleştir'}
            </ActionButton>
          </div>
        </Panel>
      )

    case 'doctor':
      return (
        <Panel>
          {!doctor ? (
            <p className="text-xs text-muted-foreground">Final doctor henüz çalıştırılmadı.</p>
          ) : (
            <>
              <StatusRow label="Doctor genel sonucu" value={doctor.ok && doctor.blockers.length === 0} />
              <StatusRow label="Environment Linux" value={doctor.environment.platform === 'Linux'} />
              <StatusRow label="Computer-use readiness" value={doctor.computer.ready === true} />
              <StatusRow
                label="Local model server"
                value={asRecord(asRecord(doctor.local_runtime).server).ready === true}
              />
              <StatusRow label="Voice stack" value={doctor.voice.ok} />
              <StatusRow label="User autostart" value={doctor.autostart.enabled} />
              {doctor.blockers.length ? <ErrorNotice>{doctor.blockers.join(' ')}</ErrorNotice> : null}
            </>
          )}
          <div className="flex justify-end">
            <ActionButton busy={busy} onClick={runDoctor}>
              {doctor?.ok ? 'Kurulumu tamamla' : 'Final doctor çalıştır'}
            </ActionButton>
          </div>
        </Panel>
      )
  }
}
