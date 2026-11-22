package com.matangi.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

private val Ink = Color(0xFF0B0B12)
private val CardBg = Color(0xFF171724)
private val Gold = Color(0xFFD8AE68)
private val Purple = Color(0xFF9B7BFF)
private data class ChatMessage(val role: String, val content: String)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme(colorScheme = darkColorScheme(primary = Gold, background = Ink, surface = CardBg)) { MatangiScreen() } }
    }
}

@Composable
private fun MatangiScreen() {
    val prefs = androidx.compose.ui.platform.LocalContext.current.getSharedPreferences("matangi_ai", 0)
    var endpoint by remember { mutableStateOf(prefs.getString("endpoint", "") ?: "") }
    var apiKey by remember { mutableStateOf(prefs.getString("api_key", "") ?: "") }
    var model by remember { mutableStateOf(prefs.getString("model", "Qwen3.6-27B-AEON") ?: "Qwen3.6-27B-AEON") }
    var prompt by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var showSettings by remember { mutableStateOf(endpoint.isBlank()) }
    var status by remember { mutableStateOf("Connect your MATANGI AI server in Settings.") }
    val messages = remember { mutableStateListOf<ChatMessage>() }

    Column(Modifier.fillMaxSize().background(Ink).padding(16.dp)) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
            Column {
                Text("MATANGI", color = Gold, fontSize = 12.sp, letterSpacing = 4.sp, fontWeight = FontWeight.Bold)
                Text("AI", color = Color.White, fontSize = 30.sp, fontWeight = FontWeight.ExtraBold)
                Text("YOUR INTELLIGENCE STUDIO", color = Purple, fontSize = 9.sp, letterSpacing = 2.sp)
            }
            OutlinedButton(onClick = { showSettings = !showSettings }) { Text("Settings") }
        }
        Spacer(Modifier.height(12.dp))
        if (showSettings) {
            Card(colors = CardDefaults.cardColors(containerColor = CardBg), shape = RoundedCornerShape(18.dp)) {
                Column(Modifier.padding(14.dp)) {
                    Text("SERVER CONNECTION", color = Gold, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(endpoint, { endpoint = it }, Modifier.fillMaxWidth(), label = { Text("HTTPS API base URL") }, placeholder = { Text("https://your-server.example.com/v1") }, singleLine = true)
                    OutlinedTextField(apiKey, { apiKey = it }, Modifier.fillMaxWidth(), label = { Text("API token") }, singleLine = true)
                    OutlinedTextField(model, { model = it }, Modifier.fillMaxWidth(), label = { Text("Model name") }, singleLine = true)
                    Text("Use your secured OpenAI-compatible endpoint. Do not put provider keys in a public repository.", color = Color.LightGray, fontSize = 10.sp)
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = {
                        prefs.edit().putString("endpoint", endpoint.trim()).putString("api_key", apiKey).putString("model", model.trim()).apply()
                        showSettings = false
                        status = "Settings saved on this device."
                    }, modifier = Modifier.fillMaxWidth()) { Text("Save connection") }
                }
            }
            Spacer(Modifier.height(10.dp))
        }
        Text("CHAT", color = Gold, fontSize = 11.sp, letterSpacing = 2.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(8.dp))
        LazyColumn(Modifier.weight(1f).fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            if (messages.isEmpty()) item {
                Card(colors = CardDefaults.cardColors(containerColor = CardBg), shape = RoundedCornerShape(18.dp)) {
                    Column(Modifier.padding(18.dp)) {
                        Text("Welcome to MATANGI AI", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        Text("Chat, reason, plan, write, and code with your connected AI model.", color = Color.LightGray, fontSize = 13.sp)
                    }
                }
            }
            items(messages) { msg ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = if (msg.role == "user") Color(0xFF252033) else CardBg),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(Modifier.padding(13.dp)) {
                        Text(if (msg.role == "user") "YOU" else "MATANGI AI", color = if (msg.role == "user") Purple else Gold, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(4.dp))
                        Text(msg.content, color = Color.White, fontSize = 14.sp)
                    }
                }
            }
        }
        Text(status, color = Color.LightGray, fontSize = 10.sp)
        Spacer(Modifier.height(6.dp))
        Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(
                value = prompt, onValueChange = { prompt = it }, modifier = Modifier.weight(1f),
                placeholder = { Text("Ask MATANGI AI...") }, minLines = 1, maxLines = 4
            )
            Button(enabled = !busy && prompt.isNotBlank(), onClick = {
                val question = prompt.trim()
                prompt = ""
                messages.add(ChatMessage("user", question))
                busy = true
                status = "Thinking..."
                val url = endpoint.trim().trimEnd('/')
                val token = apiKey
                val modelName = model.trim()
                val history = JSONArray()
                messages.takeLast(20).forEach { history.put(JSONObject().put("role", it.role).put("content", it.content)) }
                Thread {
                    try {
                        require(url.startsWith("https://")) { "Set a valid HTTPS API base URL in Settings." }
                        val conn = (URL("$url/chat/completions").openConnection() as HttpURLConnection)
                        conn.requestMethod = "POST"
                        conn.connectTimeout = 20000
                        conn.readTimeout = 120000
                        conn.setRequestProperty("Content-Type", "application/json")
                        conn.setRequestProperty("Accept", "application/json")
                        if (token.isNotBlank()) conn.setRequestProperty("Authorization", "Bearer $token")
                        conn.doOutput = true
                        val body = JSONObject().put("model", modelName).put("messages", history).put("temperature", 0.7).put("stream", false)
                        conn.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
                        val code = conn.responseCode
                        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                        val raw = stream?.bufferedReader()?.use { it.readText() } ?: "{}"
                        conn.disconnect()
                        if (code !in 200..299) throw IllegalStateException("Server returned HTTP $code: $raw")
                        val answer = JSONObject(raw).getJSONArray("choices").getJSONObject(0).getJSONObject("message").optString("content", "No response text.")
                        runOnUiThreadSafe { messages.add(ChatMessage("assistant", answer)); status = "Connected • $modelName"; busy = false }
                    } catch (e: Exception) {
                        runOnUiThreadSafe { messages.add(ChatMessage("assistant", "Connection error: ${e.message ?: "Unknown error"}")); status = "Check server URL, model name, and token."; busy = false }
                    }
                }.start()
            }) { Text(if (busy) "…" else "Send") }
        }
    }
}

private fun runOnUiThreadSafe(block: () -> Unit) {
    android.os.Handler(android.os.Looper.getMainLooper()).post(block)
}
