import 'package:flutter/material.dart';

import '../services/api_client.dart';

class DeveloperDashboard extends StatefulWidget {
  const DeveloperDashboard({super.key});

  @override
  State<DeveloperDashboard> createState() => _DeveloperDashboardState();
}

class _DeveloperDashboardState extends State<DeveloperDashboard> {
  final ApiClient api = ApiClient();
  Map<String, dynamic>? runtime;
  String? error;
  bool loading = false;

  @override
  void initState() {
    super.initState();
    refresh();
  }

  Future<void> refresh() async {
    setState(() => loading = true);
    try {
      runtime =
          await api.get('/developer/runtime', admin: true)
              as Map<String, dynamic>;
      error = null;
    } catch (err) {
      error = err.toString();
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> runRem() async {
    await api.post('/developer/rem/run', {}, admin: true);
    await refresh();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  'Developer Runtime',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
                ),
              ),
              IconButton(
                tooltip: 'Run REM',
                onPressed: loading ? null : runRem,
                icon: const Icon(Icons.bedtime_outlined),
              ),
              IconButton(
                tooltip: 'Refresh',
                onPressed: loading ? null : refresh,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          if (error != null)
            Text(error!, style: const TextStyle(color: Colors.red)),
          const SizedBox(height: 12),
          Expanded(
            child: runtime == null
                ? const Center(child: Text('Backend not connected'))
                : GridView.count(
                    crossAxisCount: 2,
                    childAspectRatio: 2.4,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    children: [
                      _Panel(
                        title: 'Version',
                        value: runtime!['version'].toString(),
                      ),
                      _Panel(
                        title: 'Data Dir',
                        value: runtime!['data_dir'].toString(),
                      ),
                      _Panel(
                        title: 'Model',
                        value: runtime!['model'].toString(),
                      ),
                      _Panel(
                        title: 'Conversations',
                        value: runtime!['conversation_count'].toString(),
                      ),
                      _Panel(
                        title: 'Messages',
                        value: runtime!['message_count'].toString(),
                      ),
                      _Panel(
                        title: 'Memories',
                        value: runtime!['memory_count'].toString(),
                      ),
                      _Panel(
                        title: 'Emotion',
                        value: runtime!['emotion'].toString(),
                      ),
                      _Panel(
                        title: 'Plugins',
                        value: (runtime!['plugins'] as List<dynamic>)
                            .map((e) => e['name'])
                            .join(', '),
                      ),
                      _Panel(
                        title: 'Events',
                        value: (runtime!['events'] as List<dynamic>)
                            .take(4)
                            .map((e) => e['event_type'])
                            .join('\n'),
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }
}

class _Panel extends StatelessWidget {
  const _Panel({required this.title, required this.value});

  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xffd2d8d6)),
        borderRadius: BorderRadius.circular(8),
        color: const Color(0xfffafafa),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Expanded(child: Text(value, overflow: TextOverflow.fade)),
        ],
      ),
    );
  }
}
