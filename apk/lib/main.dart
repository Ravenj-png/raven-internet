import 'package:flutter/material.dart';
import 'screens/terms_agreement_screen.dart';
import 'screens/home_screen.dart';
import 'services/storage_service.dart';

void main() { WidgetsFlutterBinding.ensureInitialized(); runApp(const RavenVpnApp()); }
class RavenVpnApp extends StatelessWidget {
  const RavenVpnApp({super.key});
  @override Widget build(BuildContext context) => MaterialApp(
    title: 'Raven VPN', debugShowCheckedModeBanner: false,
    theme: ThemeData(primarySwatch: Colors.blue, scaffoldBackgroundColor: const Color(0xFF0b1120), useMaterial3: true),
    home: const StartupRouter());
}
class StartupRouter extends StatefulWidget {
  const StartupRouter({super.key}); @override State<StartupRouter> createState() => _StartupRouterState();
}
class _StartupRouterState extends State<StartupRouter> {
  @override void initState() { super.initState(); _route(); }
  Future<void> _route() async {
    final ok = await StorageService.isTermsAccepted();
    if (!mounted) return;
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => ok ? const HomeScreen() : const TermsAgreementScreen()));
  }
  @override Widget build(BuildContext context) => const Scaffold(body: Center(child: CircularProgressIndicator()));
}
