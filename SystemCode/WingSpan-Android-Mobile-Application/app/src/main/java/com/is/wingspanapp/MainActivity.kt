package com.`is`.wingspanapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.`is`.wingspanapp.ui.theme.WingSpanAppTheme
import android.webkit.WebView
import android.content.Intent
import android.net.Uri
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.result.ActivityResultLauncher

class MainActivity : ComponentActivity() {
    private var uploadMessage: ValueCallback<Array<Uri>>? = null
    private lateinit var contentFileLauncher: ActivityResultLauncher<Intent>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val myWebView: WebView = findViewById(R.id.webview)
        myWebView.settings.javaScriptEnabled = true

        contentFileLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (uploadMessage == null) return@registerForActivityResult
            val data = if (result.data == null || result.resultCode != RESULT_OK) null else result.data
            uploadMessage?.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(result.resultCode, data))
            uploadMessage = null
        }

        myWebView.webChromeClient = object : WebChromeClient() {
            // For Lollipop 5.0+ Devices
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                uploadMessage?.onReceiveValue(null)
                uploadMessage = filePathCallback
                fileChooserParams?.let {
                    contentFileLauncher.launch(it.createIntent())
                }
                return true
            }
        }

        myWebView.loadUrl("https://wing-span-9a1a4eb79eb0.herokuapp.com/") // Replace with your website URL
    }
}

