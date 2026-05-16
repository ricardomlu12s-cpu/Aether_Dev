import 'package:flutter/material.dart';

import '../models/memory.dart';
import '../services/api_client.dart';

class MemoryViewer extends StatefulWidget {
  const MemoryViewer({super.key});

  @override
  State<MemoryViewer> createState() => _MemoryViewerState();
}

class _MemoryViewerState extends State<MemoryViewer> {
  final ApiClient api = ApiClient();
  final TextEditingController query = TextEditingController();
  List<MemoryItem> memories = [];
  bool loading = false;
  String? error;

  @override
  void initState() {
    super.initState();
    loadRecent();
  }

  Future<void> loadRecent() async {
    setState(() => loading = true);
    try {
      final raw = await api.get('/memory/recent') as List<dynamic>;
      memories = raw.map((item) => MemoryItem.fromJson(item)).toList();
      error = null;
    } catch (err) {
      error = err.toString();
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> search() async {
    final text = query.text.trim();
    if (text.isEmpty) {
      await loadRecent();
      return;
    }
    setState(() => loading = true);
    try {
      final raw =
          await api.get('/memory/query?q=${Uri.encodeQueryComponent(text)}')
              as List<dynamic>;
      memories = raw.map((item) => MemoryItem.fromJson(item)).toList();
      error = null;
    } catch (err) {
      error = err.toString();
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> setLevel(MemoryItem item, String level) async {
    await api.post('/memory/${item.id}/level/$level', {}, admin: true);
    await loadRecent();
  }

  Future<void> deleteMemory(MemoryItem item) async {
    await api.delete('/memory/${item.id}', admin: true);
    await loadRecent();
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
                  'Memory Viewer',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
                ),
              ),
              IconButton(
                tooltip: 'Refresh',
                onPressed: loading ? null : loadRecent,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: query,
                  onSubmitted: (_) => search(),
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    hintText: 'Search memories',
                  ),
                ),
              ),
              const SizedBox(width: 8),
              IconButton.filled(
                tooltip: 'Search',
                onPressed: loading ? null : search,
                icon: const Icon(Icons.search),
              ),
            ],
          ),
          if (error != null)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(error!, style: const TextStyle(color: Colors.red)),
            ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView.builder(
              itemCount: memories.length,
              itemBuilder: (context, index) {
                final item = memories[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Chip(label: Text(item.level)),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                item.summary,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                            PopupMenuButton<String>(
                              tooltip: 'Set level',
                              onSelected: (level) => setLevel(item, level),
                              itemBuilder: (context) => const [
                                PopupMenuItem(
                                  value: 'L1',
                                  child: Text('Set L1'),
                                ),
                                PopupMenuItem(
                                  value: 'L2',
                                  child: Text('Set L2'),
                                ),
                                PopupMenuItem(
                                  value: 'L3',
                                  child: Text('Set L3'),
                                ),
                              ],
                            ),
                            IconButton(
                              tooltip: 'Delete memory',
                              onPressed: () => deleteMemory(item),
                              icon: const Icon(Icons.delete_outline),
                            ),
                          ],
                        ),
                        Text(item.content),
                        const SizedBox(height: 8),
                        Text(
                          'importance=${item.importanceScore.toStringAsFixed(2)} updated=${item.updatedAt}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
