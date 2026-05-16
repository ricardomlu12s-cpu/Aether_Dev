import 'dart:async';
import 'dart:math' as math;

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
  List<Map<String, dynamic>> events = [];
  String? error;
  Timer? timer;

  @override
  void initState() {
    super.initState();
    refresh();
    timer = Timer.periodic(const Duration(seconds: 5), (_) => refresh());
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  Future<void> refresh() async {
    try {
      final data = await api.get('/developer/runtime', admin: true) as Map<String, dynamic>;
      if (!mounted) return;
      setState(() {
        runtime = data;
        events = (data['events'] as List<dynamic>?)
                ?.map((e) => Map<String, dynamic>.from(e as Map))
                .toList() ??
            [];
        error = null;
      });
    } catch (err) {
      if (!mounted) return;
      setState(() => error = err.toString());
    }
  }

  Future<void> runRem() async {
    await api.post('/developer/rem/run', {}, admin: true);
    await refresh();
  }

  @override
  Widget build(BuildContext context) {
    if (error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Backend not connected', style: TextStyle(color: Colors.red[700], fontSize: 16)),
            const SizedBox(height: 8),
            Text(error!, style: const TextStyle(fontSize: 12, color: Colors.grey)),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: refresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }
    if (runtime == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final emotion = runtime!['emotion'] as Map<String, dynamic>? ?? {};
    final pleasure = (emotion['pleasure'] as num?)?.toDouble() ?? 0.0;
    final arousal = (emotion['arousal'] as num?)?.toDouble() ?? 0.0;
    final dominance = (emotion['dominance'] as num?)?.toDouble() ?? 0.0;
    final energy = (emotion['energy'] as num?)?.toDouble() ?? 100.0;
    final model = runtime!['model'] as Map<String, dynamic>? ?? {};
    final vector = runtime!['vector_store'] as Map<String, dynamic>? ?? {};

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text('Runtime', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
              ),
              IconButton(tooltip: 'Run REM', onPressed: runRem, icon: const Icon(Icons.bedtime_outlined)),
            ],
          ),
          const SizedBox(height: 20),

          // --- Emotion Dashboard ---
          const Text('Emotion State', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(flex: 2, child: _PadGauge(label: 'Pleasure', value: pleasure, color: const Color(0xFF4CAF50))),
              const SizedBox(width: 16),
              Expanded(flex: 2, child: _PadGauge(label: 'Arousal', value: arousal, color: const Color(0xFFFF9800))),
              const SizedBox(width: 16),
              Expanded(flex: 2, child: _PadGauge(label: 'Dominance', value: dominance, color: const Color(0xFF2196F3))),
            ],
          ),
          const SizedBox(height: 16),
          _EnergyBar(energy: energy),
          const SizedBox(height: 24),

          // --- Stats ---
          const Text('System', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _StatChip(icon: Icons.chat_bubble_outline, label: 'Convos', value: '${runtime!['conversation_count']}'),
              _StatChip(icon: Icons.message_outlined, label: 'Messages', value: '${runtime!['message_count']}'),
              _StatChip(icon: Icons.storage_outlined, label: 'Memories', value: '${runtime!['memory_count']}'),
              _StatChip(icon: Icons.memory_outlined, label: 'Index', value: '${vector['terms'] ?? '-'} terms'),
              _StatChip(icon: Icons.smart_toy_outlined, label: 'Model', value: model['provider'] ?? '-'),
              _StatChip(icon: Icons.extension_outlined, label: 'Plugins', value: '${(runtime!['plugins'] as List?)?.length ?? 0}'),
            ],
          ),
          const SizedBox(height: 24),

          // --- Event Feed ---
          Row(
            children: [
              const Text('Event Feed', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              const Spacer(),
              Text('${events.length} events', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 200,
            child: events.isEmpty
                ? Center(child: Text('No events yet', style: TextStyle(color: Colors.grey[500])))
                : ListView.separated(
                    itemCount: events.length > 20 ? 20 : events.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, i) {
                      final ev = events[i];
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            _eventIcon(ev['event_type'] as String? ?? ''),
                            const SizedBox(width: 10),
                            Expanded(child: Text(ev['event_type'] ?? '', style: const TextStyle(fontSize: 13))),
                            Text(ev['status'] ?? '', style: TextStyle(fontSize: 11, color: Colors.grey[500])),
                          ],
                        ),
                      );
                    },
                  ),
          ),

          const SizedBox(height: 12),
          Text('v${runtime!['version']}  |  ${runtime!['data_dir']}', style: TextStyle(color: Colors.grey[500], fontSize: 11)),
        ],
      ),
    );
  }

  Widget _eventIcon(String type) {
    IconData icon = Icons.circle;
    Color color = Colors.grey;
    if (type.contains('message')) { icon = Icons.chat_bubble_outline; color = Colors.blue; }
    if (type.contains('memory')) { icon = Icons.storage_outlined; color = Colors.teal; }
    if (type.contains('emotion')) { icon = Icons.mood_outlined; color = Colors.orange; }
    if (type.contains('rem')) { icon = Icons.bedtime_outlined; color = Colors.deepPurple; }
    return Icon(icon, size: 16, color: color);
  }
}

// --- PAD Gauge ---
class _PadGauge extends StatelessWidget {
  const _PadGauge({required this.label, required this.value, required this.color});
  final String label;
  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final pct = ((value + 1) / 2).clamp(0.0, 1.0);
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
        color: Colors.white,
      ),
      child: Column(
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
          const SizedBox(height: 10),
          SizedBox(
            height: 80,
            width: 80,
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  height: 80, width: 80,
                  child: CircularProgressIndicator(
                    value: pct,
                    strokeWidth: 8,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation(color),
                  ),
                ),
                Text(value.toStringAsFixed(3), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
              ],
            ),
          ),
          const SizedBox(height: 6),
          Text('${(value * 100).toStringAsFixed(0)}%', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        ],
      ),
    );
  }
}

// --- Energy Bar ---
class _EnergyBar extends StatelessWidget {
  const _EnergyBar({required this.energy});
  final double energy;

  Color _color(double e) {
    if (e > 70) return const Color(0xFF4CAF50);
    if (e > 30) return const Color(0xFFFF9800);
    return const Color(0xFFF44336);
  }

  @override
  Widget build(BuildContext context) {
    final pct = (energy / 100).clamp(0.0, 1.0);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
        color: Colors.white,
      ),
      child: Row(
        children: [
          const Icon(Icons.bolt, color: Color(0xFFFF9800)),
          const SizedBox(width: 10),
          const Text('Energy', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
          const SizedBox(width: 12),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(
                value: pct,
                minHeight: 14,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation(_color(energy)),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Text(energy.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
        ],
      ),
    );
  }
}

// --- Stat Chip ---
class _StatChip extends StatelessWidget {
  const _StatChip({required this.icon, required this.label, required this.value});
  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 160,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.grey[300]!),
        color: Colors.white,
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[700]),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: TextStyle(fontSize: 11, color: Colors.grey[600])),
              Text(value, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
            ],
          ),
        ],
      ),
    );
  }
}
