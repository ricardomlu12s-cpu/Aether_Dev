import 'package:flutter/material.dart';

import 'screens/chat_screen.dart';
import 'screens/developer_dashboard.dart';
import 'screens/memory_viewer.dart';
import 'services/app_launcher.dart';

void main() {
  runApp(const AetherDevApp());
}

class AetherDevApp extends StatelessWidget {
  const AetherDevApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Aether Dev',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xff2f6f6d),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      home: const ShellScreen(),
    );
  }
}

class ShellScreen extends StatefulWidget {
  const ShellScreen({super.key});

  @override
  State<ShellScreen> createState() => _ShellScreenState();
}

class _ShellScreenState extends State<ShellScreen> {
  int selectedIndex = 0;
  BackendProcessHandle? backendHandle;
  String backendStatus = 'External backend';

  @override
  void initState() {
    super.initState();
    startBackendIfConfigured();
  }

  Future<void> startBackendIfConfigured() async {
    final handle = await AppLauncher().startFromEnvironment();
    if (!mounted) return;
    setState(() {
      backendHandle = handle;
      backendStatus = handle == null
          ? 'External backend'
          : 'Managed dev backend';
    });
  }

  @override
  void dispose() {
    backendHandle?.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      const ChatScreen(),
      const MemoryViewer(),
      const DeveloperDashboard(),
    ];

    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: selectedIndex,
            onDestinationSelected: (index) =>
                setState(() => selectedIndex = index),
            labelType: NavigationRailLabelType.all,
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.chat_bubble_outline),
                selectedIcon: Icon(Icons.chat_bubble),
                label: Text('Chat'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.storage_outlined),
                selectedIcon: Icon(Icons.storage),
                label: Text('Memory'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.dashboard_outlined),
                selectedIcon: Icon(Icons.dashboard),
                label: Text('Runtime'),
              ),
            ],
          ),
          const VerticalDivider(width: 1),
          Expanded(
            child: Column(
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  color: const Color(0xffeef4f2),
                  child: Text(backendStatus),
                ),
                Expanded(child: pages[selectedIndex]),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
