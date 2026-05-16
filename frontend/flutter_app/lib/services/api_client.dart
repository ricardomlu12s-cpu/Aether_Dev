import 'dart:convert';
import 'dart:io';

class ApiClient {
  ApiClient({
    this.baseUrl = 'http://127.0.0.1:8000',
    this.adminToken = 'dev-admin-token',
  });

  final String baseUrl;
  final String adminToken;

  Future<dynamic> get(String path, {bool admin = false}) async {
    final client = HttpClient();
    final request = await client.getUrl(Uri.parse('$baseUrl$path'));
    if (admin) {
      request.headers.set(
        HttpHeaders.authorizationHeader,
        'Bearer $adminToken',
      );
    }
    final response = await request.close();
    return _decode(response);
  }

  Future<dynamic> post(
    String path,
    Map<String, dynamic> body, {
    bool admin = false,
  }) async {
    final client = HttpClient();
    final request = await client.postUrl(Uri.parse('$baseUrl$path'));
    request.headers.contentType = ContentType.json;
    if (admin) {
      request.headers.set(
        HttpHeaders.authorizationHeader,
        'Bearer $adminToken',
      );
    }
    request.write(jsonEncode(body));
    final response = await request.close();
    return _decode(response);
  }

  Future<dynamic> delete(String path, {bool admin = false}) async {
    final client = HttpClient();
    final request = await client.deleteUrl(Uri.parse('$baseUrl$path'));
    if (admin) {
      request.headers.set(
        HttpHeaders.authorizationHeader,
        'Bearer $adminToken',
      );
    }
    final response = await request.close();
    return _decode(response);
  }

  Future<dynamic> _decode(HttpClientResponse response) async {
    final raw = await response.transform(utf8.decoder).join();
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, raw);
    }
    if (raw.isEmpty) {
      return null;
    }
    return jsonDecode(raw);
  }
}

class ApiException implements Exception {
  ApiException(this.statusCode, this.body);

  final int statusCode;
  final String body;

  @override
  String toString() => 'ApiException($statusCode): $body';
}
