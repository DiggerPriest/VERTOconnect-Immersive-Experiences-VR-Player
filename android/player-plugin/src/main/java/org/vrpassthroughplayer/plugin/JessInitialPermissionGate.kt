package org.vrpassthroughplayer.plugin

/** The web page starts only after the system microphone dialog has finished. */
internal class JessInitialPermissionGate {
    private var awaiting = false
    fun begin(alreadyGranted: Boolean): Boolean {
        awaiting = !alreadyGranted
        return awaiting
    }
    fun completed(panelAlive: Boolean): Boolean {
        if (!awaiting) return false
        awaiting = false
        return panelAlive
    }
}
