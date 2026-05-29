import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/vpn_service.dart';
import '../services/storage_service.dart';

class ConnectScreen extends StatefulWidget {
  const ConnectScreen({super.key});
  @override
  State<ConnectScreen> createState() => _ConnectScreenState();
}

class _ConnectScreenState extends State<ConnectScreen> {
  final _codeCtrl = TextEditingController();
  bool _connecting = false, _connected = false;
  int _remainingMB = 1024, _totalMB = 1024;
  DateTime? _expiresAt;
  Timer? _pollTimer;

  @override
  void initState() { super.initState(); _checkExistingSession(); }
  @override
  void dispose() { _pollTimer?.cancel(); _codeCtrl.dispose(); super.dispose(); }

  Future<void> _checkExistingSession() async {
    final token = await StorageService.getJwtToken();
    if (token != null) {
      try {
        final status = await ApiService.getSessionStatus(token);
        setState(() { _connected = true; _remainingMB = status['remaining_mb'] ?? _remainingMB; _totalMB = status['total_mb'] ?? _totalMB; if (status['expires_at'] != null) _expiresAt = DateTime.parse(status['expires_at']); });
        _startPolling(token);
      } catch (_) { await StorageService.clearSession(); }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🦅 Raven VPN'), centerTitle: true, backgroundColor: const Color(0xFF1e3c72)),
      body: Padding(padding: const EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        const Center(child: Column(children: [Icon(Icons.vpn_lock, size: 64, color: Color(0xFF10b981)), SizedBox(height: 16), Text('Enter Your Access Code', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)), SizedBox(height: 8), Text('Code from Raven Student app or SMS', style: TextStyle(color: Colors.grey))])),
        const SizedBox(height: 32),
        TextField(controller: _codeCtrl, keyboardType: TextInputType.text, maxLength: 10, textAlign: TextAlign.center, style: const TextStyle(fontSize: 24, letterSpacing: 2, fontFamily: 'monospace'), decoration: InputDecoration(hintText: 'RVN-XXXXXXX', counterText: '', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)), focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF3b82f6), width: 2)))),
        const SizedBox(height: 24),
        ElevatedButton(onPressed: _connecting || _connected ? null : _connect, style: ElevatedButton.styleFrom(backgroundColor: _connected ? Colors.grey : const Color(0xFF10b981), padding: const EdgeInsets.symmetric(vertical: 16), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))), child: _connecting ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2)) : Text(_connected ? 'Connected' : '🔌 Connect Now', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold))),
        if (_connected) ...[
          const SizedBox(height: 16),
          Container(padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: const Color(0xFF064e3b), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFF10b981))), child: Column(children: [Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text('Status:', style: TextStyle(color: Colors.grey)), Text('🟢 Active', style: const TextStyle(color: Color(0xFF10b981), fontWeight: FontWeight.bold))]), const SizedBox(height: 8), Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text('Data:', style: TextStyle(color: Colors.grey)), Text('$_remainingMB MB / $_totalMB MB', style: const TextStyle(fontWeight: FontWeight.w500))]), if (_expiresAt != null) const SizedBox(height: 4), if (_expiresAt != null) Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text('Expires:', style: TextStyle(color: Colors.grey)), Text('${_timeRemaining()}', style: const TextStyle(fontWeight: FontWeight.w500))])])),
          const SizedBox(height: 16),
          OutlinedButton(onPressed: _disconnect, style: OutlinedButton.styleFrom(foregroundColor: Colors.red, side: const BorderSide(color: Colors.red)), child: const Text('🔌 Disconnect')),
        ],
        const Spacer(),
        Center(child: Text('Need a code? Open Raven Student app or check SMS', style: TextStyle(color: Colors.grey[600], fontSize: 12), textAlign: TextAlign.center)),
      ])),
    );
  }

  String _timeRemaining() { if (_expiresAt == null) return ''; final diff = _expiresAt!.difference(DateTime.now()); return '${diff.inHours}h ${diff.inMinutes.remainder(60)}m'; }

  Future<void> _connect() async {
    final code = _codeCtrl.text.trim().toUpperCase();
    if (!RegExp(r'^[A-Z]{3}-[A-Z0-9]{7}$').hasMatch(code)) { ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter valid code: RVN-XXXXXXX'))); return; }
    setState(() => _connecting = true);
    try {
      final response = await ApiService.activateVoucher(code);
      final token = response['access_token'];
      final configText = response['config'];
      final signature = response['signature'];
      if (!await ApiService.verifyConfigSignature(configText, signature)) throw Exception('Invalid config signature');
      await StorageService.saveJwtToken(token);
      await VpnService.connect(configText);
      setState(() { _connected = true; _connecting = false; });
      _startPolling(token);
    } catch (e) { setState(() => _connecting = false); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Connection failed: $e'))); }
  }

  Future<void> _disconnect() async {
    final token = await StorageService.getJwtToken();
    if (token != null) { await ApiService.disconnectSession(token); await StorageService.clearSession(); }
    await VpnService.disconnect();
    _pollTimer?.cancel();
    setState(() => _connected = false);
  }

  void _startPolling(String token) {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(seconds: 30), (_) async {
      try {
        final status = await ApiService.getSessionStatus(token);
        setState(() { _remainingMB = status['remaining_mb'] ?? _remainingMB; _totalMB = status['total_mb'] ?? _totalMB; if (status['expires_at'] != null) _expiresAt = DateTime.parse(status['expires_at']); });
        if (_remainingMB <= 0) _disconnect();
      } catch (_) {}
    });
  }
}
