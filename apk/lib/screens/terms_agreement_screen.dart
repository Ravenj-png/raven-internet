import 'package:flutter/material.dart';
import '../services/storage_service.dart';
import 'home_screen.dart';

class TermsAgreementScreen extends StatefulWidget {
  const TermsAgreementScreen({super.key});

  @override
  State<TermsAgreementScreen> createState() => _TermsAgreementScreenState();
}

class _TermsAgreementScreenState extends State<TermsAgreementScreen> {
  bool _read = false;
  bool _agree = false;

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () => Future.value(false),
      child: Scaffold(
        backgroundColor: const Color(0xFF0b1120),
        body: SafeArea(
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: const BoxDecoration(
                  color: Color(0xFF1e293b),
                  borderRadius: BorderRadius.vertical(
                    bottom: Radius.circular(20),
                  ),
                ),
                child: const Column(
                  children: [
                    Text(
                      '🦅 Raven VPN',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF10b981),
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Terms & Copyright Agreement',
                      style: TextStyle(color: Color(0xFF94a3b8)),
                    ),
                  ],
                ),
              ),
              Container(
                margin: const EdgeInsets.all(16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF450a0a),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFef4444)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: Colors.red, size: 24),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        '⚠️ APPEARS ONCE.\nPlease read carefully.',
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                flex: 1,
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '1. Acceptable Use',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const Text(
                        '• Personal, lawful use only.\n'
                        '• No sharing, reselling, or multi-device.\n'
                        '• No torrenting, hacking, or illegal content.\n'
                        '• Violations = instant suspension.',
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        '2. Copyright',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const Text(
                        '• All software & configs are protected.\n'
                        '• Reverse engineering or modification prohibited.\n'
                        '• Do not distribute copyrighted material.',
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        '3. Service',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const Text(
                        '• Provided "as-is". Payments non-refundable after activation.\n'
                        '• Raven reserves right to suspend for network protection.',
                      ),
                    ],
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1e293b),
                  border: const Border(
                    top: BorderSide(color: Color(0xFF334155)),
                  ),
                ),
                child: Column(
                  children: [
                    CheckboxListTile(
                      value: _read,
                      onChanged: (v) => setState(() => _read = v ?? false),
                      title: const Text(
                        'I read & accept Terms & Acceptable Use',
                        style: TextStyle(color: Colors.white, fontSize: 13),
                      ),
                      dense: true,
                      activeColor: const Color(0xFF10b981),
                    ),
                    CheckboxListTile(
                      value: _agree,
                      onChanged: (v) => setState(() => _agree = v ?? false),
                      title: const Text(
                        'I agree not to modify or redistribute APK',
                        style: TextStyle(color: Colors.white, fontSize: 13),
                      ),
                      dense: true,
                      activeColor: const Color(0xFF10b981),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: (_read && _agree) ? _accept : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF10b981),
                          disabledBackgroundColor: const Color(0xFF334155),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        child: const Text(
                          '✅ I AGREE',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _accept() async {
    await StorageService.acceptTerms();
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const HomeScreen()),
    );
  }
}
