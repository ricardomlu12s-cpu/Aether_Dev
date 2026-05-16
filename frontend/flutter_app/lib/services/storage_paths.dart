import 'dart:io';

class StoragePaths {
  static Directory applicationSupportDir() {
    final home = Platform.environment['HOME'];
    if (home == null || home.isEmpty) {
      throw StateError('HOME is not available');
    }
    return Directory('$home/Library/Application Support/Aether Dev');
  }

  static Directory logsDir() {
    return Directory('${applicationSupportDir().path}/logs');
  }
}
