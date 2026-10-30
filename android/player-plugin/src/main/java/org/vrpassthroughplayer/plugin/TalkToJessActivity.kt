package org.vrpassthroughplayer.plugin

import android.Manifest
import android.app.Activity
import android.app.ActivityManager
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
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

/** A system 2D panel over the immersive activity, not a browser injected into Godot's renderer. */
class TalkToJessActivity : Activity() {
    private val home = "https://vertoconnect.au/quest"
    private var webView: WebView? = null
    private var pendingAudio: PermissionRequest? = null
    private var pageFailed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
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
                        "NotReadableError", "AbortError" -> "Microphone is unavailable or in use."
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
                        request.deny()
                    } else if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                        request.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
                    } else {
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
        if (requestCode != AUDIO_PERMISSION) return
        val request = pendingAudio ?: return
        pendingAudio = null
        if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED && JessWebPolicy.canCaptureAudio(request.origin.toString(), request.resources)) {
            request.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
        } else {
            request.deny()
        }
    }

    override fun onDestroy() {
        pendingAudio?.deny()
        pendingAudio = null
        webView?.apply {
            stopLoading()
            loadUrl("about:blank")
            (parent as? ViewGroup)?.removeView(this)
            destroy()
        }
        webView = null
        if (isFinishing) restorePlayerTask()
        super.onDestroy()
    }

    private fun returnToPlayer() {
        val playerTask = intent.getIntExtra(EXTRA_PLAYER_TASK, -1)
        if (JessWebPolicy.removePanelTask(isTaskRoot, taskId, playerTask)) finishAndRemoveTask() else finish()
    }

    private fun restorePlayerTask() {
        val playerTask = intent.getIntExtra(EXTRA_PLAYER_TASK, -1)
        if (playerTask < 0) return
        runCatching {
            val manager = getSystemService(ActivityManager::class.java)
            manager.appTasks.firstOrNull { it.taskInfo.id == playerTask }?.moveToFront()
        }
    }

    companion object {
        const val EXTRA_PLAYER_TASK = "org.vrpassthroughplayer.plugin.PLAYER_TASK"
        private const val AUDIO_PERMISSION = 0x4A45
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
