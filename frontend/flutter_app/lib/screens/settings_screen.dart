import 'package:flutter/material.dart';

import '../services/api_client.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final ApiClient api = ApiClient();

  String provider = 'openai_compatible';
  String model = 'deepseek-chat';
  String baseUrl = 'https://api.deepseek.com/v1';
  String apiKey = '';
  String language = 'zh';
  String? activeLang;

  bool loading = false;
  bool saving = false;
  String? status;
  String? error;

  final Map<String, String> providers = {
    'openai': 'OpenAI',
    'openai_compatible': 'OpenAI Compatible',
    'deepseek': 'DeepSeek',
    'mock': 'Mock (Testing)',
  };

  final Map<String, String> languages = {
    'zh': '中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어',
    'fr': 'Français',
    'de': 'Deutsch',
    'auto': 'Auto',
  };

  final Map<String, String> providerDefaults = {
    'openai': 'https://api.openai.com/v1',
    'openai_compatible': 'https://api.deepseek.com/v1',
    'deepseek': 'https://api.deepseek.com/v1',
  };

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    setState(() => loading = true);
    try {
      final data = await api.get('/settings') as Map<String, dynamic>;
      final m = data['model'] as Map<String, dynamic>? ?? {};
      setState(() {
        provider = m['provider'] ?? 'openai_compatible';
        model = m['model'] ?? 'deepseek-chat';
        baseUrl = m['base_url'] ?? 'https://api.deepseek.com/v1';
        apiKey = m['api_key'] ?? '';
        activeLang = (data['language'] ?? 'zh') as String;
        language = activeLang ?? 'zh';
        error = null;
      });
    } catch (err) {
      setState(() => error = err.toString());
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> saveModel() async {
    setState(() => saving = true);
    try {
      await api.put('/settings/model', {
        'provider': provider,
        'model': model,
        'base_url': baseUrl,
        'api_key': apiKey,
      });
      setState(() { status = 'Model saved'; error = null; });
      await Future.delayed(const Duration(seconds: 2));
      if (mounted) setState(() => status = null);
    } catch (err) {
      setState(() => error = err.toString());
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  Future<void> saveLanguage() async {
    try {
      await api.put('/settings/language', {'language': language});
      setState(() { activeLang = language; status = 'Language saved'; error = null; });
      await Future.delayed(const Duration(seconds: 2));
      if (mounted) setState(() => status = null);
    } catch (err) {
      setState(() => error = err.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator());

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Settings', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text('Configure model API and language. Memory system is independent and unaffected by changes here.',
              style: TextStyle(color: Colors.grey[600], fontSize: 13)),
          if (error != null) ...[
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red[200]!),
              ),
              child: Text(error!, style: TextStyle(color: Colors.red[800], fontSize: 13)),
            ),
          ],
          if (status != null) ...[
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green[200]!),
              ),
              child: Text(status!, style: TextStyle(color: Colors.green[800], fontSize: 13)),
            ),
          ],
          const SizedBox(height: 24),

          // ---- Model Section ----
          _SectionHeader(title: 'Model API', onReset: () {
            setState(() {
              provider = 'openai_compatible';
              model = 'deepseek-chat';
              baseUrl = 'https://api.deepseek.com/v1';
              apiKey = '';
            });
          }),
          const SizedBox(height: 12),
          _Card(children: [
            _DropdownRow(
              label: 'Provider',
              value: provider,
              items: providers,
              onChanged: (v) {
                setState(() {
                  provider = v;
                  if (providerDefaults.containsKey(v)) {
                    baseUrl = providerDefaults[v]!;
                  }
                });
              },
            ),
            const _Div(),
            _TextFieldRow(label: 'Base URL', value: baseUrl, hint: 'https://api.example.com/v1', onChanged: (v) => baseUrl = v),
            const _Div(),
            _TextFieldRow(label: 'Model Name', value: model, hint: 'gpt-4, deepseek-chat, claude-3-opus', onChanged: (v) => model = v),
            const _Div(),
            _TextFieldRow(label: 'API Key', value: apiKey, hint: 'sk-...', obscure: true, onChanged: (v) => apiKey = v),
          ]),
          const SizedBox(height: 12),
          Align(
            alignment: Alignment.centerRight,
            child: FilledButton.icon(
              onPressed: saving ? null : saveModel,
              icon: saving ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.save, size: 18),
              label: Text(saving ? 'Saving...' : 'Save Model Config'),
            ),
          ),
          const SizedBox(height: 32),

          // ---- Language Section ----
          _SectionHeader(title: 'Language', onReset: null),
          const SizedBox(height: 12),
          _Card(children: [
            _DropdownRow(
              label: 'Response Language',
              value: language,
              items: languages,
              onChanged: (v) {
                setState(() => language = v);
                saveLanguage();
              },
            ),
          ]),
          if (activeLang != null) ...[
            const SizedBox(height: 8),
            Text('Active: ${languages[activeLang] ?? activeLang}', style: TextStyle(color: Colors.grey[500], fontSize: 13)),
          ],

          const SizedBox(height: 40),
          Text('Memory and emotion systems are independent. Changing API does not affect stored data.',
              style: TextStyle(color: Colors.grey[400], fontSize: 11)),
        ],
      ),
    );
  }
}

// ---- Reusable Widgets ----

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, this.onReset});
  final String title;
  final VoidCallback? onReset;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
        const Spacer(),
        if (onReset != null)
          TextButton.icon(
            onPressed: onReset,
            icon: const Icon(Icons.restart_alt, size: 16),
            label: const Text('Reset Defaults', style: TextStyle(fontSize: 12)),
          ),
      ],
    );
  }
}

class _Card extends StatelessWidget {
  const _Card({required this.children});
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
        color: Colors.white,
      ),
      child: Column(children: children),
    );
  }
}

class _Div extends StatelessWidget {
  const _Div();
  @override
  Widget build(BuildContext context) => Divider(height: 1, color: Colors.grey[200]);
}

class _DropdownRow extends StatelessWidget {
  const _DropdownRow({required this.label, required this.value, required this.items, required this.onChanged});
  final String label;
  final String value;
  final Map<String, String> items;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          SizedBox(width: 120, child: Text(label, style: const TextStyle(fontSize: 14))),
          Expanded(
            child: DropdownButtonFormField<String>(
              value: items.containsKey(value) ? value : items.keys.first,
              isExpanded: true,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                isDense: true,
              ),
              items: items.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value, style: const TextStyle(fontSize: 14)))).toList(),
              onChanged: (v) { if (v != null) onChanged(v); },
            ),
          ),
        ],
      ),
    );
  }
}

class _TextFieldRow extends StatelessWidget {
  const _TextFieldRow({required this.label, required this.value, required this.hint, this.obscure = false, required this.onChanged});
  final String label;
  final String value;
  final String hint;
  final bool obscure;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          SizedBox(width: 120, child: Text(label, style: const TextStyle(fontSize: 14))),
          Expanded(
            child: TextField(
              controller: TextEditingController(text: value)..selection = TextSelection.collapsed(offset: value.length),
              obscureText: obscure,
              decoration: InputDecoration(
                border: const OutlineInputBorder(),
                hintText: hint,
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                isDense: true,
                suffixIcon: obscure ? const Icon(Icons.key, size: 18) : null,
              ),
              style: const TextStyle(fontSize: 14, fontFamily: 'monospace'),
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }
}
