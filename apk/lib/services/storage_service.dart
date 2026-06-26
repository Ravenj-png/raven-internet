import 'package:flutter_secure_storage/flutter_secure_storage.dart';
class StorageService {
  static const _s = FlutterSecureStorage();
  static Future<void> saveJwtToken(String t) => _s.write(key:'jwt_token', value:t);
  static Future<String?> getJwtToken() => _s.read(key:'jwt_token');
  static Future<void> clearSession() => _s.delete(key:'jwt_token');
  static Future<bool> isTermsAccepted() async => await _s.read(key:'raven_terms_v1')=='true';
  static Future<void> acceptTerms() => _s.write(key:'raven_terms_v1', value:'true');
}
