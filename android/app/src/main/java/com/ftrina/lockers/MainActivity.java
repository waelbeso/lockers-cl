package com.ftrina.lockers;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private static final String PREFS_NAME = "lockers_settings";
    private static final String PREF_START_URL = "start_url";
    private static final String DEFAULT_URL = "http://127.0.0.1:8090";

    private WebView webView;
    private View settingsPanel;
    private EditText hostInput;
    private SharedPreferences preferences;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        preferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        webView = findViewById(R.id.lockersWebView);
        settingsPanel = findViewById(R.id.settingsPanel);
        hostInput = findViewById(R.id.hostInput);
        Button saveButton = findViewById(R.id.saveButton);

        configureWebView();
        loadInitialUrl();

        saveButton.setOnClickListener(v -> {
            String candidate = hostInput.getText().toString().trim();
            if (!candidate.isEmpty()) {
                preferences.edit().putString(PREF_START_URL, candidate).apply();
                loadUrl(candidate);
            }
        });
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new LockerWebViewClient());
    }

    private void loadInitialUrl() {
        loadUrl(getStartUrl());
    }

    private void loadUrl(String url) {
        settingsPanel.setVisibility(View.GONE);
        webView.setVisibility(View.VISIBLE);
        webView.loadUrl(url);
    }

    private String getStartUrl() {
        return preferences.getString(PREF_START_URL, DEFAULT_URL);
    }

    private void showSettings(String failingUrl) {
        runOnUiThread(() -> {
            webView.stopLoading();
            webView.setVisibility(View.GONE);
            settingsPanel.setVisibility(View.VISIBLE);
            if (failingUrl != null && failingUrl.startsWith("http")) {
                hostInput.setText(failingUrl);
            } else {
                hostInput.setText(getStartUrl());
            }
        });
    }

    private class LockerWebViewClient extends WebViewClient {
        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            super.onReceivedError(view, request, error);
            if (request.isForMainFrame()) {
                showSettings(request.getUrl() != null ? request.getUrl().toString() : null);
            }
        }
    }
}
