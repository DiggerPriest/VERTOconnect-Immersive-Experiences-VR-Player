package org.vrpassthroughplayer.plugin

import android.Manifest
import android.app.Activity
import android.app.ActivityManager
import android.content.ComponentName
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.webkit.PermissionRequest
import android.webkit.WebChromeClient
import android.webkit.ConsoleMessage
import android.webkit.WebResourceRequest
import android.webkit.WebResourceError
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.LinearLayout
import android.widget.FrameLayout
import android.widget.ProgressBar
import android.widget.TextView
import java.util.concurrent.atomic.AtomicBoolean
import java.lang.ref.WeakReference

/** A system 2D panel over the immersive activity, not a browser injected into Godot's renderer. */
class TalkToJessActivity : Activity() {
    private val home = "https://vertoconnect.au/quest"
    private var webView: WebView? = null
    private var pendingAudio: PermissionRequest? = null
    private var pageFailed = false
    private var diagnosticStatus: TextView? = null
    private val probing = AtomicBoolean(false)
    private var returnStarted = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        current = WeakReference(this)
        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.BLACK)
        }
        val close = Button(this).apply {
            text = "Return to videos"
            setOnClickListener { returnToPlayer() }
        }
        container.addView(close, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        val microphoneStatus = TextView(this).apply {
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.rgb(72, 46, 20))
            gravity = Gravity.CENTER
            setPadding(16, 8, 16, 8)
            visibility = View.GONE
        }
        container.addView(microphoneStatus, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        val checkMicrophone = Button(this).apply {
            visibility = View.GONE
            text = "Test headset microphone"
            setOnClickListener {
                if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                    runMicrophoneProbe()
                } else {
                    requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), PROBE_PERMISSION)
                }
            }
        }
        container.addView(checkMicrophone, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        diagnosticStatus = TextView(this).apply {
            visibility = View.GONE
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.rgb(30, 33, 40))
            setPadding(16, 8, 16, 8)
            text = "Mic test: stop any Jess conversation, then press the button and speak."
        }
        container.addView(diagnosticStatus, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        val stage = FrameLayout(this)
        val browser = WebView(this)
        webView = browser
        browser.setBackgroundColor(Color.rgb(12, 14, 20))
        stage.addView(browser, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        val loading = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.rgb(12, 14, 20))
        }
        fun showLoading() {
            loading.removeAllViews()
            loading.addView(ProgressBar(this@TalkToJessActivity))
            loading.addView(TextView(this@TalkToJessActivity).apply {
                text = "Opening Talk to Jess…"
                setTextColor(Color.WHITE)
                gravity = Gravity.CENTER
                setPadding(0, 24, 0, 0)
            })
            loading.visibility = View.VISIBLE
        }
        showLoading()
        stage.addView(loading, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        browser.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = false
            allowContentAccess = false
            mediaPlaybackRequiresUserGesture = true
            mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
        }
        browser.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                request.isForMainFrame && !JessWebPolicy.trusted(request.url.toString())

            override fun onPageStarted(view: WebView, url: String, favicon: android.graphics.Bitmap?) {
                pageFailed = false
                showLoading()
            }

            override fun onPageFinished(view: WebView, url: String) {
                if (!pageFailed) {
                    loading.visibility = View.GONE
                    if (JessWebPolicy.trusted(url)) view.evaluateJavascript(MICROPHONE_DIAGNOSTICS, null)
                }
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
                if (!request.isForMainFrame) return
                pageFailed = true
                loading.removeAllViews()
                loading.addView(TextView(this@TalkToJessActivity).apply {
                    text = "Couldn’t open Talk to Jess. Check the internet connection and try again."
                    setTextColor(Color.WHITE)
                    gravity = Gravity.CENTER
                    setPadding(32, 0, 32, 24)
                })
                loading.addView(Button(this@TalkToJessActivity).apply {
                    text = "Try again"
                    setOnClickListener { view.loadUrl(home) }
                })
                loading.visibility = View.VISIBLE
            }
        }
        browser.webChromeClient = object : WebChromeClient() {
            override fun onConsoleMessage(message: ConsoleMessage): Boolean {
                val value = message.message().removePrefix("VERTO_MIC:")
                if (message.message().startsWith("VERTO_MIC:")) {
                    val safeStatus = if (value in setOf("ready", "NotAllowedError", "SecurityError", "NotFoundError", "unavailable", "NotReadableError", "AbortError", "OverconstrainedError")) value else "other"
                    val explanation = when (safeStatus) {
                        "ready" -> ""
                        "NotAllowedError", "SecurityError" -> "Microphone blocked by the device or browser."
                        "NotFoundError", "unavailable" -> "No microphone is available to the browser."
                        "NotReadableError" -> "Browser microphone capture failed (NotReadableError)."
                        "AbortError" -> "Browser microphone capture was interrupted (AbortError)."
                        "OverconstrainedError" -> "The headset microphone doesn't support the requested audio settings."
                        else -> "Microphone could not start."
                    }
                    microphoneStatus.text = explanation
                    microphoneStatus.visibility = if (explanation.isEmpty()) View.GONE else View.VISIBLE
                    android.util.Log.i("TalkToJess", "Microphone status: $safeStatus")
                    return true
                }
                return super.onConsoleMessage(message)
            }
            override fun onPermissionRequest(request: PermissionRequest) {
                runOnUiThread {
                    val resources = request.resources
                    if (!JessWebPolicy.canCaptureAudio(request.origin.toString(), resources) || pendingAudio != null) {
                        diagnosticStatus?.text = "Browser microphone request: blocked or another request is pending."
                        request.deny()
                    } else if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                        diagnosticStatus?.text = "Browser microphone request: permitted for VERTOconnect."
                        request.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
                    } else {
                        diagnosticStatus?.text = "Browser microphone request: awaiting headset permission."
                        pendingAudio = request
                        requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), AUDIO_PERMISSION)
                    }
                }
            }

            override fun onPermissionRequestCanceled(request: PermissionRequest) {
                if (pendingAudio === request) pendingAudio = null
            }
        }
        container.addView(stage, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        setContentView(container)
        browser.loadUrl(home)
    }

    @Deprecated("Android permission callback")
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PROBE_PERMISSION) {
            if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) runMicrophoneProbe()
            else diagnosticStatus?.text = "Mic test: headset permission was not granted."
            return
        }
        if (requestCode != AUDIO_PERMISSION) return
        val request = pendingAudio ?: return
        pendingAudio = null
        if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED && JessWebPolicy.canCaptureAudio(request.origin.toString(), request.resources)) {
            diagnosticStatus?.text = "Browser microphone request: permitted for VERTOconnect."
            request.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
        } else {
            diagnosticStatus?.text = "Browser microphone request: headset permission was not granted."
            request.deny()
        }
    }

    /** Brief native capture probe. Audio samples are never stored or transmitted. */
    private fun runMicrophoneProbe() {
        if (!probing.compareAndSet(false, true)) return
        diagnosticStatus?.text = "Mic test: keep speaking for three seconds…"
        Thread({
            val result = try {
                val mic = probeAudioSource(MediaRecorder.AudioSource.MIC)
                val recognition = probeAudioSource(MediaRecorder.AudioSource.VOICE_RECOGNITION)
                val communication = probeAudioSource(MediaRecorder.AudioSource.VOICE_COMMUNICATION)
                "Mic test: MIC $mic | RECOGNITION $recognition | COMMUNICATION $communication. Sound detected does not confirm Jess received it."
            } finally {
                probing.set(false)
            }
            runOnUiThread { if (!isFinishing && !isDestroyed) diagnosticStatus?.text = result }
        }, "VertoMicProbe").start()
    }

    private fun probeAudioSource(source: Int): String {
            var recorder: AudioRecord? = null
            return try {
                val rate = 16000
                val minimum = AudioRecord.getMinBufferSize(rate, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
                if (minimum <= 0) {
                    "unsupported ($minimum)"
                } else {
                    val instance = AudioRecord(source, rate, AudioFormat.CHANNEL_IN_MONO,
                        AudioFormat.ENCODING_PCM_16BIT, maxOf(minimum, rate))
                    recorder = instance
                    if (instance.state != AudioRecord.STATE_INITIALIZED) {
                        "not initialized"
                    } else {
                        instance.startRecording()
                        if (instance.recordingState != AudioRecord.RECORDSTATE_RECORDING) {
                            "not started"
                        } else {
                            val samples = ShortArray(1024)
                            var total = 0
                            var errorCode = 0
                            var audible = false
                            repeat(20) {
                                if (errorCode == 0) {
                                    val count = instance.read(samples, 0, samples.size, AudioRecord.READ_NON_BLOCKING)
                                    if (count < 0) errorCode = count else {
                                        total += count
                                        for (index in 0 until count) {
                                            if (kotlin.math.abs(samples[index].toInt()) > 128) audible = true
                                        }
                                    }
                                    samples.fill(0)
                                    Thread.sleep(50)
                                }
                            }
                            when {
                                total <= 0 -> "no frames ($errorCode)"
                                audible -> "sound detected"
                                else -> "silent"
                            }
                        }
                    }
                }
            } catch (error: Exception) {
                "failed (${error.javaClass.simpleName})"
            } finally {
                runCatching { recorder?.stop() }
                recorder?.release()
            }
    }

    override fun onDestroy() {
        pendingAudio?.deny()
        pendingAudio = null
        closeBrowser()
        diagnosticStatus = null
        if (isFinishing && !returnStarted) schedulePlayerRestore()
        if (current?.get() === this) current = null
        super.onDestroy()
    }

    private fun closeBrowser() {
        webView?.apply {
            stopLoading()
            loadUrl("about:blank")
            (parent as? ViewGroup)?.removeView(this)
            destroy()
        }
        webView = null
    }

    private fun returnToPlayer() {
        if (returnStarted) return
        returnStarted = true
        closeBrowser()
        val playerTask = intent.getIntExtra(EXTRA_PLAYER_TASK, -1)
        if (JessWebPolicy.removePanelTask(isTaskRoot, taskId, playerTask)) finishAndRemoveTask() else finish()
        schedulePlayerRestore()
    }

    @Deprecated("System panel back")
    override fun onBackPressed() = returnToPlayer()

    private fun schedulePlayerRestore() {
        val app = applicationContext
        val component = ComponentName.unflattenFromString(intent.getStringExtra(EXTRA_PLAYER_COMPONENT) ?: "")
        val playerTask = intent.getIntExtra(EXTRA_PLAYER_TASK, -1)
        // The panel must first relinquish its system focus. Starting the immersive
        // activity while the panel is still active can leave XR merely VISIBLE.
        Handler(Looper.getMainLooper()).postDelayed({
            if (current?.get()?.let { !it.isFinishing && !it.isDestroyed } == true) return@postDelayed
            val launched = component != null && component.packageName == app.packageName && runCatching {
                app.startActivity(Intent(Intent.ACTION_MAIN).setComponent(component)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT))
            }.isSuccess
            if (!launched && playerTask >= 0) runCatching {
                val manager = app.getSystemService(ActivityManager::class.java)
                manager.appTasks.firstOrNull { it.taskInfo.id == playerTask }?.moveToFront()
            }
        }, 500)
    }

    private fun endSessionOnRemoval() {
        val browser = webView ?: return
        if (!JessWebPolicy.trusted(browser.url ?: "")) return
        // Ask the site to end the call, then reload to disconnect any remaining browser media.
        browser.evaluateJavascript("document.querySelector('[aria-label=\"End call\"]')?.click()", null)
        browser.postDelayed({
            if (!isFinishing && !isDestroyed && webView === browser && JessWebPolicy.trusted(browser.url ?: "")) {
                browser.loadUrl(home)
            }
        }, 1500)
    }

    companion object {
        const val EXTRA_PLAYER_TASK = "org.vrpassthroughplayer.plugin.PLAYER_TASK"
        const val EXTRA_PLAYER_COMPONENT = "org.vrpassthroughplayer.plugin.PLAYER_COMPONENT"
        @Volatile private var current: WeakReference<TalkToJessActivity>? = null
        fun onHeadsetRemoved() {
            val activity = current?.get() ?: return
            activity.runOnUiThread { if (!activity.isFinishing && !activity.isDestroyed) activity.endSessionOnRemoval() }
        }
        private const val AUDIO_PERMISSION = 0x4A45
        private const val PROBE_PERMISSION = 0x4A46
        private val MICROPHONE_DIAGNOSTICS = """
            (() => {
              const devices = navigator.mediaDevices;
              if (!devices || !devices.getUserMedia) { console.info('VERTO_MIC:unavailable'); return; }
              if (devices.__vertoMicObserved) return;
              const original = devices.getUserMedia.bind(devices);
              devices.getUserMedia = function(constraints) {
                return original(constraints).then(stream => {
                  if (constraints && constraints.audio) console.info('VERTO_MIC:ready');
                  return stream;
                }).catch(error => {
                  if (constraints && constraints.audio) {
                    const allowed = ['NotAllowedError','SecurityError','NotFoundError','NotReadableError','AbortError','OverconstrainedError'];
                    console.info('VERTO_MIC:' + (allowed.includes(error && error.name) ? error.name : 'other'));
                  }
                  throw error;
                });
              };
              devices.__vertoMicObserved = true;
            })();
        """.trimIndent()
    }
}
