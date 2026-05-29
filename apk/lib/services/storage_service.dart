import 'package:flutter_secure_storage/flutter_secure_storage.dart';
class StorageService {
  static final _storage = const FlutterSecureStorage();
  static Future<void> saveJwtToken(String token) async => await _storage.write(key: 'jwt_token', value: token);
  static Future<String?> getJwtToken() async => await _storage.read(key: 'jwt_token');
  static Future<void> clearSession() async { await _storage.delete(key: 'jwt_token'); }
}
