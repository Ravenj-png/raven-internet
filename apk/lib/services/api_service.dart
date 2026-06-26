import 'dart:convert'; import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:pointycastle/signers/ed25519_signer.dart'; import 'package:pointycastle/asymmetric/ed25519.dart';
import 'package:pointycastle/api.dart'; import 'package:convert/convert.dart';
import 'package:flutter/services.dart' show rootBundle;
class ApiService {
  static const _base = String.fromEnvironment('RAVEN_API', defaultValue:'https://api.ravenstudent.com');
  static Future<Map<String,dynamic>> activateVoucher(String c) async {
    final r=await http.post(Uri.parse('$_base/api/vouchers/activate'), headers:{'Content-Type':'application/json'}, body:jsonEncode({'voucher_code':c}));
    if(r.statusCode!=200) throw Exception('Failed'); final d=jsonDecode(r.body); if(!d['success']) throw Exception(d['message']??'Error'); return d; }
  static Future<List<Map>> getNotifications(String t) async { final r=await http.get(Uri.parse('$_base/api/notifications'), headers:{'Authorization':'Bearer $t'}); return r.statusCode==200?List<Map>.from(jsonDecode(r.body)):[]; }
  static Future<void> disconnectSession(String t) => http.post(Uri.parse('$_base/api/session/disconnect'), headers:{'Authorization':'Bearer $t'});
  static Future<bool> verifySignature(String cfg, String sig) async { try{final pub=(await rootBundle.load('assets/wg_pub.raw')).buffer.asUint8List(); final pk=Ed25519PublicKeyParameters(pub); final s=Ed25519Signer(); s.init(false, PublicKeyParameter(pk)); return s.verifySignature(Uint8List.fromList(utf8.encode(cfg)), base64Decode(sig));}catch{ return false; } }
  static Future<Map> checkVersion() async => jsonDecode((await http.get(Uri.parse('$_base/api/version'))).body);
}
