package org.vrpassthroughplayer.plugin

import java.net.URI

internal object JessWebPolicy {
    const val AUDIO = "android.webkit.resource.AUDIO_CAPTURE"

    fun trusted(url: String): Boolean = runCatching {
        val uri = URI(url)
        uri.scheme.equals("https", true) && uri.host.equals("vertoconnect.au", true) &&
            (uri.port == -1 || uri.port == 443) && uri.userInfo == null
    }.getOrDefault(false)

    fun canCaptureAudio(origin: String, resources: Array<out String>): Boolean =
        trusted(origin) && resources.size == 1 && resources[0] == AUDIO
}
