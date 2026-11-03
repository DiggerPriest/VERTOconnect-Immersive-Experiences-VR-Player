package org.vrpassthroughplayer.plugin

import org.junit.Assert.*
import org.junit.Test

class JessInitialPermissionGateTest {
    @Test fun firstGrantOrDenialBothStartThePageExactlyOnceAfterTheDialog() {
        for (granted in listOf(true, false)) {
            val gate = JessInitialPermissionGate()
            assertTrue(gate.begin(false))
            // Both outcomes load the page; WebView applies the actual permission.
            assertTrue(gate.completed(true))
            assertFalse(gate.completed(true))
        }
    }
    @Test fun alreadyGrantedDoesNotWaitAndClosedPanelDoesNotLoad() {
        val gate = JessInitialPermissionGate()
        assertFalse(gate.begin(true))
        assertFalse(gate.completed(true))
        assertTrue(gate.begin(false))
        assertFalse(gate.completed(false))
    }
}
