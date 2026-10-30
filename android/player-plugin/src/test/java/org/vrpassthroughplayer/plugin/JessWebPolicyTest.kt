package org.vrpassthroughplayer.plugin

import org.junit.Assert.*
import org.junit.Test

class JessWebPolicyTest {
    @Test fun allowsOnlyTheIntendedSecureOriginAndMicrophone() {
        assertTrue(JessWebPolicy.canCaptureAudio("https://vertoconnect.au", arrayOf(JessWebPolicy.AUDIO)))
        assertTrue(JessWebPolicy.trusted("https://vertoconnect.au/quest"))
        for (bad in listOf("http://vertoconnect.au", "https://vertoconnect.au.evil.test", "https://evil.test", "https://user@vertoconnect.au", "https://vertoconnect.au:444")) {
            assertFalse(JessWebPolicy.canCaptureAudio(bad, arrayOf(JessWebPolicy.AUDIO)))
        }
        assertFalse(JessWebPolicy.canCaptureAudio("https://vertoconnect.au", arrayOf("android.webkit.resource.VIDEO_CAPTURE")))
        assertTrue(JessWebPolicy.canCaptureAudio("https://vertoconnect.au", arrayOf(JessWebPolicy.AUDIO, "android.webkit.resource.VIDEO_CAPTURE")))
    }

    @Test fun removesOnlyASeparatePanelRootTask() {
        assertTrue(JessWebPolicy.removePanelTask(true, 4, 3))
        assertFalse(JessWebPolicy.removePanelTask(true, 3, 3))
        assertFalse(JessWebPolicy.removePanelTask(false, 4, 3))
        assertFalse(JessWebPolicy.removePanelTask(true, 4, -1))
    }
}
