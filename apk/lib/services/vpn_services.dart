import 'package:wireguard_flutter/wireguard_flutter.dart';
class VpnService { static final wg=WireGuardFlutter.instance;
  static Future<void> connect(String cfg, String ep) async { await wg.initialize(interfaceName:'wg0'); await wg.startVpn(serverAddress:ep, wgQuickConfig:cfg, providerBundleIdentifier:'com.ravenvpn.app'); }
  static Future<void> disconnect() => wg.stopVpn(); }
