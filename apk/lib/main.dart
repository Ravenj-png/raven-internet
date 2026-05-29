import 'package:flutter/material.dart';
import 'screens/connect_screen.dart';
void main() => runApp(const RavenVpnApp());
class RavenVpnApp extends StatelessWidget {
  const RavenVpnApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Raven VPN', debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue, scaffoldBackgroundColor: const Color(0xFF0f172a), useMaterial3: true),
      home: const ConnectScreen(),
    );
  }
}
