import 'dart:io';

class BackendProcessHandle {
  BackendProcessHandle(this.process);

  final Process process;

  Future<void> stop() async {
    process.kill(ProcessSignal.sigterm);
    await process.exitCode.timeout(
      const Duration(seconds: 5),
      onTimeout: () {
        process.kill(ProcessSignal.sigkill);
        return -1;
      },
    );
  }
}

class AppLauncher {
  static const String projectRootEnv = 'AETHER_PROJECT_ROOT';

  /// Development launcher. Packaged builds should point this to the bundled
  /// backend executable created by PyInstaller.
  Future<BackendProcessHandle> startDevBackend(String projectRoot) async {
    final process = await Process.start(
      'bash',
      ['$projectRoot/scripts/start_backend.sh'],
      workingDirectory: projectRoot,
      mode: ProcessStartMode.normal,
    );
    return BackendProcessHandle(process);
  }

  Future<BackendProcessHandle?> startFromEnvironment() async {
    final projectRoot = Platform.environment[projectRootEnv];
    if (projectRoot == null || projectRoot.isEmpty) {
      return null;
    }
    return startDevBackend(projectRoot);
  }
}
