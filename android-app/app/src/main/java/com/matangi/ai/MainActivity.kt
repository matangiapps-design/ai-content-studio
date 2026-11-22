package com.matangi.ai

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.json.JSONObject

private val bg = Color(0xFF101114)
private val panel = Color(0xFF1B1D22)
private val copper = Color(0xFFC77B4A)
private val muted = Color(0xFF9A9DA5)
private val engines = listOf("LTX-2.5", "Wan 2.2 Animate", "Wan 2.2 I2V", "HuMo")

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme(colorScheme = darkColorScheme(primary = copper, background = bg, surface = panel)) { StudioScreen() } }
    }
}

@Composable
fun StudioScreen() {
    val context = androidx.compose.ui.platform.LocalContext.current
    var project by remember { mutableStateOf(JSONObject("""{"name":"Copper Hour","studio":"MATANGI","videoType":"hybrid","engine":"LTX-2.5","imageModel":"z-image","upscaler":"seedvr2","resolution":"1080p","ratio":"16:9","bpm":96,"key":"A minor","duration":48,"concept":"A night that will not end, sung from a rooftop down into the street.","look":"35mm anamorphic, copper practicals, sodium streets, fine grain","characterBible":"Keep the lead character's face, hair, age, clothing palette and body proportions identical in every scene. Preserve screen direction and visual identity.","scenes":[]}""")) }
    var selected by remember { mutableIntStateOf(-1) }
    var message by remember { mutableStateOf("Ready • Local project workspace") }
    var editPrompt by remember { mutableStateOf("") }
    var engineMenu by remember { mutableStateOf(false) }
    var selectedEngine by remember(project) { mutableStateOf(project.optString("engine", "LTX-2.5")) }
    var characterBible by remember(project) { mutableStateOf(project.optString("characterBible")) }
    val scenes = remember(project) { project.optJSONArray("scenes") }

    val import = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri?.let { try { context.contentResolver.openInputStream(it)?.bufferedReader()?.use { reader -> project = JSONObject(reader.readText()); selected = -1; message = "Project imported successfully" } } catch (e: Exception) { message = "Import failed: invalid project JSON" } }
    }
    val export = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri: Uri? ->
        uri?.let { try { context.contentResolver.openOutputStream(it)?.use { out -> out.write(project.toString(2).toByteArray()) }; message = "Project JSON exported" } catch (e: Exception) { message = "Export failed" } }
    }

    Column(Modifier.fillMaxSize().background(bg).padding(18.dp)) {
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
                Spacer(Modifier.height(6.dp))
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
                                message = "$engine selected as the project default"
                            })
                        }
                    }
                }
                Text("Selection is saved in project JSON. Rendering requires a connected cloud/API service.", color = muted, fontSize = 10.sp)
                Spacer(Modifier.height(10.dp))
                Text("CHARACTER CONTINUITY BIBLE", color = copper, fontSize = 11.sp, letterSpacing = 1.sp)
                OutlinedTextField(value = characterBible, onValueChange = { characterBible = it; project.put("characterBible", it) }, modifier = Modifier.fillMaxWidth(), minLines = 2, maxLines = 4, placeholder = { Text("Describe fixed character appearance and wardrobe") })
            }
        }
        Spacer(Modifier.height(12.dp))
        Text("SCENE TIMELINE", color = copper, fontSize = 12.sp, letterSpacing = 2.sp)
        Spacer(Modifier.height(8.dp))
        if (scenes == null || scenes.length() == 0) {
            Text("Import the Copper Hour JSON file to load its scenes.", color = muted, modifier = Modifier.padding(12.dp))
        } else {
            LazyColumn(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                itemsIndexed((0 until scenes.length()).map { scenes.getJSONObject(it) }) { index, scene ->
                    val locked = scene.optBoolean("locked", false)
                    Card(onClick = { selected = index; editPrompt = scene.optString("videoPrompt") }, colors = CardDefaults.cardColors(containerColor = if (selected == index) Color(0xFF38271F) else panel), shape = RoundedCornerShape(12.dp)) {
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
                    Switch(checked = locked, onCheckedChange = {
                        locked = it
                        scene.put("locked", it)
                        message = if (it) "Scene locked against prompt edits" else "Scene unlocked"
                    })
                }
            }
            OutlinedTextField(value = editPrompt, onValueChange = { if (!locked) editPrompt = it }, modifier = Modifier.fillMaxWidth(), minLines = 2, maxLines = 4, enabled = !locked)
            Button(onClick = {
                if (!locked) {
                    scene.put("videoPrompt", editPrompt)
                    scene.put("engine", selectedEngine)
                    message = "Scene prompt and engine saved"
                } else message = "Unlock this scene before editing"
            }, modifier = Modifier.fillMaxWidth(), enabled = !locked) { Text("Save scene prompt") }
        }
        Spacer(Modifier.height(8.dp))
        Text(message, color = muted, fontSize = 11.sp)
        Text("Cloud rendering is not connected in this APK yet. Engine choice and continuity notes are project controls only.", color = muted, fontSize = 10.sp)
    }
}

@Composable
private fun Metric(label: String, value: String) {
    Column { Text(label, color = muted, fontSize = 9.sp); Text(value, color = Color.White, fontSize = 13.sp) }
}
