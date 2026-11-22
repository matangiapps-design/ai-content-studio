package com.matangi.ai

import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.io.IOException

private val bg = Color(0xFF101114)
private val panel = Color(0xFF1B1D22)
private val copper = Color(0xFFC77B4A)
private val muted = Color(0xFF9A9DA5)
private val engines = listOf("WaveSpeed Wan 3.0 (LIVE)", "LTX-2.5 (not connected)", "Wan 2.2 Animate (not connected)", "Wan 2.2 I2V (not connected)", "HuMo (not connected)")

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme(colorScheme = darkColorScheme(primary = copper, background = bg, surface = panel)) { StudioScreen() } }
    }
}

private fun apiCall(base: String, token: String, path: String, method: String = "GET", body: JSONObject? = null): JSONObject {
    val cleanBase = base.trim().trimEnd('/')
    require(cleanBase.startsWith("https://")) { "Use your backend HTTPS address." }
    val connection = (URL(cleanBase + path).openConnection() as HttpURLConnection)
    connection.requestMethod = method
    connection.connectTimeout = 15000
    connection.readTimeout = 45000
    connection.setRequestProperty("Authorization", "Bearer " + token.trim())
    connection.setRequestProperty("Accept", "application/json")
    if (body != null) {
        connection.doOutput = true
        connection.setRequestProperty("Content-Type", "application/json")
        connection.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
    }
    val code = connection.responseCode
    val stream = if (code in 200..299) connection.inputStream else connection.errorStream
    val response = stream?.bufferedReader()?.use { it.readText() } ?: "{}"
    connection.disconnect()
    if (code !in 200..299) {
        val detail = try { JSONObject(response).optString("detail", response) } catch (_: Exception) { response }
        throw IOException("HTTP $code: $detail")
    }
    return JSONObject(response)
}

@Composable
fun StudioScreen() {
    val context = androidx.compose.ui.platform.LocalContext.current
    val mainHandler = remember { Handler(Looper.getMainLooper()) }
    var project by remember { mutableStateOf(JSONObject("""{"name":"Copper Hour","studio":"MATANGI","videoType":"hybrid","engine":"WaveSpeed Wan 3.0","imageModel":"z-image","upscaler":"seedvr2","resolution":"720p","ratio":"16:9","bpm":96,"key":"A minor","duration":48,"concept":"A night that will not end, sung from a rooftop down into the street.","look":"35mm anamorphic, copper practicals, sodium streets, fine grain","characterBible":"Keep the lead character's face, hair, age, clothing palette and body proportions identical in every scene. Preserve screen direction and visual identity.","scenes":[]}""")) }
    var selected by remember { mutableIntStateOf(-1) }
    var message by remember { mutableStateOf("Ready • Local project workspace") }
    var editPrompt by remember { mutableStateOf("") }
    var engineMenu by remember { mutableStateOf(false) }
    var selectedEngine by remember(project) { mutableStateOf(project.optString("engine", "WaveSpeed Wan 3.0")) }
    var characterBible by remember(project) { mutableStateOf(project.optString("characterBible")) }
    var apiBase by remember { mutableStateOf("") }
    var apiToken by remember { mutableStateOf("") }
    var renderDuration by remember { mutableIntStateOf(5) }
    var renderResolution by remember { mutableStateOf("720p") }
    var renderRatio by remember { mutableStateOf("16:9") }
    var renderAudio by remember { mutableStateOf(true) }
    var renderBusy by remember { mutableStateOf(false) }
    var renderJobId by remember { mutableStateOf("") }
    var renderState by remember { mutableStateOf("No render submitted") }
    var renderReady by remember { mutableStateOf(false) }
    var pendingDownloadId by remember { mutableStateOf("") }
    val scenes = remember(project) { project.optJSONArray("scenes") }

    val import = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri?.let { try { context.contentResolver.openInputStream(it)?.bufferedReader()?.use { reader -> project = JSONObject(reader.readText()); selected = -1; message = "Project imported successfully" } } catch (_: Exception) { message = "Import failed: invalid project JSON" } }
    }
    val export = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri: Uri? ->
        uri?.let { try { context.contentResolver.openOutputStream(it)?.use { out -> out.write(project.toString(2).toByteArray()) }; message = "Project JSON exported" } catch (_: Exception) { message = "Export failed" } }
    }
    val saveVideo = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("video/mp4")) { uri: Uri? ->
        if (uri != null && pendingDownloadId.isNotBlank()) {
            val base = apiBase
            val token = apiToken
            val job = pendingDownloadId
            Thread {
                try {
                    require(base.startsWith("https://")) { "Backend must use HTTPS." }
                    val conn = URL(base.trimEnd('/') + "/api/wan3/jobs/" + job + "/video").openConnection() as HttpURLConnection
                    conn.setRequestProperty("Authorization", "Bearer " + token.trim())
                    conn.connectTimeout = 15000
                    conn.readTimeout = 120000
                    if (conn.responseCode !in 200..299) throw IOException("Download failed: HTTP " + conn.responseCode)
                    context.contentResolver.openOutputStream(uri)?.use { output -> conn.inputStream.use { input -> input.copyTo(output) } }
                    conn.disconnect()
                    mainHandler.post { renderState = "MP4 saved to your selected folder." }
                } catch (e: Exception) {
                    mainHandler.post { renderState = "Download error: " + (e.message ?: "unknown error") }
                }
            }.start()
        }
    }

    fun renderSelectedScene() {
        if (renderBusy) return
        if (apiBase.isBlank() || apiToken.isBlank()) {
            renderState = "Enter the HTTPS backend URL and Studio API token first."
            return
        }
        if (!selectedEngine.startsWith("WaveSpeed Wan 3.0")) {
            renderState = "This engine is not connected yet. Choose WaveSpeed Wan 3.0."
            return
        }
        val prompt = if (selected >= 0 && scenes != null && selected < scenes.length()) editPrompt.trim() else project.optString("concept").trim()
        if (prompt.length < 8) {
            renderState = "Add a scene prompt of at least 8 characters."
            return
        }
        renderBusy = true
        renderReady = false
        renderJobId = ""
        renderState = "Connecting to MATANGI render server..."
        val base = apiBase
        val token = apiToken
        val request = JSONObject().apply {
            put("prompt", prompt + "\n\nCharacter continuity: " + characterBible + "\nVisual look: " + project.optString("look"))
            put("duration", renderDuration)
            put("resolution", renderResolution)
            put("aspect_ratio", renderRatio)
            put("enable_audio", renderAudio)
            put("enable_prompt_expansion", true)
        }
        Thread {
            try {
                val submitted = apiCall(base, token, "/api/wan3/generate", "POST", request)
                val id = submitted.getString("job_id")
                mainHandler.post { renderJobId = id; renderState = "Queued: " + id }
                var finished = false
                var attempts = 0
                while (!finished && attempts < 360) {
                    Thread.sleep(5000)
                    attempts++
                    val status = apiCall(base, token, "/api/wan3/jobs/" + id)
                    val state = status.optString("status", "unknown")
                    val step = status.optString("step", state)
                    mainHandler.post { renderState = state.uppercase() + " • " + step }
                    when (state) {
                        "completed" -> {
                            finished = true
                            mainHandler.post { renderBusy = false; renderReady = true; renderState = "Render complete. Save the MP4 below." }
                        }
                        "failed", "cancelled" -> {
                            finished = true
                            val error = status.optString("error", "Render failed")
                            mainHandler.post { renderBusy = false; renderState = "Render failed: " + error }
                        }
                    }
                }
                if (!finished) mainHandler.post { renderBusy = false; renderState = "Still processing. Job ID: " + id + " — reconnect and check the server job later." }
            } catch (e: Exception) {
                mainHandler.post { renderBusy = false; renderState = "Connection error: " + (e.message ?: "unknown error") }
            }
        }.start()
    }

    Column(Modifier.fillMaxSize().background(bg).verticalScroll(rememberScrollState()).padding(18.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Column {
                Text("MATANGI", color = copper, fontSize = 13.sp, letterSpacing = 4.sp)
                Text("COPPER HOUR", color = Color.White, fontSize = 25.sp)
                Text("CINEMATIC PROJECT STUDIO", color = muted, fontSize = 10.sp, letterSpacing = 2.sp)
            }
            Icon(Icons.Default.Movie, contentDescription = null, tint = copper, modifier = Modifier.size(34.dp))
        }
        Spacer(Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { import.launch(arrayOf("application/json", "text/*", "*/*")) }) { Icon(Icons.Default.FolderOpen, null); Spacer(Modifier.width(6.dp)); Text("Import") }
            OutlinedButton(onClick = { export.launch(project.optString("name", "project").replace(" ", "_") + ".json") }) { Icon(Icons.Default.Save, null); Spacer(Modifier.width(6.dp)); Text("Export") }
        }
        Spacer(Modifier.height(12.dp))
        Card(colors = CardDefaults.cardColors(containerColor = panel), shape = RoundedCornerShape(16.dp)) {
            Column(Modifier.padding(16.dp)) {
                Text(project.optString("name", "Untitled Project"), color = Color.White, fontSize = 20.sp)
                Text(project.optString("concept", "Import a project to begin"), color = muted, fontSize = 12.sp)
                Spacer(Modifier.height(12.dp))
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Metric("DURATION", project.optInt("duration").toString() + "s")
                    Metric("FORMAT", project.optString("resolution", "—"))
                    Metric("RATIO", project.optString("ratio", "—"))
                    Metric("SCENES", (scenes?.length() ?: 0).toString())
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        Card(colors = CardDefaults.cardColors(containerColor = panel), shape = RoundedCornerShape(14.dp)) {
            Column(Modifier.padding(14.dp)) {
                Text("VIDEO ENGINE", color = copper, fontSize = 11.sp, letterSpacing = 2.sp)
                Box {
                    OutlinedButton(onClick = { engineMenu = true }, modifier = Modifier.fillMaxWidth()) {
                        Text(selectedEngine, modifier = Modifier.weight(1f))
                        Icon(Icons.Default.ExpandMore, contentDescription = "Choose engine")
                    }
                    DropdownMenu(expanded = engineMenu, onDismissRequest = { engineMenu = false }) {
                        engines.forEach { engine ->
                            DropdownMenuItem(text = { Text(engine) }, onClick = {
                                selectedEngine = engine
                                project.put("engine", engine)
                                engineMenu = false
                                message = "$engine selected"
                            })
                        }
                    }
                }
                Text("Only WaveSpeed Wan 3.0 is connected to live rendering. Other engines are shown as future integrations, not active providers.", color = muted, fontSize = 10.sp)
                Spacer(Modifier.height(10.dp))
                Text("CHARACTER CONTINUITY BIBLE", color = copper, fontSize = 11.sp, letterSpacing = 1.sp)
                OutlinedTextField(value = characterBible, onValueChange = { characterBible = it; project.put("characterBible", it) }, modifier = Modifier.fillMaxWidth(), minLines = 2, maxLines = 4)
            }
        }
        Spacer(Modifier.height(12.dp))
        Card(colors = CardDefaults.cardColors(containerColor = panel), shape = RoundedCornerShape(14.dp)) {
            Column(Modifier.padding(14.dp)) {
                Text("CLOUD RENDER CONNECTION", color = copper, fontSize = 11.sp, letterSpacing = 2.sp)
                OutlinedTextField(value = apiBase, onValueChange = { apiBase = it.trim() }, modifier = Modifier.fillMaxWidth(), label = { Text("Backend HTTPS URL") }, placeholder = { Text("https://your-domain.com") }, singleLine = true)
                OutlinedTextField(value = apiToken, onValueChange = { apiToken = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Studio API token") }, visualTransformation = PasswordVisualTransformation(), singleLine = true)
                Text("The Studio token is used only in memory while this screen is open. Keep WaveSpeed API keys on the server; never enter them here.", color = muted, fontSize = 10.sp)
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = {
                        Thread {
                            try {
                                val info = apiCall(apiBase, apiToken, "/api/wan3/status")
                                mainHandler.post { renderState = if (info.optBoolean("configured")) "Server connected • WaveSpeed key configured" else "Server connected • WaveSpeed key missing" }
                            } catch (e: Exception) { mainHandler.post { renderState = "Connection check failed: " + (e.message ?: "unknown error") } }
                        }.start()
                    }) { Text("Test connection") }
                }
                Spacer(Modifier.height(8.dp))
                Text("RENDER SETTINGS", color = copper, fontSize = 11.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(value = renderDuration.toString(), onValueChange = { it.toIntOrNull()?.let { v -> renderDuration = v.coerceIn(2, 30) } }, modifier = Modifier.weight(1f), label = { Text("Seconds (2–30)") }, singleLine = true)
                    OutlinedTextField(value = renderResolution, onValueChange = { if (it in listOf("480p", "720p", "1080p")) renderResolution = it }, modifier = Modifier.weight(1f), label = { Text("Resolution") }, singleLine = true)
                }
                OutlinedTextField(value = renderRatio, onValueChange = { if (it in listOf("16:9", "9:16", "1:1", "4:3", "3:4")) renderRatio = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Aspect ratio: 16:9, 9:16, 1:1, 4:3, 3:4") }, singleLine = true)
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Generate audio", color = Color.White)
                    Switch(checked = renderAudio, onCheckedChange = { renderAudio = it })
                }
                Button(onClick = { renderSelectedScene() }, modifier = Modifier.fillMaxWidth(), enabled = !renderBusy) {
                    if (renderBusy) CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
                    else Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text(if (renderBusy) "Rendering..." else "Render selected scene")
                }
                Text(renderState, color = if (renderReady) copper else muted, fontSize = 11.sp)
                if (renderJobId.isNotBlank()) Text("JOB ID  $renderJobId", color = muted, fontSize = 10.sp)
                if (renderReady) {
                    Button(onClick = { pendingDownloadId = renderJobId; saveVideo.launch("MATANGI_scene_$renderJobId.mp4") }, modifier = Modifier.fillMaxWidth()) {
                        Icon(Icons.Default.Download, contentDescription = null)
                        Spacer(Modifier.width(8.dp))
                        Text("Save MP4 to phone")
                    }
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        Text("SCENE TIMELINE", color = copper, fontSize = 12.sp, letterSpacing = 2.sp)
        Spacer(Modifier.height(8.dp))
        if (scenes == null || scenes.length() == 0) {
            Text("Import your project JSON to load its scenes. The project concept can be rendered without a selected scene.", color = muted, modifier = Modifier.padding(12.dp))
        } else {
            for (index in 0 until scenes.length()) {
                val scene = scenes.getJSONObject(index)
                val locked = scene.optBoolean("locked", false)
                Card(onClick = { selected = index; editPrompt = scene.optString("videoPrompt") }, modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp), colors = CardDefaults.cardColors(containerColor = if (selected == index) Color(0xFF38271F) else panel), shape = RoundedCornerShape(12.dp)) {
                    Column(Modifier.padding(13.dp)) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("%02d  %s".format(index + 1, scene.optString("section", "Scene")), color = Color.White)
                            Row {
                                if (locked) Icon(Icons.Default.Lock, contentDescription = "Scene locked", tint = copper, modifier = Modifier.size(16.dp))
                                Spacer(Modifier.width(6.dp))
                                Text(scene.optInt("start").toString() + "–" + scene.optInt("end") + "s", color = copper)
                            }
                        }
                        Text(scene.optString("lyrics"), color = muted, fontSize = 12.sp)
                        Text("ENGINE  " + scene.optString("engine", selectedEngine).uppercase() + "     " + if (scene.optBoolean("lipSync")) "LIP SYNC" else "NARRATIVE", color = copper, fontSize = 10.sp)
                    }
                }
            }
        }
        if (selected >= 0 && scenes != null && selected < scenes.length()) {
            val scene = scenes.getJSONObject(selected)
            var locked by remember(selected, project) { mutableStateOf(scene.optBoolean("locked", false)) }
            Spacer(Modifier.height(8.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("SCENE " + (selected + 1) + " PROMPT", color = copper, fontSize = 11.sp)
                Row {
                    Text(if (locked) "Locked" else "Editable", color = muted, fontSize = 11.sp)
                    Spacer(Modifier.width(6.dp))
                    Switch(checked = locked, onCheckedChange = { locked = it; scene.put("locked", it); message = if (it) "Scene locked" else "Scene unlocked" })
                }
            }
            OutlinedTextField(value = editPrompt, onValueChange = { if (!locked) editPrompt = it }, modifier = Modifier.fillMaxWidth(), minLines = 3, maxLines = 6, enabled = !locked)
            Button(onClick = { if (!locked) { scene.put("videoPrompt", editPrompt); scene.put("engine", selectedEngine); message = "Scene prompt saved" } }, modifier = Modifier.fillMaxWidth(), enabled = !locked) { Text("Save scene prompt") }
        }
        Spacer(Modifier.height(8.dp))
        Text(message, color = muted, fontSize = 11.sp)
        Text("Wan 3.0 supports clips up to 30 seconds per request. Full films require multiple scene renders and editing. Native 4K is not claimed; upscale separately.", color = muted, fontSize = 10.sp)
    }
}

@Composable
private fun Metric(label: String, value: String) {
    Column { Text(label, color = muted, fontSize = 9.sp); Text(value, color = Color.White, fontSize = 13.sp) }
}
