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
        trusted(origin) && resources.any { it == AUDIO }

    // Never remove a task containing the immersive player.
    fun removePanelTask(isRoot: Boolean, panelTask: Int, playerTask: Int): Boolean =
        isRoot && panelTask >= 0 && playerTask >= 0 && panelTask != playerTask
}
